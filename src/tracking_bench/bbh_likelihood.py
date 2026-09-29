"""BBH first-token API protocol; deliberately distinct from HF full-choice acc_norm.

Canonical candidates are exact ASCII tokens A..G. No stripping, token merging,
logit bias, or invented scores. A truncated top-k list can certify its best
candidate only when that candidate is strictly above the omitted-token bound.
"""
import math
import json
from .openrouter import request_for, validate_response

INSTRUCTION = ('Select the correct option. Respond with exactly one uppercase letter '
               '(A, B, C, D, E, F, or G) from the options, without parentheses, '
               'whitespace, explanation, or reasoning.')


def messages(question, demos):
    result = [dict(role='system', content=INSTRUCTION)]
    for demo in demos:
        result.extend([dict(role='user', content=demo['input']),
                       dict(role='assistant', content=demo['target'][1:-1])])
    return result + [dict(role='user', content=question['input'])]


def request(chat, model, provider):
    required = {'logprobs', 'top_logprobs', 'temperature', 'top_p', 'max_tokens'}
    if not required <= set(model['supported_parameters']):
        raise ValueError('route lacks required logprob parameters')
    if not chat or any(set(m) != {'role', 'content'} or m['role'] not in ('system','user','assistant')
                       or not isinstance(m['content'], str) for m in chat):
        raise ValueError('invalid messages')
    req = request_for(dict(prompt=''), model, 1, dict(temperature=1, top_p=1),
                      provider, 'text-v2', 'off')
    req.update(messages=chat, logprobs=True, top_logprobs=20)
    return req


def decision(raw, candidates):
    candidates = list(candidates)
    if not candidates or candidates != list('ABCDEFG'[:len(candidates)]):
        raise ValueError('expected canonical A..G candidates')
    scores = dict.fromkeys(candidates)
    result = dict(status='unresolved', prediction=None, candidate_logprobs=scores,
                  missing_candidates=candidates, omitted_logprob_upper_bound=None)
    parsed = validate_response(raw)
    if parsed['status'] not in ('stop','length'):
        return dict(result, reason=parsed['status'])
    try:
        body = json.loads(raw['body'])
        choice = body['choices'][0]
        message = choice['message']
        usage = body.get('usage') or {}
        if not isinstance(usage,dict):
            raise ValueError('invalid usage metadata')
        details = usage.get('completion_tokens_details')
        if details is None:
            details = {}
        if not isinstance(details,dict):
            raise ValueError('invalid reasoning metadata')
        if (any(message.get(k) for k in ('reasoning','reasoning_content','reasoning_details'))
                or (details.get('reasoning_tokens') or 0) > 0):
            raise ValueError('reported reasoning violates first-token protocol')
        content = choice['logprobs']['content']
        # max_tokens=1; extra tokens violate the protocol, including reasoning.
        if not isinstance(content,list) or len(content)!=1:
            raise ValueError('expected exactly one scored output token')
        sample = content[0]
        emitted, emitted_lp = sample['token'], sample['logprob']
        if (not isinstance(emitted,str) or emitted != parsed['text']
                or isinstance(emitted_lp,bool) or not isinstance(emitted_lp,(int,float))
                or not math.isfinite(emitted_lp) or emitted_lp > 0
                or (sample.get('bytes') is not None and sample['bytes'] != list(emitted.encode('utf-8')))):
            raise ValueError('invalid emitted token')
        entries = sample['top_logprobs']
        if not isinstance(entries,list) or not 1 <= len(entries) <= 20:
            raise ValueError('missing top candidates')
        observed = {}
        for entry in entries:
            text, lp = entry['token'], entry['logprob']
            if (not isinstance(text,str) or text in observed or isinstance(lp,bool)
                    or not isinstance(lp,(float,int)) or not math.isfinite(lp)
                    or lp > 0 or lp <= -9999):
                raise ValueError('invalid token probability')
            if entry.get('bytes') is not None and entry['bytes'] != list(text.encode('utf-8')):
                raise ValueError('token byte mismatch')
            observed[text] = lp
        if sum(math.exp(v) for v in observed.values()) > 1.00001:
            raise ValueError('probability mass exceeds one')
        if emitted in observed and abs(emitted_lp-observed[emitted]) > 1e-5:
            raise ValueError('emitted probability contradicts top list')
        if emitted not in observed and emitted_lp > min(observed.values()) + 1e-5:
            raise ValueError('emitted probability contradicts omission bound')
        scores.update({c:observed[c] for c in candidates if c in observed})
        missing = [c for c in candidates if scores[c] is None]
        bound = min(observed.values())
        result.update(missing_candidates=missing, omitted_logprob_upper_bound=bound)
        known = [c for c in candidates if scores[c] is not None]
        if not known:
            return dict(result, reason='no_candidate_in_top_k')
        winner = max(known, key=scores.__getitem__)
        if missing and scores[winner] <= bound:
            return dict(result, reason='tie_at_omission_boundary')
        return dict(result, status='resolved', prediction=winner, reason='complete' if not missing else 'top_k_certificate')
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError) as exc:
        return dict(result, reason='invalid_logprobs', detail=str(exc))


def summarize(rows):
    if not rows:
        raise ValueError('empty planned population')
    total = len(rows)
    resolved = sum(r['prediction'] is not None for r in rows)
    correct = sum(r['prediction'] is not None and r['prediction'] == r['gold'] for r in rows)
    return dict(planned=total, resolved=resolved, correct=correct, coverage=resolved/total,
                accuracy=correct/total if resolved==total else None,
                accuracy_resolved=correct/resolved if resolved else None,
                accuracy_lower=correct/total, accuracy_upper=(correct+total-resolved)/total)


def attempt(out, name, req, transport, ledger, ceiling, limits):
    """Persist before sending; no automatic retry or reuse of an uncertain attempt."""
    from pathlib import Path
    from .common import write_new, digest
    out = Path(out)
    write_new(out/(name+'.request.json'), req)
    attempt_id = 'bbh-token/' + digest(dict(root=str(out.resolve()), name=name))
    ledger.reserve(attempt_id, ceiling, limits)
    raw = transport.complete(req)
    write_new(out/(name+'.response.json'), raw)
    parsed = validate_response(raw)
    try:
        if parsed['cost'] is not None:
            ledger.settle(attempt_id, parsed['cost'])
    except ValueError as exc:
        write_new(out/(name+'.receipt.json'), dict(attempt_id=attempt_id, settlement_error=str(exc), **parsed))
        raise
    write_new(out/(name+'.receipt.json'), dict(attempt_id=attempt_id, **parsed))
    return raw

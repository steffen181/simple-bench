"""Single-use execution plans with receipts before and after each paid attempt."""
from datetime import datetime, timezone
from pathlib import Path
import time
import uuid

from .budget import Budget, money
from .common import digest, file_hash, read_json, write_new
from .corpus import validate_corpus
from .openrouter import OpenRouter, ceiling_for, request_for, validate_response, reasoning_evidence
from .scoring import score


def _now():
    return datetime.now(timezone.utc).isoformat()


def prepare(corpus, config, catalog, out):
    validate_corpus(corpus)
    if set(config) - {'models', 'max_tokens', 'budget_ledger', 'total_budget_usd', 'mode', 'spending_limits'}:
        raise ValueError('unknown config fields (credentials must stay in environment)')
    if config.get('mode') not in ('live', 'offline_fixture'):
        raise ValueError('explicit live/offline_fixture mode required')
    if not corpus['cases'] or not config['models'] or not config['max_tokens']:
        raise ValueError('empty execution plan')
    tokens = config['max_tokens']
    if len(set(tokens)) != len(tokens):
        raise ValueError('duplicate token budgets')
    catalog_models = {m['id']: m for m in catalog['data']}
    if len(catalog_models) != len(catalog['data']):
        raise ValueError('duplicate catalog model')
    models = config['models']
    if len({m['id'] for m in models}) != len(models):
        raise ValueError('duplicate requested model')
    ledger = Budget(config['budget_ledger'], config['total_budget_usd'], mode=config['mode'])
    ledger.snapshot()  # Validate an existing campaign's shared limit.
    config = dict(config, budget_ledger=str(ledger.path))
    schedule = []
    for model in models:
        if set(model) - {'id', 'parameters', 'provider', 'accepted_response_models', 'accepted_response_providers', 'price_policy', 'reasoning_policy'}:
            raise ValueError('unknown model config field')
        info = catalog_models[model['id']]
        for budget in tokens:
            request_for(corpus['cases'][0], info, budget, model.get('parameters'), model.get('provider'), model.get('price_policy'), model.get('reasoning_policy'))
            for case in corpus['cases']:
                item = dict(case_id=case['id'], model=model['id'], max_tokens=budget)
                item['id'] = digest(item)
                schedule.append(item)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'code').mkdir()
    hashes = {}
    for name, value in [('corpus.json', corpus), ('config.json', config), ('catalog.json', catalog), ('schedule.json', schedule)]:
        write_new(out / name, value)
        hashes[name] = file_hash(out / name)
    for path in sorted(Path(__file__).parent.glob('*.py')):
        target = out / 'code' / path.name
        with target.open('xb') as stream:
            stream.write(path.read_bytes())
        hashes[str(target.relative_to(out))] = file_hash(target)
    manifest = dict(schema='benchmark-plan-v1', run_id=uuid.uuid4().hex, created=_now(),
                    execution_kind=config['mode'], corpus_hash=corpus['hash'], hashes=hashes,
                    planned=len(schedule), budget_ledger=str(ledger.path))
    write_new(out / 'manifest.json', manifest)
    return manifest


def _check_hashes(out, hashes):
    for relative, expected in hashes.items():
        path = out / relative
        if not path.is_relative_to(out) or '..' in Path(relative).parts or Path(relative).is_absolute():
            raise ValueError('invalid receipt path')
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f'hash mismatch: {relative}')


def _load_plan(out, executing=False):
    manifest = read_json(out / 'manifest.json')
    if manifest['schema'] != 'benchmark-plan-v1':
        raise ValueError('unsupported plan schema')
    _check_hashes(out, manifest['hashes'])
    corpus = read_json(out / 'corpus.json')
    validate_corpus(corpus)
    if corpus['hash'] != manifest['corpus_hash']:
        raise ValueError('corpus hash mismatch')
    if executing:
        current = {p.name: file_hash(p) for p in Path(__file__).parent.glob('*.py')}
        frozen = {Path(k).name: v for k, v in manifest['hashes'].items() if k.startswith('code/')}
        if current != frozen:
            raise ValueError('implementation changed since plan creation; prepare a new run')
    return manifest, corpus, read_json(out / 'config.json'), read_json(out / 'catalog.json'), read_json(out / 'schedule.json')


def observation(case, raw, model):
    response = validate_response(raw)
    allowed = {model['id'], *model.get('accepted_response_models', [])}
    if response['status'] in ('stop', 'length') and response['model'] not in allowed:
        response['status'] = 'model_identity_mismatch'
    if response['status'] in ('stop', 'length', 'refusal') and model.get('provider'):
        allowed_providers = {model['provider'], *model.get('accepted_response_providers', [])}
        if response['provider'] not in allowed_providers:
            response['status'] = 'provider_identity_mismatch'
    if model.get('reasoning_policy') == 'off' and response['status'] in ('stop', 'length', 'refusal'):
        evidence = reasoning_evidence(raw)
        if evidence != 'off_verified':
            response['status'] = evidence
    return dict(response=response, score=score(case, response))


def run(out, transport=None):
    out = Path(out).resolve()
    manifest, corpus, config, catalog, schedule = _load_plan(out, executing=True)
    if transport is None:
        if config['mode'] != 'live':
            raise ValueError('offline_fixture mode requires an explicit fixture transport')
        transport = OpenRouter()
        if not transport.key:
            raise ValueError('OPENROUTER_API_KEY is not configured')
    elif config['mode'] == 'offline_fixture' and isinstance(transport, OpenRouter):
        raise ValueError('API transport forbidden in offline_fixture mode')
    elif config['mode'] == 'live' and not isinstance(transport, OpenRouter):
        raise ValueError('live mode requires the OpenRouter transport')
    write_new(out / 'claim.json', dict(started=_now(), manifest_hash=file_hash(out / 'manifest.json')))
    for name in ('requests', 'responses', 'receipts'):
        (out / name).mkdir()
    cases = {c['id']: c for c in corpus['cases']}
    models = {m['id']: m for m in config['models']}
    infos = {m['id']: m for m in catalog['data']}
    ledger = Budget(config['budget_ledger'], config['total_budget_usd'], mode=config['mode'])
    reason, observed = None, 0
    for index, item in enumerate(schedule):
        case, model, info = cases[item['case_id']], models[item['model']], infos[item['model']]
        request = request_for(case, info, item['max_tokens'], model.get('parameters'), model.get('provider'), model.get('price_policy'), model.get('reasoning_policy'))
        attempt_id = manifest['run_id'] + ':' + item['id']
        ceiling = ceiling_for(info, item['max_tokens'], model.get('price_policy'))
        try:
            ledger.reserve(attempt_id, ceiling, limits=config.get('spending_limits'))
        except ValueError:
            reason = 'budget_unavailable'
            break
        name = f'{index:06d}.json'
        req_path, raw_path = out / 'requests' / name, out / 'responses' / name
        write_new(req_path, dict(attempt_id=attempt_id, schedule_id=item['id'], request=request, reserved_usd=str(ceiling), started=_now()))
        start = time.monotonic()
        try:
            raw = transport.complete(request)
        except Exception as exc:
            # Never serialize exception text; it can include authorization headers.
            raw = dict(http_status=None, error=type(exc).__name__)
        elapsed = time.monotonic() - start
        write_new(raw_path, raw)  # Durable before JSON parsing/scoring or cost settlement.
        result = observation(case, raw, model)
        response = result['response']
        if response['cost'] is None:
            reason = 'unknown_cost'
        else:
            try:
                ledger.settle(attempt_id, response['cost'])
            except ValueError:
                reason = 'cost_ceiling_exceeded'
        if response['status'] not in ('stop', 'length', 'refusal'):
            reason = response['status'] if reason is None else reason
        write_new(out / 'receipts' / name, dict(schedule_id=item['id'], request_hash=file_hash(req_path),
                  response_hash=file_hash(raw_path), elapsed_seconds=elapsed, **result))
        observed += 1
        if reason:
            break
    summary = dict(status='COMPLETE' if reason is None and observed == len(schedule) else 'STOPPED',
                   reason=reason, observed=observed, planned=len(schedule), finished=_now(),
                   execution_kind=config['mode'], budget=ledger.snapshot())
    write_new(out / 'summary.json', summary)
    # Final seal includes the manifest and every execution receipt. Reports are derived.
    hashes = {str(p.relative_to(out)): file_hash(p) for p in out.rglob('*.json')}
    hashes.update({str(p.relative_to(out)): file_hash(p) for p in (out / 'code').glob('*.py')})
    write_new(out / 'seal.json', hashes)
    verify(out)
    return summary


def verify(out):
    out = Path(out).resolve()
    manifest, corpus, config, catalog, schedule = _load_plan(out)
    if not (out / 'seal.json').exists():
        raise ValueError('run not finalized: NOT_RUN or interrupted; no completeness claim')
    seal = read_json(out / 'seal.json')
    _check_hashes(out, seal)
    expected_paths = {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name != 'seal.json'}
    if set(seal) != expected_paths:
        raise ValueError('unsealed/missing run files')
    claim, summary = read_json(out / 'claim.json'), read_json(out / 'summary.json')
    if claim['manifest_hash'] != file_hash(out / 'manifest.json'):
        raise ValueError('manifest hash mismatch')
    cases, models = {c['id']: c for c in corpus['cases']}, {m['id']: m for m in config['models']}
    infos = {m['id']: m for m in catalog['data']}
    observed = summary['observed']
    if not 0 <= observed <= len(schedule) or len(schedule) != manifest['planned'] or summary['planned'] != len(schedule):
        raise ValueError('invalid coverage')
    for directory in ('requests', 'responses', 'receipts'):
        if sorted(p.name for p in (out / directory).glob('*.json')) != [f'{i:06d}.json' for i in range(observed)]:
            raise ValueError('receipt coverage mismatch')
    technically_complete = True
    for i, item in enumerate(schedule[:observed]):
        name = f'{i:06d}.json'
        receipt, request, raw = [read_json(out / d / name) for d in ('receipts', 'requests', 'responses')]
        case, model = cases[item['case_id']], models[item['model']]
        expected_request = request_for(case, infos[item['model']], item['max_tokens'], model.get('parameters'), model.get('provider'), model.get('price_policy'), model.get('reasoning_policy'))
        if request['request'] != expected_request or request['schedule_id'] != item['id'] or receipt['schedule_id'] != item['id']:
            raise ValueError('request/plan mismatch')
        if receipt['request_hash'] != file_hash(out / 'requests' / name) or receipt['response_hash'] != file_hash(out / 'responses' / name):
            raise ValueError('receipt hash mismatch')
        result = observation(case, raw, model)
        response = result['response']
        ceiling = ceiling_for(infos[item['model']], item['max_tokens'], model.get('price_policy'))
        technically_complete &= (response['status'] in ('stop', 'length', 'refusal')
                                   and response['cost'] is not None
                                   and money(response['cost']) <= ceiling)
        if any(receipt[k] != result[k] for k in result):
            raise ValueError('response/scoring mismatch')
    complete = observed == len(schedule) and summary['reason'] is None and technically_complete
    if (summary['status'] == 'COMPLETE') != complete:
        raise ValueError('false completeness claim')
    return dict(status='VERIFIED', observed=observed, planned=len(schedule), execution_status=summary['status'], manifest_hash=file_hash(out / 'manifest.json'))

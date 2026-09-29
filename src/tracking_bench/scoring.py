"""Frozen owner-explicit-v2 grammar; gold is used only after parsing."""
import re

PARSER_VERSION = 'owner-explicit-v2'


def parse_answer(text, names, obj):
    lines = [line.strip().replace('**', '') for line in text.strip().splitlines() if line.strip()]
    marked = set()
    invalid = False
    for line in lines:
        marker = re.fullmatch(r'(?:Final answer|Answer):\s*(.*)', line)
        if marker:
            body = marker.group(1)
            marked.update(name for name in names if re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', body))
            invalid |= not any(body in (name, name + '.') for name in names)
    if len(marked) > 1:
        return 'ambiguous', None
    if invalid:
        return 'unsupported', None
    last = re.fullmatch(r'(?:Final answer|Answer):\s*([A-Za-z]+)\.?', lines[-1]) if lines else None
    if last:
        return ('accepted', last[1]) if last[1] in names else ('unsupported', None)
    text = text.strip()
    mentioned = {name for name in names if re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', text)}
    if len(mentioned) > 1:
        return 'ambiguous', None
    for name in names:
        if text in (name, name + '.') or (obj is not None and re.fullmatch(re.escape(name) + ' holds the ' + re.escape(obj) + r'(?: now)?\.?', text)):
            return 'accepted', name
    return 'unsupported', None


def score(case, response):
    if 'bbh_protocol' in case:
        from .bbh import score_bbh
        return score_bbh(case, response)
    status = response['status']
    result = dict(status=status, answer=None, person=None, correct=None,
                  strict_correct=None, first_correct=None, first_answer=None)
    if status not in ('stop', 'length'):
        return result
    text = response['text'].strip()
    first = re.match(r'^([A-Za-z]+)(?=\s|[:.!?,]|$)', text)
    first = first[1] if first and first[1] in case['candidates'] else None
    parsed, answer = parse_answer(text, case['candidates'], case['object']) if status == 'stop' else ('truncated', None)
    result.update(status=parsed, answer=answer, person=case['answer_to_person'].get(answer),
                  correct=answer == case['gold'], strict_correct=status == 'stop' and text == case['gold'],
                  first_answer=first, first_correct=first == case['gold'])
    return result

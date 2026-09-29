"""Import sealed historical inputs, replay gold independently, preserve user text."""
from pathlib import Path

from .common import digest, file_hash, read_json
from .scoring import PARSER_VERSION

SOURCES = {
    'discovery': 'verification/functional_discovery_20260918/run',
    'narrative': 'verification/functional_template_diagnosis_20260919/narrative',
    'compact': 'verification/functional_template_diagnosis_20260919/compact',
    'controls': 'verification/functional_controls_20260920/run',
    'bottleneck': 'verification/functional_bottleneck_20260920/run',
    'name_only': 'verification/functional_name_only_20260920/run',
    'answer_budget': 'verification/functional_answer_budget_20260920/run',
    'swap_wording': 'verification/functional_swap_wording_20260921/run',
    'repetition': 'verification/functional_response_repetition_20260923/qwen7b',
    'tokenizer': 'verification/functional_tokenizer_pilot_20260923/run',
    'swap_structures': 'verification/functional_swap_structures_20260923/run',
}
NEW_GENERATORS = {'swap-structures-v1', 'tokenizer-pilot-v1'}
COPY_NAMES = ['Alice', 'Ben', 'Clara', 'David', 'Emma', 'Frank', 'Grace', 'Henry']


def replay(row):
    """Return person index; validate every archived trace state and gold label."""
    state = list(row['initial_state'])
    if sorted(state) != [0, 1, 2, 3] or row['query'] not in range(4):
        raise ValueError('invalid initial state/query')
    modern = row['generator_version'] in NEW_GENERATORS
    handoff = row.get('task_family') == 'handoff'
    if handoff and not modern:
        state = [state.index(obj) for obj in range(4)]
    trace = [state.copy()]
    for event in row['events']:
        if modern:
            kind = event['kind']
            a, b = event.get('source'), event['target']
            if b not in range(4) or (a is not None and a not in range(4)):
                raise ValueError('invalid event person')
            if kind == 'swap':
                state = [b if owner == a else a if owner == b else owner for owner in state]
            elif kind in ('give', 'assign'):
                obj = event['object']
                if kind == 'give' and state[obj] != a:
                    raise ValueError('invalid giver')
                state[obj] = b
            else:
                raise ValueError('unsupported event kind')
        else:
            a, b = event
            if handoff:
                if state[row['query']] != a:
                    raise ValueError('invalid giver')
                state[row['query']] = b
            else:
                state[a], state[b] = state[b], state[a]
        trace.append(state.copy())
    gold = state[row['query']] if modern or handoff else state.index(row['query'])
    if trace != row['oracle_trace'] or gold != row['gold_answer']:
        raise ValueError('oracle mismatch')
    if 'gold_mark' in row and row['gold_mark'] != 'ABCD'[row['answer_order'].index(gold)]:
        raise ValueError('oracle mark mismatch')
    return gold


def _source(repo, directory, name, receipts):
    path = directory / name
    seal = directory.parent / 'sha256.json'
    hashes = read_json(seal)
    relative = str(path.relative_to(repo))
    expected = hashes.get(relative, hashes.get(str(path.relative_to(directory.parent))))
    actual = file_hash(path)
    if expected != actual:
        raise ValueError(f'archive hash mismatch: {relative}')
    receipts[relative] = actual
    receipts[str(seal.relative_to(repo))] = file_hash(seal)
    return read_json(path)


def build_corpus(repo, suites=None):
    repo = Path(repo)
    suites = list(SOURCES) if suites is None else list(suites)
    if not suites or len(set(suites)) != len(suites) or set(suites) - SOURCES.keys():
        raise ValueError('unknown, empty or duplicate suites')
    receipts, cases = {}, []
    for suite in suites:
        directory = repo / SOURCES[suite]
        rows = _source(repo, directory, 'scenarios.json', receipts)
        scenarios = {r['scenario_id']: r for r in rows}
        if len(scenarios) != len(rows):
            raise ValueError('duplicate scenario')
        for row in rows:
            replay(row)
        prompts = _source(repo, directory, 'prompts.json', receipts) if (directory / 'prompts.json').exists() else [dict(scenario_id=r['scenario_id'], condition_id='ownership-mark', prompt=r['prompt']) for r in rows]
        for p in prompts:
            row = scenarios.get(p['scenario_id'])
            condition = p['condition_id']
            if row is None:
                if condition != 'copy-context-free' or p['scenario_id'] not in ['copy-context-free-' + n for n in COPY_NAMES]:
                    raise ValueError('unknown scenario')
                names = COPY_NAMES
                gold = p['scenario_id'].removeprefix('copy-context-free-')
                mapping = {n: i for i, n in enumerate(names)}
                obj, family = None, p['scenario_id']
                stratum = dict(task='copy', k_total=0)
            else:
                names = p.get('names', row.get('entities'))
                is_mark = condition.endswith('-mark') or condition == 'labels'
                mapping = dict(zip('ABCD', p.get('answer_order', row.get('answer_order', [])))) if is_mark else {name: i for i, name in enumerate(names)}
                gold = next(answer for answer, person in mapping.items() if person == row['gold_answer'])
                obj = row.get('objects', ['key', 'book', 'cup', 'ring'])[row['query']]
                family = row['group_id']
                stratum = dict(task=row.get('task_family', 'swap'), k_total=len(row['events']),
                               k_target=row.get('difficulty', {}).get('k_target'), relevant_updates=row.get('relevant_updates'),
                               template=row.get('template_id'), cell=row.get('cell'), word=row.get('word'),
                               query=row['query'], orientation=row.get('orientation'), rotation=row.get('rotation'))
            stratum.update(condition=condition, variant=p.get('variant_id'), repetition=p.get('repetition', 1),
                           alias_set=p.get('alias_set'), legacy_name_group=p.get('token_group'), native_token_group='UNKNOWN')
            candidates = p.get('candidates', list(mapping))
            if set(candidates) != set(mapping):
                raise ValueError('candidate mapping mismatch')
            # Variants share a semantic episode. Structure orientation is excluded
            # explicitly; person rotation, query and alias vocabulary remain fixed.
            pair = dict(suite=suite, scenario=p['scenario_id'], condition=condition,
                        alias=p.get('alias_set'), legacy_group=p.get('token_group'))
            if suite == 'swap_structures':
                pair['scenario'] = [row['word'], row['query'], row['rotation']]
            case = dict(suite=suite, scenario_id=p['scenario_id'], family_id=family,
                        prompt=p['prompt'], prompt_hash=digest(p['prompt']), candidates=candidates,
                        gold=gold, object=obj, answer_to_person=mapping, stratum=stratum,
                        pair_id=digest(pair), control=condition.startswith(('copy', 'lookup')),
                        data_role='discovery', source=SOURCES[suite])
            case['id'] = digest(case)
            cases.append(case)
    corpus = dict(schema='functional-benchmark-corpus-v1', parser=PARSER_VERSION,
                  sources=receipts, suites=suites, cases=cases,
                  limitations=['Reused discovery inputs; not an independent holdout.',
                               'Suite overlap: do not pool as independent observations.',
                               'Native prefill, activations and full candidate teacher scores unsupported.',
                               'Historical token groups are Qwen-specific; native API tokenization UNKNOWN.'])
    corpus['hash'] = digest(corpus)
    validate_corpus(corpus)
    return corpus


def validate_corpus(corpus):
    if corpus.get('hash') != digest({k: v for k, v in corpus.items() if k != 'hash'}):
        raise ValueError('corpus hash mismatch')
    if corpus['schema'] != 'functional-benchmark-corpus-v1' or corpus['parser'] not in (PARSER_VERSION, 'bbh-generative-v1'):
        raise ValueError('unsupported corpus version')
    ids = set()
    if corpus['parser'] != 'bbh-generative-v1' and any('bbh_protocol' in c for c in corpus['cases']):
        raise ValueError('BBH scoring requires BBH corpus version')
    if corpus['parser'] == 'bbh-generative-v1' and any(c.get('bbh_protocol') not in ('direct', 'cot') for c in corpus['cases']):
        raise ValueError('invalid BBH protocol')
    for case in corpus['cases']:
        if case['id'] != digest({k: v for k, v in case.items() if k != 'id'}) or case['prompt_hash'] != digest(case['prompt']):
            raise ValueError('case hash mismatch')
        if case['id'] in ids or case['gold'] not in case['candidates'] or set(case['candidates']) != set(case['answer_to_person']):
            raise ValueError('invalid case identity/labels')
        ids.add(case['id'])

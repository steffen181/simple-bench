"""Development-only paired prompts; historical parser and episodes stay fixed."""
from copy import deepcopy
import random
from .common import digest
from .corpus import validate_corpus

FINAL_INSTRUCTION = ('End your response with exactly one final line: Final answer: NAME. '
                     'Replace NAME with Alice, Ben, Clara, or David.')


def build_pilot(dense):
    validate_corpus(dense)
    selected, seen_prompts = [], set()
    ordered = sorted(dense['cases'], key=lambda c: c['id'])
    for task in ('swap', 'handoff'):
        for k in (0, 2, 8, 32):
            for gold in ('Alice', 'Ben', 'Clara', 'David'):
                options = [c for c in ordered if c['stratum']['task'] == task
                           and c['stratum']['k_total'] == k and c['gold'] == gold
                           and c['stratum']['relevance_group'] == ('all' if k else 'none')
                           and c['prompt_hash'] not in seen_prompts]
                if not options:
                    raise ValueError(f'missing development cell: {task}/{k}/{gold}')
                c = options[0]
                selected.append(c)
                seen_prompts.add(c['prompt_hash'])
                if task == 'swap':
                    controls = [x for x in ordered if x['control'] and x['family_id'] == c['family_id']]
                    if len(controls) != 1:
                        raise ValueError('missing or duplicate copy cell')
                    selected.extend(controls)
    cases = []
    for source in selected:
        for variant in ('original', 'final_line'):
            case = deepcopy(source)
            case.pop('id')
            case.update(development_case_id=source['id'], data_role='development_pilot')
            case['stratum']['variant'] = variant
            if variant == 'final_line':
                case['prompt'] = case['prompt'].rsplit('\n', 1)[0] + '\n' + FINAL_INSTRUCTION
                case['prompt_hash'] = digest(case['prompt'])
            case['id'] = digest(case)
            cases.append(case)
    random.Random(2026092701).shuffle(cases)
    corpus = dict(schema=dense['schema'], parser=dense['parser'], sources={}, suites=dense['suites'],
                  cases=cases, limitations=['Historical development cases; not a holdout.',
                  'Four cases per task/length/variant; all-relevant nonzero events only.',
                  'Copy and swap share episodes; never pool as independent evidence.'])
    corpus['hash'] = digest(corpus)
    validate_corpus(corpus)
    return corpus

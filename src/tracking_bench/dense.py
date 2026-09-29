"""Frozen balanced state-tracking episodes, without answer-dependent selection."""
from itertools import permutations
from math import sqrt
import random
from .common import digest
from .corpus import validate_corpus
from .scoring import PARSER_VERSION

LENGTHS = (0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64)
NAMES = ('Alice', 'Ben', 'Clara', 'David')
OBJECTS = ('key', 'book', 'cup', 'ring')


def wilson(correct, n):
    if not n:
        return None, None
    z = 1.959963984540054
    p, d = correct / n, 1 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (0 if correct == 0 else max(0, center - half),
            1 if correct == n else min(1, center + half))


def _episode(rng, task, k, relevant):
    owners = list(range(4))
    rng.shuffle(owners)
    initial, query = owners.copy(), rng.randrange(4)
    flags = [True] * relevant + [False] * (k - relevant)
    rng.shuffle(flags)
    events = []
    for flag in flags:
        if task == 'swap':
            owner = owners[query]
            if flag:
                a, b = sorted((owner, rng.choice([p for p in range(4) if p != owner])))
            else:
                a, b = sorted(rng.sample([p for p in range(4) if p != owner], 2))
            owners = [b if p == a else a if p == b else p for p in owners]
            events.append(dict(kind='swap', source=a, target=b))
        else:
            obj = query if flag else rng.choice([o for o in range(4) if o != query])
            a = owners[obj]
            b = rng.choice([p for p in range(4) if p != a])
            owners[obj] = b
            events.append(dict(kind='give', object=obj, source=a, target=b))
    return dict(task=task, initial=initial, query=query, events=events), owners[query]


def _cases(episode, gold_index, group, relevant):
    task, initial, query, events = (episode[k] for k in ('task', 'initial', 'query', 'events'))
    family = digest(episode)
    lines = ['Track who holds each object. Follow the events in order.']
    lines += [f'{NAMES[owner]} initially holds the {OBJECTS[obj]}.' for obj, owner in enumerate(initial)]
    for e in events:
        a, b = NAMES[e['source']], NAMES[e['target']]
        lines.append(f'{a} and {b} swap all the objects they hold.' if e['kind'] == 'swap'
                     else f"{a} gives the {OBJECTS[e['object']]} to {b}.")
    prefix = '\n'.join(lines) + '\n'
    for control in ([False, True] if task == 'swap' else [False]):
        question = (f'Repeat this name: {NAMES[gold_index]}.' if control else f'Who holds the {OBJECTS[query]} now?')
        prompt = prefix + 'Question: ' + question + '\nAnswer with only one name: Alice, Ben, Clara, or David.'
        case = dict(suite='dense-v1', scenario_id=family, family_id=family, prompt=prompt,
                    prompt_hash=digest(prompt), candidates=list(NAMES), gold=NAMES[gold_index],
                    object=OBJECTS[query], answer_to_person={n: i for i, n in enumerate(NAMES)},
                    stratum=dict(task='copy' if control else task, k_total=len(events),
                                 relevant_updates=relevant, irrelevant_events=len(events)-relevant,
                                 relevance_group=group, query=query, condition='copy' if control else 'ownership'),
                    pair_id=family, control=control, data_role='prospective_generator_sample',
                    source='dense-v1/seed-2026092501', structure=episode)
        case['id'] = digest(case)
        yield case


def build_dense(seed=2026092501):
    rng = random.Random(seed)
    cases = []
    for task in ('swap', 'handoff'):
        for k in LENGTHS:
            if k == 0:
                for initial in permutations(range(4)):
                    for query in range(4):
                        episode = dict(task=task, initial=list(initial), query=query, events=[])
                        cases.extend(_cases(episode, initial[query], 'none', 0))
                continue
            seen, counts = set(), {}
            for _ in range(100000):
                group = 'half' if sum(v for (g, _), v in counts.items() if g == 'half') < 64 else 'all'
                relevant = k // 2 if group == 'half' else k
                episode, gold = _episode(rng, task, k, relevant)
                identity = digest(episode)
                if identity in seen or counts.get((group, gold), 0) == 16:
                    continue
                seen.add(identity)
                counts[group, gold] = counts.get((group, gold), 0) + 1
                cases.extend(_cases(episode, gold, group, relevant))
                if len(seen) == 128:
                    break
            else:
                raise ValueError('could not fill unique balanced structural cells')
    rng.shuffle(cases)  # Avoid confounding length/task with chronological API drift.
    corpus = dict(schema='functional-benchmark-corpus-v1', parser=PARSER_VERSION,
                  sources={}, suites=['dense-v1'], cases=cases,
                  generator=dict(version='dense-v1', seed=seed, lengths=list(LENGTHS)),
                  limitations=['Distinct indexed structures, not equivalence classes under person/object relabeling.',
                               'Four fixed names/objects; conclusions limited to this generator and vocabulary.',
                               'k=0 exhaustive 96 cases; unavoidable historical structural overlap.',
                               'Copy shares swap episodes; never pool as independent evidence.',
                               'Wilson intervals are descriptive binomial approximations for balanced generator samples.'])
    corpus['hash'] = digest(corpus)
    validate_corpus(corpus)
    return corpus

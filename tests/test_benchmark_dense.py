"""Counterhypothesis: curves count aliases, invalid transfers or wrong gold."""
from collections import Counter, defaultdict
import re
from tracking_bench.dense import build_dense, wilson
from tracking_bench.corpus import validate_corpus


def test_dense_balance_uniqueness_and_independent_text_replay():
    corpus = build_dense()
    validate_corpus(corpus)
    assert corpus == build_dense()
    assert len(corpus['cases']) == 4512
    groups = defaultdict(list)
    pairs = defaultdict(list)
    for c in corpus['cases']:
        groups[c['stratum']['task'], c['stratum']['k_total']].append(c)
        pairs[c['family_id']].append(c)
        state = {n: set() for n in c['candidates']}
        relevant = 0
        for sentence in c['prompt'].split('\n'):
            if m := re.fullmatch(r'(\w+) initially holds the (\w+)\.', sentence):
                state[m[1]].add(m[2])
            elif m := re.fullmatch(r'(\w+) and (\w+) swap all the objects they hold\.', sentence):
                relevant += c['object'] in state[m[1]] | state[m[2]]
                state[m[1]], state[m[2]] = state[m[2]], state[m[1]]
            elif m := re.fullmatch(r'(\w+) gives the (\w+) to (\w+)\.', sentence):
                assert m[2] in state[m[1]]
                relevant += m[2] == c['object']
                state[m[1]].remove(m[2]); state[m[3]].add(m[2])
        assert next(n for n, objects in state.items() if c['object'] in objects) == c['gold']
        assert relevant == c['stratum']['relevant_updates']
    for (task, k), rows in groups.items():
        assert len(rows) == (96 if k == 0 else 128)
        assert len({c['family_id'] for c in rows}) == len(rows)
        assert set(Counter(c['gold'] for c in rows).values()) == {len(rows) // 4}
        if k:
            assert Counter(c['stratum']['relevance_group'] for c in rows) == {'half': 64, 'all': 64}
    for rows in pairs.values():
        if len(rows) == 2:
            swap, copy = sorted(rows, key=lambda c: c['control'])
            assert swap['stratum']['task'] == 'swap' and copy['stratum']['task'] == 'copy'
            assert swap['prompt'].split('Question:')[0] == copy['prompt'].split('Question:')[0]
            assert swap['gold'] == copy['gold']
        else:
            assert rows[0]['stratum']['task'] == 'handoff'


def test_wilson_uncertainty_and_empty():
    assert wilson(0, 0) == (None, None)
    low, high = wilson(64, 128)
    assert .41 < low < .42 and .58 < high < .59
    assert wilson(0, 128)[0] == 0
    assert wilson(128, 128)[1] == 1

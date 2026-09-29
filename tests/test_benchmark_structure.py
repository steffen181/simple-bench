"""Counterhypothesis: aliases hide leakage, or equal endpoints hide different paths."""
from copy import deepcopy
from itertools import permutations
import pytest
from tracking_bench.structure import solve, canonical_structure, structure_audit


def episode():
    return dict(task='swap', initial=[2,0,1], query=0,
                events=[dict(kind='swap',source=2,target=0),dict(kind='swap',source=0,target=1)])


def test_solver_uses_real_possessions_and_rejects_invalid_giver():
    assert solve(episode()) == 1
    give = dict(task='handoff',initial=[0,1,2],query=0,events=[
        dict(kind='give',object=0,source=0,target=1),dict(kind='give',object=0,source=1,target=2)])
    assert solve(give) == 2
    bad = deepcopy(give); bad['events'][1]['source'] = 0
    with pytest.raises(ValueError,match='giver'): solve(bad)
    with pytest.raises(ValueError): canonical_structure(bad)
    with pytest.raises(ValueError): solve(dict(give,initial=[0,0,2]))
    with pytest.raises(ValueError): solve(dict(give,query=-1))


def relabel(e, people, objects):
    out = deepcopy(e)
    for obj, owner in enumerate(e['initial']):
        out['initial'][objects[obj]] = people[owner]
    out['query'] = objects[e['query']]
    for event in out['events']:
        event['source'], event['target'] = people[event['source']], people[event['target']]
        if 'object' in event: event['object'] = objects[event['object']]
    return out


def test_structure_is_invariant_under_all_renamings_and_swap_endpoint_order():
    e = episode()
    identity = canonical_structure(e)
    for people in permutations(range(3)):
        for objects in permutations(range(3)):
            renamed = relabel(e,people,objects)
            assert solve(renamed) == people[1]
            assert canonical_structure(renamed) == identity
            for event in renamed['events']:
                event['source'],event['target'] = event['target'],event['source']
            assert canonical_structure(renamed) == identity


def test_order_and_directed_give_are_preserved_but_zero_event_task_aliases_collapse():
    e = episode()
    assert canonical_structure(dict(e,events=list(reversed(e['events'])))) != canonical_structure(e)
    a = dict(task='swap',initial=[0,1,2],query=0,events=[])
    b = dict(task='handoff',initial=[2,0,1],query=2,events=[])
    assert canonical_structure(a) == canonical_structure(b)
    assert canonical_structure(dict(a,initial=[0,1,2,3])) != canonical_structure(a)
    give = dict(task='handoff',initial=[0,1,2],query=0,events=[dict(kind='give',object=0,source=0,target=1)])
    assert canonical_structure(give) == canonical_structure(relabel(give,[2,0,1],[1,2,0]))
    assert canonical_structure(give) != canonical_structure(dict(a,events=[dict(kind='swap',source=0,target=1)]))


def test_audit_counts_aliases_and_fails_closed_on_missing_structure():
    a = {'structure': episode(), 'stratum': {'task':'swap','k_total':2}}
    b = dict(a, structure=relabel(episode(),[2,0,1],[1,2,0]))
    result = structure_audit([a,b])
    assert result['cases'] == 2 and result['canonical_structures'] == 1
    with pytest.raises(ValueError,match='structure'): structure_audit([{}])

import importlib
import random
from copy import deepcopy
import pytest
from tracking_bench.structure import canonical_structure
from tracking_bench.ladder import replay_text, _episode


def modules():
    return importlib.import_module('tracking_bench.structure_large'), importlib.import_module('tracking_bench.ladder_v2')


def renamed(e, rng):
    n=len(e['initial']);persons=list(range(n));objects=list(range(n));rng.shuffle(persons);rng.shuffle(objects)
    out=deepcopy(e);out['initial']=[0]*n;out['query']=objects[e['query']]
    for obj,owner in enumerate(e['initial']):out['initial'][objects[obj]]=persons[owner]
    for event in out['events']:
        event['source']=persons[event['source']];event['target']=persons[event['target']]
        if 'object' in event:event['object']=objects[event['object']]
    return out


def test_graph_classes_match_exact_small_oracle_and_renaming():
    s,_=modules();rng=random.Random(811);old_to_new={};new_to_old={}
    for n in (3,4,5):
        for task in ('swap','handoff'):
            for _ in range(35):
                e,_=_episode(rng,n,5,rng.randrange(6),task)
                old=canonical_structure(e);new=s.canonical_id(e)
                assert old_to_new.setdefault(old,new)==new
                assert new_to_old.setdefault(new,old)==old
                assert s.canonical_id(renamed(e,rng))==new
                if task=='swap':
                    reverse=deepcopy(e)
                    for event in reverse['events']:event['source'],event['target']=event['target'],event['source']
                    assert s.canonical_id(reverse)==new
    assert s.canonical_id(dict(task='swap',initial=list(range(64)),query=0,events=[]))!=s.canonical_id(dict(task='swap',initial=list(range(63)),query=0,events=[]))
    assert s.canonical_id(dict(task='swap',initial=[0,1,2],query=0,events=[]))==s.canonical_id(dict(task='handoff',initial=[0,1,2],query=0,events=[]))


def test_large_ladder_replay_groups_and_exclusions():
    s,g=modules();args=dict(entities=[10,32,64],steps=[32],relevant_updates=16,tasks=['swap','handoff'],per_cell=2,seed=71)
    a=g.generate(**args);assert a==g.generate(**args);assert len(a['cases'])==24
    groups=set()
    for c in a['cases']:
        assert replay_text(c['prompt'])==c['gold']==g.NAMES[s.solve(c['structure'])]
        assert c['canonical_id']==s.canonical_id(c['structure'])
        e=c['structure'];owners=e['initial'].copy();updates=0
        for event in e['events']:
            prev=owners[e['query']];x,y=event['source'],event['target']
            if event['kind']=='swap':owners=[y if p==x else x if p==y else p for p in owners]
            else:owners[event['object']]=y
            updates+=prev!=owners[e['query']]
        assert updates==16
        groups.add(c['canonical_id'])
    assert len(groups)==12
    b=g.generate(**args,blocked=groups);assert groups.isdisjoint(c['canonical_id'] for c in b['cases'])


def test_legacy_exclusions_and_invalid_grid():
    _,g=modules();a=g.generate([3],[8],4,['swap'],1,44,[])
    blocked=[canonical_structure(c['structure']) for c in a['cases']]
    b=g.generate([3],[8],4,['swap'],1,44,blocked)
    assert set(blocked).isdisjoint(canonical_structure(c['structure']) for c in b['cases'])
    for args in [dict(entities=[65]),dict(steps=[129]),dict(relevant_updates=99),dict(tasks=['wrong']),dict(entities=[True])]:
        with pytest.raises(ValueError):g.generate(**args)
    assert g.generate([64],[0],0,['swap'],1,5,[])['cases']
    with pytest.raises(ValueError):g.generate([64],[0],0,['swap'],2,5,[])

import json
from pathlib import Path
import pytest
from test_structured_campaign import fixture_inputs,Fixture
from tracking_bench.common import read_json,file_hash


def mod():
    from tracking_bench import factorial_campaign
    return factorial_campaign


def test_full_grid_is_fresh_and_crosses_all_axes():
    m=mod();cases=m.population([],groups_per_seed=1)
    assert len(cases)==432
    cells={}
    for c in cases:
        s=c['stratum'];key=(s['entities'],s['relevant_updates'],s['irrelevant_events'],s['task'])
        assert s['k_total']==s['relevant_updates']+s['irrelevant_events']
        cells.setdefault(key,set()).add(c['canonical_id'])
    assert len(cells)==72 and all(len(v)==3 for v in cells.values())
    assert len(set.union(*cells.values()))==216
    blocked=[c['canonical_id'] for c in cases]
    fresh=m.population(blocked,levels=[7],relevant=[8],distractors=[8],seeds=[20261221],groups_per_seed=2)
    assert not set(blocked)&{c['canonical_id'] for c in fresh}


def test_custom_budget_and_phase_replay(tmp_path):
    m=mod();catalog,eps=fixture_inputs();cases=m.population([],levels=[7],relevant=[4],distractors=[8],seeds=[20261211])
    root=tmp_path/'run';m.freeze_population(root,cases,catalog,eps,[],[],'0.10',{'develop':'0.10'},dict(stage='develop'),mode='offline_fixture')
    from tracking_bench import structured_campaign as runner
    r=runner.run(root,transport=Fixture());assert r['status']=='COMPLETE' and r['observed']==8
    assert runner.audit(root)['status']=='PASS'
    assert set(r['phases'])=={'develop'}
    assert read_json(root/'protocol.json')['cap']=='0.10'


def test_prior_spend_is_derived_and_duplicates_rejected(tmp_path):
    from tracking_bench.budget import Budget
    m=mod();ledger=tmp_path/'prior.json';b=Budget(ledger,'1',mode='offline_fixture');b.reserve('x','.5');b.settle('x','.2')
    prior=dict(path=str(ledger),hash=file_hash(ledger),spent='0')
    with pytest.raises(ValueError,match='spend'):m.validate_priors([prior],'1')
    prior['spent']='0.2'
    assert m.validate_priors([prior],'1')=='0.2'
    with pytest.raises(ValueError,match='duplicate'):m.validate_priors([prior,prior],'1')
    b.reserve('unknown','.1');prior['hash']=file_hash(ledger)
    with pytest.raises(ValueError,match='unsettled'):m.validate_priors([prior],'1')


def test_confirmation_support_excludes_small_finite_cells():
    m=mod();selection={'cells':[dict(task='swap',n=7,r=4,d=0),dict(task='handoff',n=7,r=8,d=8)]}
    cases,unsupported=m.confirmation_population(selection,[])
    assert len(cases)==48 and len({c['canonical_id'] for c in cases})==24
    assert len(unsupported)==1 and unsupported[0]['cell']['r']==4

from collections import Counter
from pathlib import Path
import pytest
from tracking_bench.common import read_json
from test_structured_campaign import fixture_inputs,Fixture


def test_full_balanced_swap_grid_and_round_schedule():
    from tracking_bench.swap_curves import population,balanced
    cases=population([])
    counts=Counter((c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) for c in cases)
    assert len(counts)==36 and set(counts.values())=={18}
    assert {c['stratum']['entities'] for c in cases}=={4,8,16,32}
    assert all(c['stratum']['task']=='swap' for c in cases)
    assert len({c['canonical_id'] for c in cases})==324
    ordered=balanced(cases)
    for offset in range(0,len(ordered),72):
        block=ordered[offset:offset+72]
        assert len({(c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) for c in block})==36
        assert len({c['stratum']['seed'] for c in block})==1
    assert len({c['id'] for c in ordered})==648


def test_new_budget_scope_keeps_history_separate_and_replays(tmp_path):
    from tracking_bench.swap_curves import freeze,audit,analyze
    from tracking_bench import structured_campaign as runner
    catalog,endpoints=fixture_inputs();root=tmp_path/'study'
    freeze(root,catalog,endpoints,[],[],history_spent='2.839507050',mode='offline_fixture')
    p=read_json(root/'protocol.json')
    assert p['cap']=='3.75' and p['priors']==[] and p['prior_spent']=='0'
    assert p['design']['historical_spent']=='2.839507050' and p['format_errors_as_wrong'] is True
    assert len(p['schedule'])==1300
    runner.run(root,transport=Fixture());result=audit(root)
    assert result['summary']['observed']==1300 and result['summary']['status']=='COMPLETE'
    data=analyze(root)
    assert data['axes']['n']==[4,8,16,32] and data['presentation']['kind']=='swap-curves'
    assert data['budget']['total_accounted']=='0.01300'
    assert len(data['descriptive']['pairs'])==36 and not data['inference']
    from tracking_bench.factorial_dashboard import export
    export(data,tmp_path/'dashboard')
    print('SWAP_FIXTURE_DASHBOARD',tmp_path/'dashboard')

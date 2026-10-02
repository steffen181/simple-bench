"""Descriptive output must preserve pairing, missingness and strict format failures."""
import pytest
from tracking_bench.campaign_contract import MODELS


def records():
    rows=[]
    for group,seed in [('g1',1),('g2',2),('g3',3)]:
        for rotation in range(2):
            c=dict(canonical_id=group,stratum=dict(task='swap',entities=7,relevant_updates=8,irrelevant_events=8,k_total=16,seed=seed,variant=f'rotation{rotation}'))
            for model in MODELS:
                correct=(group=='g3' or group=='g2' and rotation==0) if model.startswith('openai/') else True
                receipt=dict(audit=dict(technical_ok=True),score=dict(correct=correct,status='accepted'))
                if group=='g1' and rotation==0 and model.startswith('openai/'):receipt['score']['status']='invalid_json'
                rows.append(('develop',c,model,receipt))
    return rows


def test_group_scores_preserve_two_rotations_and_paired_differences():
    # Collapsing rotations to separate independent observations or losing pairing must fail.
    from tracking_bench.factorial_descriptive import describe
    d=describe(records());assert len(d['groups'])==6 and len(d['cells'])==2
    a=next(c for c in d['cells'] if c['model'].startswith('openai/'))
    assert a['group_count']==3 and a['complete_groups']==3
    assert a['mean']==.5 and a['minimum']==0 and a['maximum']==1
    assert a['distribution']=={'0':1,'1':1,'2':1} and a['format_failures']==1
    scores=[g['score'] for g in d['groups'] if g['model'].startswith('openai/')]
    assert sorted(scores)==[0,.5,1]
    pair=d['pairs'][0];assert pair['difference']==-.5
    assert sorted(g['difference'] for g in pair['groups'])==[-1,-.5,0]
    assert describe(list(reversed(records())))==d


def test_partial_or_technical_group_stays_unknown_and_phases_are_separate():
    from tracking_bench.factorial_descriptive import describe
    rows=records();phase,c,model,r=rows[0];rows[0]=(phase,c,model,None)
    d=describe(rows);cell=next(c for c in d['cells'] if c['model']==model)
    assert cell['mean'] is None and cell['complete_groups']==2 and cell['group_count']==3
    assert d['pairs'][0]['difference'] is None and len(d['pairs'][0]['groups'])==3
    assert sum(g['difference'] is None for g in d['pairs'][0]['groups'])==1
    rows[0]=(phase,c,model,dict(audit=dict(technical_ok=False),score=dict(correct=None,status='transport_error')))
    assert next(c for c in describe(rows)['cells'] if c['model']==model)['mean'] is None
    fresh=[('confirm',c,m,r) for _,c,m,r in records()]
    assert len(describe(records()+fresh)['cells'])==4


def test_export_contains_group_values_and_keeps_formal_results_in_appendix(tmp_path):
    from tracking_bench.factorial_dashboard import export
    from tracking_bench.factorial_descriptive import describe
    import json
    data=dict(cells=[],limitations=[],descriptive=describe(records()),inference=[dict(status='INCONCLUSIVE',effect=.4)])
    export(data,tmp_path/'out');public=json.loads((tmp_path/'out/results.json').read_text())
    assert public['descriptive']==data['descriptive']
    assert public['inference']==data['inference']
    assert (tmp_path/'out/groups.csv').exists()
    html=(tmp_path/'out/index.html').read_text()
    assert '<details id="methods"' in html and 'id="group-detail"' in html
    report=(tmp_path/'out/REPORT.md').read_text()
    assert report.index('Beobachtete Ergebnisse')<report.index('Methodenanhang')


def test_technical_error_is_unknown_even_if_every_request_has_receipt(tmp_path):
    import json
    from tracking_bench.factorial_dashboard import export
    data=dict(cells=[dict(phase='develop',task='swap',model='openai/gpt-6-luna',seed='all',n=7,k=16,relevant_updates=8,d=8,correct=1,observed=2,technical_ok=1,planned=2,accuracy_all_planned=.5)],limitations=[])
    export(data,tmp_path/'out')
    assert json.loads((tmp_path/'out/results.json').read_text())['cells'][0]['display_accuracy'] is None

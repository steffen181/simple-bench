import importlib
import pytest
from test_frontier_campaign import inputs,Fixture


def test_aggregate_coverage_pairing_and_no_private_data(tmp_path):
    m=importlib.import_module('tracking_bench.frontier_campaign');a=importlib.import_module('tracking_bench.frontier_analysis')
    catalog,eps=inputs();root=tmp_path/'c';m.freeze({'mode':'offline_fixture'},catalog,eps,root);m.execute_phase(root,'gate',transport=Fixture())
    result=a.analyze_campaign(root)
    assert result['execution_kind']=='offline_fixture' and result['native_acc_norm'] is None
    assert sum(c['observed'] for c in result['cells'] if c['task']=='all' and c['seed']=='all')==8
    assert all(c['accuracy_all_planned']==1 for c in result['cells'])
    assert all(p['difference']==0 for p in result['comparisons'])
    import json
    assert 'attempt_id' not in json.dumps(result) and 'request_id' not in json.dumps(result)


def test_group_bootstrap_uses_shared_rotations_and_models():
    a=importlib.import_module('tracking_bench.frontier_analysis')
    rows=[dict(group=str(i),seed=1,task='swap',left=v,right=0.) for i,v in enumerate([0.,0.,1.,1.])]
    r=a.paired_interval(rows,seed=91,reps=200)
    assert r['difference']==.5 and r['groups']==4 and r['ci'][0]<=.5<=r['ci'][1]
    assert r==a.paired_interval(rows,seed=91,reps=200)


def test_difference_sign_is_luna_minus_sonnet_after_json_roundtrip(tmp_path):
    import json
    from tracking_bench.frontier_campaign import freeze,execute_phase,_block
    from tracking_bench.ladder_v2 import generate,NAMES
    from tracking_bench.frontier_analysis import analyze_campaign
    catalog,eps=inputs();root=tmp_path/'c';freeze({'mode':'offline_fixture'},catalog,eps,root);execute_phase(root,'gate',transport=Fixture())
    class Asymmetric(Fixture):
        def complete(self,request):
            raw=super().complete(request);body=json.loads(raw['body'])
            if request['model'].startswith('anthropic/'):
                body['choices'][0]['message']['content']=next(n for n in NAMES[:3] if n!=body['choices'][0]['message']['content'])
            raw['body']=json.dumps(body);return raw
    cases=generate([3],[4],2,['swap'],1,872,[])['cases']
    _block(root,'smoke','asymmetric',cases,Asymmetric())
    comparisons=[c for c in analyze_campaign(root)['comparisons'] if c['phase']=='smoke']
    assert all(c['left']=='openai/gpt-6-luna' and c['right']=='anthropic/claude-sonnet-5' and c['difference']==1 for c in comparisons)


def test_bbh_original_groups_are_not_option_rotation_pairs(tmp_path):
    from tracking_bench.frontier_campaign import freeze,execute_phase,_block
    from tracking_bench.ladder_v2 import generate
    from tracking_bench.frontier_analysis import analyze_campaign
    catalog,eps=inputs();root=tmp_path/'c';freeze({'mode':'offline_fixture'},catalog,eps,root);execute_phase(root,'gate',transport=Fixture())
    # A BBH original subset can contain multiple questions in one structure group.
    _block(root,'bbh','original-group-fixture',generate([3],[4],2,['swap'],1,987,[])['cases'],Fixture())
    cells=[c for c in analyze_campaign(root)['cells'] if c['phase']=='bbh']
    assert cells and all(c['rotation_pairs']==0 and c['rotation_agreement'] is None for c in cells)


def test_unequal_cluster_sizes_preserve_question_weighted_estimand():
    from tracking_bench.frontier_analysis import paired_interval
    rows=[dict(group='a',seed=1,task='swap',left=1.,right=0.,weight=3),dict(group='b',seed=1,task='swap',left=0.,right=0.,weight=1)]
    result=paired_interval(rows,reps=200)
    assert result['difference']==.75 and result['groups']==2


def test_token_limit_endings_remain_visible_separately_from_parser(tmp_path):
    import json
    from tracking_bench.frontier_campaign import freeze,execute_phase,_block
    from tracking_bench.ladder_v2 import generate
    from tracking_bench.frontier_analysis import analyze_campaign
    catalog,eps=inputs();root=tmp_path/'c';freeze({'mode':'offline_fixture'},catalog,eps,root);execute_phase(root,'gate',transport=Fixture())
    class Limited(Fixture):
        def complete(self,request):
            raw=super().complete(request);body=json.loads(raw['body']);body['choices'][0]['finish_reason']='length';raw['body']=json.dumps(body);return raw
    _block(root,'smoke','limited',generate([3],[4],2,['swap'],1,723,[])['cases'],Limited())
    cells=[c for c in analyze_campaign(root)['cells'] if c['phase']=='smoke']
    assert cells and all(c['length_terminated']==c['observed'] and c['finish_counts']=={'length':c['observed']} for c in cells)

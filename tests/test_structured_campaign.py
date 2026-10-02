import json
import pytest
from tracking_bench.common import read_json,file_hash
from test_frontier_campaign import inputs


def module():
    from tracking_bench import structured_campaign
    return structured_campaign


def fixture_inputs():
    catalog,endpoints=inputs()
    for item in endpoints.values():item['data']['endpoints'][0]['supported_parameters']+=['response_format','structured_outputs']
    return catalog,endpoints


class Fixture:
    def __init__(self,broken=False):self.broken=broken;self.calls=0
    def complete(self,request):
        self.calls+=1
        if self.broken:return {'http_status':502,'body':'[]'}
        from tracking_bench.ladder import replay_text
        answer=replay_text(request['messages'][0]['content'].split('\n\n')[1])
        return {'http_status':200,'body':json.dumps(dict(model=request['model'],provider='OpenAI' if request['model'].startswith('openai/') else 'Anthropic',choices=[dict(finish_reason='stop',message={'content':json.dumps({'answer':answer})})],usage=dict(cost=.00001,prompt_tokens=100,completion_tokens=12,completion_tokens_details={'reasoning_tokens':0})))}


def freeze_fixture(tmp_path):
    m=module();catalog,endpoints=fixture_inputs();root=tmp_path/'run'
    m.freeze(root,catalog,endpoints,[],[],[],mode='offline_fixture',levels=[3,7],seeds=[20261111,20261112,20261113])
    return m,root


def test_fresh_groups_fixed_population_and_full_replay(tmp_path):
    m,root=freeze_fixture(tmp_path);p=read_json(root/'protocol.json')
    gate={c['canonical_id'] for c in p['cases'] if c['phase']=='gate'}
    main=[c for c in p['cases'] if c['phase']=='confirm']
    assert len(main)==48 and len({c['canonical_id'] for c in main})==24
    assert gate.isdisjoint(c['canonical_id'] for c in main)
    result=m.run(root,transport=Fixture());assert result['status']=='COMPLETE' and result['observed']==108
    a=m.audit(root);assert a['status']=='PASS'
    public=m.analyze(root);cells=[c for c in public['cells'] if c['phase']=='confirm' and c['task']=='all' and c['seed']=='all']
    assert len(cells)==4 and all(c['correct']==24 and c['groups']==12 and c['rotation_agreement']==1 for c in cells)
    assert public['conditions']['max_tokens']==256 and public['native_acc_norm'] is None
    with pytest.raises(ValueError):m.run(root,transport=Fixture())


def test_unknown_charge_stops_without_retry_and_keeps_population(tmp_path):
    m,root=freeze_fixture(tmp_path);f=Fixture(True);r=m.run(root,transport=f)
    assert r['observed']==1 and r['planned']==108 and f.calls==1
    a=m.audit(root);assert float(a['budget']['reserved'])>0
    cells=m.analyze(root)['cells'];assert all(c['accuracy_all_planned'] is None for c in cells if c['phase']=='confirm')


def test_model_pair_budget_check_leaves_no_extra_request(tmp_path,monkeypatch):
    m,root=freeze_fixture(tmp_path)
    monkeypatch.setattr(m,'available',lambda *args:0)
    f=Fixture();r=m.run(root,transport=f)
    assert r['observed']==0 and f.calls==0 and r['reason']=='budget_pair_unavailable'
    assert m.audit(root)['status']=='PASS'


def test_prior_exclusions_and_prior_budget_binding(tmp_path):
    from tracking_bench.ladder_v2 import generate
    m=module();catalog,endpoints=fixture_inputs();old=generate([3],[32],16,['swap','handoff'],2,20261111,[])['cases']
    prior=tmp_path/'budget.json';prior.write_text('{}');source=dict(path=str(prior),hash=file_hash(prior),spent='0.60')
    root=tmp_path/'run';m.freeze(root,catalog,endpoints,[source],old,[],mode='offline_fixture',levels=[3],seeds=[20261111])
    p=read_json(root/'protocol.json');assert {c['canonical_id'] for c in old}.isdisjoint(c['canonical_id'] for c in p['cases'] if c['phase']=='confirm')
    prior.write_text('{"changed":true}')
    with pytest.raises(ValueError,match='prior'):m.run(root,transport=Fixture())


def test_schema_parser_rejects_invalid_extra_fields_and_duplicates():
    from tracking_bench.structured_output import parse_answer
    assert parse_answer('{"answer":"Alice"}',['Alice'])['schema_valid']
    for text in ['{"answer":"Alice","answer":"Alice"}','{"answer":"Alice","extra":1}','```json\n{"answer":"Alice"}\n```','{"answer":"Bob"}']:
        assert not parse_answer(text,['Alice'])['schema_valid']


def reseal(root):
    (root/'sha256.json').write_text(json.dumps({str(f.relative_to(root)):file_hash(f) for f in sorted(root.rglob('*')) if f.is_file() and f.name!='sha256.json' and not f.name.endswith('.lock')}))


@pytest.mark.parametrize('kind',['schema','length','zero_event','technical'])
def test_audit_rejects_continuation_after_mandatory_stop(tmp_path,kind):
    m,root=freeze_fixture(tmp_path);m.run(root,transport=Fixture())
    p=read_json(root/'protocol.json');item=p['schedule'][0];case=p['cases'][0]
    path=root/'responses/000000.json';raw=read_json(path);body=json.loads(raw['body'])
    if kind=='schema':body['choices'][0]['message']['content']='{}'
    elif kind=='length':body['choices'][0]['finish_reason']='length'
    elif kind=='zero_event':body['choices'][0]['message']['content']=json.dumps({'answer':next(a for a in case['candidates'] if a!=case['gold'])})
    else:body['usage']['completion_tokens_details']['reasoning_tokens']=1
    raw['body']=json.dumps(body);path.write_text(json.dumps(raw))
    receipt_path=root/'receipts/000000.json';r=read_json(receipt_path)
    r['audit']=m.check_response(raw,p['contracts'][item['model']],item['quote']);r['score']=m.score(case,r['audit']);r['response_hash']=file_hash(path)
    receipt_path.write_text(json.dumps(r));reseal(root)
    with pytest.raises(ValueError,match='stop'):m.audit(root)


@pytest.mark.parametrize('kind',['schema','length','zero_event','nontrivial_wrong'])
def test_runtime_stop_policy(tmp_path,kind):
    m,root=freeze_fixture(tmp_path);cases=read_json(root/'protocol.json')['cases']
    class Altered(Fixture):
        def complete(self,request):
            raw=super().complete(request);body=json.loads(raw['body'])
            if kind=='schema':body['choices'][0]['message']['content']='{}'
            elif kind=='length':body['choices'][0]['finish_reason']='length'
            elif kind=='zero_event' or (kind=='nontrivial_wrong' and 4<=self.calls-1<12):
                c=cases[(self.calls-1)//2];body['choices'][0]['message']['content']=json.dumps({'answer':next(a for a in c['candidates'] if a!=c['gold'])})
            raw['body']=json.dumps(body);return raw
    r=m.run(root,transport=Altered())
    assert r['status']==('COMPLETE' if kind=='nontrivial_wrong' else 'STOPPED')
    assert m.audit(root)['status']=='PASS'

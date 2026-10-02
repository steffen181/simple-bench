import json
from copy import deepcopy
from collections import Counter
import pytest
from test_structured_campaign import fixture_inputs,Fixture
from tracking_bench.campaign_contract import resolve_route
from tracking_bench.common import read_json


def inputs():
    catalog,endpoints=fixture_inputs()
    for m in catalog['data']:m['reasoning']['supported_efforts']=['none','low','medium','high']
    return catalog,endpoints


def test_low_reasoning_counts_usage_and_rejects_unverified_counts():
    from tracking_bench.reasoning_campaign import build_request,quote,check_response
    catalog,endpoints=inputs();mid='openai/gpt-6-luna';c=resolve_route(mid,catalog,endpoints[mid])
    req=build_request({'prompt':'Example','candidates':['Alice','Bob']},c)
    assert req['reasoning']=={'effort':'low','exclude':True} and req['max_tokens']==2048
    q=quote(req,c)
    raw={'http_status':200,'body':json.dumps(dict(model=mid,provider='OpenAI',choices=[dict(finish_reason='stop',message={'content':'{"answer":"Alice"}'})],usage=dict(cost=.00001,prompt_tokens=100,completion_tokens=112,completion_tokens_details={'reasoning_tokens':100})))}
    checked=check_response(raw,c,q)
    assert checked['technical_ok'] and checked['reasoning_tokens']==100 and checked['answer_tokens']==12 and not checked['reasoning_off']
    for bad in [None,-1,True,113]:
        d=json.loads(raw['body']);d['usage']['completion_tokens_details']['reasoning_tokens']=bad
        assert not check_response(dict(raw,body=json.dumps(d)),c,q)['technical_ok']
    bad=deepcopy(req);bad['reasoning']['effort']='high'
    with pytest.raises(ValueError):quote(bad,c)


def test_efficiency_includes_tokens_spent_on_wrong_answers():
    from tracking_bench.reasoning_campaign import metrics
    observations=[dict(correct=True,reasoning_tokens=100,completion_tokens=112,prompt_tokens=50,cost='0.01',status='accepted'),dict(correct=False,reasoning_tokens=300,completion_tokens=312,prompt_tokens=50,cost='0.03',status='accepted')]
    m=metrics(observations,2)
    assert m['accuracy']==.5 and m['reasoning_tokens']==400 and m['completion_tokens_per_correct']==424 and m['usd_per_correct']==.04
    assert metrics(observations,3)['accuracy'] is None
    assert metrics([dict(observations[1])],1)['completion_tokens_per_correct'] is None
    assert metrics([None],1)['reasoning_mean'] is None


class ThinkingFixture(Fixture):
    def __init__(self,missing=False):super().__init__();self.missing=missing
    def complete(self,request):
        raw=super().complete(request);d=json.loads(raw['body']);d['usage']['completion_tokens']=112;d['usage']['completion_tokens_details']['reasoning_tokens']=None if self.missing else 100;raw['body']=json.dumps(d);return raw


def test_paired_population_and_live_runner_replay_offline(tmp_path):
    from tracking_bench import swap_curves,structured_campaign as runner,reasoning_campaign as m
    catalog,endpoints=inputs();baseline=tmp_path/'baseline'
    swap_curves.freeze(baseline,catalog,endpoints,[],[],history_spent='0',mode='offline_fixture')
    runner.run(baseline,transport=Fixture())
    root=tmp_path/'reasoning';m.freeze(root,baseline,catalog,endpoints,mode='offline_fixture')
    p=read_json(root/'protocol.json');assert p['cap']=='4.75' and p['prior_spent']=='0'
    main=[c for c in p['cases'] if c['phase']=='confirm']
    assert len(main)==216 and len({c['canonical_id'] for c in main})==108
    assert set(Counter((c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) for c in main).values())=={6}
    for start in range(0,216,72):assert len({(c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) for c in main[start:start+72]})==36
    result=runner.run(root,transport=ThinkingFixture());assert result['status']=='COMPLETE' and result['observed']==436
    assert m.audit(root)['status']=='PASS'
    d=m.analyze(root)
    assert len(d['cells'])==144 and {c['effort'] for c in d['cells']}=={'off','low'}
    low=[c for c in d['cells'] if c['effort']=='low'];assert all(c['planned']==6 and c['reasoning_tokens']==600 and c['completion_tokens_per_correct']==112 for c in low)
    assert all(c['reasoning_tokens']==0 for c in d['cells'] if c['effort']=='off')
    m.export(d,tmp_path/'dashboard');assert (tmp_path/'dashboard/index.html').exists()
    bad=tmp_path/'missing';m.freeze(bad,baseline,catalog,endpoints,mode='offline_fixture');runner.run(bad,transport=ThinkingFixture(missing=True))
    a=m.audit(bad);assert a['summary']['status']=='STOPPED' and a['summary']['observed']==1
    assert all(c['accuracy'] is None for c in m.analyze(bad)['cells'] if c['effort']=='low')


def test_audit_replays_phase_budget_before_historical_requests(tmp_path):
    from test_structured_campaign import freeze_fixture,reseal
    from tracking_bench.common import file_hash
    m,root=freeze_fixture(tmp_path);m.run(root,transport=Fixture())
    p=read_json(root/'protocol.json');p['scope_caps']['gate']='0.0001'
    (root/'protocol.json').write_text(json.dumps(p))
    for name in ['freeze.json','execution.claim.json']:(root/name).write_text(json.dumps({'protocol_hash':file_hash(root/'protocol.json')}))
    reseal(root)
    with pytest.raises(ValueError,match='historical.*budget'):m.audit(root)


def test_format_and_length_failures_keep_reasoning_costs_and_off_policy():
    from tracking_bench import reasoning_campaign as m,structured_campaign as runner
    from tracking_bench.campaign_contract import check_response as off_check
    catalog,endpoints=inputs();mid='openai/gpt-6-luna';c=resolve_route(mid,catalog,endpoints[mid])
    case=dict(prompt='Test',candidates=['Alice'],gold='Alice',answer_to_person={'Alice':0},phase='confirm',stratum={'k_total':4})
    quoted=m.quote(m.build_request(case,c),c)
    for finish in ['stop','length']:
        raw={'http_status':200,'body':json.dumps(dict(model=mid,provider='OpenAI',choices=[dict(finish_reason=finish,message={'content':'{}'})],usage=dict(cost=.00001,prompt_tokens=100,completion_tokens=112,completion_tokens_details={'reasoning_tokens':100})))}
        a=m.check_response(raw,c,quoted);s=runner.score(case,a)
        assert s['correct'] is False and runner.required_stop(case,a,s,False,True) is None
        summary=m.metrics([m.observation({'audit':a,'score':s},'low')],1)
        assert summary['reasoning_tokens']==100 and summary['format_failures']==1 and summary['completion_tokens_per_correct'] is None
        assert not off_check(raw,c,quoted)['technical_ok']
    c['info']['reasoning']['supported_efforts'].insert(0,'minimal')
    with pytest.raises(ValueError,match='lowest'):m.build_request(case,c)

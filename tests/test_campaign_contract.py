import importlib,json
from copy import deepcopy
from decimal import Decimal
import pytest


def mod():return importlib.import_module('tracking_bench.campaign_contract')

def fixture():
    model=dict(id='openai/gpt-6-luna',canonical_slug='openai/gpt-6-luna-20260922',reasoning={'mandatory':False},supported_parameters=['reasoning','max_tokens'])
    endpoint=dict(tag='openai',provider_name='OpenAI',supported_parameters=['reasoning','max_tokens'],context_length=1050000,max_prompt_tokens=922000,pricing={'prompt':'0.0000001','completion':'0.0000005'})
    return model,endpoint


def contract():
    m,e=fixture();return mod().resolve_route(m['id'],{'data':[m]},{'data':{'endpoints':[e]}})


def response(reasoning=0,cost=0.001,text='Alice',model='openai/gpt-6-luna-20260922'):
    usage=dict(cost=cost,prompt_tokens=20,completion_tokens=1,completion_tokens_details={} if reasoning is None else {'reasoning_tokens':reasoning})
    return dict(http_status=200,body=json.dumps(dict(model=model,provider='OpenAI',choices=[dict(finish_reason='stop',message={'content':text})],usage=usage)))


def test_route_capabilities_and_secret_loader(tmp_path):
    m,e=fixture();m['reasoning']['mandatory']=True
    with pytest.raises(ValueError):mod().resolve_route(m['id'],{'data':[m]},{'data':{'endpoints':[e]}})
    m['reasoning']['mandatory']=False;e['supported_parameters']=[]
    with pytest.raises(ValueError):mod().resolve_route(m['id'],{'data':[m]},{'data':{'endpoints':[e]}})
    p=tmp_path/'key';p.write_text('OPENROUTER_API_KEY="sk-or-v1-testtoken"\n')
    assert mod().load_key(p)=='sk-or-v1-testtoken'
    p.write_text('OPENROUTER_API_KEY=$(touch bad)')
    with pytest.raises(ValueError):mod().load_key(p)


def test_off_identity_budget_and_usage_binding():
    c=contract();r=mod().request_for_case({'prompt':'Return Alice.','gold':'DO_NOT_SEND'},c)
    assert 'DO_NOT_SEND' not in json.dumps(r) and r['reasoning']=={'enabled':False}
    assert 'temperature' not in r and r['provider']['allow_fallbacks'] is False
    q=mod().quote_request(r,c);assert 0<Decimal(q['ceiling_usd'])<Decimal('.15')
    assert c['context_length']==1050000
    assert mod().check_response(response(cost=.000002),c,q)['technical_ok']
    for raw in [response(reasoning=1),response(reasoning=None),response(cost=None),response(model='wrong')]:
        assert not mod().check_response(raw,c,q)['technical_ok']
    assert not mod().check_response(response(cost=10),c,q)['technical_ok']
    raw=response();body=json.loads(raw['body']);body['usage']['prompt_tokens']=q['input_tokens_bound']+1;raw['body']=json.dumps(body)
    assert not mod().check_response(raw,c,q)['technical_ok']


def test_bounds_cannot_be_reused_for_changed_requests():
    c=contract();r=mod().request_for_case({'prompt':'Alice'},c);q=mod().quote_request(r,c)
    assert q['request_hash']!=mod().quote_request(dict(r,messages=[{'role':'user','content':'Bob'}]),c)['request_hash']
    for extra in [dict(tools=[{}]),dict(plugins=[{}]),dict(reasoning={'enabled':True})]:
        with pytest.raises(ValueError):mod().quote_request(dict(r,**extra),c)

import json
import pytest
from tracking_bench.structured_output import build_request,quote,parse_answer
from tracking_bench.campaign_contract import resolve_route,check_response


def contract():
    m={'id':'openai/gpt-6-luna','canonical_slug':'openai/gpt-6-luna','reasoning':{'mandatory':False}}
    e={'tag':'openai','provider_name':'OpenAI','supported_parameters':['reasoning','max_tokens','response_format','structured_outputs'],'context_length':100000,'pricing':{'prompt':'0.000002','completion':'0.00001','input_cache_write_1h':'0.000004'}}
    return resolve_route(m['id'],{'data':[m]},{'data':{'endpoints':[e]}})


def test_only_schema_changes_between_paired_requests():
    case={'prompt':'Find the owner.','candidates':['Alice','Ben'],'gold':'PRIVATE_ORACLE'};c=contract()
    a=build_request(case,c,256,False);b=build_request(case,c,256,True)
    assert a=={k:v for k,v in b.items() if k!='response_format'}
    assert 'PRIVATE_ORACLE' not in json.dumps(b)
    assert b['response_format']['json_schema']['schema']['properties']['answer']['enum']==['Alice','Ben']
    assert b['reasoning']=={'enabled':False} and b['provider']['require_parameters'] and not b['provider']['allow_fallbacks']
    assert b['response_format']['json_schema']['strict'] is True


@pytest.mark.parametrize('text,valid', [(' {"answer":"Alice"} ',True),('{"answer":"Ben"}',True),('{"answer":"Eve"}',False),('{"answer":"Alice","extra":1}',False),('```json\n{"answer":"Alice"}\n```',False),('{"answer":"Alice","answer":"Ben"}',False),('Explanation {"answer":"Alice"}',False),('null',False),('{"answer":3}',False)])
def test_strict_schema_parser(text,valid):
    result=parse_answer(text,['Alice','Ben'])
    assert result['schema_valid']==valid
    if not valid:assert result['answer'] is None


def test_cost_quote_covers_whole_schema_and_output_budget():
    c=contract();case={'prompt':'Owner?','candidates':['Alice','Ben']}
    a=quote(build_request(case,c,256,False),c);b=quote(build_request(case,c,1024,True),c)
    assert b['input_tokens_bound']>a['input_tokens_bound'] and b['output_tokens_bound']==1024
    assert float(b['ceiling_usd'])>=b['input_tokens_bound']*.000004+1024*.00001
    with pytest.raises(ValueError):quote(dict(build_request(case,c,256,True),tools=[{}]),c)
    raw={'http_status':200,'body':json.dumps({'model':c['model_id'],'provider':'OpenAI','choices':[{'finish_reason':'stop','message':{'content':'{"answer":"Alice"}'}}],'usage':{'cost':.0001,'prompt_tokens':10,'completion_tokens':8,'completion_tokens_details':{'reasoning_tokens':0}}})}
    assert check_response(raw,c,b)['technical_ok']
    body=json.loads(raw['body']);body['usage']['completion_tokens']=1025;raw['body']=json.dumps(body)
    assert not check_response(raw,c,b)['technical_ok']

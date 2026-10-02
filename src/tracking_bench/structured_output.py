"""Strict enum-constrained JSON answers and conservative schema-aware quotes."""
import json
from .common import digest
from .openrouter import request_for,_text_prices


def build_request(case,contract,max_tokens,structured):
    if max_tokens not in (256,1024):raise ValueError('unapproved output budget')
    if not {'response_format','structured_outputs'}<=set(contract['info']['supported_parameters']):raise ValueError('route lacks schema support')
    req=request_for({'prompt':case['prompt']},contract['info'],max_tokens,{},contract['provider'],'text-v2','off')
    req['transforms']=[]
    if structured:
        req['response_format']={'type':'json_schema','json_schema':{'name':'tracking_answer','strict':True,'schema':{'type':'object','properties':{'answer':{'type':'string','enum':case['candidates']}},'required':['answer'],'additionalProperties':False}}}
    return req


def quote(request,contract):
    allowed={'model','messages','max_tokens','stream','provider','reasoning','transforms','response_format'}
    if set(request)-allowed or request.get('max_tokens') not in (256,1024) or request.get('reasoning')!={'enabled':False} or request.get('transforms')!=[]:raise ValueError('unapproved request features')
    if len(request['messages'])!=1 or request['messages'][0]['role']!='user' or not isinstance(request['messages'][0]['content'],str):raise ValueError('one text message required')
    bound=len(json.dumps(request,ensure_ascii=False,sort_keys=True).encode())+4096
    if bound+request['max_tokens']>contract['context_length']:raise ValueError('context exceeded')
    p=_text_prices(contract['info']);ceiling=bound*p['input_bound']+request['max_tokens']*p['completion']+p['request']
    return dict(request_hash=digest(request),contract_hash=digest(contract),input_tokens_bound=bound,output_tokens_bound=request['max_tokens'],ceiling_usd=str(ceiling),basis='whole-request-UTF8-bytes-plus-4096-envelope-user-accepted-assumption',provider_certified_token_count=False)


def parse_answer(text,candidates):
    def unique(pairs):
        obj={}
        for key,value in pairs:
            if key in obj:raise ValueError('duplicate JSON key')
            obj[key]=value
        return obj
    try:
        value=json.loads(text,object_pairs_hook=unique)
        valid=isinstance(value,dict) and set(value)=={'answer'} and isinstance(value['answer'],str) and value['answer'] in candidates
    except (ValueError,TypeError):value={};valid=False
    return dict(schema_valid=valid,answer=value['answer'] if valid else None)


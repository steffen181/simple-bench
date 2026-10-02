"""Pinned direct-route campaign contract and conservative, explicitly qualified quotes."""
from pathlib import Path
import json
import re
from .common import digest
from .budget import money
from .openrouter import request_for, validate_response, reasoning_evidence, _text_prices
MODELS={'openai/gpt-6-luna':'openai','anthropic/claude-sonnet-5':'anthropic'}
ENVELOPE_TOKENS=4096


def load_key(path):
    values=[]
    for line in Path(path).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        if line.startswith('export '):line=line[7:]
        if line.startswith('OPENROUTER_API_KEY='):value=line.split('=',1)[1].strip().strip('\"\'')
        elif line.startswith('sk-or-v1-'):value=line
        else:continue
        if not re.fullmatch(r'sk-or-v1-[A-Za-z0-9_-]+',value):raise ValueError('unsupported key syntax')
        values.append(value)
    if len(values)!=1:raise ValueError('exactly one API key required')
    return values[0]


def resolve_route(model_id,catalog,endpoints):
    if model_id not in MODELS:raise ValueError('unapproved campaign model')
    model=next((m for m in catalog['data'] if m['id']==model_id),None)
    if not model or not model.get('reasoning') or model['reasoning'].get('mandatory') is not False:raise ValueError('reasoning-off not supported')
    endpoint=next((e for e in endpoints['data']['endpoints'] if e['tag']==MODELS[model_id]),None)
    if not endpoint or not {'reasoning','max_tokens'}<=set(endpoint['supported_parameters']):raise ValueError('direct route lacks required parameters')
    info=dict(model,pricing=endpoint['pricing'],supported_parameters=endpoint['supported_parameters'],context_length=endpoint['context_length'])
    _text_prices(info)
    return dict(model_id=model_id,canonical_slug=model.get('canonical_slug'),provider=endpoint['tag'],provider_name=endpoint['provider_name'],
        context_length=endpoint['context_length'],quantization=endpoint.get('quantization','unknown'),info=info,endpoint=endpoint,
        input_bound_policy='utf8-bytes-plus-4096-envelope-assumption-v1')


def request_for_case(case,contract):
    result=request_for({'prompt':case['prompt']},contract['info'],32,{},contract['provider'],'text-v2','off')
    result['transforms']=[]
    return result


def quote_request(request,contract):
    if set(request)-{'model','messages','max_tokens','stream','provider','reasoning','transforms'}:raise ValueError('quote only supports plain text without extra features')
    if request.get('model')!=contract['model_id'] or request.get('max_tokens')!=32 or request.get('stream') is not False or request.get('reasoning')!={'enabled':False}:raise ValueError('request protocol differs')
    if request.get('transforms',[])!=[] or len(request.get('messages',[]))!=1:raise ValueError('unexpected context transforms/messages')
    message=request['messages'][0]
    if set(message)!={'role','content'} or message['role']!='user' or not isinstance(message['content'],str):raise ValueError('only one plain user message supported')
    bound=len(message['content'].encode('utf-8'))+ENVELOPE_TOKENS
    if bound+32>contract['context_length']:raise ValueError('input exceeds supported context')
    prices=_text_prices(contract['info'])
    # Cache surcharges are accounted for even though this request does not request caching.
    ceiling=prices['input_bound']*bound+prices['completion']*32+prices['request']
    return dict(request_hash=digest(request),contract_hash=digest(contract),input_tokens_bound=bound,output_tokens_bound=32,ceiling_usd=str(ceiling),
        basis=contract['input_bound_policy'],provider_certified_token_count=False,
        limitation='Byte-token upper bound plus a 4096-token envelope assumption; not a certified count for a private tokenizer. Live execution requires explicit acceptance of this assumption.')


def check_response(raw,contract,quote):
    parsed=validate_response(raw);reason=None
    if parsed['status'] not in ('stop','length'):reason=parsed['status']
    elif parsed['model'] not in (contract['model_id'],contract['canonical_slug']):reason='model_identity_mismatch'
    elif parsed['provider']!=contract['provider_name']:reason='provider_identity_mismatch'
    else:
        try:evidence=reasoning_evidence(raw)
        except (ValueError,TypeError,KeyError,IndexError):evidence='reasoning_unverified'
        if evidence!='off_verified':reason=evidence
    try:
        data=json.loads(raw.get('body','{}'))
        usage=data.get('usage') if isinstance(data,dict) else {}
        usage=usage if isinstance(usage,dict) else {}
        inp=usage.get('prompt_tokens');out=usage.get('completion_tokens')
        if any(type(v) is not int or v<0 for v in (inp,out)):reason=reason or 'usage_unverified'
        elif inp>quote['input_tokens_bound'] or out>quote['output_tokens_bound']:reason=reason or 'token_bound_exceeded'
        if parsed['cost'] is None:reason=reason or 'unknown_cost'
        elif money(parsed['cost'])>money(quote['ceiling_usd']):reason=reason or 'cost_bound_exceeded'
    except (ValueError,TypeError,KeyError):reason=reason or 'usage_unverified';inp=out=None
    return dict(technical_ok=reason is None,reason=reason,response=parsed,prompt_tokens=inp,completion_tokens=out,reasoning_off=reason is None)

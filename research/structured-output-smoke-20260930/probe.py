"""Disposable structured-output feasibility probe; not a supported benchmark runner.

Freeze before paid execution; reuse diagnosed cases, no fresh-validation claim.
No raw provider data or credentials belong in the public aggregate export.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import time
import urllib.request
from tracking_bench.common import digest,file_hash,read_json,write_new
from tracking_bench.campaign_contract import MODELS,resolve_route,load_key,check_response
from tracking_bench.openrouter import request_for,_text_prices,OpenRouter
from tracking_bench.budget import Budget,money
from tracking_bench.frontier_campaign import audit_campaign,_sources


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


def freeze(prior,out):
    prior=Path(prior).resolve();out=Path(out).resolve();a=audit_campaign(prior)
    if a['budget']['reserved']!='0' or a['budget']['halted']:raise ValueError('prior budget unresolved')
    available=money('3.75')-money(a['budget']['spent'])
    if available<money('.75'):raise ValueError('insufficient total budget')
    cases=[]
    def choose(label,n=None,task=None):
        folder=next((prior/'blocks').glob('*-'+label));source=read_json(folder/'cases.json')
        rows=[c for c in source if (n is None or c['stratum']['entities']==n) and (task is None or c['stratum']['task']==task)]
        if label=='gate':rows=[c for c in rows if c['stratum']['k_total']==0]
        c=min(rows,key=lambda x:x['id']);body=c['prompt']
        if 'bbh_protocol' in c:
            prefix='Answer the final question with exactly one parenthesized option, for example (A). Do not explain.\n\n'
            assert body.startswith(prefix);body=body[len(prefix):];kind='bbh'
        else:
            body=body.rsplit('\nAnswer with only one of these names:',1)[0];kind='control' if label=='gate' else 'generated'
        instruction='Return only one JSON object with exactly one string field named "answer". No explanation, markdown or other fields. The answer must be exactly one of: '+json.dumps(c['candidates'])+'.'
        prompt=instruction+'\n\n'+body+'\n\n'+instruction
        row=dict(source_case_id=c['id'],source_file=str((folder/'cases.json').relative_to(prior)),source_sha256=file_hash(folder/'cases.json'),kind=kind,n=c['stratum']['entities'],task=c['stratum']['task'],group=c['canonical_id'],prompt=prompt,candidates=c['candidates'],gold=c['gold'])
        row['id']=digest(row);cases.append(row)
    choose('gate')
    for n in (3,32):
        for task in ('swap','handoff'):choose(f'n{n}-k32',n,task)
    for n in (3,5,7):choose('bbh-original',n)
    def get(url):
        with urllib.request.urlopen(url,timeout=30) as r:return json.load(r)
    catalog=get('https://openrouter.ai/api/v1/models')
    contracts={m:resolve_route(m,catalog,get('https://openrouter.ai/api/v1/models/'+m+'/endpoints')) for m in MODELS}
    schedule=[];conditions=[(256,False),(256,True),(1024,True),(1024,False)]
    for i,case in enumerate(cases):
        shifted=conditions[i%4:]+conditions[:i%4]
        for j,(budget,structured) in enumerate(shifted):
            for model in list(MODELS) if (i+j)%2==0 else list(MODELS)[::-1]:
                request=build_request(case,contracts[model],budget,structured);q=quote(request,contracts[model])
                schedule.append(dict(case_id=case['id'],model=model,max_tokens=budget,structured=structured,request=request,quote=q))
    out.mkdir(parents=True,exist_ok=False)
    protocol=dict(kind='diagnostic_reused_cases_NOT_fresh_confirmation',hypothesis='Schema improves format compliance at fixed prompt/model/budget; competing explanation: increased budget or JSON instruction alone suffices.',models=contracts,cases=cases,schedule=schedule,prior_directory=str(prior),prior_budget_hash=file_hash(prior/'budget.json'),prior_protocol_hash=a['protocol_hash'],prior_spent=a['budget']['spent'],probe_cap='.75',total_cap='4.00',reserved_overall='.25',source_hashes=_sources(),probe_source_hash=file_hash(__file__),selection='Lexicographically first case ID per fixed stratum, no score filtering.',stop='No retries. Stop on unknown cost, identity/reasoning/usage/price mismatch or budget exhaustion; format/accuracy are outcomes.')
    write_new(out/'protocol.json',protocol);write_new(out/'freeze.json',{'protocol_hash':file_hash(out/'protocol.json')})
    for d in ['requests','responses','receipts']:(out/d).mkdir()
    Budget(out/'budget.json','.75').snapshot()
    print('FROZEN',len(cases),'cases',len(schedule),'requests; worst-case sum',sum(money(s['quote']['ceiling_usd']) for s in schedule),flush=True)


def check_freeze(root,executing=False):
    p=read_json(root/'protocol.json')
    if file_hash(root/'protocol.json')!=read_json(root/'freeze.json')['protocol_hash']:raise ValueError('protocol changed')
    if file_hash(Path(p['prior_directory'])/'budget.json')!=p['prior_budget_hash']:raise ValueError('prior budget changed')
    if executing and (p['source_hashes']!=_sources() or p['probe_source_hash']!=file_hash(__file__)):raise ValueError('execution source changed')
    return p


def run(root,key_file):
    p=check_freeze(root,True);transport=OpenRouter(api_key=load_key(key_file));budget=Budget(root/'budget.json','.75')
    credits=transport._request('/credits')
    if credits['http_status']!=200:raise ValueError('credit check failed')
    data=json.loads(credits['body'])['data']
    if money(data['total_credits'])-money(data['total_usage'])<money('.75'):raise ValueError('insufficient available credit')
    write_new(root/'execution.claim.json',{'protocol_hash':file_hash(root/'protocol.json')})
    lookup={c['id']:c for c in p['cases']};stop=None;observed=0
    for i,item in enumerate(p['schedule']):
        check_freeze(root,True)
        if i%2==0:
            pair=sum(money(s['quote']['ceiling_usd']) for s in p['schedule'][i:i+2])
            if pair>money(budget.snapshot()['remaining']):stop='budget_pair_unavailable';break
        name=f'{i:04d}.json';attempt=f'structured-smoke/{i:04d}'
        try:budget.reserve(attempt,item['quote']['ceiling_usd'])
        except ValueError:stop='budget_unavailable';break
        write_new(root/'requests'/name,dict(attempt=attempt,**item));start=time.monotonic()
        try:raw=transport.complete(item['request'])
        except Exception as exc:raw={'http_status':None,'error':type(exc).__name__}
        elapsed=time.monotonic()-start;write_new(root/'responses'/name,raw)
        checked=check_response(raw,p['models'][item['model']],item['quote']);settlement_error=False
        if checked['response']['cost'] is not None:
            try:budget.settle(attempt,checked['response']['cost'])
            except ValueError:settlement_error=True
        parsed=parse_answer(checked['response']['text'],lookup[item['case_id']]['candidates'])
        completed=checked['technical_ok'] and checked['response']['status']=='stop'
        scored=dict(parsed,completed=completed,correct=completed and parsed['schema_valid'] and parsed['answer']==lookup[item['case_id']]['gold'])
        write_new(root/'receipts'/name,dict(index=i,attempt=attempt,request_hash=file_hash(root/'requests'/name),response_hash=file_hash(root/'responses'/name),audit=checked,score=scored,elapsed=elapsed,settlement_error=settlement_error));observed+=1
        if not checked['technical_ok'] or settlement_error:stop=checked['reason'] or 'settlement_error';break
        if (i+1)%8==0:print('Measured',i+1,'/',len(p['schedule']),'spent',budget.snapshot()['spent'],flush=True)
    write_new(root/'summary.json',dict(status='COMPLETE' if stop is None else 'STOPPED',reason=stop,observed=observed,planned=len(p['schedule'])))
    write_new(root/'sha256.json',{str(f.relative_to(root)):file_hash(f) for f in sorted(root.rglob('*')) if f.is_file() and not f.name.endswith('.lock')})
    print(read_json(root/'summary.json'),flush=True)


def audit(root):
    p=check_freeze(root);manifest=read_json(root/'sha256.json')
    actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() and f.name!='sha256.json' and not f.name.endswith('.lock')}
    if actual!=set(manifest):raise ValueError('file set changed')
    for name,h in manifest.items():
        if Path(name).is_absolute() or '..' in Path(name).parts or file_hash(root/name)!=h:raise ValueError('sealed file changed')
    budget=Budget(root/'budget.json','.75').snapshot();lookup={c['id']:c for c in p['cases']};records=[]
    for f in sorted((root/'receipts').glob('*.json')):
        r=read_json(f);item=p['schedule'][r['index']];case=lookup[item['case_id']];req=read_json(root/'requests'/f.name);raw=read_json(root/'responses'/f.name)
        assert case['id']==digest({k:v for k,v in case.items() if k!='id'})
        original=Path(p['prior_directory'])/case['source_file'];assert file_hash(original)==case['source_sha256']
        source=next(c for c in read_json(original) if c['id']==case['source_case_id']);assert source['gold']==case['gold'] and source['candidates']==case['candidates']
        assert req==dict(attempt=r['attempt'],**item)
        expected=build_request(case,p['models'][item['model']],item['max_tokens'],item['structured'])
        assert expected==item['request'] and quote(expected,p['models'][item['model']])==item['quote']
        checked=check_response(raw,p['models'][item['model']],item['quote']);parsed=parse_answer(checked['response']['text'],case['candidates']);completed=checked['technical_ok'] and checked['response']['status']=='stop'
        scored=dict(parsed,completed=completed,correct=completed and parsed['schema_valid'] and parsed['answer']==case['gold'])
        assert r['audit']==checked and r['score']==scored
        assert r['request_hash']==file_hash(root/'requests'/f.name) and r['response_hash']==file_hash(root/'responses'/f.name)
        a=budget['attempts'][r['attempt']];assert a['ceiling']==item['quote']['ceiling_usd'] and a['cost']==checked['response']['cost']
        records.append(dict(model=item['model'],budget=item['max_tokens'],structured=item['structured'],kind=case['kind'],n=case['n'],task=case['task'],case_id=case['id'],technical_ok=checked['technical_ok'],reasoning_off=checked['reasoning_off'],finish=checked['response']['finish_reason'],completion_tokens=checked['completion_tokens'],cost=checked['response']['cost'],elapsed=r['elapsed'],**scored))
    assert len(records)==len(budget['attempts'])==read_json(root/'summary.json')['observed']
    total=money(p['prior_spent'])+money(budget['spent'])+money(budget['reserved']);assert total<=money('3.75')
    rows=[]
    for model in MODELS:
        for limit in (256,1024):
            for structured in (False,True):
                for kind in ('all','control','generated','bbh'):
                    selected=[r for r in records if r['model']==model and r['budget']==limit and r['structured']==structured and (kind=='all' or r['kind']==kind)]
                    planned=sum(kind=='all' or c['kind']==kind for c in p['cases'])
                    rows.append(dict(model=model,max_tokens=limit,structured=structured,kind=kind,planned=planned,observed=len(selected),schema_valid=sum(r['schema_valid'] for r in selected),completed=sum(r['completed'] for r in selected),valid_complete=sum(r['schema_valid'] and r['completed'] for r in selected),correct=sum(r['correct'] for r in selected),length=sum(r['finish']=='length' for r in selected),cost_usd=sum(float(r['cost']) for r in selected if r['cost'] is not None)))
    return dict(status='PASS',summary=read_json(root/'summary.json'),protocol_hash=file_hash(root/'protocol.json'),probe_source_hash=p['probe_source_hash'],prior_spent=p['prior_spent'],spent=budget['spent'],reserved=budget['reserved'],total_accounted=str(total),reasoning_off=bool(records) and all(r['reasoning_off'] for r in records),rows=rows,records=records)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','run','audit']);parser.add_argument('directory',type=Path);parser.add_argument('--prior',type=Path);parser.add_argument('--key-file',type=Path);args=parser.parse_args()
    if args.command=='freeze':freeze(args.prior,args.directory)
    elif args.command=='run':run(args.directory,args.key_file)
    else:print(json.dumps(audit(args.directory),indent=2))

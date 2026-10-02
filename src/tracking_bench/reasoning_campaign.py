"""Paired lowest-effort measurement, explicit token accounting and separate budget."""
import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from importlib.resources import files
from . import structured_campaign as runner, swap_curves
from .structured_output import build_request as off_request
from .campaign_contract import MODELS,resolve_route
from .openrouter import validate_response,_text_prices
from .common import digest,file_hash,read_json,write_new
from .budget import Budget,money
from .frontier_campaign import _sources

CAP='4.75'
SCOPES={'gate':'.10','bbh':'1.00','confirm':'3.65'}
SETTINGS={'effort':'low','max_tokens':2048}


def build_request(case,contract):
    efforts=contract['info'].get('reasoning',{}).get('supported_efforts',[])
    active=[e for e in ['minimal','low','medium','high','xhigh','max'] if e in efforts]
    if not active or active[0]!='low':raise ValueError('lowest supported effort changed')
    if contract['endpoint'].get('max_completion_tokens',2048)<2048:raise ValueError('output limit unsupported')
    req=off_request(case,contract,256,True)
    req['max_tokens']=2048;req['reasoning']={'effort':'low','exclude':True}
    return req


def quote(req,contract):
    allowed={'model','messages','max_tokens','stream','provider','reasoning','transforms','response_format'}
    if set(req)!=allowed or req['model']!=contract['model_id'] or req['stream'] is not False or req['max_tokens']!=2048 or req['reasoning']!={'effort':'low','exclude':True} or req['transforms']!=[]:raise ValueError('unapproved reasoning request')
    if len(req['messages'])!=1 or req['messages'][0]['role']!='user' or not isinstance(req['messages'][0]['content'],str):raise ValueError('one user text required')
    bound=len(json.dumps(req,ensure_ascii=False,sort_keys=True).encode())+4096
    if bound+2048>contract['context_length']:raise ValueError('context exceeded')
    p=_text_prices(contract['info']);ceiling=bound*p['input_bound']+2048*p['completion']+p['request']
    return dict(request_hash=digest(req),contract_hash=digest(contract),input_tokens_bound=bound,output_tokens_bound=2048,ceiling_usd=str(ceiling),basis='whole-request-UTF8-bytes-plus-4096-envelope-user-accepted-assumption',provider_certified_token_count=False)


def check_response(raw,contract,quoted):
    parsed=validate_response(raw);reason=None;inp=out=thinking=None
    if parsed['status'] not in ('stop','length'):reason=parsed['status']
    elif parsed['model'] not in (contract['model_id'],contract['canonical_slug']):reason='model_identity_mismatch'
    elif parsed['provider']!=contract['provider_name']:reason='provider_identity_mismatch'
    try:
        usage=json.loads(raw.get('body','{}')).get('usage',{})
        inp=usage.get('prompt_tokens');out=usage.get('completion_tokens')
        thinking=(usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
        if any(type(x) is not int or x<0 for x in (inp,out,thinking)) or thinking>out:reason=reason or 'reasoning_usage_unverified'
        elif inp>quoted['input_tokens_bound'] or out>quoted['output_tokens_bound']:reason=reason or 'token_bound_exceeded'
        if parsed['cost'] is None:reason=reason or 'unknown_cost'
        elif money(parsed['cost'])>money(quoted['ceiling_usd']):reason=reason or 'cost_bound_exceeded'
    except (ValueError,TypeError,AttributeError):reason=reason or 'reasoning_usage_unverified'
    valid=reason is None
    return dict(technical_ok=valid,reason=reason,response=parsed,prompt_tokens=inp,completion_tokens=out,reasoning_tokens=thinking,answer_tokens=out-thinking if valid else None,reasoning_off=valid and thinking==0,requested_effort='low')


def selected_cases(parent):
    """First canonical group per seed/cell, independent of response outcomes."""
    first={}
    for c in parent['cases']:
        if c['phase']!='confirm':continue
        s=c['stratum'];key=(s['seed'],s['entities'],s['relevant_updates'],s['irrelevant_events'])
        first[key]=min(first.get(key,c['canonical_id']),c['canonical_id'])
    result=[]
    for c in parent['cases']:
        s=c['stratum']
        if c['phase']!='confirm' or c['canonical_id']==first[(s['seed'],s['entities'],s['relevant_updates'],s['irrelevant_events'])]:result.append(c)
    return result


def freeze(out,baseline,catalog,endpoints,mode='live',source_files=None):
    baseline=Path(baseline).resolve();a=swap_curves.audit(baseline);old=runner.protocol(baseline)
    if a['summary']['status']!='COMPLETE' or a['budget']['reserved']!='0' or old['mode']!=mode:raise ValueError('baseline must be complete, settled and same provenance')
    contracts={m:resolve_route(m,catalog,endpoints[m]) for m in MODELS}
    for m in MODELS:
        if contracts[m]['canonical_slug']!=old['contracts'][m]['canonical_slug'] or contracts[m]['provider']!=old['contracts'][m]['provider']:raise ValueError('baseline model/route differs')
    cases=selected_cases(old);schedule=[]
    for i,c in enumerate(cases):
        for m in list(MODELS) if i%2==0 else list(MODELS)[::-1]:
            req=build_request(c,contracts[m]);schedule.append(dict(case_id=c['id'],model=m,phase=c['phase'],request_hash=digest(req),quote=quote(req,contracts[m])))
    sources={str(baseline/'sha256.json'):file_hash(baseline/'sha256.json'),str(baseline/'protocol.json'):file_hash(baseline/'protocol.json'),**(source_files or {})}
    p=dict(schema='reasoning-effort-v1',mode=mode,reasoning_protocol=SETTINGS,baseline=str(baseline),contracts=contracts,cases=cases,schedule=schedule,blocked=old['blocked'],source_files=sources,source_hashes=_sources(),priors=[],prior_spent='0',cap=CAP,scope_caps=SCOPES,total_work_cap=CAP,total_cap='5',reserved_overall='.25',format_errors_as_wrong=True,
        design=dict(kind='paired-reasoning',levels=swap_curves.LEVELS,relevant=swap_curves.RELEVANT,distractors=swap_curves.DISTRACTORS,seeds=swap_curves.SEEDS,groups_per_cell=3,selection='lexicographically first canonical group per seed/cell from prior fixed series; outcomes not consulted',fresh=False),
        limitations=['Historical paired baseline uses 256 output tokens, low uses 2048 including reasoning; this measures deployed configurations, not an isolated causal reasoning effect.','Provider low labels and tokenizers are not guaranteed equivalent compute. Zero reported reasoning is allowed; missing usage is never interpreted as zero.','No retries. Format/completion failures count false. Technical/unknown-cost failures stop. Unobserved measurements remain unknown.'])
    out=Path(out);out.mkdir(parents=True,exist_ok=False);write_new(out/'protocol.json',p);write_new(out/'freeze.json',dict(protocol_hash=file_hash(out/'protocol.json')))
    for folder in ['requests','responses','receipts']:(out/folder).mkdir()
    Budget(out/'budget.json',CAP,mode=mode).snapshot()
    return dict(status='FROZEN',planned=len(schedule),groups=108,cap=CAP)


def audit(root):
    root=Path(root);p=runner.protocol(root);a=runner.audit(root)
    if p['schema']!='reasoning-effort-v1' or p['reasoning_protocol']!=SETTINGS or p['cap']!=CAP or p['total_work_cap']!=CAP or p['scope_caps']!=SCOPES or p['total_cap']!='5' or p['priors'] or p['prior_spent']!='0' or p['format_errors_as_wrong'] is not True:raise ValueError('reasoning protocol differs')
    baseline=Path(p['baseline']);old=runner.protocol(baseline);previous=swap_curves.audit(baseline)
    if previous['summary']['status']!='COMPLETE' or old['mode']!=p['mode']:raise ValueError('baseline incomplete/provenance differs')
    if p['cases']!=selected_cases(old) or p['blocked']!=old['blocked']:raise ValueError('paired population differs')
    for m in MODELS:
        if p['contracts'][m]['canonical_slug']!=old['contracts'][m]['canonical_slug'] or p['contracts'][m]['provider']!=old['contracts'][m]['provider']:raise ValueError('paired model differs')
    return a


def observation(receipt,effort):
    if receipt is None:return None
    a=receipt['audit'];r=receipt['score'];tokens=a.get('reasoning_tokens',0 if a.get('reasoning_off') else None)
    return dict(correct=r['correct'],reasoning_tokens=tokens,completion_tokens=a['completion_tokens'],prompt_tokens=a['prompt_tokens'],cost=a['response']['cost'],status=r['status'])


def metrics(observations,planned):
    present=[x for x in observations if x is not None]
    valid=[x for x in present if x['correct'] is not None and type(x['reasoning_tokens']) is int and type(x['completion_tokens']) is int]
    complete=len(valid)==planned and planned>0
    correct=sum(x['correct'] for x in valid);rs=[x['reasoning_tokens'] for x in valid];outputs=sum(x['completion_tokens'] for x in valid)
    spent=sum((money(x['cost']) for x in present if x['cost'] is not None),money(0))
    return dict(planned=planned,observed=len(present),technical_ok=len(valid),correct=correct,accuracy=correct/planned if complete else None,reasoning_tokens=sum(rs) if complete else None,
                reasoning_mean=sum(rs)/planned if complete else None,reasoning_median=median(rs) if complete else None,reasoning_max=max(rs) if complete else None,completion_tokens=outputs if complete else None,
                completion_tokens_per_correct=outputs/correct if complete and correct else None,usd_per_correct=float(spent)/correct if complete and correct else None,cost_usd=str(spent),
                format_failures=sum(x['status'] in ('invalid_json','truncated') for x in present),truncated=sum(x['status']=='truncated' for x in present),zero_reasoning=sum(x['reasoning_tokens']==0 for x in valid))


def analyze(root):
    root=Path(root);p=runner.protocol(root);a=audit(root);previous=swap_curves.audit(Path(p['baseline']))
    wanted={c['id'] for c in p['cases']};buckets=defaultdict(list);groups=defaultdict(list);totals=defaultdict(list)
    for effort,records in [('off',previous['records']),('low',a['records'])]:
        for phase,c,m,r in records:
            if c['id'] not in wanted:continue
            s=c['stratum'];n=s['entities'];relevant=s.get('relevant_updates');d=s.get('irrelevant_events');o=observation(r,effort)
            # Original BBH has varying K/R; report its fixed N subset separately.
            key=(phase,m,effort,n,relevant if phase=='confirm' else None,d if phase=='confirm' else None)
            buckets[key].append(o);totals[(phase,m,effort)].append(o)
            if phase=='confirm':groups[(m,effort,n,relevant,d,c['canonical_id'],s['seed'])].append(o)
    cells=[];bbh=[]
    for (phase,m,e,n,r,d),obs in sorted(buckets.items(),key=lambda x:str(x[0])):
        row=dict(phase=phase,model=m,effort=e,n=n,r=r,d=d,**metrics(obs,len(obs)))
        if phase=='confirm':cells.append(row)
        elif phase=='bbh':bbh.append(row)
    group_rows=[dict(model=m,effort=e,n=n,r=r,d=d,group_id=g,seed=seed,**metrics(obs,len(obs))) for (m,e,n,r,d,g,seed),obs in sorted(groups.items())]
    summary=[dict(phase=phase,model=m,effort=e,**metrics(obs,len(obs))) for (phase,m,e),obs in sorted(totals.items())]
    return dict(schema='reasoning-effort-results-v1',execution_kind=p['mode'],audit={k:v for k,v in a.items() if k!='records'},axes=dict(n=swap_curves.LEVELS,r=swap_curves.RELEVANT,d=swap_curves.DISTRACTORS,effort=['off','low']),
                conditions=dict(groups_per_cell=3,seeds=swap_curves.SEEDS,rotations=2,generator_shots=0,bbh_shots=3,max_tokens={'off':256,'low':2048},baseline='Historical matched cases from swap-curves-20261001',format='strict JSON answer enum',api_seed=None),
                models=[dict(id=m,slug=c['canonical_slug'],provider=c['provider_name']) for m,c in p['contracts'].items()],budget=dict(limit='5',spent=a['budget']['spent'],reserved=a['budget']['reserved'],reserve='.25',baseline_charged='0'),
                cells=cells,bbh=bbh,groups=group_rows,totals=summary,limitations=p['limitations'],native_acc_norm=None)


def export(data,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);write_new(out/'results.json',data)
    blob=json.dumps(data,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    (out/'index.html').write_text(files('tracking_bench').joinpath('templates/reasoning.html').read_text().replace('__DATA__',blob))
    for name,rows in [('cells',data['cells']),('groups',data['groups']),('bbh',data['bbh'])]:
        stream=io.StringIO()
        if rows:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (out/(name+'.csv')).write_text(stream.getvalue())
    lines=['# Reasoning low: gepaarter Swap-Vergleich','', '[Dashboard](index.html) · [Zellen](cells.csv) · [Gruppen](groups.csv) · [BBH](bbh.csv)', '',f"Herkunft: {data['execution_kind']}. Audit {data['audit']['status']}; neue Kosten {data['budget']['spent']} / 5 USD.",'','Off: historische Antworten derselben ausgewählten Fälle, 256 Tokens. Low: neue Antworten, 2048 Tokens inklusive Reasoning. Drei Gruppen je Zelle, zwei Antwortanordnungen. Fehlversuche gehen in den Tokenverbrauch ein. Bei null richtigen Antworten sind Tokens/Kosten pro richtiger Antwort nicht definiert. Unvollständige Messpunkte bleiben unbekannt.','', '| Phase | Modell | Effort | Richtig/geplant | Reasoning-Tokens gesamt | Ausgabetokens/richtige Antwort |','|---|---|---|---:|---:|---:|']
    if data['execution_kind']!='live':lines[2:2]=['**OFFLINE-TESTDATEN, keine Modellmessung.**','']
    for t in data['totals']:lines.append(f"| {t['phase']} | {t['model']} | {t['effort']} | {t['correct']}/{t['planned']} | {t['reasoning_tokens']} | {t['completion_tokens_per_correct']} |")
    lines+=['','BBH ist eine separate Referenz aus 45 Originalfragen, Chat-3shot/JSON-Generation, keine native acc_norm.','',*data['limitations']]
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n');(out/'SHA256SUMS').write_text(''.join(f'{file_hash(f)}  {f.name}\n' for f in sorted(out.iterdir()) if f.is_file()))
    return dict(status='EXPORTED',directory=str(out))


def main(argv=None):
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    for cmd in ['freeze','run','audit','export']:
        p=sub.add_parser(cmd);p.add_argument('directory',type=Path)
        if cmd=='freeze':p.add_argument('--baseline',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True)
        if cmd=='run':p.add_argument('--key-file',type=Path,required=True)
        if cmd=='export':p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='freeze':
        catalog=read_json(args.metadata/'catalog.json');endpoints={m:read_json(args.metadata/(m.split('/')[0]+'.json')) for m in MODELS}
        paths=[args.metadata/'catalog.json',args.metadata/'openai.json',args.metadata/'anthropic.json']
        result=freeze(args.directory,args.baseline,catalog,endpoints,source_files={str(p.resolve()):file_hash(p) for p in paths})
    elif args.command=='run':result=runner.run(args.directory,args.key_file)
    elif args.command=='audit':result={k:v for k,v in audit(args.directory).items() if k!='records'}
    else:result=export(analyze(args.directory),args.out)
    print(json.dumps(result,indent=2,ensure_ascii=False));return 2 if result.get('status')=='STOPPED' else 0

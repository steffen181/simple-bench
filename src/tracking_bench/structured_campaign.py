"""Frozen fresh comparison with strict JSON, shared prior-spend accounting and replay."""
import argparse
import importlib.util
import json
from pathlib import Path
import random
import time
import urllib.request
from collections import Counter
from .common import digest,file_hash,read_json,write_new
from .campaign_contract import MODELS,resolve_route,load_key,check_response
from .structured_output import build_request,quote,parse_answer
from .frontier_campaign import _sources,audit_campaign
from .frontier_analysis import aggregate_records,make_bbh_reference
from .budget import Budget,money
from .ladder_v2 import generate
from .ladder import replay_text
from .structure_large import solve,canonical_id
from .reference import resource
from .openrouter import OpenRouter

LEVELS=[3,5,7,10,16,24,32,48,64]
SEEDS=[20261111,20261112,20261113]
CAP='2.75'
SCOPES={'gate':'0.15','bbh':'0.50','confirm':'2.10'}


def prepare_case(base,phase):
    body=base['prompt']
    if 'bbh_protocol' in base:
        prefix='Answer the final question with exactly one parenthesized option, for example (A). Do not explain.\n\n'
        if not body.startswith(prefix):raise ValueError('unexpected BBH prompt contract')
        body=body[len(prefix):]
    else:
        if '\nAnswer with only one of these names:' not in body:raise ValueError('unexpected generator prompt')
        body=body.rsplit('\nAnswer with only one of these names:',1)[0]
    instruction='Return only one JSON object with exactly one string field named "answer". No explanation, markdown or other fields. The answer must be exactly one of: '+json.dumps(base['candidates'])+'.'
    case={k:v for k,v in base.items() if k!='id'}
    case.update(phase=phase,base_case=base,prompt=instruction+'\n\n'+body+'\n\n'+instruction)
    case['prompt_hash']=digest(case['prompt']);case['id']=digest(case)
    return case


def freeze(out,catalog,endpoints,priors,history,bbh_cases,mode='live',levels=None,seeds=None,source_files=None):
    levels=LEVELS if levels is None else levels;seeds=SEEDS if seeds is None else seeds
    if mode not in ('live','offline_fixture'):raise ValueError('invalid mode')
    if mode=='live' and (levels!=LEVELS or seeds!=SEEDS or len(bbh_cases)!=45 or len(priors)!=2):raise ValueError('live study matrix differs from approved protocol')
    if len(set(levels))!=len(levels) or len(set(seeds))!=len(seeds) or not levels or not seeds:raise ValueError('duplicate/empty study dimensions')
    previous=sum((money(r['spent']) for r in priors),money(0))
    if previous+money(CAP)>money('3.75'):raise ValueError('cumulative work cap exceeded')
    for prior in priors:
        if file_hash(prior['path'])!=prior['hash']:raise ValueError('prior budget changed')
    blocked=set(resource('historical-bbh-structures.json')['groups'])
    for c in history:
        blocked.update(x for x in [c.get('canonical_id'),c.get('legacy_canonical_id')] if x)
    frozen_blocked=sorted(blocked)
    gate=generate([3],[0],0,['swap'],1,20261030,[])['cases']
    controls=generate([5],[8],4,['swap','handoff'],1,20261031,blocked)['cases'];gate+=controls
    blocked.update(c['canonical_id'] for c in controls)
    cases=[prepare_case(c,'gate') for c in gate]
    cases += [prepare_case(c,'bbh') for c in bbh_cases]
    blocks=[]
    for n in levels:
        for seed in seeds:
            corpus=generate([n],[32],16,['swap','handoff'],2,seed,blocked)
            blocked.update(c['canonical_id'] for c in corpus['cases'])
            blocks.append([prepare_case(c,'confirm') for c in corpus['cases']])
    random.Random(20261030).shuffle(blocks)
    for block in blocks:cases+=block
    contracts={mid:resolve_route(mid,catalog,endpoints[mid]) for mid in MODELS}
    schedule=[]
    for i,c in enumerate(cases):
        for mid in list(MODELS) if i%2==0 else list(MODELS)[::-1]:
            req=build_request(c,contracts[mid],256,True)
            schedule.append(dict(case_id=c['id'],model=mid,phase=c['phase'],request_hash=digest(req),quote=quote(req,contracts[mid])))
    p=dict(schema='structured-comparison-v1',mode=mode,contracts=contracts,priors=priors,prior_spent=str(previous),cap=CAP,scope_caps=SCOPES,total_cap='4.00',reserved_overall='.25',levels=levels,seeds=seeds,per_seed_task=2,cases=cases,schedule=schedule,blocked=frozen_blocked,source_files=source_files or {},source_hashes=_sources(),
        hypothesis='Under a fixed strict JSON protocol, compare correctness over increasing entities; competing explanation: residual format failure, stochastic variation or weak baseline prevents a capacity-boundary conclusion.',
        independence='Generated main groups exclude every supplied prior case canonical/legacy ID and bundled BBH history; nontrivial gate groups also excluded. Zero-event control and BBH originals are reused and not fresh validation.',
        stop_policy='No retries. Stop on uncertain costs, identity/usage/reasoning failure, schema/length failure, or wrong zero-event control. Nontrivial valid wrong answers remain outcomes. Reserve both model quotes before each case; budget stops preserve full planned denominators.')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    write_new(out/'protocol.json',p);write_new(out/'freeze.json',{'protocol_hash':file_hash(out/'protocol.json')})
    for folder in ['requests','responses','receipts']:(out/folder).mkdir()
    Budget(out/'budget.json',CAP,mode=mode).snapshot()
    return dict(status='FROZEN',cases=len(cases),planned=len(schedule),fresh_groups=len({c['canonical_id'] for c in cases if c['phase']=='confirm'}),prior_spent=str(previous),cap=CAP)


def protocol(root,executing=False):
    p=read_json(root/'protocol.json')
    if file_hash(root/'protocol.json')!=read_json(root/'freeze.json')['protocol_hash']:raise ValueError('protocol changed')
    for prior in p['priors']:
        if file_hash(prior['path'])!=prior['hash']:raise ValueError('prior budget changed')
    if executing and p['source_hashes']!=_sources():raise ValueError('source changed since freeze')
    return p


def available(budget,phase,scope_caps=None):
    scope_caps=SCOPES if scope_caps is None else scope_caps
    b=budget.snapshot()
    if b['halted']:return money(0)
    used=sum((money(a['cost'] if a['cost'] is not None else a['ceiling']) for a in b['attempts'].values() if phase in a.get('scopes',[])),money(0))
    return min(money(b['remaining']),money(scope_caps[phase])-used)


def score(case,checked):
    parsed=parse_answer(checked['response']['text'],case['candidates']);completed=checked['technical_ok'] and checked['response']['status']=='stop'
    status='accepted' if completed and parsed['schema_valid'] else 'truncated' if checked['response']['status']=='length' else 'invalid_json'
    if not checked['technical_ok']:status=checked['reason']
    return dict(**parsed,completed=completed,status=status,correct=(completed and parsed['schema_valid'] and parsed['answer']==case['gold']) if checked['technical_ok'] else None,person=case['answer_to_person'].get(parsed['answer']) if completed and parsed['schema_valid'] else None)


def required_stop(case, checked, scored, settlement_error, format_errors_as_wrong=False):
    if settlement_error or not checked['technical_ok']:
        return checked['reason'] or 'cost_bound_exceeded'
    if scored['status'] != 'accepted' and not format_errors_as_wrong:
        return 'schema_or_completion_failure'
    if case['phase'] == 'gate' and case['stratum']['k_total'] == 0 and not scored['correct']:
        return 'zero_event_control_failed'
    return None


def phases(p,receipts,stop):
    result={}
    for phase in dict.fromkeys(s['phase'] for s in p['schedule']):
        indices=[i for i,s in enumerate(p['schedule']) if s['phase']==phase]
        if not indices:continue
        observed=sum(i in receipts for i in indices)
        result[phase]=dict(phase=phase,planned=len(indices),observed=observed,status='COMPLETE' if observed==len(indices) and not any(receipts[i].get('stop_reason') for i in indices if i in receipts) else 'STOPPED' if observed else 'NOT_RUN',reason=next((receipts[i]['stop_reason'] for i in indices if i in receipts and receipts[i].get('stop_reason')),None) or (stop if observed<len(indices) else None))
    return result


def case_start(schedule,index):
    return index==0 or schedule[index-1]['case_id']!=schedule[index]['case_id']


def case_ceiling(schedule,index):
    return sum((money(s['quote']['ceiling_usd']) for s in schedule[index:index+2] if s['case_id']==schedule[index]['case_id']),money(0))


def campaign_request(case,contract,p):
    if 'reasoning_protocol' in p:
        from .reasoning_campaign import build_request as build
        return build(case,contract)
    return build_request(case,contract,256,True)


def campaign_quote(request,contract,p):
    if 'reasoning_protocol' in p:
        from .reasoning_campaign import quote as quoted
        return quoted(request,contract)
    return quote(request,contract)


def campaign_check(raw,contract,quoted,p):
    if 'reasoning_protocol' in p:
        from .reasoning_campaign import check_response as check
        return check(raw,contract,quoted)
    return check_response(raw,contract,quoted)


def run(directory,key_file=None,transport=None):
    root=Path(directory);p=protocol(root,True)
    if (root/'execution.claim.json').exists():raise ValueError('study already claimed; no automatic resume')
    if 'continuation' in p:
        from .factorial_continuation import validate_continuation
        validate_continuation(p)
    for path,h in p['source_files'].items():
        if file_hash(path)!=h:raise ValueError('historical source changed')
    if transport is None:
        if p['mode']!='live':raise ValueError('fixture transport required')
        transport=OpenRouter(api_key=load_key(key_file))
        credit=transport._request('/credits')
        if credit['http_status']!=200:raise ValueError('credit check failed')
        data=json.loads(credit['body'])['data']
        if money(data['total_credits'])-money(data['total_usage'])<money(p['cap']):raise ValueError('credit below authorized study cap')
    elif p['mode']!='offline_fixture':raise ValueError('custom transport forbidden in live mode')
    write_new(root/'execution.claim.json',{'protocol_hash':file_hash(root/'protocol.json')})
    budget=Budget(root/'budget.json',p['cap'],mode=p['mode']);cases={c['id']:c for c in p['cases']};receipts={};stop=None
    for i,item in enumerate(p['schedule']):
        protocol(root,True)
        if case_start(p['schedule'],i):
            pair=case_ceiling(p['schedule'],i)
            if pair>available(budget,item['phase'],p['scope_caps']):stop='budget_pair_unavailable';break
        case=cases[item['case_id']];contract=p['contracts'][item['model']];req=campaign_request(case,contract,p)
        if digest(req)!=item['request_hash'] or campaign_quote(req,contract,p)!=item['quote']:raise ValueError('request differs from freeze')
        attempt=f'structured-comparison/{i:06d}';name=f'{i:06d}.json'
        try:budget.reserve(attempt,item['quote']['ceiling_usd'],{item['phase']:p['scope_caps'][item['phase']]})
        except ValueError:stop='budget_unavailable';break
        write_new(root/'requests'/name,dict(attempt=attempt,request=req,quote=item['quote']));start=time.monotonic()
        try:raw=transport.complete(req)
        except Exception as exc:raw={'http_status':None,'error':type(exc).__name__}
        elapsed=time.monotonic()-start;write_new(root/'responses'/name,raw)
        checked=campaign_check(raw,contract,item['quote'],p);settlement_error=False
        if checked['response']['cost'] is not None:
            try:budget.settle(attempt,checked['response']['cost'])
            except ValueError:settlement_error=True
        scored=score(case,checked)
        stop=required_stop(case,checked,scored,settlement_error,p.get('format_errors_as_wrong',False))
        receipt=dict(index=i,attempt=attempt,request_hash=file_hash(root/'requests'/name),response_hash=file_hash(root/'responses'/name),audit=checked,score=scored,elapsed_seconds=elapsed,settlement_error=settlement_error,stop_reason=stop)
        write_new(root/'receipts'/name,receipt);receipts[i]=receipt
        if (i+1)%16==0 or i+1==len(p['schedule']) or (i+1<len(p['schedule']) and p['schedule'][i+1]['phase']!=item['phase']):print(item['phase'],i+1,'/',len(p['schedule']),'spent',budget.snapshot()['spent'],flush=True)
        if stop:break
    summary=dict(status='COMPLETE' if stop is None else 'STOPPED',reason=stop,observed=len(receipts),planned=len(p['schedule']),phases=phases(p,receipts,stop))
    write_new(root/'summary.json',summary)
    write_new(root/'sha256.json',{str(f.relative_to(root)):file_hash(f) for f in sorted(root.rglob('*')) if f.is_file() and not f.name.endswith('.lock')})
    return summary


def audit(directory):
    root=Path(directory);p=protocol(root);manifest=read_json(root/'sha256.json')
    actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() and f.name!='sha256.json' and not f.name.endswith('.lock')}
    if actual!=set(manifest):raise ValueError('file set changed')
    for name,h in manifest.items():
        if Path(name).is_absolute() or '..' in Path(name).parts or file_hash(root/name)!=h:raise ValueError('sealed file changed')
    for name,h in p['source_files'].items():
        if file_hash(name)!=h:raise ValueError('historical source changed')
    blocked=set(p['blocked']);gate_groups=set();main_groups=set();cases={}
    for c in p['cases']:
        base=c['base_case']
        if base['id']!=digest({k:v for k,v in base.items() if k!='id'}) or prepare_case(base,c['phase'])!=c:raise ValueError('case/prompt binding differs')
        if 'structure' in base:
            if canonical_id(base['structure'])!=base['canonical_id'] or solve(base['structure'])!=base['answer_to_person'][base['gold']] or replay_text(base['prompt'])!=base['gold']:raise ValueError('generator oracle differs')
        if c['phase']=='gate':gate_groups.add(c['canonical_id'])
        elif c['phase'] in ('confirm','develop'):
            if c['canonical_id'] in blocked or c.get('legacy_canonical_id') in blocked:raise ValueError('historical overlap')
            main_groups.add(c['canonical_id'])
        cases[c['id']]=c
    if gate_groups&main_groups:raise ValueError('gate/main overlap')
    expected=[]
    for i,c in enumerate(p['cases']):
        for mid in list(MODELS) if i%2==0 else list(MODELS)[::-1]:
            req=campaign_request(c,p['contracts'][mid],p);expected.append(dict(case_id=c['id'],model=mid,phase=c['phase'],request_hash=digest(req),quote=campaign_quote(req,p['contracts'][mid],p)))
    if 'continuation' in p:
        from .factorial_continuation import validate_continuation
        validate_continuation(p,expected)
        expected=expected[p['continuation']['offset']:]
    if expected!=p['schedule']:raise ValueError('schedule differs')
    budget=Budget(root/'budget.json',p['cap'],mode=p['mode']).snapshot();receipts={};attempts=set();records=[]
    files=sorted((root/'receipts').glob('*.json'));derived_stop=None;derived_halted=False
    prefix_used=money(0);prefix_scopes={phase:money(0) for phase in p['scope_caps']}
    for i,f in enumerate(files):
        r=read_json(f);item=p['schedule'][i];c=cases[item['case_id']];req=read_json(root/'requests'/f.name);raw=read_json(root/'responses'/f.name);contract=p['contracts'][item['model']]
        if f.name!=f'{i:06d}.json' or r['index']!=i:raise ValueError('noncontiguous receipts')
        capacity=min(money(p['cap'])-prefix_used,money(p['scope_caps'][item['phase']])-prefix_scopes[item['phase']])
        needed=case_ceiling(p['schedule'],i) if case_start(p['schedule'],i) else money(item['quote']['ceiling_usd'])
        if needed>capacity:raise ValueError('historical phase/pair budget exceeded')
        checked=campaign_check(raw,contract,item['quote'],p);scored=score(c,checked)
        if r['audit']!=checked or r['score']!=scored:raise ValueError('score replay differs')
        cost=checked['response']['cost']
        settlement_error=cost is not None and money(cost)>money(item['quote']['ceiling_usd'])
        derived_halted |= settlement_error
        derived_stop=required_stop(c,checked,scored,settlement_error,p.get('format_errors_as_wrong',False))
        if r['settlement_error']!=settlement_error or r['stop_reason']!=derived_stop:raise ValueError('stop replay differs')
        if derived_stop and i!=len(files)-1:raise ValueError('continued after mandatory stop')
        if req!=dict(attempt=r['attempt'],request=campaign_request(c,contract,p),quote=item['quote']):raise ValueError('request replay differs')
        if r['request_hash']!=file_hash(root/'requests'/f.name) or r['response_hash']!=file_hash(root/'responses'/f.name):raise ValueError('receipt hashes differ')
        a=budget['attempts'][r['attempt']]
        if a['ceiling']!=item['quote']['ceiling_usd'] or a['cost']!=checked['response']['cost'] or a['scopes']!=[item['phase']]:raise ValueError('budget binding differs')
        charged=money(cost if cost is not None else item['quote']['ceiling_usd'])
        prefix_used+=charged;prefix_scopes[item['phase']]+=charged
        attempts.add(r['attempt']);receipts[i]=r
    if attempts!=set(budget['attempts']):raise ValueError('unreconciled attempts')
    summary=read_json(root/'summary.json')
    if budget['halted']!=derived_halted:raise ValueError('halt replay differs')
    if derived_stop is None and len(receipts)<len(p['schedule']):
        index=len(receipts);item=p['schedule'][index];capacity=available(Budget(root/'budget.json',p['cap'],mode=p['mode']),item['phase'],p['scope_caps'])
        if case_start(p['schedule'],index) and case_ceiling(p['schedule'],index)>capacity:
            derived_stop='budget_pair_unavailable'
        elif money(item['quote']['ceiling_usd'])>capacity:
            derived_stop='budget_unavailable'
        else:raise ValueError('unjustified stop before schedule completion')
    if summary['reason']!=derived_stop or summary['status']!=('STOPPED' if derived_stop else 'COMPLETE'):raise ValueError('summary stop replay differs')
    if summary['observed']!=len(receipts) or summary['planned']!=len(p['schedule']) or summary['phases']!=phases(p,receipts,summary['reason']):raise ValueError('coverage differs')
    if summary['status']=='COMPLETE' and len(receipts)!=len(p['schedule']):raise ValueError('false completion')
    total=money(p['prior_spent'])+money(budget['spent'])+money(budget['reserved'])
    if total>money(p.get('total_work_cap','3.75')):raise ValueError('global work budget exceeded')
    for i,item in enumerate(p['schedule']):records.append((item['phase'],cases[item['case_id']],item['model'],receipts.get(i)))
    return dict(status='PASS',summary=summary,budget={k:budget[k] for k in ['spent','reserved','remaining','halted']},total_accounted=str(total),protocol_hash=file_hash(root/'protocol.json'),records=records)


def analyze(directory):
    root=Path(directory);a=audit(root);p=protocol(root);cells,comparisons=aggregate_records(a['records'])
    prior=money(p['prior_spent']);spent=prior+money(a['budget']['spent'])
    return dict(schema='frontier-public-results-v1',execution_kind=p['mode'],native_acc_norm=None,metric='strict_JSON_answer_accuracy_NOT_native_acc_norm',audit_status=a['status'],protocol_hash=a['protocol_hash'],
        budget=dict(limit_usd=4,working_limit_usd=3.75,spent=str(spent),study_spent=a['budget']['spent'],prior_spent=str(prior),reserved=a['budget']['reserved'],remaining=str(money(4)-spent-money(a['budget']['reserved'])),halted=a['budget']['halted']),phases=a['summary']['phases'],
        models=[dict(id=m,canonical_slug=p['contracts'][m]['canonical_slug'],provider=p['contracts'][m]['provider_name'],quantization=p['contracts'][m]['quantization']) for m in MODELS],cells=cells,comparisons=comparisons,selection=None,
        conditions=dict(fixed_matrix=True,levels=p['levels'],reasoning='off, explicit zero tokens audited',max_tokens=256,temperature='provider default',api_seed='not set',ladder_shots=0,bbh_shots=3,response_format='strict JSON schema, one answer field, enum candidates, no additional fields',seeds=p['seeds'],analysis_code_sha256=file_hash(Path(__file__)),aggregate_code_sha256=file_hash(Path(__file__).with_name('frontier_analysis.py'))),
        limitations=['Kostenkarte: kumulative Kosten aller drei Laeufe; Zellkosten beziehen sich nur auf diese neue Messung.','Frische Generatorgruppen, vorab fixierte Matrix; alle geplanten Faelle bleiben im Nenner. Unbeobachtete Zellen sind unbekannt.','BBH: dieselben 45 Originalfragen unter Chat-3shot/JSON-Generation; keine native acc_norm und kein BBH-Gesamtscore.','Leiter 0-shot und BBH 3-shot sind getrennte Protokolle. Unterschiede zum 32-Token-Lauf sind durch geaenderte Prompts, Budget und neue Generatorfaelle mitbedingt.','Punktweise 95%-Bootstrapintervalle ueber Strukturgruppen; zwei Gruppen je Seed/Aufgabe, keine simultane Absicherung einer Einbruchsschwelle. Reine 0/1-Stichproben koennen degenerierte Intervalle ergeben.','Strukturelle Frische gilt relativ zu den eingefrorenen Ausschluessen, nicht zu unbekannten Trainingsdaten. Anbieterpraezision und private Gewichte sind nicht verifiziert.','Kostenbound: freigegebene konservative UTF8-/4096-Envelope-Annahme, keine zertifizierte Tokenzaehlung.']+(['OFFLINE FIXTURE: keine Modellmessung.'] if p['mode']=='offline_fixture' else []))


def main(argv=None):
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    f=sub.add_parser('freeze');f.add_argument('directory',type=Path);f.add_argument('--prior',type=Path,required=True);f.add_argument('--probe',type=Path,required=True)
    for name in ['run','audit','export']:
        f=sub.add_parser(name);f.add_argument('directory',type=Path)
        if name=='run':f.add_argument('--key-file',type=Path,required=True)
        if name=='export':f.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='freeze':
        prior=args.prior.resolve();probe=args.probe.resolve();old=audit_campaign(prior)
        if old['budget']['reserved']!='0' or old['budget']['halted']:raise ValueError('prior campaign unsettled')
        code=Path.cwd()/'research/structured-output-smoke-20260930/probe.py'
        spec=importlib.util.spec_from_file_location('archived_structured_probe',code);archived=importlib.util.module_from_spec(spec);spec.loader.exec_module(archived)
        verified=archived.audit(probe)
        if verified['reserved']!='0' or verified['summary']['status']!='COMPLETE':raise ValueError('probe unsettled/incomplete')
        priors=[dict(path=str(folder/'budget.json'),hash=file_hash(folder/'budget.json'),spent=spent) for folder,spent in [(prior,old['budget']['spent']),(probe,verified['spent'])]]
        history=[];sources={}
        for path in sorted((prior/'blocks').glob('*/cases.json')):history+=read_json(path);sources[str(path)]=file_hash(path)
        for name in ['protocol.json','sha256.json']:
            for folder in [prior,probe]:sources[str(folder/name)]=file_hash(folder/name) if (folder/name).exists() else None
        sources={k:v for k,v in sources.items() if v is not None}
        bbh=make_bbh_reference(prior/'bbh-sources')['cases']
        for path in (prior/'bbh-sources').iterdir():
            if path.is_file():sources[str(path)]=file_hash(path)
        def get(url):
            with urllib.request.urlopen(url,timeout=30) as r:return json.load(r)
        catalog=get('https://openrouter.ai/api/v1/models');endpoints={mid:get('https://openrouter.ai/api/v1/models/'+mid+'/endpoints') for mid in MODELS}
        result=freeze(args.directory,catalog,endpoints,priors,history,bbh,source_files=sources)
    elif args.command=='run':result=run(args.directory,args.key_file)
    elif args.command=='audit':result={k:v for k,v in audit(args.directory).items() if k!='records'}
    else:
        from .dashboard import export
        result=export(analyze(args.directory),args.out)
    print(json.dumps(result,indent=2));return 2 if result.get('status')=='STOPPED' else 0


if __name__=='__main__':raise SystemExit(main())

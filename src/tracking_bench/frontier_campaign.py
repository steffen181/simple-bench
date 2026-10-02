"""Single-use campaign phases with paired requests, conservative reservations and replay."""
from contextlib import contextmanager
from pathlib import Path
from collections import defaultdict
import fcntl
import time
import uuid
from .common import read_json,write_new,file_hash,digest
from .budget import Budget,money
from .campaign_contract import MODELS,resolve_route,request_for_case,quote_request,check_response,load_key
from .openrouter import OpenRouter
from .ladder_v2 import generate
from .scoring import score
CAPS={'gate':'0.15','smoke':'0.60','bbh':'0.60','confirm':'2.40'}
LEVELS=[3,5,7,10,16,24,32,48,64]


def _sources():
    root=Path(__file__).parent
    return {str(p.relative_to(root)):file_hash(p) for p in sorted(root.rglob('*')) if p.is_file() and p.suffix in ('.py','.html','.json') and '__pycache__' not in p.parts}


def freeze(config,catalog,endpoints,out):
    if set(config)-{'mode','accept_input_bound_assumption','confirmation_groups_per_seed_task'}:raise ValueError('unknown campaign config')
    mode=config.get('mode','live')
    if mode not in ('live','offline_fixture'):raise ValueError('invalid mode')
    if mode=='live' and config.get('accept_input_bound_assumption') is not True:raise ValueError('live use needs explicit acceptance of estimated input bound')
    per=config.get('confirmation_groups_per_seed_task',2)
    if type(per) is not int or per not in (2,4):raise ValueError('confirmation count must be 2 or 4')
    contracts={mid:resolve_route(mid,catalog,endpoints[mid]) for mid in MODELS}
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);(out/'blocks').mkdir()
    config=dict(config,mode=mode,confirmation_groups_per_seed_task=per)
    protocol=dict(schema='frontier-campaign-v1',campaign_id=uuid.uuid4().hex,config=config,contracts=contracts,
        total_budget_usd='4.00',work_budget_usd='3.75',phase_caps=CAPS,levels=LEVELS,smoke_seed=20261001,
        confirmation_seeds=[20261011,20261012,20261013],bbh_seed=20261003,max_tokens=32,
        metric='generative_accuracy_NOT_native_acc_norm',source_hashes=_sources(),
        budget_policy='Reserve every request and check capacity for both model calls before a case; no retry. Fixed planned population can stop with explicit undercoverage.',
        selection_rule='<=75% and >=20pp below N3 on two neighboring complete levels; union of model neighborhoods plus baseline')
    write_new(out/'protocol.json',protocol);write_new(out/'freeze.json',{'protocol_sha256':file_hash(out/'protocol.json')})
    Budget(out/'budget.json','4.00',mode=mode).snapshot()
    return dict(directory=str(out),status='FROZEN',mode=mode)


def _protocol(root,executing=False):
    p=read_json(root/'protocol.json')
    if file_hash(root/'protocol.json')!=read_json(root/'freeze.json')['protocol_sha256']:raise ValueError('protocol changed')
    if executing and p['source_hashes']!=_sources():raise ValueError('implementation changed since freeze')
    return p


def _seal(folder):
    write_new(folder/'sha256.json',{str(p.relative_to(folder)):file_hash(p) for p in sorted(folder.rglob('*')) if p.is_file()})


def _verify(folder):
    manifest=read_json(folder/'sha256.json')
    actual={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() and p.name!='sha256.json'}
    if set(manifest)!=actual:raise ValueError('block file set changed')
    for name,h in manifest.items():
        if Path(name).is_absolute() or '..' in Path(name).parts or file_hash(folder/name)!=h:raise ValueError('block changed')


def _available(budget,scope):
    snapshot=budget.snapshot()
    if snapshot['halted']:return money(0)
    amounts={}
    for name,cap in [('work','3.75'),(scope,CAPS[scope])]:
        used=sum((money(a['cost'] if a['cost'] is not None else a['ceiling']) for a in snapshot['attempts'].values() if name in a.get('scopes',[])),money(0))
        amounts[name]=money(cap)-used
    return min(money(snapshot['remaining']),*amounts.values())


def _block(root,phase,label,cases,transport):
    p=_protocol(root,True);contracts=p['contracts'];models=list(MODELS)
    folder=root/'blocks'/f'{len(list((root/"blocks").iterdir())):03d}-{label}';folder.mkdir()
    for directory in ['requests','responses','receipts']:(folder/directory).mkdir()
    schedule=[]
    for i,c in enumerate(cases):
        if c['id']!=digest({k:v for k,v in c.items() if k!='id'}):raise ValueError('invalid case identity')
        for mid in models if i%2==0 else models[::-1]:schedule.append({'case_id':c['id'],'model':mid})
    write_new(folder/'cases.json',cases);write_new(folder/'schedule.json',schedule)
    write_new(folder/'claim.json',dict(phase=phase,label=label,protocol_hash=file_hash(root/'protocol.json')))
    lookup={c['id']:c for c in cases};budget=Budget(root/'budget.json','4.00',mode=p['config']['mode']);reason=None;observed=0
    for index,item in enumerate(schedule):
        case=lookup[item['case_id']];contract=contracts[item['model']]
        request=request_for_case(case,contract);quote=quote_request(request,contract)
        if index%2==0:
            pair=sum((money(quote_request(request_for_case(case,contracts[mid]),contracts[mid])['ceiling_usd']) for mid in models),money(0))
            if pair>_available(budget,phase):reason='budget_pair_unavailable';break
        attempt=p['campaign_id']+'/'+folder.name+f'/{index:06d}'
        try:budget.reserve(attempt,quote['ceiling_usd'],{'work':'3.75',phase:CAPS[phase]})
        except ValueError:reason='budget_unavailable';break
        name=f'{index:06d}.json'
        write_new(folder/'requests'/name,dict(attempt_id=attempt,request=request,quote=quote))
        started=time.monotonic()
        try:raw=transport.complete(request)
        except Exception as exc:raw={'http_status':None,'error':type(exc).__name__}
        elapsed=time.monotonic()-started;write_new(folder/'responses'/name,raw)
        checked=check_response(raw,contract,quote)
        if checked['response']['cost'] is not None:
            try:budget.settle(attempt,checked['response']['cost'])
            except ValueError:checked['technical_ok']=False;checked['reason']='cost_bound_exceeded'
        scored=score(case,checked['response'])
        if not checked['technical_ok']:scored=dict(scored,correct=None,status=checked['reason'])
        receipt=dict(**item,attempt_id=attempt,request_hash=file_hash(folder/'requests'/name),response_hash=file_hash(folder/'responses'/name),elapsed_seconds=elapsed,audit=checked,score=scored)
        write_new(folder/'receipts'/name,receipt);observed+=1
        if not checked['technical_ok']:reason=checked['reason'];break
        if phase=='gate' and not scored['correct']:reason='control_failed';break
    result=dict(phase=phase,label=label,status='COMPLETE' if reason is None else 'STOPPED',reason=reason,observed=observed,planned=len(schedule))
    write_new(folder/'summary.json',result);_seal(folder)
    print(f'{phase}/{label}: {result["status"]} {observed}/{len(schedule)}',flush=True)
    return result


def _all_cases(root):
    return [c for folder in sorted((root/'blocks').iterdir()) if (folder/'cases.json').exists() for c in read_json(folder/'cases.json')]


def smoke_rows(root):
    p=_protocol(root);rows=[]
    for folder in sorted((root/'blocks').iterdir()):
        summary=read_json(folder/'summary.json')
        if summary['phase']!='smoke':continue
        cases=read_json(folder/'cases.json');first=cases[0]['stratum'];scores=defaultdict(list)
        for f in sorted((folder/'receipts').glob('*.json')):
            receipt=read_json(f);scores[receipt['model']].append(receipt['score'])
        for mid in p['contracts']:
            values=scores[mid];complete=summary['status']=='COMPLETE' and len(values)==len(cases)
            formats=sum(v['status']=='accepted' for v in values)
            rows.append(dict(model=mid,n=first['entities'],k=first['k_total'],r=first['relevant_updates'],accuracy=sum(v['correct'] is True for v in values)/len(cases),complete=complete,format_ok=complete and formats==len(values)))
    return rows


def select_frontier(rows,frozen_rule=None):
    bymodel=defaultdict(dict)
    for row in rows:bymodel[row['model']][(row['n'],row['k'])]=row
    selected={};models={}
    valid=lambda r:r is not None and r['complete'] and r.get('format_ok',True)
    for mid,lookup in bymodel.items():
        values=sorted((r for r in lookup.values() if valid(r)),key=lambda r:(r['k'],r['n']))
        if not values:continue
        base=lookup.get((3,32));base=base if valid(base) else None
        boundary=None;chosen=[]
        if base and base['accuracy']>.75:
            # Never bridge missing/invalid levels or join the N and K axes.
            axes=[[(n,32) for n in LEVELS],[(64,k) for k in (32,64,128)]]
            for axis in axes:
                for i in range(1,len(axis)-1):
                    pair=[lookup.get(key) for key in axis[i:i+2]]
                    if all(valid(r) and r['accuracy']<=.75 and base['accuracy']-r['accuracy']>=.20-1e-10 for r in pair):
                        boundary=pair[0];chosen=[lookup[key] for key in axis[max(0,i-1):i+2] if valid(lookup.get(key))];break
                if boundary:break
        if not chosen:chosen=values[-3:]
        if base:chosen=[base,*chosen]
        for c in chosen:selected[(c['n'],c['k'],c['r'])]=dict(n=c['n'],k=c['k'],r=c['r'])
        models[mid]=dict(boundary_n=boundary['n'] if boundary else None,boundary_k=boundary['k'] if boundary else None,baseline=base['accuracy'] if base else None,reason='screening_boundary' if boundary else 'no_confirmed_boundary_or_low_baseline')
    cells=sorted(selected.values(),key=lambda c:(c['k'],c['n']))
    if len(cells)>7:cells=[cells[0],*cells[-6:]]
    return dict(cells=cells,models=models)


@contextmanager
def _lock(root):
    with (root/'execution.lock').open('a') as stream:
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise ValueError('campaign already executing') from exc
        yield


def execute_phase(campaign,phase,key_file=None,transport=None):
    root=Path(campaign).resolve();p=_protocol(root,True)
    if phase not in CAPS:raise ValueError('unknown phase')
    if transport is None:
        if p['config']['mode']!='live':raise ValueError('fixture transport required')
        transport=OpenRouter(api_key=load_key(key_file) if key_file else None)
        if not transport.key:raise ValueError('missing API key')
    elif p['config']['mode']!='offline_fixture':raise ValueError('custom transport forbidden for live campaign')
    with _lock(root):
        if (root/(phase+'.claim.json')).exists():raise ValueError('phase already claimed; no automatic retries')
        if any((root/'blocks').iterdir()):audit_campaign(root)
        if phase!='gate' and (not (root/'gate.json').exists() or read_json(root/'gate.json')['status']!='COMPLETE'):raise ValueError('gate has not passed')
        if any(read_json(f).get('status')=='STOPPED' and read_json(f).get('reason') not in ('budget_pair_unavailable','budget_unavailable') for f in (root/'blocks').glob('*/summary.json')):raise ValueError('campaign stopped on a technical failure')
        write_new(root/(phase+'.claim.json'),{'phase':phase,'protocol_hash':file_hash(root/'protocol.json')})
        blocked={c['canonical_id'] for c in _all_cases(root)};results=[]
        def run_cell(n,k,r,seed,per,label,scope):
            corpus=generate([n],[k],r,['swap','handoff'],per,seed,blocked)
            blocked.update(c['canonical_id'] for c in corpus['cases'])
            results.append(_block(root,scope,label,corpus['cases'],transport))
        if phase=='gate':
            cases=generate([3],[0],0,['swap'],1,20260930,[])['cases']+generate([3],[1],1,['handoff'],1,20260931,[])['cases']
            results.append(_block(root,'gate','gate',cases,transport))
        elif phase=='smoke':
            for n in p['levels']:
                run_cell(n,32,16,p['smoke_seed']+n,2,f'n{n}-k32','smoke')
                if results[-1]['status']!='COMPLETE':break
                selection=select_frontier(smoke_rows(root))
                if len(selection['models'])==2 and all(v['boundary_n'] is not None for v in selection['models'].values()):break
            rows=smoke_rows(root)
            if results[-1]['status']=='COMPLETE' and len([r for r in rows if r['n']==64 and r['accuracy']>.75 and r['complete']])==2:
                for k in (64,128):
                    run_cell(64,k,k//2,p['smoke_seed']+k+1000,2,f'n64-k{k}','smoke')
                    if results[-1]['status']!='COMPLETE':break
            write_new(root/'selection.json',select_frontier(smoke_rows(root)))
        elif phase=='confirm':
            if not (root/'selection.json').exists():raise ValueError('smoke selection missing')
            selection=read_json(root/'selection.json')
            if not selection['cells']:raise ValueError('no valid shared cells')
            per=p['config']['confirmation_groups_per_seed_task']
            population=[]
            for cell in selection['cells']:
                for seed in p['confirmation_seeds']:
                    corpus=generate([cell['n']],[cell['k']],cell['r'],['swap','handoff'],per,seed,blocked)
                    blocked.update(c['canonical_id'] for c in corpus['cases'])
                    population.append(dict(label=f'confirm-n{cell["n"]}-k{cell["k"]}-s{seed}',cases=corpus['cases']))
            write_new(root/'confirmation-population.json',population)
            write_new(root/'confirmation-freeze.json',dict(selection_hash=file_hash(root/'selection.json'),population_hash=file_hash(root/'confirmation-population.json'),cells=selection['cells'],seeds=p['confirmation_seeds'],per_seed_task=per,planned_policy='Fixed common population; budget stops are explicit undercoverage.'))
            for block in population:
                results.append(_block(root,'confirm',block['label'],block['cases'],transport))
                if results[-1]['status']!='COMPLETE':break
        elif phase=='bbh':
            from .frontier_analysis import make_bbh_reference
            source=root/'bbh-sources'
            if not source.exists():
                from .reference import fetch
                fetch(source)
            # Freeze a small balanced reference; never resize it after seeing answers.
            corpus=make_bbh_reference(source,p['bbh_seed'],15,0)
            write_new(root/'bbh-freeze.json',dict(corpus_hash=corpus['hash'],per_n=15,fresh_per_n=0,metric='BBH_tracking_subset_chat3shot_generation',reason='Conservative fixed reference population under the 0.60 USD scope; likelihood unavailable.'))
            results.append(_block(root,'bbh','bbh-original',corpus['cases'],transport))
        result=dict(phase=phase,status='COMPLETE' if all(r['status']=='COMPLETE' for r in results) else 'STOPPED',reason=next((r['reason'] for r in results if r['reason']),None),planned=sum(r['planned'] for r in results),observed=sum(r['observed'] for r in results))
        if phase=='confirm':result['planned']=sum(len(b['cases'])*len(MODELS) for b in population)
        write_new(root/(phase+'.json'),result);return result


def audit_campaign(campaign):
    root=Path(campaign);p=_protocol(root);attempts={};blocks=[];groups={}
    for folder in sorted((root/'blocks').iterdir()):
        _verify(folder);summary=read_json(folder/'summary.json');cases={c['id']:c for c in read_json(folder/'cases.json')};schedule=read_json(folder/'schedule.json')
        if read_json(folder/'claim.json')['protocol_hash']!=file_hash(root/'protocol.json'):raise ValueError('block protocol binding differs')
        for c in cases.values():
            if c['id']!=digest({k:v for k,v in c.items() if k!='id'}) or c['prompt_hash']!=digest(c['prompt']):raise ValueError('case modified')
            if summary['phase'] in ('gate','smoke','confirm'):
                group=c['canonical_id'];prior=groups.setdefault(group,summary['phase'])
                if prior!=summary['phase']:raise ValueError('development/confirmation overlap')
        receipts=sorted((folder/'receipts').glob('*.json'))
        if len(receipts)!=summary['observed'] or summary['planned']!=len(schedule):raise ValueError('invalid block coverage')
        for i,path in enumerate(receipts):
            receipt=read_json(path);raw=read_json(folder/'responses'/path.name);req=read_json(folder/'requests'/path.name);item=schedule[i];c=cases[item['case_id']];contract=p['contracts'][item['model']]
            if receipt['case_id']!=item['case_id'] or receipt['model']!=item['model']:raise ValueError('schedule mismatch')
            expected=request_for_case(c,contract)
            if req['request']!=expected or req['quote']!=quote_request(expected,contract):raise ValueError('request/quote mismatch')
            audit=check_response(raw,contract,req['quote']);scored=score(c,audit['response'])
            if not audit['technical_ok']:scored=dict(scored,correct=None,status=audit['reason'])
            if receipt['audit']!=audit or receipt['score']!=scored:raise ValueError('receipt replay mismatch')
            if receipt['request_hash']!=file_hash(folder/'requests'/path.name) or receipt['response_hash']!=file_hash(folder/'responses'/path.name):raise ValueError('receipt hashes differ')
            attempts[req['attempt_id']]=(req,audit,summary['phase'])
        blocks.append(summary)
    if (root/'selection.json').exists() and read_json(root/'selection.json')!=select_frontier(smoke_rows(root)):raise ValueError('selection differs from smoke')
    if (root/'confirmation-freeze.json').exists() and read_json(root/'confirmation-freeze.json')['selection_hash']!=file_hash(root/'selection.json'):raise ValueError('confirmation selection changed')
    if (root/'confirmation-freeze.json').exists() and read_json(root/'confirmation-freeze.json')['population_hash']!=file_hash(root/'confirmation-population.json'):raise ValueError('confirmation population changed')
    if (root/'confirmation-population.json').exists():
        population={b['label']:b['cases'] for b in read_json(root/'confirmation-population.json')}
        for folder in (root/'blocks').iterdir():
            claim=read_json(folder/'claim.json')
            if claim['phase']=='confirm' and read_json(folder/'cases.json')!=population.get(claim['label']):raise ValueError('confirmation block differs from frozen population')
    if (root/'bbh-freeze.json').exists():
        from .frontier_analysis import make_bbh_reference
        frozen=read_json(root/'bbh-freeze.json');corpus=make_bbh_reference(root/'bbh-sources',p['bbh_seed'],frozen['per_n'],frozen['fresh_per_n'])
        if frozen['corpus_hash']!=corpus['hash']:raise ValueError('BBH corpus differs from freeze')
        for folder in (root/'blocks').iterdir():
            if read_json(folder/'claim.json')['phase']=='bbh' and read_json(folder/'cases.json')!=corpus['cases']:raise ValueError('BBH block differs from frozen corpus')
    for phase in CAPS:
        path=root/(phase+'.json')
        if path.exists():
            selected=[r for r in blocks if r['phase']==phase]
            expected=dict(phase=phase,status='COMPLETE' if all(r['status']=='COMPLETE' for r in selected) else 'STOPPED',reason=next((r['reason'] for r in selected if r['reason']),None),planned=sum(r['planned'] for r in selected),observed=sum(r['observed'] for r in selected))
            if phase=='confirm':expected['planned']=sum(len(b['cases'])*len(MODELS) for b in read_json(root/'confirmation-population.json'))
            if read_json(path)!=expected:raise ValueError('phase summary differs')
    budget=Budget(root/'budget.json','4.00',mode=p['config']['mode']).snapshot()
    if set(attempts)!=set(budget['attempts']):raise ValueError('unreconciled reservations/attempts')
    for attempt,(req,audit,phase) in attempts.items():
        a=budget['attempts'][attempt]
        if money(a['ceiling'])!=money(req['quote']['ceiling_usd']) or a['scopes']!=['work',phase]:raise ValueError('ledger binding differs')
        cost=audit['response']['cost']
        if (cost is None)!=(a['cost'] is None) or (cost is not None and money(cost)!=money(a['cost'])):raise ValueError('ledger cost differs')
    if money(budget['spent'])+money(budget['reserved'])>money('4.00'):raise ValueError('campaign budget exceeded')
    return dict(status='PASS',mode=p['config']['mode'],blocks=blocks,budget={k:budget[k] for k in ['spent','reserved','remaining','halted']},protocol_hash=file_hash(root/'protocol.json'),observed=len(attempts))

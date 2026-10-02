"""Frozen N/R/D populations; shared audited execution and cumulative accounting."""
from pathlib import Path
import random
from .common import read_json,write_new,digest,file_hash
from .budget import Budget,money
from .campaign_contract import MODELS,resolve_route
from .structured_output import build_request,quote
from .structured_campaign import prepare_case
from .frontier_campaign import _sources
from .ladder_v2 import generate

LEVELS=[3,7,16,32]
RELEVANT=[4,8,16]
DISTRACTORS=[0,8,16]
SEEDS=[20261211,20261212,20261213]
CONFIRM_SEEDS=[20261221,20261222,20261223]
DEV_CAP='1.40'
CONFIRM_CAP='0.89'
SCOPES={'gate':'.03','bbh':'.17','develop':'1.20'}
SELECTION_RULE=dict(minimum_effect=.15,baseline_minimum=.75,maximum_contrasts=2,confirmation_groups=24,family_alpha=.05,interval='Hoeffding bounded independent structure groups; Bonferroni two contrasts',ties='lexicographic task/N/R/D/model/axis')


def validate_priors(priors,cap):
    paths=set();total=money(0)
    for prior in priors:
        path=Path(prior['path']).resolve()
        if path in paths:raise ValueError('duplicate prior ledger')
        paths.add(path)
        if file_hash(path)!=prior['hash']:raise ValueError('prior ledger changed')
        data=read_json(path)
        b=Budget(path,data['limit'],mode=data['mode']).snapshot()
        if money(b['reserved']) or b['halted']:raise ValueError('unsettled prior ledger')
        if money(prior['spent'])!=money(b['spent']):raise ValueError('prior spend mismatch')
        total+=money(b['spent'])
    if total+money(cap)>money('3.75'):raise ValueError('cumulative authorized work cap exceeded')
    return str(total)


def population(blocked,levels=None,relevant=None,distractors=None,seeds=None,groups_per_seed=1,tasks=None):
    blocked=set(blocked);result=[]
    for n in LEVELS if levels is None else levels:
        for r in RELEVANT if relevant is None else relevant:
            for d in DISTRACTORS if distractors is None else distractors:
                for task in ['swap','handoff'] if tasks is None else tasks:
                    for seed in SEEDS if seeds is None else seeds:
                        cases=generate([n],[r+d],r,[task],groups_per_seed,seed,blocked)['cases']
                        result+=cases
                        for c in cases:blocked.update(x for x in [c['canonical_id'],c.get('legacy_canonical_id')] if x)
    return result


def freeze_population(out,cases,catalog,endpoints,priors,blocked,cap,scopes,design,source_files=None,mode='live',format_errors_as_wrong=False):
    if mode not in ('live','offline_fixture'):raise ValueError('invalid mode')
    previous=validate_priors(priors,cap)
    if not scopes or sum((money(x) for x in scopes.values()),money(0))>money(cap):raise ValueError('invalid scope allocation')
    prepared=[prepare_case(item[0],item[1]) if isinstance(item,tuple) else prepare_case(item,design['stage']) for item in cases]
    contracts={m:resolve_route(m,catalog,endpoints[m]) for m in MODELS};schedule=[]
    for i,c in enumerate(prepared):
        if c['phase'] not in scopes:raise ValueError('phase has no scope')
        for model in list(MODELS) if i%2==0 else list(MODELS)[::-1]:
            request=build_request(c,contracts[model],256,True)
            schedule.append(dict(case_id=c['id'],model=model,phase=c['phase'],request_hash=digest(request),quote=quote(request,contracts[model])))
    p=dict(schema='factorial-comparison-v1',mode=mode,contracts=contracts,priors=priors,prior_spent=previous,cap=cap,scope_caps=scopes,total_cap='4.00',reserved_overall='.25',cases=prepared,schedule=schedule,blocked=sorted(blocked),source_files=source_files or {},source_hashes=_sources(),design=design)
    if format_errors_as_wrong:p['format_errors_as_wrong']=True
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    write_new(out/'protocol.json',p);write_new(out/'freeze.json',{'protocol_hash':file_hash(out/'protocol.json')})
    for name in ['requests','responses','receipts']:(out/name).mkdir()
    return dict(status='FROZEN',cases=len(prepared),planned=len(schedule),prior_spent=previous,cap=cap)


def shuffled(cases,seed):
    groups={}
    for c in cases:groups.setdefault(c['canonical_id'],[]).append(c)
    values=list(groups.values());random.Random(seed).shuffle(values)
    return [c for group in values for c in group]


def confirmation_population(selection,blocked):
    used=set(blocked);cases=[];unsupported=[]
    for cell in selection['cells']:
        try:
            fresh=population(used,levels=[cell['n']],relevant=[cell['r']],distractors=[cell['d']],tasks=[cell['task']],seeds=CONFIRM_SEEDS,groups_per_seed=8)
        except ValueError as exc:
            if 'support exhausted' not in str(exc):raise
            unsupported.append(dict(cell=cell,reason='insufficient_fresh_canonical_support'));continue
        cases+=fresh
        for c in fresh:used.update(x for x in [c['canonical_id'],c.get('legacy_canonical_id')] if x)
    return shuffled(cases,20261220),unsupported

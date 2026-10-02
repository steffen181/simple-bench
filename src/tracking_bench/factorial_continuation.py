"""Explicit approved suffix execution; immutable stopped prefix, no repeated calls."""
from copy import deepcopy
from pathlib import Path
from .common import read_json,write_new,file_hash
from .budget import money,Budget
from .frontier_campaign import _sources
from . import structured_campaign as runner


def ledger(root):
    path=(Path(root)/'budget.json').resolve();data=read_json(path)
    b=Budget(path,data['limit'],mode=data['mode']).snapshot()
    if money(b['reserved']) or b['halted']:raise ValueError('unsettled prior ledger')
    return dict(path=str(path),hash=file_hash(path),spent=b['spent'])


def remaining_scopes(parent):
    p=runner.protocol(parent);data=read_json(parent/'budget.json')
    return {phase:str(money(cap)-sum((money(a['cost']) for a in data['attempts'].values() if phase in a['scopes']),money(0))) for phase,cap in p['scope_caps'].items()}


def validate_continuation(p,expected=None):
    from .factorial_campaign import validate_priors
    c=p['continuation'];parent=Path(c['parent']);old=runner.protocol(parent);a=runner.audit(parent)
    if 'continuation' in old:raise ValueError('nested continuation unsupported')
    if a['summary']['reason']!='schema_or_completion_failure':raise ValueError('only approved format stop can continue')
    offset=a['summary']['observed']
    if offset!=c['offset'] or not 0<offset<len(old['schedule']):raise ValueError('continuation offset differs')
    if c['parent_seal']!=file_hash(parent/'sha256.json'):raise ValueError('parent seal changed')
    amendment=Path(c['amendment'])
    if p['source_files'].get(str(amendment))!=file_hash(amendment) or read_json(amendment).get('policy')!='format_errors_as_wrong' or p.get('format_errors_as_wrong') is not True:raise ValueError('format policy amendment differs')
    for key in ['cases','contracts','blocked','design','mode','total_cap','reserved_overall']:
        if p[key]!=old[key]:raise ValueError('continuation population/conditions differ')
    if p['schedule']!=old['schedule'][offset:] or (expected is not None and expected!=old['schedule']):raise ValueError('continuation schedule differs')
    if p['priors']!=old['priors']+[ledger(parent)]:raise ValueError('continuation accounting differs')
    if money(p['cap'])!=money(old['cap'])-money(a['budget']['spent']) or p['scope_caps']!=remaining_scopes(parent):raise ValueError('continuation allocation differs')
    if p['prior_spent']!=validate_priors(p['priors'],p['cap']):raise ValueError('continuation prior spend differs')


def freeze_continuation(parent,out,amendment):
    from .factorial_campaign import validate_priors
    parent=Path(parent).resolve();out=Path(out);amendment=Path(amendment).resolve()
    old=runner.protocol(parent);a=runner.audit(parent);offset=a['summary']['observed'];p=deepcopy(old)
    p.update(schedule=old['schedule'][offset:],priors=old['priors']+[ledger(parent)],cap=str(money(old['cap'])-money(a['budget']['spent'])),scope_caps=remaining_scopes(parent),source_hashes=_sources(),format_errors_as_wrong=True,
             continuation=dict(parent=str(parent),parent_seal=file_hash(parent/'sha256.json'),offset=offset,amendment=str(amendment)))
    p['prior_spent']=validate_priors(p['priors'],p['cap'])
    p['source_files'].update({str(amendment):file_hash(amendment),str(parent/'sha256.json'):file_hash(parent/'sha256.json')})
    validate_continuation(p)
    out.mkdir(parents=True,exist_ok=False);write_new(out/'protocol.json',p);write_new(out/'freeze.json',{'protocol_hash':file_hash(out/'protocol.json')})
    for name in ['requests','responses','receipts']:(out/name).mkdir()
    return dict(status='FROZEN',planned=len(p['schedule']),offset=offset,cap=p['cap'],prior_spent=p['prior_spent'])


def merged_development(root):
    root=Path(root);old=runner.audit(root/'development')
    if not (root/'continuation/sha256.json').exists():return old
    new=runner.audit(root/'continuation');p=runner.protocol(root/'continuation');offset=p['continuation']['offset']
    if Path(p['continuation']['parent']).resolve()!=(root/'development').resolve():raise ValueError('merged parent differs')
    if Path(p['continuation']['amendment']).resolve()!=(root/'format-policy-amendment.json').resolve():raise ValueError('merged amendment differs')
    # Audited prefix observations plus the exact frozen suffix; missing stays missing.
    records=old['records'][:offset]+new['records']
    if len(records)!=old['summary']['planned']:raise ValueError('merged coverage differs')
    observed=sum(r is not None for _,_,_,r in records);summary=dict(status=new['summary']['status'],reason=new['summary']['reason'],observed=observed,planned=len(records),phases={})
    for phase in dict.fromkeys(phase for phase,_,_,_ in records):
        rows=[r for ph,_,_,r in records if ph==phase];count=sum(r is not None for r in rows)
        suffix_phase=new['summary']['phases'].get(phase,{})
        reason=suffix_phase.get('reason')
        summary['phases'][phase]=dict(phase=phase,planned=len(rows),observed=count,status='COMPLETE' if count==len(rows) and not reason else 'STOPPED' if count else 'NOT_RUN',reason=reason or (None if count==len(rows) else summary['reason']))
    return dict(status='PASS',summary=summary,budget=dict(new['budget'],spent=str(money(old['budget']['spent'])+money(new['budget']['spent']))),total_accounted=new['total_accounted'],protocol_hash=old['protocol_hash'],records=records,
                segments={name:{k:v for k,v in a.items() if k!='records'} for name,a in [('original_stopped',old),('continuation',new)]},format_errors_as_wrong=True)

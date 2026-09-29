"""Native HF acc_norm primary; generated answers remain a separate secondary endpoint."""
import math
from . import bbh_fresh as fresh
from .bbh_mc import score as native_score
from .common import digest
CONDITIONS=fresh.CONDITIONS
PRIMARY='native_raw_3shot_acc_norm'
COT_PRIMARY=fresh.PRIMARY
messages=fresh.messages
score=fresh.score
interval=fresh.interval
require_lock=fresh.require_lock
audit_resource=fresh.audit_resource


def make_phase(originals,blocked,seeds,per_cell,phase):
    rows=fresh.make_phase(originals,blocked,seeds,per_cell,phase)
    if phase=='confirmation':
        for r in originals:
            c=dict(r,origin='reference',phase=phase,seed=None,rotation=0,group='reference-'+str(r['n'])+'-'+str(r['source_index']))
            c.pop('id',None);c['id']=digest(c);rows.append(c)
    return rows


def requests(cases):
    return [dict(case_id=c['id'],condition=PRIMARY) for c in cases]+fresh.requests([c for c in cases if c['origin']!='reference'])


def native_result(n,target,values):
    return native_score(['('+letter+')' for letter in 'ABCDEFG'[:n]],values,target)


def token_requests(lm,context,n):
    rows=[]
    for letter in 'ABCDEFG'[:n]:
        answer=' ('+letter+')';ctx,cont=lm._encode_pair(context,answer)
        if not ctx or not cont or len(ctx)+len(cont)>lm.max_length:raise ValueError('empty or truncated native continuation')
        rows.append(dict(context=context,answer=answer,context_ids=ctx,answer_ids=cont))
    if any(r['context_ids']!=rows[0]['context_ids'] for r in rows):raise ValueError('candidate-dependent context')
    return rows


def audit_rows(cases,planned,rows):
    by_id={c['id']:c for c in cases};keys=[(r['case_id'],r['condition']) for r in rows];wanted={(r['case_id'],r['condition']) for r in planned}
    if len(by_id)!=len(cases) or len(wanted)!=len(planned) or len(set(keys))!=len(keys) or set(keys)!=wanted:raise ValueError('receipt coverage')
    for r in rows:
        if r['condition']!=PRIMARY:continue
        c=by_id[r['case_id']];values=r['loglikelihoods'];n=c['n']
        if len(values)!=n or any(type(v) not in (int,float) or not math.isfinite(v) or v>0 for v in values):raise ValueError('invalid native likelihoods')
        normalized=[v/3 for v in values];winner=max(range(n),key=normalized.__getitem__);label='('+chr(65+winner)+')'
        expected=dict(prediction=label,correct=label==c['target'],normalized_loglikelihoods=normalized)
        if expected!=r['result'] or r['native_acc_norm']!=float(expected['correct']):raise ValueError('native metric replay differs')
    cotrows=[r for r in rows if r['condition']!=PRIMARY];cotplanned=[r for r in planned if r['condition']!=PRIMARY]
    fresh.audit_rows(cases,cotplanned,cotrows)
    return len(rows)


def harness_sources(hflm_file):
    from pathlib import Path
    return sorted(Path(hflm_file).resolve().parents[1].rglob('*.py'))

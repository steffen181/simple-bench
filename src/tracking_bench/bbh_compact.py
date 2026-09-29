"""Frozen exploratory compact-model comparison, independent of inference backends."""
import re
from collections import defaultdict
from . import bbh_protocol_pilot as pilot
from .common import file_hash


def build_cases(bundle):
    return [c for c in pilot.build_cases(bundle,10) if c['variant']=='identity']


def cot_messages(case):
    return [dict(role='user',content=case['input']+
        '\n\nThink step by step. End with a separate final line in exactly this format: The answer is (X). Replace X with the correct option letter.')]


def parse_cot(text,n):
    lines=text.strip().splitlines()
    if not lines:return None
    match=re.fullmatch(r'The answer is \(([A-G])\)\.?',lines[-1].strip(),re.IGNORECASE)
    if not match or match[1].upper() not in 'ABCDEFG'[:n]:return None
    return '('+match[1].upper()+')'


def cot_result(text,output_ids,budget,eos_ids,n,gold):
    if not output_ids or len(output_ids)>budget:raise ValueError('invalid generated token count')
    stopped=output_ids[-1] in eos_ids
    if not stopped and len(output_ids)<budget:raise ValueError('unexplained early generation stop')
    truncated=not stopped
    answer=parse_cot(text,n)
    return dict(parsed_answer=answer,truncated=truncated,ended_eos=stopped,
                generated_tokens=len(output_ids),correct=not truncated and answer==gold)


def summarize(cases,receipts):
    by_id={c['id']:c for c in cases}
    if len(by_id)!=len(cases):raise ValueError('duplicate case')
    seen=set();rows=defaultdict(list);totals=defaultdict(int)
    def key(c):return (c['origin'],c['n'],c.get('control_kind'))
    for c in cases:totals[key(c)]+=1
    for r in receipts:
        if r['case_id'] in seen or r['case_id'] not in by_id:raise ValueError('duplicate/unknown receipt')
        seen.add(r['case_id']);rows[key(by_id[r['case_id']])].append(r)
    cells=[]
    for k,total in totals.items():
        observed=rows[k];complete=len(observed)==total
        cell=dict(zip(['origin','n','control_kind'],k),total=total,completed=len(observed))
        for method in ('full','single','cot'):
            correct=sum(r['cot']['correct'] if method=='cot' else r[method+'_correct'] for r in observed)
            cell[method+'_correct']=correct;cell[method+'_accuracy']=correct/total if complete else None
            cell[method+'_wilson95']=pilot.wilson(correct,total) if complete else [None,None]
        cell['cot_truncated']=sum(r['cot']['truncated'] for r in observed)
        cell['cot_invalid']=sum(r['cot']['parsed_answer'] is None for r in observed)
        cells.append(cell)
    return dict(status='COMPLETE' if len(seen)==len(cases) else 'INCOMPLETE',expected=len(cases),completed=len(seen),cells=cells,scientific_success=False)


def verify_files(root,manifest):
    for name,expected in manifest.items():
        path=root/name
        if not path.is_file() or file_hash(path)!=expected:raise ValueError('file missing/changed: '+name)


def audit_receipt(case,row,budget,eos_ids):
    """Independent replay: arithmetic and finite label lookup, not production scorer."""
    import math
    n=case['n'];gold=case['target']
    for method,denom in [('full',3),('single',1)]:
        values=row[method+'_loglikelihoods']
        if len(values)!=n or any(type(v) not in (float,int) or not math.isfinite(v) or v>0 for v in values):
            raise ValueError('invalid likelihoods')
        index=max(range(n),key=lambda i:values[i]/denom)
        answer='('+chr(65+index)+')';pred=answer if method=='full' else answer[1]
        if row[method]['prediction']!=pred or row[method]['correct']!=(answer==gold) or row[method+'_correct']!=(answer==gold):
            raise ValueError('likelihood decision mismatch')
        if row[method]['normalized_loglikelihoods']!=[v/denom for v in values]:raise ValueError('normalization mismatch')
    lines=row['generated_text'].strip().splitlines();last=lines[-1].strip().lower() if lines else ''
    labels={f'the answer is ({c.lower()})'+end:'('+c+')' for c in 'ABCDEFG'[:n] for end in ('','.')}
    answer=labels.get(last);ids=row['generated_token_ids']
    if not ids or len(ids)>budget:raise ValueError('invalid output token count')
    stopped=ids[-1] in eos_ids
    if not stopped and len(ids)!=budget:raise ValueError('unexplained early stop')
    expected=dict(parsed_answer=answer,truncated=not stopped,ended_eos=stopped,generated_tokens=len(ids),correct=stopped and answer==gold)
    if expected!=row['cot']:raise ValueError('CoT decision mismatch')


def generation_contract():
    # Do not inherit checkpoint-specific repetition penalties or beam search.
    return dict(do_sample=False,max_new_tokens=1024,use_cache=True,repetition_penalty=1.0,num_beams=1)

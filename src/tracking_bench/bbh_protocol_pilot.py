"""Offline exploratory protocol controls, with no model loading or fitting."""
import math
import random
import re
from collections import defaultdict
from .bbh import parse_question, solve_backward
from .bbh_mc import task_configs, score
from .common import digest, read_json


def configs(bundle):
    return {len(c['doc_to_choice']): c for c in task_configs(bundle) if '_original_' in c['task']}


def control_gold(row):
    obj=solve_backward(row['initial'],row['events'],row['query'])
    return '('+chr(65+row['objects'].index(obj))+')'


def controls():
    rows=[]
    for n in (3,5,7):
        names=['Ada','Ben','Cara','Dan','Eva','Finn','Gia'][:n]
        objects=['red ball','blue ball','green ball','white ball','pink ball','black ball','yellow ball'][:n]
        for kind in ('zero_swap','one_swap','readout'):
            for query in (0,2):
                initial=objects[1:]+objects[:1]
                events=[(0,1)] if kind=='one_swap' else []
                if kind=='readout':initial=initial[::-1]
                text=('The final assignments are: ' if kind=='readout' else 'Initially: ')
                text+='; '.join(f'{a} has the {b}' for a,b in zip(names,initial))+'. '
                text+=('Ada and Ben swap their balls. ' if events else 'No balls are exchanged. ')
                text+=f'Which ball does {names[query]} have now?\nOptions:\n'
                text+='\n'.join(f'({chr(65+i)}) {obj}' for i,obj in enumerate(objects))
                row=dict(input=text,n=n,origin='control',variant='identity',control_kind=kind,
                         initial=initial,events=events,query=query,objects=objects,index=query)
                row['target']=control_gold(row);row['id']=digest(row);rows.append(row)
    return rows


def validate_case(row):
    if row['origin']=='control':
        state=list(row['initial'])
        for a,b in row['events']:state[a],state[b]=state[b],state[a]
        expected='('+chr(65+row['objects'].index(state[row['query']]))+')'
        if expected!=control_gold(row) or row['target']!=expected:
            raise ValueError('control gold mismatch')
    elif parse_question(row['input'])['gold']!=row['target']:
        raise ValueError('BBH gold mismatch')


def build_cases(bundle,per_cell=10):
    if type(per_cell) is not int or not 1<=per_cell<=250:raise ValueError('invalid per_cell')
    cases=[]
    for cfg in task_configs(bundle):
        n=len(cfg['doc_to_choice']);origin='generated' if '_generated_' in cfg['task'] else 'original'
        for index,doc in enumerate(read_json(cfg['dataset_kwargs']['data_files']['test'])[:per_cell]):
            parsed=parse_question(doc['input'])
            row=dict(doc,n=n,origin=origin,index=index,variant='identity',objects=parsed['objects'])
            row['id']=digest(row);cases.append(row)
            objects=row['objects'][1:]+row['objects'][:1]
            correct=row['objects'][ord(row['target'][1])-65]
            question=re.sub(r'(\(([A-G])\) )[^\n]+',
                            lambda match:match[1]+objects[ord(match[2])-65],row['input'])
            rotated=dict(row,input=question,objects=objects,target='('+chr(65+objects.index(correct))+')',
                         variant='rotated',parent_id=row['id'])
            rotated.pop('id');rotated['id']=digest(rotated);cases.append(rotated)
    cases+=controls()
    for c in cases:validate_case(c)
    return cases


def raw_prompt(case,cfg):
    examples=[f"Q: {s['input']}\nA: {s['target']}" for s in cfg['fewshot_config']['samples']]
    from jinja2 import Environment, StrictUndefined
    description=Environment(undefined=StrictUndefined).from_string(cfg['description']).render()
    return description+cfg['fewshot_delimiter'].join(examples+[f"Q: {case['input']}\nA:"])


def chat_messages(case,cfg):
    messages=[dict(role='system',content=cfg['description'].strip()+' Answer with only the option label, for example (A).')]
    for s in cfg['fewshot_config']['samples']:
        messages.extend([dict(role='user',content=s['input']),dict(role='assistant',content=s['target'])])
    messages.append(dict(role='user',content=case['input']))
    return messages


def parse_generation(text,n):
    # Only a standalone label on the first nonempty line; no answer mining.
    lines=text.strip().splitlines()
    if not lines:return None
    match=re.fullmatch(r'(?:\(([A-G])\)|([A-G]))\.?',lines[0].strip())
    if not match:return None
    letter=match[1] or match[2]
    return '('+letter+')' if letter in 'ABCDEFG'[:n] else None


def decisions(n,gold,full,single,text):
    a=score([f'({c})' for c in 'ABCDEFG'[:n]],full,gold)
    b=score(list('ABCDEFG'[:n]),single,gold[1])
    generated=parse_generation(text,n)
    return dict(full=a,single=b,generated=dict(prediction=generated,correct=generated==gold),
                agreement=a['prediction'][1]==b['prediction'])


def wilson(k,n):
    if n<=0:return [None,None]
    z=1.959963984540054;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,center-half),min(1,center+half)]


def paired_interval(differences):
    if not differences:return [None,None]
    rng=random.Random(20260928);n=len(differences)
    values=sorted(sum(rng.choices(differences,k=n))/n for _ in range(2000))
    return [values[49],values[1949]]


def summarize(cases,receipts,conditions):
    by_id={c['id']:c for c in cases};seen=set();groups=defaultdict(list)
    for row in receipts:
        key=(row['case_id'],row['condition'])
        if key in seen or key[0] not in by_id or key[1] not in conditions:raise ValueError('duplicate/unknown receipt')
        seen.add(key);case=by_id[key[0]]
        groups[(case['origin'],case['n'],case['variant'],case.get('control_kind'),key[1])].append(row['result'])
    expected=defaultdict(int)
    for c in cases:
        for condition in conditions:expected[(c['origin'],c['n'],c['variant'],c.get('control_kind'),condition)]+=1
    cells=[]
    for key,total in expected.items():
        rows=groups[key];cell=dict(zip(['origin','n','variant','control_kind','condition'],key),total=total,completed=len(rows))
        for method in ('full','single','generated'):
            correct=sum(r[method]['correct'] for r in rows)
            cell[method+'_accuracy']=correct/total if len(rows)==total else None
            cell[method+'_correct']=correct
            cell[method+'_wilson95']=wilson(correct,total) if len(rows)==total else [None,None]
        cell['generated_valid']=sum(r['generated']['prediction'] is not None for r in rows)
        cell['prediction_agreement']=sum(r['agreement'] for r in rows)/total if len(rows)==total else None
        cells.append(cell)
    return dict(status='COMPLETE' if len(seen)==len(cases)*len(conditions) else 'INCOMPLETE',
                expected=len(cases)*len(conditions),completed=len(seen),cells=cells,
                scientific_success=False,interpretation='Exploratory protocol pilot; no equivalence or confirmation claim')


def token_requests(lm,context,n,condition,max_new_tokens=8):
    if condition not in ('raw','chat'):raise ValueError('invalid condition')
    requests=[]
    for choice in [f'({c})' for c in 'ABCDEFG'[:n]]+list('ABCDEFG'[:n]):
        answer=(' ' if condition=='raw' else '')+choice
        if condition=='raw':ctx,cont=lm._encode_pair(context,answer)
        else:
            # The chat template already includes special tokens and its final newline.
            # Explicit token continuations retain that exact API-like boundary.
            ctx=lm.tok_encode(context,add_special_tokens=False)
            cont=lm.tok_encode(answer,add_special_tokens=False)
        if not ctx or not cont:raise ValueError('empty token context/answer')
        if len(ctx)+max(len(cont),max_new_tokens)>lm.max_length:raise ValueError('would truncate')
        requests.append(dict(context=context,answer=answer,context_ids=ctx,answer_ids=cont))
    if any(len(r['answer_ids'])!=1 for r in requests[n:]):raise ValueError('short candidate is not one token')
    if any(r['context_ids']!=requests[0]['context_ids'] for r in requests):raise ValueError('candidate-dependent context')
    return requests


def stream_hash(path):
    import hashlib
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def snapshot_files(snapshot):
    from pathlib import Path
    snapshot=Path(snapshot)
    needed={'config.json','tokenizer.json'}
    index=snapshot/'model.safetensors.index.json'
    if index.exists():needed.update(read_json(index)['weight_map'].values())
    else:needed.add('model.safetensors')
    if any(not (snapshot/name).is_file() for name in needed):raise ValueError('missing snapshot files')
    return {p.name:stream_hash(p) for p in sorted(snapshot.iterdir()) if p.is_file()}


def check_thinking_disabled(context):
    without_empty=re.sub(r'<think>\s*</think>','',context)
    if '/think' in without_empty or '<think>' in without_empty or '</think>' in without_empty:
        raise ValueError('thinking-enabled template')


def resource_status(available_bytes,process_swap_bytes,initial_process_swap_bytes,global_swap_bytes):
    """Guard the measured process; global paging can belong to unrelated IDE jobs."""
    growth=max(0,process_swap_bytes-initial_process_swap_bytes)
    return dict(approved=available_bytes>=1024**3 and growth<=64*1024**2,
                available_bytes=available_bytes,process_swap_bytes=process_swap_bytes,
                process_swap_growth=growth,global_swap_bytes=global_swap_bytes)

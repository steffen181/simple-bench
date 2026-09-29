"""Prospective structure-disjoint BBH study. Pure generation, scoring and grouped analysis."""
import random
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from . import bbh
from .common import digest,read_json,file_hash

CONDITIONS={
 'cot0_1024':dict(style='cot',shots=0,budget=1024),
 'direct0_1024':dict(style='direct',shots=0,budget=1024),
 'cot3_1024':dict(style='cot',shots=3,budget=1024),
 'cot0_256':dict(style='cot',shots=0,budget=256),
}
PRIMARY='cot0_1024'


def rotate(case):
    objects=case['objects'][1:]+case['objects'][:1]
    correct=case['objects'][ord(case['target'][1])-65]
    text=re.sub(r'(\(([A-G])\) )[^\n]+',lambda m:m[1]+objects[ord(m[2])-65],case['input'])
    target='('+chr(65+objects.index(correct))+')'
    return dict(case,input=text,objects=objects,target=target,gold=target,initial=[(i-1)%case['n'] for i in case['initial']],rotation=1)


def controls(phase):
    rows=[];names=['Iris','Jules','Kira','Leon','Mara','Nils','Olga'];objects=['red ball','blue ball','green ball','white ball','pink ball','black ball','yellow ball']
    for n in (5,7):
        for kind in ('copy','readout','one_swap'):
            for query in (0,n-1):
                initial=objects[1:n]+objects[:1];events=[(0,n-1)] if kind=='one_swap' else []
                if kind=='copy':
                    target='('+chr(65+query)+')';text=f'Copy this option label exactly as the answer: {target}. The allowed option labels are '+', '.join('('+c+')' for c in 'ABCDEFG'[:n])+'.'
                else:
                    text='Initially, '+'; '.join(f'{names[i]} has the {initial[i]}' for i in range(n))+'. '
                    text+=(f'{names[0]} and {names[n-1]} swap their balls. ' if events else 'No balls are exchanged. ')
                    text+=f'Which ball does {names[query]} have now?\nOptions:\n'+'\n'.join(f'({chr(65+i)}) {v}' for i,v in enumerate(objects[:n]))
                    final=initial.copy()
                    for a,b in events:final[a],final[b]=final[b],final[a]
                    expected=bbh.solve_backward(initial,events,query)
                    assert final[query]==expected
                    target='('+chr(65+objects[:n].index(expected))+')'
                c=dict(phase=phase,origin='control',control_kind=kind,n=n,seed=None,group=f'control-{kind}-{n}-{query}',rotation=0,
                       input=text,target=target,objects=objects[:n],initial=initial,events=events,query_person=query)
                c['id']=digest(c);rows.append(c)
    return rows


def make_phase(originals,blocked,seeds,per_cell,phase):
    if not seeds or len(set(seeds))!=len(seeds) or per_cell<1:raise ValueError('invalid generator settings')
    used=set(blocked);used_anchors=set();rows=[]
    for seed in seeds:
        rng=random.Random(seed)
        for n in (5,7):
            templates=[r for r in originals if r['n']==n and digest(r['input']) not in used_anchors]
            chosen=rng.sample(templates,per_cell)
            for template in chosen:
                used_anchors.add(digest(template['input']));pairs=list(combinations(range(n),2))
                for attempt in range(100000):
                    events=[rng.choice(pairs) for _ in range(n)]
                    if any(a==b for a,b in zip(events,events[1:])) or set(sum((list(e) for e in events),[]))!=set(range(n)):continue
                    group=bbh.structure_id(dict(n=n,query_person=template['query_person'],events=events))
                    if group in used:continue
                    used.add(group);break
                else:raise ValueError('fresh structural support exhausted')
                events=[e if rng.randrange(2) else e[::-1] for e in events]
                event_text=' '.join(f"{('First' if j==0 else 'Finally' if j==n-1 else 'Then')}, {bbh.NAMES[a]} and {bbh.NAMES[b]} {bbh.VERBS[template['context']]}." for j,(a,b) in enumerate(events))
                text=template['input'];start=text.index('First, ');end=text.index(' At the end of ',start)
                text=text[:start]+event_text+text[end:]
                target='('+chr(65+bbh.solve_backward(template['initial'],events,template['query_person']))+')'
                fresh=bbh.verify_example(dict(input=text,target=target))
                assert fresh['structure_id']==group
                for origin,source in [('generated',fresh),('anchor',template)]:
                    base=dict(source,phase=phase,origin=origin,group=group,seed=seed,rotation=0,anchor_source_index=template['source_index'])
                    for c in (base,rotate(base)):
                        checked=bbh.verify_example(c)
                        assert checked['structure_id']==source['structure_id']
                        c.pop('id',None);c['id']=digest(c);rows.append(c)
    return controls(phase)+rows


def answer(text,n,strict=False):
    lines=text.strip().splitlines()
    if not lines:return None
    last=lines[-1].strip()
    if not strict:last=last.replace('**','').replace('`','')
    found=re.fullmatch(r'The answer is \(([A-G])\)\.?',last,re.I)
    return '('+found[1].upper()+')' if found and found[1].upper() in 'ABCDEFG'[:n] else None


def score(text,ids,budget,eos,n,target):
    if not ids or len(ids)>budget:raise ValueError('invalid output count')
    complete=ids[-1] in eos
    if not complete and len(ids)<budget:raise ValueError('unexplained early stop')
    label=answer(text,n);strict=answer(text,n,True)
    return dict(prediction=label,correct=complete and label==target,strict_correct=complete and strict==target,
                strict_format=strict is not None,invalid=label is None,truncated=not complete,tokens=len(ids))


def instruction(condition):
    style=CONDITIONS[condition]['style']
    return ('Think step by step.' if style=='cot' else 'Do not include reasoning.')+' End with a separate final line in exactly this format: The answer is (X). Replace X with the correct option letter.'


def demo_answer(demo):
    parsed=bbh.verify_example(demo);state=list(parsed['initial']);lines=[]
    for i,(a,b) in enumerate(parsed['events']):
        state[a],state[b]=state[b],state[a]
        lines.append(f'After swap {i+1}: '+', '.join(f'{bbh.NAMES[j]} has {parsed["objects"][state[j]]}' for j in range(parsed['n']))+'.')
    assert '('+chr(65+state[parsed['query_person']])+')'==demo['target']
    return '\n'.join(lines)+f'\nThe answer is {demo["target"]}.'


def messages(case,condition,demos):
    cfg=CONDITIONS[condition];result=[];suffix='\n\n'+instruction(condition)
    for d in demos[:cfg['shots']]:
        result.extend([dict(role='user',content=d['input']+suffix),dict(role='assistant',content=demo_answer(d))])
    result.append(dict(role='user',content=case['input']+suffix))
    return result


def requests(cases):
    return [dict(case_id=c['id'],condition=condition) for c in cases for condition in ([PRIMARY] if c['origin']=='anchor' else CONDITIONS)]


def require_lock(root,protocol_hash):
    path=Path(root)/'post_development_lock.json'
    if not path.is_file():raise ValueError('confirmation requires successful development lock')
    lock=read_json(path)
    if lock.get('protocol_sha256')!=protocol_hash or lock.get('development_audit_sha256')!=file_hash(Path(root)/'development/audit.json') or not lock.get('approved'):
        raise ValueError('invalid development lock')
    dev=Path(root)/'development';audit=read_json(dev/'audit.json')
    if audit.get('status')!='PASS' or not audit.get('approved') or audit.get('protocol_sha256')!=protocol_hash:
        raise ValueError('development audit did not approve this protocol')
    if file_hash(dev/'sha256.json')!=lock.get('development_manifest_sha256'):
        raise ValueError('development manifest changed')
    for name,expected in read_json(dev/'sha256.json').items():
        if file_hash(dev/name)!=expected:raise ValueError('sealed development changed')
    return lock


def interval(records,coverage):
    if not records:return [None,None]
    if len({r['group'] for r in records})!=len(records):raise ValueError('duplicate group')
    groups=defaultdict(list)
    for r in records:groups[(r['seed'],r['n'])].append(r['value'])
    if any(len(v)<2 for v in groups.values()):return [None,None]
    rng=random.Random(2026092930);values=[]
    for _ in range(5000):
        values.append(sum(sum(rng.choices(v,k=len(v))) for v in groups.values())/len(records))
    values.sort();tail=(1-coverage)/2
    return [values[int(tail*len(values))],values[min(len(values)-1,int((1-tail)*len(values)))]]


def audit_rows(cases,planned,rows):
    by_id={c['id']:c for c in cases};wanted={(r['case_id'],r['condition']) for r in planned}
    keys=[(r['case_id'],r['condition']) for r in rows]
    if len(by_id)!=len(cases) or len(wanted)!=len(planned) or len(set(keys))!=len(keys) or set(keys)!=wanted:
        raise ValueError('incomplete/duplicate/unknown receipt coverage')
    for row in rows:
        c=by_id[row['case_id']];budget=CONDITIONS[row['condition']]['budget'];ids=row['output_ids']
        if not ids or len(ids)>budget:raise ValueError('invalid output tokens')
        complete=ids[-1] in row['eos_ids']
        if not complete and len(ids)!=budget:raise ValueError('unexplained stop')
        lines=row['text'].strip().splitlines();last=lines[-1].strip().lower() if lines else ''
        legal={f'the answer is ({letter.lower()})'+dot:'('+letter+')' for letter in 'ABCDEFG'[:c['n']] for dot in ('','.')}
        pred=legal.get(last.replace('**','').replace('`',''));strict=legal.get(last)
        expected=dict(prediction=pred,correct=complete and pred==c['target'],strict_correct=complete and strict==c['target'],
            strict_format=strict is not None,invalid=pred is None,truncated=not complete,tokens=len(ids))
        if expected!=row['result']:raise ValueError('independent score replay differs')
    return len(rows)


def audit_resource(row,initial_swap):
    growth=max(0,row['process_swap_bytes']-initial_swap)
    approved=row['available_bytes']>=1024**3 and growth<=64*1024**2
    if row['process_swap_growth']!=growth or row['approved']!=approved or not approved:
        raise ValueError('independent resource audit failed')

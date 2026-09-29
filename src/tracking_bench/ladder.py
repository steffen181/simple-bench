"""Seeded complexity grid; no model outcomes enter sampling or gold construction."""
import random
import re
from .common import digest
from .corpus import validate_corpus
from .scoring import PARSER_VERSION
from .structure import canonical_structure,solve
NAMES=('Alice','Ben','Clara','David','Emma','Frank','Grace')
OBJECTS=('key','book','cup','ring','coin','card','pen')


def replay_text(prompt):
    owners={};query=None
    for line in prompt.splitlines():
        if m:=re.fullmatch(r'(\w+) initially holds the (\w+)\.',line):
            if m[2] in owners:raise ValueError('duplicate object')
            owners[m[2]]=m[1]
        elif m:=re.fullmatch(r'(\w+) and (\w+) swap all the objects they hold\.',line):
            owners={obj:m[2] if p==m[1] else m[1] if p==m[2] else p for obj,p in owners.items()}
        elif m:=re.fullmatch(r'(\w+) gives the (\w+) to (\w+)\.',line):
            if owners.get(m[2])!=m[1]:raise ValueError('invalid giver')
            owners[m[2]]=m[3]
        elif m:=re.fullmatch(r'Who holds the (\w+) now\?',line):query=m[1]
        elif line!='Track who holds each object. Follow the events in order.' and not re.fullmatch(r'Answer with only one of these names: [A-Za-z, ]+\.',line):raise ValueError('unknown prompt clause')
    if query not in owners:raise ValueError('missing queried object')
    return owners[query]


def _episode(rng,n,k,relevant,task):
    state=list(range(n));rng.shuffle(state);initial=state.copy();query=rng.randrange(n)
    flags=[True]*relevant+[False]*(k-relevant);rng.shuffle(flags);events=[]
    for flag in flags:
        if task=='swap':
            owner=state[query]
            a,b=(owner,rng.choice([p for p in range(n) if p!=owner])) if flag else rng.sample([p for p in range(n) if p!=owner],2)
            events.append(dict(kind='swap',source=a,target=b));state=[b if x==a else a if x==b else x for x in state]
        else:
            obj=query if flag else rng.choice([o for o in range(n) if o!=query]);a=state[obj];b=rng.choice([p for p in range(n) if p!=a])
            events.append(dict(kind='give',object=obj,source=a,target=b));state[obj]=b
    episode=dict(task=task,initial=initial,query=query,events=events)
    if solve(episode)!=state[query]:raise ValueError('independent oracle mismatch')
    return episode,state[query]


def generate(entities=(4,),steps=(4,8,16,32),per_cell=4,seed=20260929,blocked=()):
    entities=list(entities);steps=list(steps)
    if not entities or not steps or len(set(entities))!=len(entities) or len(set(steps))!=len(steps):raise ValueError('empty/duplicate grid')
    if any(type(n) is not int or not 3<=n<=7 for n in entities) or any(type(k) is not int or not 0<=k<=128 for k in steps):raise ValueError('entities3..7 and steps0..128 required')
    if type(seed) is not int or type(per_cell) is not int or not 1<=per_cell<=64:raise ValueError('integer seed and per_cell1..64 required')
    if 0 in steps and per_cell!=1:raise ValueError('zero-event support is one canonical class per entity count')
    if len(entities)*len(steps)*per_cell*8>8192:raise ValueError('grid too large; use separate sealed corpora')
    blocked=set(blocked)
    if any(not isinstance(x,str) or len(x)!=64 or any(c not in '0123456789abcdef' for c in x) for x in blocked):raise ValueError('invalid canonical exclusions')
    used=set(blocked);rng=random.Random(seed);cases=[]
    for n in entities:
        for k in steps:
            for task in ('swap','handoff') if k else ('swap',):
                for relevant in sorted({k//2,k}):
                    count=0
                    for _ in range(10000):
                        episode,gold=_episode(rng,n,k,relevant,task);identity=canonical_structure(episode)
                        if identity in used:continue
                        used.add(identity);count+=1
                        prefix=['Track who holds each object. Follow the events in order.']
                        prefix += [f'{NAMES[owner]} initially holds the {OBJECTS[obj]}.' for obj,owner in enumerate(episode['initial'])]
                        for e in episode['events']:
                            a,b=NAMES[e['source']],NAMES[e['target']]
                            prefix.append(f'{a} and {b} swap all the objects they hold.' if e['kind']=='swap' else f"{a} gives the {OBJECTS[e['object']]} to {b}.")
                        prefix.append(f"Who holds the {OBJECTS[episode['query']]} now?")
                        for rotation in (0,1):
                            names=list(NAMES[:n]);names=names[rotation:]+names[:rotation]
                            prompt='\n'.join(prefix+[f"Answer with only one of these names: {', '.join(names)}."])
                            if replay_text(prompt)!=NAMES[gold]:raise ValueError('independent text replay failed')
                            c=dict(suite='tracking-ladder-v1',scenario_id=identity,family_id=identity,canonical_id=identity,pair_id=identity,
                                prompt=prompt,prompt_hash=digest(prompt),candidates=names,gold=NAMES[gold],object=OBJECTS[episode['query']],answer_to_person={name:i for i,name in enumerate(NAMES[:n])},
                                stratum=dict(entities=n,task=task,k_total=k,relevant_updates=relevant,irrelevant_events=k-relevant,condition='ownership',variant=f'rotation{rotation}'),
                                control=k==0,data_role='calibration' if k==0 else 'generator_sample',source=f'tracking-ladder-v1/seed-{seed}',structure=episode)
                            c['id']=digest(c);cases.append(c)
                        if count==per_cell:break
                    else:raise ValueError(f'canonical support exhausted for N={n}, steps={k}, relevant={relevant}, task={task}; lower per_cell or change grid')
    rng.shuffle(cases)
    corpus=dict(schema='functional-benchmark-corpus-v1',parser=PARSER_VERSION,sources={},suites=['tracking-ladder-v1'],cases=cases,
        generator=dict(version='tracking-ladder-v1',seed=seed,entities=entities,steps=steps,per_cell=per_cell,blocked=sorted(blocked)),
        limitations=['Complexity grid, not proven monotonically increasing model difficulty.','No outcome-dependent balancing, selection or fitting; inspect label distribution.',
            'Groups invariant to person/object relabeling; both answer orderings share a group.','Exclusions cover supplied canonical IDs only; provider training data unknown.',
            'Zero-event cells are calibration, not novel structure claims.','Names/objects fixed; not an exact BBH prompt or acc_norm endpoint.'])
    corpus['hash']=digest(corpus);validate_corpus(corpus);return corpus

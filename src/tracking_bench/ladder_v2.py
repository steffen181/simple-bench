"""Scalable seeded ladder; fixed cells, independent oracle, no model-based sampling."""
import random
import re
from .common import digest
from .corpus import validate_corpus
from .ladder import replay_text
from .structure import canonical_structure
from .structure_large import solve,canonical_id
from .scoring import PARSER_VERSION
NAMES=tuple('Alice Ben Clara David Emma Frank Grace Henry Iris Jack Kara Liam Maya Noah Olivia Paul Quinn Rose Sam Tina Uma Victor Wendy Xavier Yara Zack Ada Bella Caleb Diana Ethan Fiona Gavin Hazel Isaac Julia Kevin Laura Miles Nora Oscar Petra Riley Sofia Theo Vera Walter Xena Yusuf Zoe Aaron Blair Colin Dora Edwin Flora Hugo Ingrid Jonas Kate Lucas Marie Nolan Owen'.split())
OBJECTS=tuple('key book cup ring coin card pen ball badge bell bolt bowl box brush button cable camera candle cap chain chair chalk clock coat comb cone dice disc doll drum fan flag flute fork glove hat jar kite knife lamp leaf lock map mask medal mirror mug nail note nut paddle pan pearl pencil phone pin plate pot radio rake rope ruler scarf shell'.split())
assert len(NAMES)==len(OBJECTS)==64 and len(set(NAMES))==len(set(OBJECTS))==64


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


def generate(entities=(4,),steps=(32,),relevant_updates=None,tasks=('swap','handoff'),per_cell=2,seed=20261001,blocked=()):
    entities=list(entities);steps=list(steps);tasks=list(tasks);blocked=set(blocked)
    if any(not vals or len(set(vals))!=len(vals) for vals in (entities,steps,tasks)):raise ValueError('empty/duplicate grid')
    if any(type(n) is not int or not 3<=n<=64 for n in entities) or any(type(k) is not int or not 0<=k<=128 for k in steps):raise ValueError('invalid dimensions')
    if any(t not in ('swap','handoff') for t in tasks) or type(per_cell) is not int or not 1<=per_cell<=64 or type(seed) is not int:raise ValueError('invalid task/count/seed')
    if relevant_updates is not None and (type(relevant_updates) is not int or any(not 0<=relevant_updates<=k for k in steps)):raise ValueError('invalid relevant updates')
    if 0 in steps and (per_cell!=1 or tasks!=['swap']):raise ValueError('zero-event support: one swap-labelled group per N')
    if len(entities)*len(steps)*len(tasks)*per_cell*2>8192:raise ValueError('grid exceeds resource cap')
    if any(not isinstance(x,str) or not re.fullmatch('[a-f0-9]{64}',x) for x in blocked):raise ValueError('invalid blocked identity')
    rng=random.Random(seed);used=set(blocked);cases=[]
    for n in entities:
        for k in steps:
            relevant=k//2 if relevant_updates is None else relevant_updates
            for task in tasks:
                count=0
                for _ in range(10000):
                    episode,gold=_episode(rng,n,k,relevant,task);identity=canonical_id(episode)
                    legacy=canonical_structure(episode) if n<=7 else None
                    if identity in used or legacy in used:continue
                    used.add(identity)
                    if legacy:used.add(legacy)
                    lines=['Track who holds each object. Follow the events in order.']
                    lines += [f'{NAMES[p]} initially holds the {OBJECTS[o]}.' for o,p in enumerate(episode['initial'])]
                    for e in episode['events']:
                        a,b=NAMES[e['source']],NAMES[e['target']]
                        lines.append(f'{a} and {b} swap all the objects they hold.' if e['kind']=='swap' else f"{a} gives the {OBJECTS[e['object']]} to {b}.")
                    lines.append(f'Who holds the {OBJECTS[episode["query"]]} now?')
                    for rotation in (0,1):
                        names=list(NAMES[:n]);names=names[rotation:]+names[:rotation]
                        prompt='\n'.join(lines+[f"Answer with only one of these names: {', '.join(names)}."])
                        if replay_text(prompt)!=NAMES[gold]:raise ValueError('independent text replay mismatch')
                        c=dict(suite='tracking-ladder-v2',scenario_id=identity,family_id=identity,canonical_id=identity,legacy_canonical_id=legacy,pair_id=identity,
                            prompt=prompt,prompt_hash=digest(prompt),candidates=names,gold=NAMES[gold],object=OBJECTS[episode['query']],answer_to_person={name:i for i,name in enumerate(NAMES[:n])},
                            stratum=dict(entities=n,task=task,k_total=k,relevant_updates=relevant,irrelevant_events=k-relevant,condition='ownership',variant=f'rotation{rotation}',seed=seed),
                            control=k==0,data_role='calibration' if k==0 else 'generator_sample',source=f'tracking-ladder-v2/seed-{seed}',structure=episode)
                        c['id']=digest(c);cases.append(c)
                    count+=1
                    if count==per_cell:break
                else:raise ValueError('canonical support exhausted')
    rng.shuffle(cases)
    result=dict(schema='functional-benchmark-corpus-v1',parser=PARSER_VERSION,sources={},suites=['tracking-ladder-v2'],cases=cases,
        generator=dict(version='tracking-ladder-v2',seed=seed,entities=entities,steps=steps,relevant_updates=relevant_updates,tasks=tasks,per_cell=per_cell,blocked=sorted(blocked)),
        limitations=['Designed complexity is not guaranteed monotonic model difficulty.','Renaming-invariant graph groups; independent text replay and possession-set solver.','Group freshness relative to supplied exclusions only; provider training unknown.','Different suite from BBH, not native acc_norm.'])
    result['hash']=digest(result);validate_corpus(result);return result

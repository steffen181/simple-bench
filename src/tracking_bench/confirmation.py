"""Prospective paired answer contracts with independent text replay."""
from collections import Counter
import random
import re
from .common import digest
from .corpus import validate_corpus
from .dense import _episode
from .scoring import PARSER_VERSION
from .structure import canonical_structure,solve

SURFACES={'A':(('Ansel','Bram','Celia','Dorian'),('lamp','drum','vase','brush')),
          'B':(('Elin','Marek','Sora','Tomas'),('rope','bell','fork','comb'))}
VARIANTS=('only_name','only_final','work_final')


def replay_prompt(prompt):
    """Read rendered ownership language independently of generator state arrays."""
    possessions={};query=None;copy=None
    for line in prompt.splitlines():
        initial=re.fullmatch(r'Initial possession: (\w+) has the (\w+)\.',line)
        reverse=re.fullmatch(r'At the start, the (\w+) belongs to (\w+)\.',line)
        if initial or reverse:
            name,obj=(initial[1],initial[2]) if initial else (reverse[2],reverse[1])
            possessions.setdefault(name,set()).add(obj);continue
        swap=(re.fullmatch(r'Exchange: (\w+) and (\w+) exchange everything they hold\.',line)
              or re.fullmatch(r'(\w+) exchanges all possessions with (\w+)\.',line))
        if swap:
            a,b=swap[1],swap[2];possessions[a],possessions[b]=possessions[b],possessions[a];continue
        give=re.fullmatch(r'Transfer: (\w+) hands the (\w+) to (\w+)\.',line)
        revgive=re.fullmatch(r'The (\w+) is passed from (\w+) to (\w+)\.',line)
        if give or revgive:
            a,obj,b=(give[1],give[2],give[3]) if give else (revgive[2],revgive[1],revgive[3])
            if obj not in possessions[a]:raise ValueError('rendered giver does not hold object')
            possessions[a].remove(obj);possessions[b].add(obj);continue
        question=(re.fullmatch(r'Current holder of the (\w+)\?',line)
                  or re.fullmatch(r'Identify the current owner of the (\w+)\.',line))
        if question:query=question[1];continue
        marker=re.fullmatch(r'Copy this person name: (\w+)\.',line)
        if marker:
            copy=marker[1];continue
        if line=='Read the ownership record in chronological order.' or line.startswith(('Respond with ','You may include ')):
            continue
        raise ValueError('unrecognized rendered line')
    if copy:return copy
    owners=[p for p,objects in possessions.items() if query in objects]
    if len(owners)!=1:raise ValueError('rendered question has no unique answer')
    return owners[0]


def render(episode,surface,variant,control=False):
    names,objects=SURFACES[surface]
    lines=['Read the ownership record in chronological order.']
    for obj,owner in enumerate(episode['initial']):
        lines.append(f'Initial possession: {names[owner]} has the {objects[obj]}.' if surface=='A'
                     else f'At the start, the {objects[obj]} belongs to {names[owner]}.')
    for e in episode['events']:
        a,b=names[e['source']],names[e['target']]
        if e['kind']=='swap':
            lines.append(f'Exchange: {a} and {b} exchange everything they hold.' if surface=='A'
                         else f'{a} exchanges all possessions with {b}.')
        else:
            obj=objects[e['object']]
            lines.append(f'Transfer: {a} hands the {obj} to {b}.' if surface=='A'
                         else f'The {obj} is passed from {a} to {b}.')
    gold=names[solve(episode)];obj=objects[episode['query']]
    lines.append(f'Copy this person name: {gold}.' if control else
                 f'Current holder of the {obj}?' if surface=='A' else f'Identify the current owner of the {obj}.')
    candidates=', '.join(names)
    ending={'only_name':f'Respond with exactly one name from {candidates}. Do not include any other text.',
            'only_final':f'Respond with exactly one line: Final answer: NAME. Replace NAME with one of {candidates}. Do not include any other text.',
            'work_final':f'You may include working text before your answer. End with exactly one final line: Final answer: NAME. Replace NAME with one of {candidates}.'}[variant]
    lines.append(ending);return '\n'.join(lines)


def _cases(episode,group,role,control=False):
    family=canonical_structure(episode)
    for surface,(names,objects) in SURFACES.items():
        for variant in VARIANTS:
            prompt=render(episode,surface,variant,control)
            gold=names[solve(episode)]
            if replay_prompt(prompt)!=gold:raise ValueError('rendered oracle mismatch')
            relevant=len(episode['events']) if group=='all' else len(episode['events'])//2
            case=dict(suite='confirmation-v1',scenario_id=family,family_id=family,canonical_id=family,
                prompt=prompt,prompt_hash=digest(prompt),candidates=list(names),gold=gold,object=objects[episode['query']],
                answer_to_person={n:i for i,n in enumerate(names)},pair_id=digest([family,surface,control]),
                control=control,data_role=role,source='confirmation-v1/seed-2026092703',structure=episode,
                stratum=dict(task='copy' if control else episode['task'],k_total=len(episode['events']),
                    relevance_group=group,relevant_updates=relevant,irrelevant_events=len(episode['events'])-relevant,
                    surface=surface,variant=variant,query=episode['query'],condition='copy' if control else 'ownership'))
            case['id']=digest(case);yield case


def build_confirmation(history):
    vocabulary={w.lower() for names,objects in SURFACES.values() for w in (*names,*objects)}
    if vocabulary&set(history['words']):raise ValueError('new vocabulary overlaps historical prompts')
    rng=random.Random(2026092703);excluded=set(history['canonical_ids']);seen=set();main=[];rejections=Counter()
    for task in ('swap','handoff'):
        for k in (8,16,32):
            for group in ('all','half'):
                counts=Counter()
                for _ in range(200000):
                    ep,gold=_episode(rng,task,k,k if group=='all' else k//2)
                    canonical=canonical_structure(ep)
                    if canonical in excluded or canonical in seen:
                        rejections['structural']+=1;continue
                    if counts[gold]>=2:
                        rejections['balance']+=1;continue
                    if solve(ep)!=gold:raise ValueError('independent oracle mismatch')
                    counts[gold]+=1;seen.add(canonical)
                    main.extend(_cases(ep,group,'prospective_confirmation'))
                    if sum(counts.values())==8:break
                else:raise ValueError('cannot fill structurally disjoint cell')
    calibration=[]
    for rotation in range(4):
        ep=dict(task='swap',initial=[(o+rotation)%4 for o in range(4)],query=0,events=[])
        for control in (False,True):calibration.extend(_cases(ep,'none','calibration',control))
    # Calibration aliases share structure but require distinct instance ids/pairs.
    for c in calibration:
        c.pop('id');c['scenario_id']=digest(c['structure'])
        c['pair_id']=digest([c['scenario_id'],c['stratum']['surface'],c['control']]);c['id']=digest(c)
    def corpus(cases):
        rng.shuffle(cases)
        c=dict(schema='functional-benchmark-corpus-v1',parser=PARSER_VERSION,sources=history['sources'],
               suites=['confirmation-v1'],cases=cases,limitations=['Disjoint from inventoried development structures, not guaranteed absent from model training.',
                    'Two surface bundles per episode are paired, not independent samples.', 'Calibration structurally overlaps historical data.'])
        c['hash']=digest(c);validate_corpus(c);return c
    if any(c['prompt_hash'] in set(history['prompt_hashes']) for c in main+calibration):raise ValueError('prompt overlap')
    return corpus(main),corpus(calibration),dict(main_classes=len(seen),historical_overlap=len(seen&excluded),
        main_cases=len(main),calibration_cases=len(calibration),rejected=dict(rejections),vocabulary=sorted(vocabulary))

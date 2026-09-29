"""BBH object-at-person bridge. No model labels enter generation or requests."""
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import random
import re
import yaml
from jinja2 import Environment, BaseLoader, StrictUndefined
from .common import digest, file_hash, read_json, write_new

PARSER = 'bbh-generative-v1'
WORDS = {3:'three',5:'five',7:'seven'}
NAMES = ('Alice','Bob','Claire','Dave','Eve','Fred','Gertrude')
VERBS = {'balls':'swap balls', 'gifts':'swap their gifts', 'books':'swap books',
         'partners':'switch partners','positions':'trade positions'}
PROLOGUES = {
    'balls': ('playing a game. At the start of the game, they are each holding a ball', 'As the game progresses, pairs of players trade balls. '),
    'gifts': ('holding a white elephant gift exchange. At the start of the event, they are each holding a present of a different color', 'As the event progresses, pairs of people swap gifts. '),
    'books': ('friends and avid readers who occasionally trade books. At the start of the semester, they each buy one new book', 'As the semester proceeds, they start trading around the new books. '),
    'partners': ('dancers at a square dance. At the start of a song, they each have a partner', 'Throughout the song, the dancers often trade partners. '),
    'positions': ('on the same team in a soccer match. At the start of the match, they are each assigned to a position', 'As the game progresses, pairs of players occasionally swap positions. '),
}

STOPS = ('</s>', 'Q', '\n\n')


def normalized(text):
    return ' '.join(text.split())


def parse_question(text):
    """Strict text replay in person->object direction, independent of generated state."""
    clean=normalized(text)
    body,opts=clean.split(' Options: ')
    options=re.findall(r'\(([A-G])\) (.*?)(?= \([A-G]\) |$)',opts)
    n=len(options)
    if n not in WORDS or [a for a,_ in options]!=list('ABCDEFG'[:n]):
        raise ValueError('invalid options')
    if ' '.join(f'({a}) {v}' for a,v in options)!=opts or len({v for _,v in options})!=n:
        raise ValueError('unrecognized/duplicate options')
    names=NAMES[:n];namepat='(?:'+'|'.join(names)+')'
    before,rest=body.split('First, ',1)
    initial=before.split(': ',1)[1].split('. ',1)[0]
    clauses=initial.replace(', and ', ', ').split(', ')
    if len(clauses)!=n:raise ValueError('invalid initial assignments')
    assignments={}
    for clause in clauses:
        m=re.fullmatch(f'({namepat}) (?:has|gets|is dancing with|is playing) (.+)',clause)
        if not m or m[1] in assignments:raise ValueError('invalid initial assignment')
        assignments[m[1]]=m[2].removeprefix('a ') if ' has a ' in clause else m[2]
    objects=[v for _,v in options]
    if set(assignments)!=set(names) or set(assignments.values())!=set(objects):
        raise ValueError('initial/option mismatch')
    if 'trade balls' in before:context='balls'
    elif 'swap gifts' in before:context='gifts'
    elif 'trade books' in before:context='books'
    elif 'square dance' in before:context='partners'
    elif 'soccer match' in before:context='positions'
    else:raise ValueError('unknown context')
    intro,trailer=PROLOGUES[context]
    people=', '.join(names[:-1])+', and '+names[-1]
    expected=people+' are '+intro+': '+initial+'. '+trailer
    if before!=expected:raise ValueError('unrecognized prologue text')
    event_text,question=('First, '+rest).split(' At the end of ',1)
    pattern=f'(First|Then|Finally), ({namepat}) and ({namepat}) {VERBS[context]}\\.'
    matches=list(re.finditer(pattern,event_text))
    if ' '.join(m[0] for m in matches)!=event_text or len(matches)!=n:
        raise ValueError('unrecognized event text/count')
    if [m[1] for m in matches]!=['First']+['Then']*(n-2)+['Finally']:
        raise ValueError('invalid event ordering')
    q=re.fullmatch(f'(?:the game|the event|the semester|the dance|the match), ({namepat}) (?:has(?: the)?|is dancing with|is playing)',question)
    if not q:raise ValueError('unknown question')
    query=names.index(q[1]);events=[];state=assignments.copy()
    for m in matches:
        a,b=m[2],m[3]
        if a==b:raise ValueError('self swap')
        events.append((names.index(a),names.index(b)))
        state[a],state[b]=state[b],state[a]
    pairs=[tuple(sorted(e)) for e in events]
    if set(sum((list(e) for e in events),[]))!=set(range(n)) or any(a==b for a,b in zip(pairs,pairs[1:])):
        raise ValueError('BBH swap constraints violated')
    return dict(n=n,context=context,query_person=query,events=events,
                initial=[objects.index(assignments[name]) for name in names],
                objects=objects,gold='('+options[objects.index(state[q[1]])][0]+')')


def solve_backward(initial,events,query):
    """Independent inverse path solver; never updates the forward state."""
    for a,b in reversed(events):
        query=b if query==a else a if query==b else query
    return initial[query]


def structure_id(row):
    """Query-person-fixed permutation identity; object names/order are irrelevant."""
    n=row['n'];q=row['query_person'];others=[i for i in range(n) if i!=q]
    canonical=None
    for labels in permutations(range(1,n)):
        rename={q:0,**dict(zip(others,labels))}
        value=tuple(tuple(sorted((rename[a],rename[b]))) for a,b in row['events'])
        if canonical is None or value<canonical:canonical=value
    return digest(dict(version='bbh-person-query-v1',n=n,events=canonical))


def verify_example(example):
    row=parse_question(example['input'])
    backward='('+chr(65+solve_backward(row['initial'],row['events'],row['query_person']))+')'
    if row['gold']!=example['target'] or row['gold']!=backward:
        raise ValueError('independent gold mismatch')
    return dict(row,input=example['input'],target=example['target'],structure_id=structure_id(row))


def load_sources(folder):
    folder=Path(folder);manifest=read_json(folder/'manifest.json')
    for name,entry in manifest['files'].items():
        if file_hash(folder/name)!=entry['sha256']:raise ValueError('source hash mismatch')
    originals=[];demos=[]
    for n,word in WORDS.items():
        task='tracking_shuffled_objects_'+word+'_objects'
        rows=read_json(folder/(task+'.json'))['examples']
        if len(rows)!=250:raise ValueError('original BBH count changed')
        for index,row in enumerate(rows):
            parsed=verify_example(row)
            if parsed['n']!=n:raise ValueError('wrong subtask')
            originals.append(dict(parsed,source_index=index))
        cfg=yaml.safe_load((folder/('fewshot_'+task+'.yaml')).read_text())
        for row in cfg['fewshot_config']['samples']:demos.append(verify_example(row))
    if len(originals)!=750 or len(demos)!=9:raise ValueError('source coverage')
    demos=list({normalized(r['input']):r for r in demos}.values())
    return originals,demos


def generate_cases(originals,demos,seed):
    """Match each original's context, initial surface, query and option order.

    Resample the swap path uniformly conditional on BBH constraints; reject exact
    normalized text overlap. Abstract structures may overlap and are audited.
    """
    rng=random.Random(seed);seen={normalized(r['input']) for r in originals+demos};generated=[]
    for index,original in enumerate(originals):
        n=original['n'];pairs=list(combinations(range(n),2))
        for attempt in range(100000):
            events=[rng.choice(pairs) for _ in range(n)]
            if any(a==b for a,b in zip(events,events[1:])) or set(sum((list(e) for e in events),[]))!=set(range(n)):continue
            events=[e if rng.randrange(2) else e[::-1] for e in events]
            event_text=' '.join(f"{('First' if j==0 else 'Finally' if j==n-1 else 'Then')}, {NAMES[a]} and {NAMES[b]} {VERBS[original['context']]}." for j,(a,b) in enumerate(events))
            text=original['input'];start=text.index('First, ');end=text.index(' At the end of ',start)
            text=text[:start]+event_text+text[end:]
            if normalized(text) in seen:continue
            gold='('+chr(65+solve_backward(original['initial'],events,original['query_person']))+')'
            parsed=verify_example(dict(input=text,target=gold));seen.add(normalized(text))
            generated.append(dict(parsed,source_index=index,generator_seed=seed,template_source_index=original['source_index']))
            break
        else:raise ValueError('text support exhausted; never pad with duplicates')
    return generated


def protocol_config(folder,n,mode):
    prefix='fewshot' if mode=='direct' else 'cot_fewshot' if mode=='cot' else None
    if prefix is None:raise ValueError('unknown protocol')
    folder=Path(folder);task='tracking_shuffled_objects_'+WORDS[n]+'_objects'
    return yaml.safe_load((folder/(prefix+'_'+task+'.yaml')).read_text())


def prompt_for(row,folder,mode):
    cfg=protocol_config(folder,row['n'],mode)
    demos=cfg['fewshot_config']['samples'];template=cfg['doc_to_text']
    # lm-eval fewshot convention: description, rendered examples + target,
    # double-newline delimiters, then final query (single text completion context).
    env=Environment(loader=BaseLoader,undefined=StrictUndefined)
    render=lambda value,doc:env.from_string(value).render(**doc)
    prefix=render(cfg['description'],{'input':row['input']})
    examples=[render(template,s)+' '+s['target'] for s in demos]
    return prefix+'\n\n'.join(examples)+'\n\n'+render(template,{'input':row['input']})


def truncate_stops(text):
    positions=[text.find(s) for s in STOPS if s in text]
    return text[:min(positions)] if positions else text


def extract(text,mode):
    text=truncate_stops(text)
    if mode=='direct':return text
    if mode!='cot':raise ValueError('unknown protocol')
    matches=re.findall(r'(?<=the answer is )(.*)(?=.)',text)
    return matches[0].strip() if matches else '[invalid]'


def score_bbh(case,response):
    status=response['status'];mode=case['bbh_protocol']
    result=dict(status=status,answer=None,person=None,correct=None,strict_correct=None,first_correct=None,first_answer=None)
    if status not in ('stop','length'):return result
    answer=extract(response['text'],mode)
    # If a native stop would have fired before provider length, it is a completed
    # harness answer; preserve raw provider status separately in the receipt.
    stopped=truncate_stops(response['text'])!=response['text']
    complete=status=='stop' or stopped
    result.update(status=('accepted' if answer in case['candidates'] else 'unsupported') if complete else 'truncated',
                  answer=answer,correct=answer==case['gold'],
                  strict_correct=complete and response['text'].strip()==case['gold'])
    return result


def build_corpus(rows,folder,origin):
    cases=[]
    for index,row in enumerate(rows):
        for mode in ('direct','cot'):
            prompt=prompt_for(row,folder,mode);choices=['('+chr(65+i)+')' for i in range(row['n'])]
            case=dict(suite='bbh-bridge-v1',scenario_id=digest(row['input']),family_id=row['structure_id'],
                pair_id=digest([origin,index]),prompt=prompt,prompt_hash=digest(prompt),gold=row['gold'],
                candidates=choices,answer_to_person={a:i for i,a in enumerate(choices)},object=None,
                control=False,data_role='bbh_reference' if origin=='original' else 'fresh_resample',source=origin,
                bbh_protocol=mode,stop_sequences=list(STOPS),question=row['input'],stratum=dict(task='bbh_swap',origin=origin,n_entities=row['n'],
                    k_total=len(row['events']),context=row['context'],variant=mode,source_index=index))
            case['id']=digest(case);cases.append(case)
    corpus=dict(schema='functional-benchmark-corpus-v1',parser=PARSER,cases=cases)
    corpus['hash']=digest(corpus)
    from .corpus import validate_corpus
    validate_corpus(corpus);return corpus


def export_harness(corpus,out):
    """Local JSON tasks preserve complete frozen prompts; no extra demonstrations."""
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    groups=sorted({(c['stratum']['origin'],c['stratum']['n_entities'],c['bbh_protocol']) for c in corpus['cases']})
    for origin,n,mode in groups:
        rows=[dict(prompt=c['prompt'],target=c['gold'],case_id=c['id']) for c in corpus['cases'] if (c['stratum']['origin'],c['stratum']['n_entities'],c['bbh_protocol'])==(origin,n,mode)]
        name=f'{origin}_{n}_{mode}'
        data=out/(name+'.json');write_new(data,rows)
        cfg=dict(task='layercast_bbh_'+name,dataset_path='json',dataset_kwargs={'data_files':{'test':str(data.resolve())}},
            test_split='test',output_type='generate_until',doc_to_text='{{prompt}}',doc_to_target='{{target}}',
            num_fewshot=0,metric_list=[dict(metric='exact_match',aggregation='mean',higher_is_better=True)],
            generation_kwargs=dict(until=list(STOPS),do_sample=False,temperature=0.0,max_gen_toks=1024),metadata={'version':1})
        if mode=='cot':cfg['filter_list']=[dict(name='get-answer',filter=[dict(function='regex',regex_pattern=r'(?<=the answer is )(.*)(?=.)'),dict(function='take_first')])]
        (out/(name+'.yaml')).write_text(yaml.safe_dump(cfg,sort_keys=False))


def distribution_audit(originals,generated,demos):
    out={}
    for n in WORDS:
        a=[r for r in originals if r['n']==n];b=[r for r in generated if r['n']==n]
        known={r['structure_id'] for r in a};few={r['structure_id'] for r in demos if r['n']==n}
        out[str(n)]=dict(original=len(a),generated=len(b),original_structures=len(known),
            generated_structures=len({r['structure_id'] for r in b}),
            generated_with_original_structure=sum(r['structure_id'] in known for r in b),
            generated_with_demo_structure=sum(r['structure_id'] in few for r in b),
            original_contexts=dict(Counter(r['context'] for r in a)),generated_contexts=dict(Counter(r['context'] for r in b)))
    return dict(groups=out,claim='Fresh text/path resampling; not a structurally disjoint holdout. Original lexical/query marginals retained.')

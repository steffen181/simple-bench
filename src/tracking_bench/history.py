"""Fail-closed inventory of historical ownership inputs, including aborted runs."""
from pathlib import Path
import re
import subprocess
from .common import digest,file_hash,read_json
from .corpus import replay,validate_corpus,NEW_GENERATORS
from .structure import canonical_structure,solve


def normalize_episode(row):
    if row['generator_version'] not in NEW_GENERATORS | {'swap-v1','handoff-v1'}:
        raise ValueError('unknown archived generator')
    gold=replay(row)
    modern=row['generator_version'] in NEW_GENERATORS
    task=row.get('task_family','swap')
    if task not in ('swap','handoff','give','assign','direct'):
        raise ValueError('unknown archived task')
    initial=list(row['initial_state']) if modern else [row['initial_state'].index(o) for o in range(4)]
    state=initial.copy();events=[]
    for e in row['events']:
        if not modern:
            a,b=e
            event=dict(kind='give',source=a,target=b,object=row['query']) if task=='handoff' else dict(kind='swap',source=a,target=b)
        else:
            event=dict(e)
            if event['kind']=='assign':
                obj=event['object'];a=state[obj];b=event['target']
                if a==b:continue
                event=dict(kind='give',object=obj,source=a,target=b)
        if event['kind']=='swap':
            a,b=event['source'],event['target']
            state=[b if owner==a else a if owner==b else owner for owner in state]
        elif event['kind']=='give':
            if state[event['object']]!=event['source']:raise ValueError('invalid archived giver')
            state[event['object']]=event['target']
        else:raise ValueError('unknown archived event')
        events.append(event)
    episode=dict(task='handoff' if task in ('handoff','give','assign') else 'swap',initial=initial,query=row['query'],events=events)
    if solve(episode)!=gold:raise ValueError('normalized oracle mismatch')
    return episode


def inventory(repo):
    repo=Path(repo).resolve();verification=repo/'verification'
    def archival_input(path):
        try:parts=path.relative_to(verification).parts
        except ValueError:return False
        return bool(parts) and (parts[-1].endswith('corpus.json') or
            (len(parts)>1 and parts[0].startswith('functional_') and parts[-1] in ('scenarios.json','prompts.json')))
    def require_present(path):
        if archival_input(path) and not path.is_file():raise ValueError(f'missing archive: {path}')
    # Git also catches deletion of an entire historical directory, including its seal.
    if (repo/'.git').exists():
        tracked=subprocess.run(['git','-C',str(repo),'ls-files','-z'],check=True,capture_output=True).stdout
        for name in tracked.decode().split('\0'):
            if name:require_present(repo/name)
    scenario_files=sorted(verification.glob('functional_*/**/scenarios.json'))
    if not scenario_files:raise ValueError('no functional archives')
    prompt_files=sorted(verification.glob('functional_*/**/prompts.json'))
    corpus_files=sorted(verification.glob('**/*corpus.json'))
    manifests={};seal_hashes={};sources={};identities=set();words=set();prompts=set();episodes={};cache={}
    counts=dict(scenario_files=len(scenario_files),prompt_files=len(prompt_files),corpus_files=len(corpus_files),
                scenarios=0,corpus_cases=0,context_free_controls=0,assign_scenarios=0)
    def verified(path):
        actual=file_hash(path)
        for parent in path.parents:
            if parent==repo.parent:break
            for name in ('sha256.json','manifest.json'):
                seal=parent/name
                if not seal.exists():continue
                if seal not in manifests:
                    raw=read_json(seal);manifests[seal]=raw.get('hashes',raw);seal_hashes[seal]=file_hash(seal)
                hashes=manifests[seal]
                for key in (str(path.relative_to(parent)),str(path.relative_to(repo))):
                    if key in hashes:
                        if hashes[key]!=actual:raise ValueError(f'archive hash mismatch: {path}')
                        sources[str(path.relative_to(repo))]=actual
                        sources[str(seal.relative_to(repo))]=seal_hashes[seal]
                        return read_json(path)
        raise ValueError(f'unsealed archive: {path}')
    def add_prompt(prompt):
        prompts.add(digest(prompt));words.update(re.findall(r'\b\w+\b',prompt.lower()))
    def identity(ep):
        key=digest(ep)
        if key not in cache:cache[key]=canonical_structure(ep)
        identities.add(cache[key]);return cache[key]
    for path in scenario_files:
        rows=verified(path)
        if not isinstance(rows,list):raise ValueError('unknown scenario archive')
        for row in rows:
            ep=normalize_episode(row);identity(ep)
            lookup=(str(path.parent.relative_to(repo)),row['scenario_id'])
            if lookup in episodes:raise ValueError('duplicate archived scenario id')
            episodes[lookup]=ep
            counts['scenarios']+=1;counts['assign_scenarios']+=row.get('task_family')=='assign'
            if 'prompt' in row:add_prompt(row['prompt'])
    for path in prompt_files:
        for row in verified(path):add_prompt(row['prompt'])
    for path in corpus_files:
        corpus=verified(path);validate_corpus(corpus)
        for c in corpus['cases']:
            add_prompt(c['prompt']);counts['corpus_cases']+=1
            if 'structure' in c:
                identity(c['structure'])
                if solve(c['structure'])!=c['answer_to_person'][c['gold']]:raise ValueError('API oracle mismatch')
            elif c['stratum'].get('condition')=='copy-context-free' and c['control']:
                counts['context_free_controls']+=1
            else:
                lookup=(c['source'],c['scenario_id'])
                if lookup not in episodes:raise ValueError(f'unmapped archived episode: {lookup}')
                if solve(episodes[lookup])!=c['answer_to_person'][c['gold']]:raise ValueError('API mapped oracle mismatch')
                identity(episodes[lookup])
    # A seal remains authoritative for input completeness even when one listed file vanishes.
    for seal,hashes in manifests.items():
        for key in hashes:
            path=(repo/key if key.startswith('verification/') else seal.parent/key).resolve()
            require_present(path)
    return dict(canonical_ids=sorted(identities),words=sorted(words),prompt_hashes=sorted(prompts),sources=sources,
                counts=counts,coverage='All functional_*/**/scenarios.json and prompts.json plus all existing verification/**/*corpus.json at freeze; versioned and encountered seal-listed inputs must exist; provider training data unknown.')

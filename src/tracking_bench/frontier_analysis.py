"""Replay-derived public counts and paired group bootstrap; no provider secrets."""
from collections import defaultdict,Counter
from pathlib import Path
import random
from .common import read_json,digest,file_hash
from .frontier_campaign import audit_campaign,_protocol
from .campaign_contract import MODELS


def paired_interval(rows,seed=20261020,reps=2000):
    if not rows:return dict(groups=0,difference=None,ci=None)
    strata=defaultdict(list)
    for r in rows:
        weight=r.get('weight',1)
        if type(weight) is not int or weight<=0:raise ValueError('positive integer group size required')
        strata[(r['seed'],r['task'])].append((r['left']-r['right'],weight))
    values=[x for v in strata.values() for x in v]
    mean=lambda xs:sum(value*weight for value,weight in xs)/sum(weight for value,weight in xs)
    average=mean(values)
    if len(values)<2:return dict(groups=len(values),difference=average,ci=None)
    rng=random.Random(seed);samples=[]
    for _ in range(reps):samples.append(mean([rng.choice(v) for v in strata.values() for _ in v]))
    samples.sort();return dict(groups=len(values),difference=average,ci=[samples[int(.025*(reps-1))],samples[int(.975*(reps-1))]])


def make_bbh_reference(sources,seed=20261003,per_n=15,fresh_per_n=0):
    from .reference import verify_sources
    from .bbh import load_sources,build_corpus
    verify_sources(sources)
    if per_n not in (15,30) or fresh_per_n!=0:raise ValueError('this campaign uses a balanced original-only BBH subset')
    originals,_=load_sources(sources);rng=random.Random(seed);selected=[]
    for n in (3,5,7):selected.extend(rng.sample([r for r in originals if r['n']==n],per_n))
    corpus=build_corpus(selected,sources,'original');cases=[]
    for c in corpus['cases']:
        if c['bbh_protocol']!='direct':continue
        c=dict(c);c.pop('id');c.pop('stop_sequences',None)
        c['prompt']='Answer the final question with exactly one parenthesized option, for example (A). Do not explain.\n\n'+c['prompt']
        c['prompt_hash']=digest(c['prompt']);c['canonical_id']=c['family_id'];c['stratum']=dict(c['stratum'],entities=c['stratum']['n_entities'],seed=seed,relevant_updates=None)
        c['id']=digest(c);cases.append(c)
    rng.shuffle(cases);corpus['cases']=cases;corpus.pop('hash');corpus['hash']=digest(corpus)
    from .corpus import validate_corpus
    validate_corpus(corpus);return corpus


def analyze_campaign(campaign):
    root=Path(campaign);audit=audit_campaign(root);p=_protocol(root);records=[];seen=set()
    for folder in sorted((root/'blocks').iterdir()):
        summary=read_json(folder/'summary.json');cases={c['id']:c for c in read_json(folder/'cases.json')}
        for i,item in enumerate(read_json(folder/'schedule.json')):
            receipt=folder/'receipts'/f'{i:06d}.json';r=read_json(receipt) if receipt.exists() else None
            records.append((summary['phase'],cases[item['case_id']],item['model'],r));seen.add((item['case_id'],item['model']))
    if (root/'confirmation-population.json').exists():
        for block in read_json(root/'confirmation-population.json'):
            for c in block['cases']:
                for mid in p['contracts']:
                    if (c['id'],mid) not in seen:records.append(('confirm',c,mid,None))
    cells,comparisons=aggregate_records(records)
    models=list(MODELS)
    phases={name:read_json(root/(name+'.json')) for name in ['gate','smoke','bbh','confirm'] if (root/(name+'.json')).exists()}
    return dict(schema='frontier-public-results-v1',execution_kind=p['config']['mode'],native_acc_norm=None,metric=p['metric'],audit_status=audit['status'],protocol_hash=audit['protocol_hash'],
        budget=dict(limit_usd=4,working_limit_usd=3.75,**audit['budget']),phases=phases,
        models=[dict(id=mid,canonical_slug=c['canonical_slug'],provider=c['provider_name'],quantization=c['quantization']) for mid in models for c in [p['contracts'][mid]]],
        cells=cells,comparisons=comparisons,selection=read_json(root/'selection.json') if (root/'selection.json').exists() else None,
        conditions=dict(analysis_code_sha256=file_hash(Path(__file__)),analysis_method='question-weighted stratified structure-group bootstrap; BBH originals are not option rotations',reasoning='off, explicitly audited',max_tokens=32,temperature='provider default; route does not expose shared temperature',api_seed='not set',ladder_shots=0,bbh_shots=3,cost_bound='UTF8 bytes + 4096 envelope, user-accepted assumption'),
        limitations=['Not native BBH acc_norm; BBH is a small original tracking subset under a shared chat generation protocol.','Smoke selects a range; confirmation uses independent structure groups.','Pointwise 95% group bootstrap intervals, not simultaneous confidence for adaptive boundary search.','Accuracy/all-planned with missing observations is a lower bound; unobserved cells have null accuracy.','Provider-reported identity, precision and reasoning metadata; private weights/tokenizers not independently verified.','Envelope cost bound is a conservative accepted assumption, not certified provider token counting.','Offline fixtures are not model evidence.'] if p['config']['mode']=='offline_fixture' else ['BBH Tracking subset / Chat-3shot / Generation; native acc_norm unavailable.','Confirmation is independent of smoke; intervals are pointwise, not simultaneous.','Missing observations remain visible; private provider weights and precision are not verified.','Cost bound uses a user-accepted conservative envelope assumption.'])


def aggregate_records(records):
    """Aggregate paired replay records without performing I/O or inference."""
    buckets=defaultdict(list)
    for phase,c,mid,r in records:
        s=c['stratum'];n=s['entities'];k=s['k_total'];relevant=s.get('relevant_updates');task=s['task'];seed=s.get('seed',0)
        for t,se in [(task,seed),(task,'all'),('all',seed),('all','all')]:buckets[(phase,mid,n,k,relevant,t,se)].append((c,r))
    cells=[];pair_groups=defaultdict(lambda:defaultdict(list))
    for key,values in buckets.items():
        phase,mid,n,k,relevant,task,seed=key;observed=[r for c,r in values if r is not None];correct=sum(r['score']['correct'] is True for r in observed);technical=sum(r['audit']['technical_ok'] for r in observed)
        group=defaultdict(list)
        for c,r in values:
            if r is not None and r['audit']['technical_ok']:group[c['canonical_id']].append((c,r))
        group_rows=[]
        for identity,entries in group.items():
            expected=sum(c['canonical_id']==identity for c,r in values)
            if len(entries)!=expected:continue
            value=sum(r['score']['correct'] is True for c,r in entries)/len(entries)
            group_rows.append(dict(group=identity,seed=entries[0][0]['stratum'].get('seed',0),task=entries[0][0]['stratum']['task'],left=value,right=0.,weight=len(entries)))
        interval=paired_interval(group_rows)
        cost=sum((float(r['audit']['response']['cost']) for r in observed if r['audit']['response']['cost'] is not None),0.)
        elapsed=sorted(r['elapsed_seconds'] for r in observed)
        cell=dict(phase=phase,model=mid,n=n,k=k,relevant_updates=relevant,task=task,seed=seed,planned=len(values),observed=len(observed),technical_ok=technical,correct=correct,
            accuracy_all_planned=correct/len(values) if observed else None,accuracy_observed=correct/technical if technical else None,
            coverage=len(observed)/len(values),chance=1/n,groups=len({c['canonical_id'] for c,r in values}),ci=interval['ci'],
            cost_usd=cost,prompt_tokens=sum(r['audit']['prompt_tokens'] or 0 for r in observed),completion_tokens=sum(r['audit']['completion_tokens'] or 0 for r in observed),
            latency_median_seconds=elapsed[len(elapsed)//2] if elapsed else None,status_counts=dict(Counter(r['score']['status'] for r in observed)),reasoning_off=bool(observed) and all(r['audit']['reasoning_off'] for r in observed))
        cell['finish_counts']=dict(Counter(r['audit']['response']['finish_reason'] or 'unknown' for r in observed))
        cell['length_terminated']=cell['finish_counts'].get('length',0)
        rotations=[v for v in group.values() if len(v)==2] if phase!='bbh' else []
        cell['rotation_pairs']=len(rotations);cell['rotation_agreement']=sum(v[0][1]['score']['person']==v[1][1]['score']['person'] and v[0][1]['score']['person'] is not None for v in rotations)/len(rotations) if rotations else None
        cells.append(cell)
        for row in group_rows:pair_groups[(phase,n,k,relevant,task,seed)][(row['group'],row['seed'],row['task'])].append((mid,(row['left'],row['weight'])))
    comparisons=[];models=list(MODELS)
    for key,groups in pair_groups.items():
        rows=[]
        for (identity,seed,task),values in groups.items():
            scores=dict(values)
            if set(scores)==set(models):rows.append(dict(group=identity,seed=seed,task=task,left=scores[models[0]][0],right=scores[models[1]][0],weight=scores[models[0]][1]))
        phase,n,k,relevant,task,seed=key
        comparisons.append(dict(phase=phase,n=n,k=k,relevant_updates=relevant,task=task,seed=seed,left=models[0],right=models[1],**paired_interval(rows)))
    return cells,comparisons

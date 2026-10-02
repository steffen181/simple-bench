"""Descriptive structure-group scores; no new inference or model calls."""
from collections import defaultdict
from .campaign_contract import MODELS


def describe(records):
    """Keep rotations together, incomplete groups unknown, and series separate."""
    buckets=defaultdict(list)
    for phase,case,model,receipt in records:
        if phase not in ('develop','confirm'):continue
        s=case['stratum']
        key=(phase,s['task'],s['entities'],s['relevant_updates'],s['irrelevant_events'],model,case['canonical_id'])
        buckets[key].append((s,receipt))
    groups=[];cells=defaultdict(list);paired=defaultdict(lambda:defaultdict(dict))
    for key,entries in sorted(buckets.items()):
        phase,task,n,r,d,model,identity=key
        seeds={s['seed'] for s,_ in entries}
        if len(seeds)!=1 or len({s['variant'] for s,_ in entries})!=len(entries):raise ValueError('inconsistent structure group')
        observations=[]
        for s,receipt in sorted(entries,key=lambda entry:entry[0]['variant']):
            valid=receipt is not None and receipt['audit']['technical_ok']
            observations.append(dict(rotation=s['variant'],correct=receipt['score']['correct'] if valid else None,status=receipt['score']['status'] if receipt else 'not_observed'))
        complete=len(observations)==2 and all(x['correct'] is not None for x in observations)
        correct=sum(x['correct'] is True for x in observations)
        row=dict(phase=phase,task=task,n=n,r=r,d=d,k=r+d,model=model,group_id=identity,seed=next(iter(seeds)),planned=len(entries),observed=sum(receipt is not None for _,receipt in entries),correct=correct,
                 score=correct/2 if complete else None,format_failures=sum(x['status'] in ('invalid_json','truncated') for x in observations),rotations=observations)
        groups.append(row);cells[key[:6]].append(row);paired[key[:5]][identity][model]=row
    summaries=[]
    for key,rows in sorted(cells.items()):
        phase,task,n,r,d,model=key;values=[g['score'] for g in rows if g['score'] is not None];complete=len(values)==len(rows)
        summaries.append(dict(phase=phase,task=task,n=n,r=r,d=d,model=model,group_count=len(rows),complete_groups=len(values),mean=sum(values)/len(values) if values and complete else None,
                              minimum=min(values) if values else None,maximum=max(values) if values else None,distribution={str(i):sum(v==i/2 for v in values) for i in range(3)},format_failures=sum(g['format_failures'] for g in rows)))
    comparisons=[];left,right=list(MODELS)
    for key,identities in sorted(paired.items()):
        phase,task,n,r,d=key;points=[]
        for identity,models in sorted(identities.items()):
            a=models.get(left,{}).get('score');b=models.get(right,{}).get('score')
            points.append(dict(group_id=identity,seed=next(iter(models.values()))['seed'],left=a,right=b,difference=a-b if a is not None and b is not None else None))
        values=[g['difference'] for g in points if g['difference'] is not None]
        comparisons.append(dict(phase=phase,task=task,n=n,r=r,d=d,left=left,right=right,groups=points,difference=sum(values)/len(values) if values and len(values)==len(points) else None,complete_groups=len(values)))
    return dict(schema='descriptive-structure-groups-v1',unit='One structure with two option rotations; no repeated identical API requests.',groups=groups,cells=summaries,pairs=comparisons)

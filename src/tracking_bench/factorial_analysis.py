"""Frozen pilot selection and conservative independent-group confirmation."""
from collections import defaultdict
from math import log,sqrt
from fractions import Fraction
from .campaign_contract import MODELS as ROUTES
from .factorial_campaign import LEVELS,RELEVANT,DISTRACTORS,SELECTION_RULE
MODELS=list(ROUTES)


def cell_key(cell):
    return (cell['task'],cell['n'],cell['r'],cell['d'])


def cell_spec(row):
    return dict(task=row['task'],n=row['n'],r=row['relevant_updates'],d=row['k']-row['relevant_updates'])


def select_contrasts(cells,eligible=None,format_errors_as_wrong=False):
    eligible_keys=None if eligible is None else {cell_key(c) for c in eligible}
    by_cell=defaultdict(dict)
    for c in cells:
        if c['phase']!='develop' or c['task']=='all' or c['seed']!='all':continue
        if c['observed']!=c['planned']:continue
        if (c.get('technical_ok',0) if format_errors_as_wrong else c['status_counts'].get('accepted',0))!=c['planned']:continue
        by_cell[cell_key(cell_spec(c))][c['model']]=c
    by_cell={key:rows for key,rows in by_cell.items() if set(rows)==set(MODELS) and (eligible_keys is None or key in eligible_keys)}
    gaps=[];losses=[]
    accuracy=lambda row: Fraction(row['correct'],row['planned'])
    threshold=Fraction(3,20)
    for key,rows in sorted(by_cell.items()):
        a,b=[accuracy(rows[m]) for m in MODELS];delta=a-b
        if abs(delta)>=threshold:
            gaps.append(dict(kind='model_gap',cell=cell_spec(rows[MODELS[0]]),left=MODELS[0] if delta>0 else MODELS[1],right=MODELS[1] if delta>0 else MODELS[0],development_effect=float(abs(delta)),_effect=abs(delta)))
        for axis,values,index in [('n',LEVELS,1),('r',RELEVANT,2),('d',DISTRACTORS,3)]:
            if key[index] not in values or key[index]==values[-1]:continue
            hard=list(key);hard[index]=values[values.index(key[index])+1];hard=tuple(hard)
            if hard not in by_cell:continue
            for model in MODELS:
                easy_score=accuracy(rows[model]);hard_score=accuracy(by_cell[hard][model])
                if easy_score>=Fraction(3,4) and easy_score-hard_score>=threshold:
                    losses.append(dict(kind='performance_drop',model=model,axis=axis,easy=cell_spec(rows[model]),hard=cell_spec(by_cell[hard][model]),development_effect=float(easy_score-hard_score),_effect=easy_score-hard_score))
    # Lexical keys make ties independent of dictionary/input order.
    gaps.sort(key=lambda x:(-x['_effect'],cell_key(x['cell']),x['left']))
    losses.sort(key=lambda x:(-x['_effect'],cell_key(x['easy']),x['model'],x['axis'],cell_key(x['hard'])))
    selected=losses[:1]+gaps[:1];unique={}
    for contrast in selected:
        contrast.pop('_effect')
        for c in [contrast['cell']] if contrast['kind']=='model_gap' else [contrast['easy'],contrast['hard']]:unique[cell_key(c)]=c
    return dict(rule=SELECTION_RULE,contrasts=selected,cells=[unique[k] for k in sorted(unique)],status='SELECTED' if selected else 'NO_ELIGIBLE_CONTRAST')


def bounded_interval(left,right=None,kind='model_gap'):
    if not left or (kind=='performance_drop' and not right):raise ValueError('empty group sample')
    if kind not in ('model_gap','performance_drop'):raise ValueError('unknown contrast')
    if any(not -1<=x<=1 for x in left) or (right is not None and any(not 0<=x<=1 for x in right)):raise ValueError('unbounded observations')
    mean=sum(left)/len(left)
    # Two fixed planned contrasts, two-sided Bonferroni family alpha=.05.
    logarithm=log(2*SELECTION_RULE['maximum_contrasts']/SELECTION_RULE['family_alpha'])
    if kind=='model_gap':radius=sqrt(2*logarithm/len(left))
    else:
        mean-=sum(right)/len(right)
        # Union of marginal cell bounds: no independence between cells assumed.
        marginal_log=log(4*SELECTION_RULE['maximum_contrasts']/SELECTION_RULE['family_alpha'])
        radius=sqrt(marginal_log/(2*len(left)))+sqrt(marginal_log/(2*len(right)))
    return mean,[max(-1.,mean-radius),min(1.,mean+radius)]


def inference(selection,records,format_errors_as_wrong=False):
    groups=defaultdict(lambda:defaultdict(list));results=[]
    for phase,case,model,receipt in records:
        if phase!='confirm' or receipt is None:continue
        if not (receipt['audit']['technical_ok'] if format_errors_as_wrong else receipt['score']['status']=='accepted'):continue
        s=case['stratum'];key=(s['task'],s['entities'],s['relevant_updates'],s['irrelevant_events'])
        groups[(key,model)][case['canonical_id']].append(float(receipt['score']['correct']))
    means={key:{group:sum(v)/2 for group,v in values.items() if len(v)==2} for key,values in groups.items()}
    for contrast in selection['contrasts']:
        result=dict(contrast=contrast,interval_method='paired-Hoeffding' if contrast['kind']=='model_gap' else 'union-of-marginal-Hoeffding-v2',status='UNKNOWN_INCOMPLETE',effect=None,ci=None,groups=[])
        if contrast['kind']=='model_gap':
            key=cell_key(contrast['cell']);a=means.get((key,contrast['left']),{});b=means.get((key,contrast['right']),{})
            identities=sorted(set(a)&set(b));left=[a[g]-b[g] for g in identities];right=None;counts=[len(left)]
        else:
            left=list(means.get((cell_key(contrast['easy']),contrast['model']),{}).values());right=list(means.get((cell_key(contrast['hard']),contrast['model']),{}).values());counts=[len(left),len(right)]
        result['groups']=counts
        if all(n==SELECTION_RULE['confirmation_groups'] for n in counts):
            point,ci=bounded_interval(left,right,contrast['kind'])
            result.update(effect=point,ci=ci,status='CONFIRMED_PRACTICAL_GAP' if ci[0]>SELECTION_RULE['minimum_effect'] else 'BELOW_PRACTICAL_THRESHOLD' if ci[1]<SELECTION_RULE['minimum_effect'] else 'INCONCLUSIVE')
        results.append(result)
    return results

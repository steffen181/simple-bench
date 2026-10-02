import pytest


def module():
    from tracking_bench import factorial_analysis
    return factorial_analysis


def row(n,r,d,task,model,accuracy,complete=True):
    return dict(phase='develop',n=n,k=r+d,relevant_updates=r,task=task,seed='all',model=model,accuracy_all_planned=accuracy,correct=round(accuracy*6),planned=6,observed=6 if complete else 4,status_counts={'accepted':6 if complete else 4})


def test_selection_freezes_direction_and_only_adjacent_single_axis_losses():
    m=module();a,b=m.MODELS;rows=[]
    for n,r,d,aa,bb in [(3,4,0,1,1),(7,4,0,.3,.8),(16,4,0,.2,.9),(3,8,8,0,0)]:
        rows += [row(n,r,d,'swap',a,aa),row(n,r,d,'swap',b,bb)]
    s=m.select_contrasts(rows)
    gap=next(x for x in s['contrasts'] if x['kind']=='model_gap');loss=next(x for x in s['contrasts'] if x['kind']=='performance_drop')
    assert gap['left']==b and gap['right']==a and gap['cell']['n']==16
    assert loss['axis']=='n' and loss['easy']['n']==3 and loss['hard']['n']==7 and loss['model']==a
    assert len(s['cells'])==3
    assert m.select_contrasts(rows)==s


def test_incomplete_or_bad_baseline_does_not_create_candidate():
    m=module();a,b=m.MODELS
    rows=[row(3,4,0,'swap',a,.5),row(3,4,0,'swap',b,.5),row(7,4,0,'swap',a,0,False),row(7,4,0,'swap',b,1)]
    assert not m.select_contrasts(rows)['contrasts']


def test_constant_samples_have_nonzero_conservative_intervals():
    m=module();point,ci=m.bounded_interval([1]*24,kind='model_gap')
    assert point==1 and 0<ci[0]<1 and ci[1]==1
    point,ci=m.bounded_interval([1]*24,[0]*24,kind='performance_drop')
    assert point==1 and 0<ci[0]<1
    assert m.bounded_interval([.5]*24,kind='model_gap')[1][0]<.15
    with pytest.raises(ValueError):m.bounded_interval([],kind='model_gap')


def test_selection_respects_precomputed_confirmation_support():
    m=module();a,b=m.MODELS;rows=[]
    for n,aa,bb in [(3,0,1),(7,.2,.7)]:rows += [row(n,8,8,'swap',a,aa),row(n,8,8,'swap',b,bb)]
    s=m.select_contrasts(rows,eligible=[dict(task='swap',n=7,r=8,d=8)])
    assert len(s['contrasts'])==1 and s['contrasts'][0]['cell']['n']==7


def test_exact_one_answer_gaps_use_lexical_ties():
    m=module();a,b=m.MODELS
    rows=[row(3,8,8,'swap',a,1),row(3,8,8,'swap',b,5/6),row(7,8,8,'swap',a,5/6),row(7,8,8,'swap',b,4/6)]
    for c in rows:c['correct']=round(c['accuracy_all_planned']*6)
    selected=m.select_contrasts(rows)
    gap=next(c for c in selected['contrasts'] if c['kind']=='model_gap')
    assert gap['cell']['n']==3


def test_loss_ties_follow_frozen_model_then_axis_order():
    m=module();a,b=m.MODELS;rows=[]
    for n,r,aa,bb in [(3,8,1,1),(3,16,.5,1),(7,8,1,.5)]:
        rows += [row(n,r,8,'swap',a,aa),row(n,r,8,'swap',b,bb)]
    selected=m.select_contrasts(rows)
    loss=next(c for c in selected['contrasts'] if c['kind']=='performance_drop')
    assert loss['model']==b and loss['axis']=='n'


def test_drop_interval_allows_shared_randomness_between_cells():
    from math import log,sqrt
    m=module();point,ci=m.bounded_interval([1]*24,[0]*24,kind='performance_drop')
    expected_radius=2*sqrt(log(4*2/.05)/(2*24))
    assert point==1 and ci[0]==pytest.approx(1-expected_radius)
    assert expected_radius==pytest.approx(.650332,abs=1e-6)

import json
import pytest
from test_structured_campaign import Fixture, fixture_inputs
from tracking_bench import factorial_campaign as study, structured_campaign as runner
from tracking_bench.common import read_json, file_hash, write_new


class Invalid(Fixture):
    def complete(self, request):
        raw=super().complete(request); body=json.loads(raw['body'])
        body['choices'][0]['message']['content']='Explanation before {"answer":"Alice"}'
        raw['body']=json.dumps(body);return raw


def stopped(tmp_path):
    catalog,eps=fixture_inputs();root=tmp_path/'development'
    cases=study.population([],levels=[7],relevant=[8],distractors=[8],seeds=[20261211])
    study.freeze_population(root,cases,catalog,eps,[],[],'0.1',{'develop':'0.1'},dict(stage='develop'),mode='offline_fixture')
    assert runner.run(root,transport=Invalid())['observed']==1
    amendment=tmp_path/'format-policy-amendment.json';write_new(amendment,{'policy':'format_errors_as_wrong','authorization':'explicit user approval'})
    return root,amendment


def test_suffix_preserves_prefix_and_counts_format_errors_without_retries(tmp_path):
    from tracking_bench.factorial_continuation import freeze_continuation, merged_development
    root,amendment=stopped(tmp_path);before={str(f):file_hash(f) for f in root.rglob('*') if f.is_file()}
    result=freeze_continuation(root,tmp_path/'continuation',amendment)
    assert result['planned']==7 and result['offset']==1
    p=runner.protocol(tmp_path/'continuation');original=runner.protocol(root)
    assert p['schedule']==original['schedule'][1:]
    f=Invalid();assert runner.run(tmp_path/'continuation',transport=f)['status']=='COMPLETE'
    assert f.calls==7
    a=merged_development(tmp_path)
    assert a['summary']['status']=='COMPLETE' and a['summary']['observed']==8
    assert all(r['score']['correct'] is False for _,_,_,r in a['records'])
    assert float(a['budget']['spent'])==pytest.approx(.00008)
    assert float(a['total_accounted'])==pytest.approx(.00008)
    assert before=={str(f):file_hash(f) for f in root.rglob('*') if f.is_file()}
    with pytest.raises(ValueError):runner.run(tmp_path/'continuation',transport=f)


def test_technical_failure_still_stops_continuation(tmp_path):
    from tracking_bench.factorial_continuation import freeze_continuation
    root,amendment=stopped(tmp_path);out=tmp_path/'continuation'
    freeze_continuation(root,out,amendment)
    f=Fixture(broken=True);result=runner.run(out,transport=f)
    assert result['status']=='STOPPED' and f.calls==1
    assert float(runner.audit(out)['budget']['reserved'])>0


def test_format_failures_are_zero_in_selection_and_confirmation():
    from tracking_bench.factorial_analysis import select_contrasts,inference,MODELS
    from test_factorial_analysis import row
    a,b=MODELS;rows=[row(7,8,8,'swap',a,0),row(7,8,8,'swap',b,1)]
    for c in rows:c['technical_ok']=6
    rows[0]['status_counts']={'invalid_json':6}
    assert not select_contrasts(rows)['contrasts']
    selected=select_contrasts(rows,format_errors_as_wrong=True)
    assert selected['contrasts'][0]['development_effect']==1
    records=[]
    for g in range(24):
        for rotation in range(2):
            case={'canonical_id':str(g),'stratum':dict(task='swap',entities=7,relevant_updates=8,irrelevant_events=8)}
            for m in MODELS:records.append(('confirm',case,m,{'audit':{'technical_ok':True},'score':{'status':'invalid_json' if m==a else 'accepted','correct':m==b}}))
    v=inference(selected,records,format_errors_as_wrong=True)[0]
    assert v['groups']==[24] and v['effect']==1 and v['status']=='CONFIRMED_PRACTICAL_GAP'
    assert inference(selected,records)[0]['status']=='UNKNOWN_INCOMPLETE'


def test_merge_rejects_continuation_of_different_parent(tmp_path):
    from tracking_bench.factorial_continuation import freeze_continuation,merged_development
    one=tmp_path/'one';two=tmp_path/'two';one.mkdir();two.mkdir()
    root1,amendment1=stopped(one);root2,amendment2=stopped(two)
    freeze_continuation(root2,one/'continuation',amendment2)
    runner.run(one/'continuation',transport=Invalid())
    with pytest.raises(ValueError,match='parent'):merged_development(one)


def test_last_technical_failure_does_not_mark_phase_complete(tmp_path):
    from tracking_bench.factorial_continuation import freeze_continuation,merged_development
    root,amendment=stopped(tmp_path);out=tmp_path/'continuation'
    freeze_continuation(root,out,amendment)
    class LastBroken(Fixture):
        def complete(self,request):
            if self.calls==6:self.broken=True
            return super().complete(request)
    runner.run(out,transport=LastBroken());a=merged_development(tmp_path)
    assert a['summary']['observed']==8 and a['summary']['status']=='STOPPED'
    assert a['summary']['phases']['develop']['status']=='STOPPED'

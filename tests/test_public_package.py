import importlib
import json
from copy import deepcopy
import pytest
from tracking_bench.common import digest


def ladder():return importlib.import_module('tracking_bench.ladder')

def test_ladder_deterministic_oracle_relevance_and_rotations():
    m=ladder();a=m.generate(entities=[4],steps=[4,8],per_cell=2,seed=71)
    assert a==m.generate(entities=[4],steps=[4,8],per_cell=2,seed=71)
    assert len(a['cases'])==32
    from tracking_bench.structure import solve,canonical_structure
    for c in a['cases']:
        assert c['gold']==m.NAMES[solve(c['structure'])]
        assert m.replay_text(c['prompt'])==c['gold']
        assert canonical_structure(c['structure'])==c['canonical_id']
        state=list(c['structure']['initial']);updates=0
        for e in c['structure']['events']:
            before=state[c['structure']['query']]
            if e['kind']=='swap':state=[e['target'] if x==e['source'] else e['source'] if x==e['target'] else x for x in state]
            else:state[e['object']]=e['target']
            updates+=before!=state[c['structure']['query']]
        assert updates==c['stratum']['relevant_updates']
    groups={c['canonical_id'] for c in a['cases']};assert len(groups)==16
    b=m.generate(entities=[4],steps=[4,8],per_cell=2,seed=71,blocked=groups)
    assert groups.isdisjoint(c['canonical_id'] for c in b['cases'])


def test_invalid_sizes_and_exhausted_zero_event_support():
    for kwargs in [dict(entities=[2]),dict(entities=[9]),dict(steps=[-1]),dict(per_cell=0),dict(entities=[3],steps=[0],per_cell=2)]:
        with pytest.raises(ValueError):ladder().generate(**kwargs)


def test_native_requests_exclude_gold_and_scores_bound_to_request():
    mod=importlib.import_module('tracking_bench.reference')
    cfg=dict(description='Task.\n\n',fewshot_delimiter='\n\n',fewshot_config=dict(samples=[dict(input='demo',target='(A)')]*3))
    c=dict(id='case',input='question\nOptions:\n(A) red\n(B) blue\n(C) green',target='(B)',n=3)
    req=mod.native_request(c,cfg)
    assert req==mod.native_request(dict(c,target='(C)'),cfg)
    assert req['continuations']==[' (A)',' (B)',' (C)'] and 'target' not in req
    reply=dict(case_id='case',request_hash=digest(req),model='fixture',protocol='native_full_continuation',loglikelihoods=[-3.,-1.,-2.])
    assert mod.score_native(c,req,reply)['correct']
    with pytest.raises(ValueError):mod.score_native(c,req,dict(reply,request_hash='wrong'))
    with pytest.raises(ValueError):mod.score_native(c,req,dict(reply,loglikelihoods=[-1.]))


def test_offline_demo_is_not_llm_evidence_and_run_is_sealed(tmp_path):
    cli=importlib.import_module('tracking_bench.cli')
    assert cli.main(['demo','--out',str(tmp_path/'demo')])==0
    from tracking_bench.run import verify
    result=verify(tmp_path/'demo/run');assert result['observed']==result['planned']
    r=json.loads((tmp_path/'demo/report/report.json').read_text())
    assert r['execution_kind']=='offline_fixture'
    file=tmp_path/'demo/run/corpus.json';file.write_text('{}')
    with pytest.raises(ValueError):verify(tmp_path/'demo/run')


def test_reference_import_checks_packaged_upstream_manifest(tmp_path):
    mod=importlib.import_module('tracking_bench.reference');manifest=mod.resource('bbh-sources.json')
    manifest['files']['tracking_shuffled_objects_three_objects.json']['sha256']='0'*64
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):mod.verify_sources(tmp_path)


def test_contrasts_preserve_complexity_cells():
    from tracking_bench.report import _contrasts
    corpus=ladder().generate(entities=[3,4],steps=[4],per_cell=1,seed=101)
    rows=[(dict(model='fixture',max_tokens=32),c,None) for c in corpus['cases']]
    result=_contrasts(rows)
    assert len(result)==8
    assert {(r['entities'],r['task'],r['relevant_updates']) for r in result}=={(n,t,k) for n in [3,4] for t in ['swap','handoff'] for k in [2,4]}


def test_native_tasks_relocate_without_changing_sealed_files(tmp_path):
    import shutil
    from tracking_bench import reference
    from tracking_bench.common import file_hash,write_new
    import yaml
    root=tmp_path/'original';(root/'tasks').mkdir(parents=True);(root/'data').mkdir()
    write_new(root/'data/reference_3.json',[dict(input='question',target='(A)')])
    (root/'tasks/example.yaml').write_text(yaml.safe_dump(dict(task='example',dataset_kwargs={'data_files':{'test':'data/reference_3.json'}})))
    write_new(root/'sha256.json',{str(p.relative_to(root)):file_hash(p) for p in root.rglob('*') if p.is_file()})
    dest=tmp_path/'moved';shutil.move(root,dest)
    tasks=reference.native_tasks(dest)
    assert tasks[0]['dataset_kwargs']['data_files']['test']==str(dest/'data/reference_3.json')
    reference.verify_bundle(dest)

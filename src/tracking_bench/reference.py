"""Pinned BBH import/export and full-continuation result contract; no proxy relabeling."""
from importlib.resources import files
from pathlib import Path
import hashlib
import json
import urllib.request
import yaml
from .common import read_json,write_new,digest,file_hash
from . import bbh,bbh_fresh
from .bbh_mc import score
from .bbh_protocol_pilot import raw_prompt


def resource(name):return json.loads(files('tracking_bench').joinpath('data',name).read_text())


def fetch(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);manifest=resource('bbh-sources.json')
    for name,item in manifest['files'].items():
        with urllib.request.urlopen(item['url'],timeout=60) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('upstream hash changed: '+name)
        with (out/name).open('xb') as stream:stream.write(data)
    write_new(out/'manifest.json',manifest)
    return dict(files=len(manifest['files']),status='DOWNLOADED_AND_HASH_VERIFIED')


def verify_sources(folder):
    """Bind caller-supplied inputs to the packaged, pinned upstream sources."""
    folder=Path(folder);expected=resource('bbh-sources.json')
    if read_json(folder/'manifest.json')!=expected:raise ValueError('BBH manifest differs from pinned upstream manifest')
    for name,item in expected['files'].items():
        if file_hash(folder/name)!=item['sha256']:raise ValueError('BBH source changed: '+name)
    return expected


def verify_bundle(bundle):
    bundle=Path(bundle).resolve();manifest=read_json(bundle/'sha256.json')
    actual={str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file() and p!=bundle/'sha256.json'}
    if set(manifest)!=actual:raise ValueError('native bundle file set changed')
    for name,expected in manifest.items():
        path=(bundle/name).resolve()
        if bundle not in path.parents or file_hash(path)!=expected:raise ValueError('native bundle changed')
    return bundle


def native_tasks(bundle):
    """Return verified harness configs with paths rebound to this bundle location."""
    bundle=verify_bundle(bundle);tasks=[]
    for path in sorted((bundle/'tasks').glob('*.yaml')):
        cfg=yaml.safe_load(path.read_text());data=cfg['dataset_kwargs']['data_files']
        for split,relative in data.items():
            target=(bundle/relative).resolve()
            if bundle not in target.parents or not target.is_file():raise ValueError('invalid native dataset path')
            data[split]=str(target)
        tasks.append(cfg)
    return tasks


def native_request(case,config):
    return dict(case_id=case['id'],protocol='native_full_continuation',context=raw_prompt(case,config),continuations=[' ('+v+')' for v in 'ABCDEFG'[:case['n']]],normalization='choice_character_length',normalization_lengths=[3]*case['n'])


def score_native(case,request,response):
    if response.get('case_id')!=case['id'] or request.get('case_id')!=case['id'] or response.get('request_hash')!=digest(request):raise ValueError('request binding mismatch')
    if response.get('protocol')!='native_full_continuation' or not isinstance(response.get('model'),str) or not response['model']:raise ValueError('missing native protocol/model identity')
    expected=[' ('+v+')' for v in 'ABCDEFG'[:case['n']]]
    if request.get('continuations')!=expected or request.get('normalization_lengths')!=[3]*case['n'] or request.get('normalization')!='choice_character_length':raise ValueError('native candidate contract differs')
    return score([x[1:] for x in expected],response['loglikelihoods'],case['target'])


def export(sources,out,seeds=(20261001,20261002,20261003),per_cell=8,blocked=()):
    verify_sources(sources)
    originals,demos=bbh.load_sources(sources)
    contracts=resource('native-contracts.json');historical=resource('historical-bbh-structures.json')
    used=set(historical['groups'])|set(blocked)|{r['structure_id'] for r in originals+demos}
    rows=[]
    for original in originals:
        c=dict(original,origin='reference');c['id']=digest(c);rows.append(c)
    generated=bbh_fresh.make_phase(originals,used,list(seeds),per_cell,'public-generator')
    rows += [c for c in generated if c['origin']!='control']
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);(out/'tasks').mkdir();(out/'data').mkdir()
    write_new(out/'cases.json',rows)
    requests=[native_request(c,contracts[str(c['n'])]) for c in rows];write_new(out/'requests.json',requests)
    tasks=[]
    for origin in ['reference','generated','anchor']:
        for n in (3,5,7):
            selected=[dict(input=c['input'],target=c['target']) for c in rows if c['origin']==origin and c['n']==n]
            if not selected:continue
            name=f'tracking_bench_{origin}_{n}';path=out/'data'/f'{origin}_{n}.json';write_new(path,selected)
            cfg=dict(contracts[str(n)],task=name,dataset_path='json',dataset_name=None,dataset_kwargs={'data_files':{'test':str(path.relative_to(out))}})
            (out/'tasks'/f'{name}.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True));tasks.append(name)
    write_new(out/'protocol.json',dict(schema='tracking-bench-native-export-v1',metric='native_acc_norm',harness_commit=resource('bbh-sources.json')['harness_commit'],
        originals=750,new_groups=len({c['group'] for c in rows if c['origin']=='generated'}),seeds=list(seeds),per_cell=per_cell,blocked=sorted(used),tasks=tasks,
        limitations=['N3 has no fresh structural support in archived history.','Full continuation backend required; token top-k is a distinct proxy.','Raw3shot, model revision, precision and task coverage remain comparison conditions.','Two option orders and matched anchors share a group.']))
    write_new(out/'sha256.json',{str(p.relative_to(out)):file_hash(p) for p in sorted(out.rglob('*')) if p.is_file()})
    return dict(directory=str(out),cases=len(rows),tasks=tasks)


def import_scores(bundle,responses,out):
    bundle=verify_bundle(bundle)
    cases=read_json(bundle/'cases.json');requests=read_json(bundle/'requests.json');raw=read_json(responses)
    contracts=resource('native-contracts.json')
    if requests!=[native_request(c,contracts[str(c['n'])]) for c in cases]:raise ValueError('native prompt contract differs')
    if len(raw)!=len(cases) or len({r['case_id'] for r in raw})!=len(raw):raise ValueError('missing or duplicate native responses')
    lookup={r['case_id']:r for r in raw}
    if set(lookup)!={c['id'] for c in cases} or len({r.get('model') for r in raw})!=1:raise ValueError('case/model identity mismatch')
    rows=[dict(case_id=c['id'],origin=c['origin'],n=c['n'],**score_native(c,q,lookup[c['id']])) for c,q in zip(cases,requests)]
    groups=[]
    for origin,n in sorted({(r['origin'],r['n']) for r in rows}):
        chosen=[r for r in rows if r['origin']==origin and r['n']==n];correct=sum(r['correct'] for r in chosen)
        groups.append(dict(origin=origin,n=n,total=len(chosen),correct=correct,acc_norm=correct/len(chosen)))
    result=dict(metric='native_acc_norm',model=raw[0]['model'],groups=groups,rows=rows,requests_sha256=file_hash(bundle/'requests.json'),responses_sha256=file_hash(responses),
        evidence='Caller-supplied full-continuation scores, not independently recomputed model logits; provider/precision provenance must accompany the submission.')
    write_new(out,result);return dict(model=result['model'],groups=groups)

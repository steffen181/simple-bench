"""Native HF BBH multiple-choice exports and explicit external reference profiles.

No chat generation, model loading, downloads, or inference in this module.
"""
import copy
import csv
import hashlib
import math
from pathlib import Path
import re
import yaml
from .bbh import verify_example
from .common import file_hash, read_json, write_new

WORDS={3:'three',5:'five',7:'seven'}
REFERENCE_DATE='2025-02-13T18-27-04.338360'

def task_name(n):return 'leaderboard_bbh_tracking_shuffled_objects_'+WORDS[n]+'_objects'

def score(choices,loglikelihoods,gold):
    """Independent audit of native Harness acc_norm; never fill missing scores."""
    if not choices or len(set(choices))!=len(choices) or any(not isinstance(c,str) or not c for c in choices):
        raise ValueError('invalid choices')
    if gold not in choices or len(loglikelihoods)!=len(choices):raise ValueError('missing candidate/gold')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v>0 for v in loglikelihoods):
        raise ValueError('invalid or missing candidate loglikelihood')
    normalized=[v/len(c) for c,v in zip(choices,loglikelihoods)]
    winner=max(range(len(choices)),key=normalized.__getitem__)
    return dict(prediction=choices[winner],correct=choices[winner]==gold,normalized_loglikelihoods=normalized)

def profile(result):
    config=result['config'];revision=config['model_sha'];template=result.get('chat_template')
    if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('unpinned model revision')
    if config['limit'] is not None:raise ValueError('partial published reference')
    if template is not None and hashlib.sha256(template.encode()).hexdigest()!=result['chat_template_sha']:
        raise ValueError('chat template hash mismatch')
    scores={};tasks={}
    for n in WORDS:
        name=task_name(n);cfg=copy.deepcopy(result['configs'][name])
        if cfg['output_type']!='multiple_choice' or cfg['num_fewshot']!=3 or len(cfg['fewshot_config']['samples'])!=3:
            raise ValueError('not the native three-shot MC contract')
        if cfg['doc_to_choice']!=[f'({x})' for x in 'ABCDEFG'[:n]] or cfg['metric_list']!=[dict(metric='acc_norm',aggregation='mean',higher_is_better=True)]:
            raise ValueError('changed choices or metric')
        if result['n-samples'][name]['effective']!=250:raise ValueError('incomplete reference')
        value=result['results'][name]['acc_norm,none']
        if not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=1:raise ValueError('invalid reference score')
        scores[n]=value;tasks[n]=cfg
    return dict(model=result['model_name'],model_revision=revision,dtype=config['model_dtype'].removeprefix('torch.'),
        published_harness_revision=result['git_hash'],apply_chat_template=template is not None,
        fewshot_as_multiturn=result['fewshot_as_multiturn'],chat_template=template,chat_template_sha=result.get('chat_template_sha'),
        bos_token=result['tokenizer_bos_token'][0],eos_token=result['tokenizer_eos_token'][0],
        system_instruction=result.get('system_instruction'),scores=scores,tasks=tasks)

def comparison(profiles):
    return [dict(model=p['model'],n=n,published_acc_norm=p['scores'][n],replication_acc_norm=None,generated_acc_norm=None,
                 status='NOT_RUN',model_revision=p['model_revision'],chat_template=p['apply_chat_template']) for p in profiles for n in WORDS]

def checked_sources(sources):
    manifest=read_json(sources/'manifest.json')
    for name,expected in manifest['files'].items():
        if file_hash(sources/name)!=expected:raise ValueError('source hash mismatch: '+name)
    return manifest

def prepare(sources,base,out):
    sources,base,out=map(Path,(sources,base,out))
    provenance=checked_sources(sources)
    seal=read_json(base/'data_seal.json')
    for name in ('originals.json','generated.json'):
        if file_hash(base/name)!=seal[name]:raise ValueError('historical data hash mismatch')
    originals=read_json(base/'originals.json');generated=read_json(base/'generated.json')
    profiles=[profile(read_json(sources/f'{size}_results_{REFERENCE_DATE}.json')) for size in ('8B','70B')]
    # A shared task is valid only when both archived task contracts agree.
    for n in WORDS:
        a,b=[{k:v for k,v in p['tasks'][n].items() if k!='group'} for p in profiles]
        if a!=b:raise ValueError('model references have different task contracts')
        hf=read_json(sources/f'hf_{WORDS[n]}.json')
        old=[dict(input=r['input'],target=r['target']) for r in originals if r['n']==n]
        if hf!=old or len(hf)!=250:raise ValueError('HF originals differ in text/order/gold')
    for origin,rows in [('original',originals),('generated',generated)]:
        for n in WORDS:
            subset=[r for r in rows if r['n']==n]
            if len(subset)!=250:raise ValueError('incomplete '+origin)
            for row in subset:verify_example(row)
    out.mkdir(parents=True,exist_ok=False);(out/'data').mkdir();(out/'tasks').mkdir()
    tasknames=[]
    for origin,rows in [('original',originals),('generated',generated)]:
        for n in WORDS:
            name=f'layercast_bbh_mc_{origin}_{n}';tasknames.append(name)
            data=out/'data'/f'{origin}_{n}.json'
            write_new(data,[dict(input=r['input'],target=r['target']) for r in rows if r['n']==n])
            cfg=copy.deepcopy(profiles[0]['tasks'][n]);cfg.pop('group',None)
            cfg.update(task=name,dataset_path='json',dataset_name=None,dataset_kwargs={'data_files':{'test':str(data.resolve())}})
            (out/'tasks'/(name+'.yaml')).write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True))
    write_new(out/'profiles.json',profiles)
    with (out/'comparison.csv').open('x',newline='') as f:
        rows=comparison(profiles);writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write_new(out/'manifest.json',dict(schema='bbh-mc-bundle-v1',inference_status='NOT_RUN',original_questions_verified=750,
        generated_questions_verified=750,candidate_evaluations_per_model=7500,task_names=tasknames,
        harness_commit=provenance['harness_commit'],harness_archive_sha256=provenance['harness_archive_sha256'],source_manifest_sha256=file_hash(sources/'manifest.json'),
        historical_questions={k:seal[k] for k in ('originals.json','generated.json')},
        generated_role='Previously queried questions, corrected measurement protocol; not an untouched holdout',
        metric='Native Harness acc_norm, character-length-normalized full continuation loglikelihood'))
    write_new(out/'seal.json',{str(p.relative_to(out)):file_hash(p) for p in sorted(out.rglob('*')) if p.is_file()})
    return read_json(out/'manifest.json')

def verify_bundle(out):
    out=Path(out)
    entries=read_json(out/'seal.json')
    files={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p!=out/'seal.json'}
    if files!=set(entries):raise ValueError('bundle file set contains missing or unsealed files')
    for name,value in entries.items():
        if file_hash(out/name)!=value:raise ValueError('bundle hash mismatch: '+name)
    return read_json(out/'manifest.json')


def audit_samples(documents,choices,samples,expected_request_hashes,reported_accuracy):
    """Recompute a complete native run from per-candidate likelihoods and freeze."""
    from .common import digest
    if len(samples)!=len(documents) or len(expected_request_hashes)!=len(documents):raise ValueError('incomplete samples')
    seen=set();correct=0
    for row in samples:
        index=row['doc_id']
        if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<len(documents) or index in seen:
            raise ValueError('duplicate or invalid document id')
        seen.add(index)
        if row['doc']!=documents[index]:raise ValueError('sample document changed')
        if [digest(a) for a in row['arguments']]!=expected_request_hashes[index]:raise ValueError('request differs from freeze')
        responses=row['filtered_resps']
        if len(responses)!=len(choices) or any(not isinstance(v,(list,tuple)) or len(v)!=2 for v in responses):raise ValueError('missing candidate response')
        value=score(choices,[v[0] for v in responses],documents[index]['target'])['correct']
        if row['acc_norm']!=float(value):raise ValueError('native metric differs from candidate scores')
        correct+=value
    accuracy=correct/len(documents)
    if not isinstance(reported_accuracy,(float,int)) or not math.isfinite(reported_accuracy) or abs(accuracy-reported_accuracy)>1e-12:
        raise ValueError('aggregate metric mismatch')
    return accuracy


def task_configs(bundle):
    """Bind data to this verified bundle, even when copied to another GPU host."""
    bundle=Path(bundle).resolve();manifest=verify_bundle(bundle);configs=[]
    for name in manifest['task_names']:
        cfg=yaml.safe_load((bundle/'tasks'/(name+'.yaml')).read_text())
        if cfg['task']!=name:raise ValueError('task identity differs from manifest')
        origin,n=name.rsplit('_',2)[-2:]
        if origin not in ('original','generated') or int(n) not in WORDS:raise ValueError('unknown task')
        cfg['dataset_kwargs']={'data_files':{'test':str(bundle/'data'/f'{origin}_{n}.json')}}
        configs.append(cfg)
    return configs

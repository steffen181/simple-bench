"""Portable commands. Generation/demo are offline; catalog/fetch/run are explicit."""
import argparse
import json
from pathlib import Path
from .common import read_json,write_new,digest
from .corpus import validate_corpus
from .ladder import generate
from .openrouter import OpenRouter
from .run import prepare,run,verify
from .report import analyze,export_report
from . import reference


def _blocked(path):
    if path is None:return []
    value=read_json(path)
    if isinstance(value,list):return value
    if 'cases' in value:
        validate_corpus(value);return sorted({c['canonical_id'] for c in value['cases']})
    return value['groups']


def demo(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    corpus=generate(entities=[4],steps=[4],per_cell=1,seed=73)
    model=dict(id='fixture/always-alice',context_length=4096,supported_parameters=['temperature','max_tokens'],pricing=dict(prompt='0',completion='0',request='0'))
    config=dict(mode='offline_fixture',models=[dict(id=model['id'],parameters={'temperature':0})],max_tokens=[32],budget_ledger=str(out/'budget.json'),total_budget_usd='1')
    prepare(corpus,config,{'data':[model]},out/'run')
    class Fixture:
        def complete(self,request):
            return dict(http_status=200,body=json.dumps(dict(id='offline-fixture',model=model['id'],provider='offline-fixture',choices=[dict(finish_reason='stop',message={'content':'Alice'})],usage=dict(cost=0,prompt_tokens=100,completion_tokens=1))))
    result=run(out/'run',Fixture());export_report(analyze(out/'run'),out/'report')
    return dict(status=result['status'],kind='offline_fixture_NOT_model_evidence',planned=result['planned'],report=str(out/'report/REPORT.md'))


def main(argv=None):
    import sys
    argv=sys.argv[1:] if argv is None else argv
    if argv and argv[0]=='reasoning':
        from .reasoning_campaign import main as reasoning_main
        return reasoning_main(argv[1:])
    if argv and argv[0]=='swap-curves':
        from .swap_curves import main as swap_main
        return swap_main(argv[1:])
    if argv and argv[0]=='factorial':
        from .factorial_cli import main as factorial_main
        return factorial_main(argv[1:])
    if argv and argv[0]=='structured':
        from .structured_campaign import main as structured_main
        return structured_main(argv[1:])
    if argv and argv[0] in ('campaign','dashboard'):
        from .frontier_cli import main as frontier_main
        return frontier_main(argv)
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('generate');p.add_argument('--version',choices=['v1','v2'],default='v1');p.add_argument('--relevant-updates',type=int);p.add_argument('--tasks',nargs='+',choices=['swap','handoff'],default=['swap','handoff']);p.add_argument('--entities',type=int,nargs='+',default=[4]);p.add_argument('--steps',type=int,nargs='+',default=[4,8,16,32]);p.add_argument('--per-cell',type=int,default=4);p.add_argument('--seed',type=int,default=20260929);p.add_argument('--blocked',type=Path);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('demo');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('catalog');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('prepare')
    for name in ['corpus','config','catalog','out']:p.add_argument('--'+name,type=Path,required=True)
    for name in ['run','verify','report']:
        p=sub.add_parser(name);p.add_argument('directory',type=Path)
        if name=='report':p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('fetch-bbh');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('export-bbh');p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seeds',nargs='+',type=int,default=[20261001,20261002,20261003]);p.add_argument('--per-cell',type=int,default=8);p.add_argument('--blocked',type=Path)
    p=sub.add_parser('score-native')
    for name in ['bundle','responses','out']:p.add_argument('--'+name,type=Path,required=True)
    p=sub.add_parser('score-token');p.add_argument('--responses',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=parser.parse_args(argv)
    try:
        if a.command=='generate':
            if a.version=='v2':
                from .ladder_v2 import generate as generate_v2
                corpus=generate_v2(a.entities,a.steps,a.relevant_updates,a.tasks,a.per_cell,a.seed,_blocked(a.blocked))
            else:
                if a.relevant_updates is not None or a.tasks!=['swap','handoff']:raise ValueError('custom relevance/tasks require v2')
                corpus=generate(a.entities,a.steps,a.per_cell,a.seed,_blocked(a.blocked))
            write_new(a.out,corpus);result=dict(cases=len(corpus['cases']),groups=len({c['canonical_id'] for c in corpus['cases']}),sha256=corpus['hash'])
        elif a.command=='demo':result=demo(a.out)
        elif a.command=='catalog':
            catalog=OpenRouter().catalog();write_new(a.out,catalog);result=dict(models=len(catalog['data']))
        elif a.command=='prepare':result=prepare(read_json(a.corpus),read_json(a.config),read_json(a.catalog),a.out)
        elif a.command=='run':result=run(a.directory)
        elif a.command=='verify':result=verify(a.directory)
        elif a.command=='report':
            export_report(analyze(a.directory),a.out);result=dict(report=str(a.out/'REPORT.md'))
        elif a.command=='fetch-bbh':result=reference.fetch(a.out)
        elif a.command=='export-bbh':result=reference.export(a.sources,a.out,a.seeds,a.per_cell,_blocked(a.blocked))
        elif a.command=='score-native':result=reference.import_scores(a.bundle,a.responses,a.out)
        else:
            from .bbh_likelihood import decision
            records=read_json(a.responses);rows=[]
            for r in records:
                if type(r.get('n')) is not int or r['n'] not in (3,5,7):raise ValueError('BBH token proxy requires n3/5/7')
                rows.append(dict(case_id=r['case_id'],**decision(r['raw'],list('ABCDEFG'[:r['n']]))))
            result=dict(metric='first_token_proxy_NOT_native_acc_norm',rows=rows);write_new(a.out,result)
    except (ValueError,KeyError,OSError) as exc:
        parser.exit(2,f'Benchmark failed: {type(exc).__name__}: {exc}\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 2 if a.command=='run' and result['status']!='COMPLETE' else 0

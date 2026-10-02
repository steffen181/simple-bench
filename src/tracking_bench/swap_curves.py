"""One fresh, balanced swap grid under a separately authorized four-dollar budget."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import json,random
from .common import read_json,file_hash,digest
from . import factorial_campaign as factory,structured_campaign as runner
from .factorial_descriptive import describe
from .frontier_analysis import aggregate_records
from .campaign_contract import MODELS
from .ladder_v2 import generate

LEVELS=[4,8,16,32]
RELEVANT=[4,8,16]
DISTRACTORS=[0,8,16]
SEEDS=[20270111,20270112,20270113]
GROUPS_PER_SEED=3
CAP='3.75'
SCOPES={'gate':'.03','bbh':'.20','confirm':'3.52'}


def population(blocked):
    return factory.population(blocked,levels=LEVELS,relevant=RELEVANT,distractors=DISTRACTORS,seeds=SEEDS,groups_per_seed=GROUPS_PER_SEED,tasks=['swap'])


def balanced(cases):
    """Each round covers every cell once before adding another group anywhere."""
    by_cell=defaultdict(lambda:defaultdict(list))
    for c in cases:
        s=c['stratum'];by_cell[(s['seed'],s['entities'],s['relevant_updates'],s['irrelevant_events'])][c['canonical_id']].append(c)
    rng=random.Random(20270110);result=[]
    for seed in SEEDS:
        cells=sorted(k for k in by_cell if k[0]==seed)
        for repetition in range(GROUPS_PER_SEED):
            order=cells.copy();rng.shuffle(order)
            for key in order:
                groups=sorted(by_cell[key]);result+=sorted(by_cell[key][groups[repetition]],key=lambda c:c['stratum']['variant'])
    return result


def freeze(out,catalog,endpoints,blocked,bbh_cases,history_spent,source_files=None,mode='live'):
    if mode=='live' and len(bbh_cases)!=45:raise ValueError('45 BBH references required')
    cases=population(blocked)
    gate=generate([4],[0],0,['swap'],1,20270110,[])['cases']
    design=dict(stage='confirm',kind='swap-curves',levels=LEVELS,relevant=RELEVANT,distractors=DISTRACTORS,seeds=SEEDS,groups_per_seed=GROUPS_PER_SEED,
                budget_authorization='New 4 USD allowance explicitly requested 2026-10-01; previous spend is historical and not charged to this allowance.',historical_spent=history_spent,
                sampling='Nine fresh structure groups per cell; three per seed; two option rotations; balanced full-grid rounds; no pilot/selection.')
    return factory.freeze_population(out,[(c,'gate') for c in gate]+[(c,'bbh') for c in bbh_cases]+[(c,'confirm') for c in balanced(cases)],catalog,endpoints,[],blocked,CAP,SCOPES,design,source_files,mode,format_errors_as_wrong=True)


def audit(root):
    root=Path(root);p=runner.protocol(root);a=runner.audit(root);d=p['design']
    if d['kind']!='swap-curves' or d['levels']!=LEVELS or d['relevant']!=RELEVANT or d['distractors']!=DISTRACTORS or d['seeds']!=SEEDS or d['groups_per_seed']!=GROUPS_PER_SEED:raise ValueError('grid differs')
    if p['cap']!=CAP or p['scope_caps']!=SCOPES or p['priors'] or p['prior_spent']!='0' or p.get('format_errors_as_wrong') is not True:raise ValueError('budget/policy differs')
    main=[c for c in p['cases'] if c['phase']=='confirm'];counts=Counter();groups=defaultdict(set)
    for c in main:
        s=c['stratum']
        if s['task']!='swap' or s['k_total']!=s['relevant_updates']+s['irrelevant_events']:raise ValueError('wrong task/events')
        key=(s['entities'],s['relevant_updates'],s['irrelevant_events'],s['seed']);counts[key]+=1;groups[key].add(c['canonical_id'])
    expected={(n,r,d,seed) for n in LEVELS for r in RELEVANT for d in DISTRACTORS for seed in SEEDS}
    if set(counts)!=expected or set(counts.values())!={6} or any(len(g)!=3 for g in groups.values()):raise ValueError('unbalanced population')
    if [c['base_case'] for c in main]!=balanced([c['base_case'] for c in main]):raise ValueError('round schedule differs')
    if len([c for c in p['cases'] if c['phase']=='gate'])!=2:raise ValueError('control population differs')
    if p['mode']=='live' and len([c for c in p['cases'] if c['phase']=='bbh'])!=45:raise ValueError('BBH population differs')
    return a


def analyze(root):
    root=Path(root);a=audit(root);p=runner.protocol(root);cells,comparisons=aggregate_records(a['records'])
    for c in cells:
        c['d']=None if c['relevant_updates'] is None else c['k']-c['relevant_updates'];c['ci']=None;c['format_failures']=sum(c['status_counts'].get(x,0) for x in ['invalid_json','truncated'])
    for c in comparisons:c['d']=None if c['relevant_updates'] is None else c['k']-c['relevant_updates'];c['ci']=None
    return dict(schema='swap-curves-results-v1',audit_status=a['status'],execution_kind=p['mode'],metric='strict_JSON_generation_NOT_native_acc_norm',native_acc_norm=None,study_hash=file_hash(root/'protocol.json'),axes=dict(n=LEVELS,r=RELEVANT,d=DISTRACTORS),
        presentation=dict(kind='swap-curves',series_name='Frische Swap-Messreihe',groups_per_cell=9,budget_scope='Neue Messreihe',historical_spent=p['design']['historical_spent']),
        conditions=dict(max_tokens=256,reasoning='off, explicit zero usage audited',generator_shots=0,bbh_shots=3,format='strict JSON answer enum',format_errors_as_wrong=True,precision='provider unknown',api_seed=None),
        models=[dict(id=m,canonical_slug=c['canonical_slug'],provider=c['provider_name']) for m,c in p['contracts'].items()],
        budget=dict(total_accounted=a['total_accounted'],study_spent=a['budget']['spent'],prior_spent='0',reserved=a['budget']['reserved'],limit='4',reserve='.25'),audits={'measurement':{k:v for k,v in a.items() if k!='records'}},
        cells=cells,comparisons=comparisons,descriptive=describe(a['records']),selection=None,inference=[],unsupported=[],
        limitations=['Eine vollständige, vorab fixierte Swap-Messreihe: alle 36 N/R/D-Zellen mit neun frischen Gruppen, drei je Generator-Seed und zwei Antwortanordnungen. Kein Pilot und keine Auswahl auffälliger Zellen.',
        'Gruppen und Spannweiten beschreiben Fallunterschiede; keine Konfidenzintervalle und keine Messung wiederholter identischer API-Anfragen. Strukturelle Eindeutigkeit ist keine Garantie statistischer Unabhängigkeit.',
        'Jede Kurve verändert genau eine Achse bei festgehaltenen anderen Achsen. Linien verbinden nur gemessene Punkte; keine behauptete stetige oder monotone Leistung.',
        'N verändert auch Promptlänge und Zufallsniveau 1/N; K=R+D. Sehr kurze Aufgaben haben begrenzte strukturelle Vielfalt. Frische gilt relativ zu den eingefrorenen bisherigen Fällen.',
        'BBH: dieselben 45 Originalfragen als separate Chat-3shot/JSON-Referenz. Keine native acc_norm und kein BBH-Gesamtscore; Generatorfälle sind 0-shot.',
        'Formatfehler zählen als falsch. Fehlende oder technisch nicht auswertbare Antworten bleiben unbekannt. Reasoning aus; Sampling-Anbieterdefaults und interne Präzision unbekannt.',
        'Separat genehmigte 4 USD für diese Messreihe, davon .25 Reserve. Frühere Kosten werden nicht auf dieses neue Budget angerechnet. Konservative UTF8-/4096-Hülltoken-Schätzung, keine zertifizierte Tokenzählung.'])


def main(argv=None):
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    for command in ['freeze','run','audit','export']:
        p=sub.add_parser(command);p.add_argument('directory',type=Path)
        if command=='freeze':p.add_argument('--history',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True)
        if command=='run':p.add_argument('--key-file',type=Path,required=True)
        if command=='export':p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv);root=args.directory
    if args.command=='freeze':
        from .factorial_cli import analyze as history_analysis
        history=args.history.resolve();prior=history_analysis(history)
        if any(a['summary']['status']!='COMPLETE' for a in prior['audits'].values()) or prior['budget']['reserved']!='0':raise ValueError('history incomplete/unsettled')
        old=runner.protocol(history/'development');blocked=set(old['blocked']);sources={}
        for stage in ['development','continuation','confirmation']:
            folder=history/stage
            if not (folder/'sha256.json').exists():continue
            for c in runner.protocol(folder)['cases']:blocked.update(x for x in [c.get('canonical_id'),c.get('legacy_canonical_id')] if x)
            sources[str(folder/'sha256.json')]=file_hash(folder/'sha256.json')
        for name in ['study.json','selection.json','confirmation-bank.json','format-policy-amendment.json']:sources[str(history/name)]=file_hash(history/name)
        catalog=read_json(args.metadata/'catalog.json');endpoints={m:read_json(args.metadata/(m.split('/')[0]+'.json')) for m in MODELS}
        for path in [args.metadata/'catalog.json']+[args.metadata/(m.split('/')[0]+'.json') for m in MODELS]:sources[str(path.resolve())]=file_hash(path)
        result=freeze(root,catalog,endpoints,blocked,[c['base_case'] for c in old['cases'] if c['phase']=='bbh'],prior['budget']['total_accounted'],sources)
    elif args.command=='run':result=runner.run(root,args.key_file)
    elif args.command=='audit':result={k:v for k,v in audit(root).items() if k!='records'}
    else:
        from .factorial_dashboard import export
        result=export(analyze(root),args.out)
    print(json.dumps(result,indent=2,ensure_ascii=False));return 2 if result.get('status')=='STOPPED' else 0

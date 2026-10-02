"""CLI orchestration for a precomputed, unopened factorial confirmation bank."""
import argparse
import json
from pathlib import Path
import urllib.request
from . import factorial_campaign as study
from . import structured_campaign as runner
from .factorial_analysis import select_contrasts,cell_key,cell_spec,inference
from .factorial_descriptive import describe
from .frontier_analysis import aggregate_records
from .common import read_json,write_new,file_hash,digest
from .budget import money
from .campaign_contract import MODELS
from .ladder_v2 import generate
from .factorial_continuation import merged_development,ledger,freeze_continuation


def dimensions():
    return [dict(task=task,n=n,r=r,d=d) for n in study.LEVELS for r in study.RELEVANT for d in study.DISTRACTORS for task in ['swap','handoff']]


def verify_study(root):
    root=Path(root);p=read_json(root/'study.json')
    if file_hash(root/'study.json')!=read_json(root/'study-freeze.json')['sha256']:raise ValueError('study design changed')
    if file_hash(root/'confirmation-bank.json')!=p['bank_hash']:raise ValueError('confirmation bank changed')
    if p['selection_rule']!=study.SELECTION_RULE:raise ValueError('selection rule changed')
    return p


def freeze(root,prior):
    root=Path(root);prior=Path(prior).resolve();verified=runner.audit(prior);previous=runner.protocol(prior)
    if verified['summary']['status']!='COMPLETE':raise ValueError('previous study incomplete')
    priors=previous['priors']+[dict(path=str(prior/'budget.json'),hash=file_hash(prior/'budget.json'),spent=verified['budget']['spent'])]
    study.validate_priors(priors,str(money(study.DEV_CAP)+money(study.CONFIRM_CAP)))
    blocked=set(previous['blocked'])
    for c in previous['cases']:blocked.update(x for x in [c.get('canonical_id'),c.get('legacy_canonical_id')] if x)
    cases=study.population(blocked);used=set(blocked)
    for c in cases:used.update(x for x in [c['canonical_id'],c.get('legacy_canonical_id')] if x)
    bank,unsupported=study.confirmation_population({'cells':dimensions()},used)
    unavailable={cell_key(x['cell']) for x in unsupported};eligible=[c for c in dimensions() if cell_key(c) not in unavailable]
    root.mkdir(parents=True,exist_ok=False);write_new(root/'confirmation-bank.json',bank)
    design=dict(schema='factorial-design-v1',levels=study.LEVELS,relevant=study.RELEVANT,distractors=study.DISTRACTORS,seeds=study.SEEDS,confirmation_seeds=study.CONFIRM_SEEDS,selection_rule=study.SELECTION_RULE,eligible=eligible,unsupported=unsupported,bank_hash=file_hash(root/'confirmation-bank.json'),priors=priors,prior_spent=study.validate_priors(priors,study.DEV_CAP),development_cap=study.DEV_CAP,confirmation_cap=study.CONFIRM_CAP)
    write_new(root/'study.json',design);write_new(root/'study-freeze.json',{'sha256':file_hash(root/'study.json')})
    sources={str(prior/'protocol.json'):file_hash(prior/'protocol.json'),str(prior/'sha256.json'):file_hash(prior/'sha256.json'),str((root/'study.json').resolve()):file_hash(root/'study.json'),str((root/'confirmation-bank.json').resolve()):file_hash(root/'confirmation-bank.json')}
    def get(url):
        with urllib.request.urlopen(url,timeout=30) as response:return json.load(response)
    catalog=get('https://openrouter.ai/api/v1/models');endpoints={m:get('https://openrouter.ai/api/v1/models/'+m+'/endpoints') for m in MODELS}
    gate=[(c,'gate') for c in generate([3],[0],0,['swap'],1,20261210,[])['cases']]
    bbh=[(c['base_case'],'bbh') for c in previous['cases'] if c['phase']=='bbh']
    population=gate+bbh+[(c,'develop') for c in study.shuffled(cases,20261210)]
    result=study.freeze_population(root/'development',population,catalog,endpoints,priors,blocked,study.DEV_CAP,study.SCOPES,dict(stage='develop',production=True,study_hash=file_hash(root/'study.json')),sources)
    return dict(**result,confirmation_eligible_cells=len(eligible),unsupported_cells=len(unsupported))


def stage_audit(root,stage):
    root=Path(root);design=verify_study(root);p=runner.protocol(root/stage)
    study.validate_priors(p['priors'],p['cap']);a=merged_development(root) if stage=='development' else runner.audit(root/stage)
    expected_stage='develop' if stage=='development' else 'confirm'
    if p['design']['stage']!=expected_stage or p['design']['study_hash']!=file_hash(root/'study.json'):raise ValueError('stage binding differs')
    if stage=='development':
        counts={};groups=set()
        for c in p['cases']:
            if c['phase']!='develop':continue
            key=cell_key(cell_spec(dict(n=c['stratum']['entities'],k=c['stratum']['k_total'],relevant_updates=c['stratum']['relevant_updates'],task=c['stratum']['task'])))
            counts.setdefault(key,[]).append(c)
            if c['canonical_id'] in groups and not any(x['id']!=c['id'] and x['canonical_id']==c['canonical_id'] for x in counts[key]):raise ValueError('duplicate group')
            groups.add(c['canonical_id'])
        if set(counts)!={cell_key(c) for c in dimensions()}:raise ValueError('factor grid differs')
        for cs in counts.values():
            if len(cs)!=6 or len({c['canonical_id'] for c in cs})!=3 or sorted(c['stratum']['seed'] for c in cs)!=sorted(study.SEEDS*2):raise ValueError('development sampling differs')
        if len(p['schedule'])!=958:raise ValueError('development planned population differs')
    else:
        selected=read_json(root/'selection.json');dev=stage_audit(root,'development');cells,_=aggregate_records(dev['records'])
        if bool(p.get('format_errors_as_wrong'))!=bool(dev.get('format_errors_as_wrong')):raise ValueError('confirmation format policy differs')
        expected=select_contrasts(cells,design['eligible'],format_errors_as_wrong=(root/'format-policy-amendment.json').exists())
        if selected!=expected or p['design']['selection_hash']!=file_hash(root/'selection.json'):raise ValueError('selection replay differs')
        bank=read_json(root/'confirmation-bank.json');wanted={cell_key(c) for c in selected['cells']}
        chosen=[c for c in bank if (c['stratum']['task'],c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) in wanted]
        if {c['base_case']['id'] for c in p['cases']}!={c['id'] for c in chosen} or len(p['cases'])!=len(chosen):raise ValueError('confirmation bank selection differs')
        dev_groups={c['canonical_id'] for c in runner.protocol(root/'development')['cases']}
        if dev_groups & {c['canonical_id'] for c in p['cases']}:raise ValueError('development/confirmation overlap')
    return a


def select(root):
    root=Path(root);design=verify_study(root);a=stage_audit(root,'development')
    if a['summary']['status']!='COMPLETE':raise ValueError('selection requires complete development')
    cells,_=aggregate_records(a['records']);selection=select_contrasts(cells,design['eligible'],format_errors_as_wrong=(root/'format-policy-amendment.json').exists());write_new(root/'selection.json',selection)
    return selection


def freeze_confirmation(root):
    root=Path(root);design=verify_study(root);selected=read_json(root/'selection.json');a=stage_audit(root,'development');cells,_=aggregate_records(a['records'])
    if a['summary']['status']!='COMPLETE' or selected!=select_contrasts(cells,design['eligible'],format_errors_as_wrong=(root/'format-policy-amendment.json').exists()):raise ValueError('unverified selection')
    if not selected['cells']:return dict(status='NO_ELIGIBLE_CONTRAST')
    p=runner.protocol(root/'development');priors=p['priors']+[ledger(root/'development')]
    if (root/'continuation/sha256.json').exists():priors.append(ledger(root/'continuation'))
    cap=str(min(money(study.CONFIRM_CAP),money('3.75')-money(a['total_accounted'])))
    bank=read_json(root/'confirmation-bank.json');keys={cell_key(c) for c in selected['cells']}
    chosen=[c for c in bank if (c['stratum']['task'],c['stratum']['entities'],c['stratum']['relevant_updates'],c['stratum']['irrelevant_events']) in keys]
    blocked=set(p['blocked'])
    for c in p['cases']:blocked.update(x for x in [c['canonical_id'],c.get('legacy_canonical_id')] if x)
    sources=dict(p['source_files'])
    amendment=root/'inference-amendment.json'
    if not amendment.exists():write_new(amendment,dict(schema='prospective-inference-amendment-v1',reason='Shared seeds do not establish independence between cells.',performance_drop='Sum of marginal Hoeffding radii sqrt(log(4*M/alpha)/(2*n)); union bound allows arbitrary between-cell dependence.',within_cell_assumption='Independent group sampling within each cell remains an assumption.',family_alpha=.05,maximum_contrasts=2,threshold=.15,confirmation_responses_observed=0))
    sources[str(amendment.resolve())]=file_hash(amendment)
    sources[str((root/'selection.json').resolve())]=file_hash(root/'selection.json');sources[str((root/'development/sha256.json').resolve())]=file_hash(root/'development/sha256.json')
    format_amendment=root/'format-policy-amendment.json'
    if format_amendment.exists():
        sources[str(format_amendment.resolve())]=file_hash(format_amendment)
        sources[str((root/'continuation/sha256.json').resolve())]=file_hash(root/'continuation/sha256.json')
    catalog={'data':[c['info'] for c in p['contracts'].values()]};endpoints={m:{'data':{'endpoints':[c['endpoint']]}} for m,c in p['contracts'].items()}
    return study.freeze_population(root/'confirmation',study.shuffled(chosen,20261220),catalog,endpoints,priors,blocked,cap,{'confirm':cap},dict(stage='confirm',production=True,study_hash=file_hash(root/'study.json'),selection_hash=file_hash(root/'selection.json')),sources,format_errors_as_wrong=format_amendment.exists())


def analyze(root):
    root=Path(root);design=verify_study(root);dev=stage_audit(root,'development');records=list(dev['records']);audits={'development':{k:v for k,v in dev.items() if k!='records'}};total=dev['total_accounted'];spent=money(dev['budget']['spent']);reserved=money(dev['budget']['reserved']);selected=read_json(root/'selection.json') if (root/'selection.json').exists() else None;verdicts=[]
    if (root/'confirmation/sha256.json').exists():
        confirm=stage_audit(root,'confirmation');records+=confirm['records'];audits['confirmation']={k:v for k,v in confirm.items() if k!='records'};total=confirm['total_accounted'];spent+=money(confirm['budget']['spent']);reserved+=money(confirm['budget']['reserved']);verdicts=inference(selected,confirm['records'],format_errors_as_wrong=(root/'format-policy-amendment.json').exists())
        if confirm['summary']['status']!='COMPLETE':
            for v in verdicts:v.update(status='UNKNOWN_INCOMPLETE',effect=None,ci=None)
    elif selected:verdicts=inference(selected,[])
    cells,comparisons=aggregate_records(records)
    # Pilot has just three groups; suppress unreliable tiny-stratum bootstrap intervals.
    for c in cells:c['d']=None if c['relevant_updates'] is None else c['k']-c['relevant_updates'];c['ci']=None
    for c in cells:c['format_failures']=sum(c['status_counts'].get(x,0) for x in ['invalid_json','truncated'])
    for c in comparisons:c['d']=None if c['relevant_updates'] is None else c['k']-c['relevant_updates'];c['ci']=None
    p=runner.protocol(root/'development')
    return dict(schema='factorial-results-v1',audit_status='PASS',execution_kind=p['mode'],metric='strict_JSON_generation_NOT_native_acc_norm',native_acc_norm=None,study_hash=file_hash(root/'study.json'),axes=dict(n=study.LEVELS,r=study.RELEVANT,d=study.DISTRACTORS),conditions=dict(max_tokens=256,reasoning='off, explicit usage audited',generator_shots=0,bbh_shots=3,format='strict JSON answer enum',format_errors_as_wrong=(root/'format-policy-amendment.json').exists(),precision='provider unknown',sampling='provider defaults',api_seed=None),models=[dict(id=m,canonical_slug=c['canonical_slug'],provider=c['provider_name']) for m,c in p['contracts'].items()],budget=dict(total_accounted=total,study_spent=str(spent),prior_spent=design['prior_spent'],reserved=str(reserved),limit='4',reserve='.25'),audits=audits,cells=cells,comparisons=comparisons,descriptive=describe(records),selection=selected,inference=verdicts,unsupported=design['unsupported'],limitations=[('Format- und Abbruchfehler zählen nach ausdrücklicher Nutzerfreigabe als falsch, auch bei Auswahl und Bestätigung. Score misst Aufgabenleistung einschließlich Formattreue; Fehlerzahlen separat ausgewiesen. Keine Wiederholung oder nachträgliche Extraktion ungültiger Antworten.' if (root/'format-policy-amendment.json').exists() else 'Ursprüngliches Protokoll: Formatfehler zählen als falsch und stoppen die Messung; Auswahl verlangt vollständig akzeptierte Zellen.'),'Entwicklung: drei verschiedene Strukturgruppen je Aufgabe/Zelle; explorativ, keine verlässlichen Zellintervalle.','Bestätigung: 24 neue Gruppen je ausgewählter Zelle; zwei Rotationen zählen als eine Gruppe. Auswahl und Richtung vor Bestätigungsantworten fixiert.','Konservative Hoeffding-Intervalle unter der Annahme unabhängiger Gruppen innerhalb jeder Zelle; diese Annahme ist durch eindeutige IDs nicht bewiesen. Zellunterschiede nutzen vereinigte marginale Intervalle ohne Annahme unabhängiger Zellen; Bonferroni für zwei Kontraste (Familienfehler .05).','Bestätigter praktisch relevanter Unterschied nur bei unterer Intervallgrenze >15 Prozentpunkten. Unklar bedeutet weder Gleichwertigkeit noch kein Effekt.','N verändert auch Promptlänge und Zufallsniveau 1/N; keine isolierte Gedächtnisgrenze. K=R+D; D-Ereignisse ändern den Besitzer des Zielobjekts nicht.','BBH: dieselben 45 Originalfragen, Chat-3shot-JSON-Generation. Keine native acc_norm, kein vollständiger BBH-Score. Generator 0-shot separat.','Strukturelle Frische gilt relativ zu den eingefrorenen Ausschlüssen; unbekannte Trainingsdaten und interne Anbieterpräzision bleiben unbeobachtet.','Kostenannahme: freigegebene UTF8-Bytes plus 4096 Hülltokens, kein zertifizierter Tokenizer-Bound. Fehlende Beobachtungen bleiben unbekannt.'])


def main(argv=None):
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    for name in ['freeze','freeze-continuation','run','select','freeze-confirmation','audit','export']:
        command=sub.add_parser(name);command.add_argument('directory',type=Path)
        if name=='freeze':command.add_argument('--prior',type=Path,required=True)
        if name=='run':command.add_argument('--stage',choices=['development','continuation','confirmation'],required=True);command.add_argument('--key-file',type=Path,required=True)
        if name=='export':command.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv);root=args.directory
    if args.command=='freeze':result=freeze(root,args.prior)
    elif args.command=='freeze-continuation':
        verify_study(root);amendment=root/'format-policy-amendment.json'
        if not amendment.exists():
            write_new(amendment,dict(schema='format-policy-amendment-v1',policy='format_errors_as_wrong',authorization='ja trotzdem fortsetzen und als falsch ausweisen.',original_seal=file_hash(root/'development/sha256.json'),original_observed=runner.audit(root/'development')['summary']['observed'],selection='Complete technically valid observations remain eligible; strict format or length failures count zero.',confirmation='Same primary scoring; separate format failure counts; no salvage or retries.',unchanged='Frozen cases, order, requests, budgets, model routes, selection thresholds/ties, confirmation bank and intervals.'))
        result=freeze_continuation(root/'development',root/'continuation',amendment)
    elif args.command=='run':verify_study(root);result=runner.run(root/args.stage,args.key_file)
    elif args.command=='select':result=select(root)
    elif args.command=='freeze-confirmation':result=freeze_confirmation(root)
    elif args.command=='audit':
        report=analyze(root);result={k:report[k] for k in ['audit_status','budget','audits','inference']}
    else:
        from .factorial_dashboard import export
        result=export(analyze(root),args.out)
    print(json.dumps(result,indent=2,ensure_ascii=False));return 2 if result.get('status')=='STOPPED' else 0


if __name__=='__main__':raise SystemExit(main())

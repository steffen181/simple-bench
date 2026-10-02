"""Self-contained N/R/D comparison export with no provider payloads."""
from pathlib import Path
from importlib.resources import files
import csv,io,json
from .common import write_new,file_hash
FIELDS={'schema','audit_status','execution_kind','metric','native_acc_norm','study_hash','axes','conditions','models','budget','audits','cells','comparisons','selection','inference','unsupported','limitations','descriptive','presentation'}


def export(data,out):
    forbidden={'raw','body','api_key','authorization','key_file','attempt','request_id'}
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k.lower() not in forbidden}
        if isinstance(value,list):return [clean(v) for v in value]
        return value
    single=data.get('presentation',{}).get('kind')=='swap-curves'
    public=clean({k:v for k,v in data.items() if k in FIELDS});out=Path(out);out.mkdir(parents=True,exist_ok=False)
    for c in public['cells']:c['display_accuracy']=c['accuracy_all_planned'] if c['observed']==c['planned'] and c.get('technical_ok',0)==c['planned'] else None
    write_new(out/'results.json',public)
    blob=json.dumps(public,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    (out/'index.html').write_text(files('tracking_bench').joinpath('templates/factorial.html').read_text().replace('__RESULTS_JSON__',blob).replace('__CURVE_SCRIPT__',files('tracking_bench').joinpath('templates/swap_curves.html').read_text() if public.get('presentation',{}).get('kind')=='swap-curves' else ''))
    columns=['phase','task','model','seed','n','k','relevant_updates','d','groups','correct','observed','planned','accuracy_all_planned','coverage','rotation_agreement','format_failures','cost_usd']
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(public['cells']);(out/'results.csv').write_text(stream.getvalue())
    group_columns=['phase','task','n','r','d','k','model','group_id','seed','correct','observed','planned','score','format_failures']
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=group_columns,extrasaction='ignore');writer.writeheader();writer.writerows(public.get('descriptive',{}).get('groups',[]));(out/'groups.csv').write_text(stream.getvalue())
    report=['# Luna / Sonnet: N/R/D-Vergleich','', '[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv)', '', 'N = Personen/Objekte; R = Besitzwechsel des Zielobjekts; D = andere Ereignisse; K = R+D. Beispiel N=7/R=8/D=16: sieben Personen, acht relevante Wechsel und 16 andere Ereignisse, insgesamt K=24. N ist keine Stichprobengroesse, R kein internes Reasoning.','',f"Audit: {public.get('audit_status','unknown')}. Kosten: {public.get('budget',{}).get('study_spent','unknown')} USD neu; {public.get('budget',{}).get('total_accounted','unknown')} USD kumuliert / 4 USD.",'',('Formatfehler und abgeschnittene Antworten zählen als falsch; die Messung läuft nach freigegebener Änderung weiter.' if public.get('conditions',{}).get('format_errors_as_wrong') else 'Ursprüngliches Protokoll: Formatfehler zählen als falsch und stoppen die Messung.')+' Fehler werden separat ausgewiesen. Der Score umfasst Aufgabenleistung und Formattreue.', '', '## Beobachtete Ergebnisse','', 'Breites Raster (Pilot) und zusätzliche frische Fälle bleiben getrennt. Jede Strukturgruppe enthält zwei Antwortanordnungen. Die Gruppenwerte 0 %, 50 % und 100 % bedeuten null, eine oder zwei richtige Antworten. Ihre Spannweite beschreibt Unterschiede zwischen Fällen und Anordnungen, keine Unsicherheit eines Mittelwerts und keine Wiederholungsstreuung identischer API-Anfragen. [Alle Gruppenwerte](groups.csv).', '', '| Messreihe | Aufgabe | Modell | N / R / D | Vollständige Gruppen | Mittelwert | Gruppen-Minimum | Gruppen-Maximum |','|---|---|---|---|---:|---:|---:|---:|']
    if public.get('execution_kind')!='live':report[2:2]=['OFFLINE-TESTDATEN: simulierte Antworten, keine Modellmessungen.' if public.get('execution_kind')=='offline_fixture' else 'Messherkunft nicht ausgewiesen.', '']
    percent=lambda value: '—' if value is None else f'{100*value:.1f} %'
    for c in public.get('descriptive',{}).get('cells',[]):
        report.append(f"| {'Pilot' if c['phase']=='develop' else 'Zusätzliche frische Fälle'} | {c['task']} | {c['model']} | {c['n']} / {c['r']} / {c['d']} | {c['complete_groups']}/{c['group_count']} | {percent(c['mean'])} | {percent(c['minimum'])} | {percent(c['maximum'])} |")
    report+=['','## Methodenanhang: ursprüngliche formale Prüfung','', 'Die folgende formale Prüfung bleibt zur Nachvollziehbarkeit erhalten. Ihr Urteil bewertet ein vorher festgelegtes Absicherungskriterium; die gemessenen Werte und ihre Streuung werden oben unabhängig davon beschrieben.','']
    for result in public.get('inference',[]):report.append('- '+json.dumps(result,ensure_ascii=False))
    if not public.get('inference'):report.append('Keine gemessene Bestaetigung; siehe Auswahl und Phasenstatus im JSON.')
    report+=['','## Zellen (Aufgaben und Phasen getrennt)','', '| Phase | Aufgabe | Modell | N | R | D | K | Korrekt / geplant | Beobachtet | Formatfehler |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in public['cells']:
        if c['seed']=='all' and c['task']!='all':report.append(f"| {c['phase']} | {c['task']} | {c['model']} | {c['n']} | {c['relevant_updates']} | {c['d']} | {c['k']} | {c.get('correct',0)}/{c['planned']} | {c['observed']} | {c.get('format_failures',0)} |")
    report+=['','## Grenzen','',*['- '+x for x in public.get('limitations',[])]]
    if single:
        report=[line.replace('Breites Raster (Pilot) und zusätzliche frische Fälle bleiben getrennt.', 'Eine vollständige frische Swap-Messreihe ohne Pilot oder Zellenauswahl.').replace('Zusätzliche frische Fälle', 'Frische Messreihe').replace('N=7/R=8/D=16: sieben Personen', 'N=8/R=8/D=16: acht Personen').replace('USD kumuliert / 4 USD.', 'USD im neu genehmigten Budget / 4 USD.') for line in report if not line.startswith(('## Methodenanhang: ursprüngliche', 'Die folgende formale Prüfung', 'Keine gemessene Bestaetigung'))]
    (out/'REPORT.md').write_text('\n'.join(report)+'\n')
    (out/'SHA256SUMS').write_text(''.join(f'{file_hash(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
    return dict(status='EXPORTED',directory=str(out))

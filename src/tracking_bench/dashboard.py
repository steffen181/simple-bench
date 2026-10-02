"""Self-contained, sanitized comparison dashboard; never calls a model."""
from pathlib import Path
from importlib.resources import files
import csv
import io
import json
from .common import write_new,file_hash
ROOT_FIELDS={'schema','execution_kind','native_acc_norm','metric','audit_status','protocol_hash','budget','phases','models','cells','comparisons','selection','conditions','limitations'}


NKR_EXPLANATION = '## Was bedeuten N, K und R?\n\n| Kuerzel | Bedeutung | Was wird gezaehlt? |\n|---|---|---|\n| **N** | Anzahl der Personen (Entitaeten) | In diesen Aufgaben gibt es auch N unterschiedliche Objekte und N moegliche Personen als Antwort. N ist nicht die Anzahl der Testfaelle. |\n| **K** | Gesamtzahl der Ereignisse pro Aufgabe | Jeder Tausch (`swap`) bzw. jede Uebergabe (`handoff`) zaehlt als ein Ereignis. Anfangszuordnung, Frage und Prompt-Beispiele zaehlen nicht mit. |\n| **R** | Relevante Besitzwechsel pro Aufgabe | Anzahl der K Ereignisse, bei denen das am Ende abgefragte Objekt den Besitzer wechselt. Die anderen K-R Ereignisse aendern dessen Besitzer nicht. |\n\n**Beispiel `N/K/R = 5/32/16`:** 5 Personen und 5 Objekte, 32 Ereignisse; bei 16 davon wechselt das abgefragte Objekt den Besitzer, bei den anderen 16 nicht. Dieselbe Person kann mehrfach beteiligt sein: R kann groesser als N sein, aber es gilt `0 <= R <= K`. R ist keine Zahl interner Reasoning-Schritte. K ist kein Tokenbudget.\n\nIm Dashboard zeigt die Achse **N/K** Personen/Ereignisse; die Tabelle **N/K/R** ergaenzt die relevanten Besitzwechsel. Die Filter heissen **K: Ereignisse** und **R: relevante Besitzwechsel**. In CSV/JSON entsprechen die Werte `n`, `k` und `relevant_updates`. Bei der BBH-Referenz wurde R nicht separat erfasst: **`—` bzw. `null` bedeutet nicht ausgewiesen, nicht null Besitzwechsel**.\n'


def export(results,out):
    public={k:results[k] for k in ROOT_FIELDS if k in results}
    # The analysis output is already an allowlisted aggregate. Reject accidental raw run objects.
    forbidden={'request_id','attempt_id','raw','body','api_key','authorization','key_file','budget_ledger','secret'}
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k.lower() not in forbidden}
        if isinstance(value,list):return [clean(v) for v in value]
        return value
    public=clean(public);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    write_new(out/'results.json',public)
    blob=json.dumps(public,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    template=files('tracking_bench').joinpath('templates','dashboard.html').read_text()
    (out/'index.html').write_text(template.replace('__RESULTS_JSON__',blob),encoding='utf-8')
    columns=['phase','model','n','k','relevant_updates','task','seed','groups','planned','observed','correct','accuracy_all_planned','accuracy_observed','coverage','cost_usd','prompt_tokens','completion_tokens','rotation_agreement','length_terminated','reasoning_off']
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(public['cells']);(out/'results.csv').write_text(stream.getvalue())
    write_new(out/'protocol.json',{k:public[k] for k in ['models','conditions','metric','native_acc_norm','protocol_hash','limitations']})
    report=['# Luna / Sonnet: Kampagnenvergleich','',f"Ausführung: **{public['execution_kind']}**. Audit: **{public['audit_status']}**.",f"Kosten: **{float(public['budget']['spent']):.6f} USD** / 4 USD; offene Reservierungen: {public['budget']['reserved']} USD.",'','[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv) · [Protokoll](protocol.json)','',NKR_EXPLANATION,'','| Phase | Modell | N | Ereignisse | Gruppen | Korrekt / geplant | Abdeckung |','|---|---|---:|---:|---:|---:|---:|']
    for c in public['cells']:
        if c['task']=='all' and c['seed']=='all':report.append(f"| {c['phase']} | {c['model']} | {c['n']} | {c['k']} | {c['groups']} | {c['correct']} / {c['planned']} | {c['coverage']:.0%} |")
    report.extend(['','## Grenzen','',*['- '+x for x in public['limitations']],'','Keine native BBH-acc_norm: Originalfragen-Teilstichprobe unter Chat-Dreishot-Generation. Smoke und Bestätigung bleiben getrennt.'])
    (out/'REPORT.md').write_text('\n'.join(report)+'\n')
    hashes={p.name:file_hash(p) for p in sorted(out.iterdir()) if p.is_file()}
    (out/'SHA256SUMS').write_text(''.join(f'{h}  {name}\n' for name,h in hashes.items()))
    return dict(directory=str(out),files=len(hashes),status='EXPORTED')

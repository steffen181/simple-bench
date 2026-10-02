"""Export replayed results with explicit format diagnostics and reproduction commands."""
import argparse
from collections import Counter
from pathlib import Path
from tracking_bench.frontier_analysis import analyze_campaign
from tracking_bench.dashboard import export
from tracking_bench.common import file_hash


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--campaign',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=analyze_campaign(args.campaign)
    aggregate=[c for c in result['cells'] if c['task']=='all' and c['seed']=='all']
    diagnostics=[]
    for model in result['models']:
        for phase in result['phases']:
            cells=[c for c in aggregate if c['model']==model['id'] and c['phase']==phase]
            statuses=Counter()
            for cell in cells:statuses.update(cell['status_counts'])
            observed=sum(c['observed'] for c in cells)
            length_terminated=sum(c['length_terminated'] for c in cells)
            diagnostics.append((phase,model['id'],observed,statuses,length_terminated))
            if observed and statuses['accepted']<observed:
                result['limitations'].append(f"{phase} / {model['id']}: {statuses['accepted']}/{observed} Antworten im verlangten Format; Formatfehler sind Teil des gemessenen Generationsprotokolls.")
            if length_terminated:
                result['limitations'].append(f"{phase} / {model['id']}: {length_terminated}/{observed} Ausgaben am Tokenlimit beendet. Das feste 32-Token-Ausgabelimit und Antwortformat begrenzen die Aussage zur Aufgabenloesung.")
    result['limitations'].append('Deaktiviertes API-Reasoning schliesst sichtbare Erklaerungen im Antworttext nicht aus. Eine abgeschnittene Erklaerung belegt keine reine Faehigkeitsgrenze.')
    result['conditions']['delivery_exporter_sha256']=file_hash(Path(__file__))
    result['limitations'].append('Kleine Stichprobe: nur zwei Gruppen je Seed/Aufgabe. Empirische Bootstrap-Intervalle koennen bei ausschliesslich falschen/richtigen Antworten auf 0/1 degenerieren; das beweist keine exakte Populationsgenauigkeit.')
    export(result,args.out)
    report=args.out/'REPORT.md'
    with report.open('a') as stream:
        stream.write('\n## Antwortformat und Phasenstatus\n\n| Phase | Modell | Beobachtet | Akzeptiert | Parser: abgeschnitten | Sonstige | API: Tokenlimit |\n|---|---|---:|---:|---:|---:|---:|\n')
        for phase,model,observed,status,length_terminated in diagnostics:
            stream.write(f"| {phase} | {model} | {observed} | {status['accepted']} | {status['truncated']} | {observed-status['accepted']-status['truncated']} | {length_terminated} |\n")
        stream.write('\nReasoning-off wird anhand expliziter Nullwerte der gemeldeten Reasoning-Tokens geprueft. Sichtbare Erklaerungen sind weiterhin moeglich. Abgeschnittene Ausgaben zaehlen unter diesem Protokoll nicht als korrekte Antworten.\n')
        if result['selection']:
            stream.write('\nAuswahl aus dem Smoke (keine nachtraegliche Anpassung der Hauptmessung):\n\n')
            for model,selection in result['selection']['models'].items():
                stream.write(f"- {model}: Baseline {selection['baseline']}; Screening-Grenze N={selection['boundary_n']}, K={selection['boundary_k']}; {selection['reason']}.\n")
            for model in result['models']:
                if model['id'] not in result['selection']['models']:
                    stream.write(f"- {model['id']}: keine vollstaendig formatgueltige Smoke-Stufe; keine eigene Grenzschaetzung. Beide Modelle erhalten dieselbe ausgewaehlte Hauptmatrix.\n")
        stream.write('\n## Reproduktion und Herkunft\n\nOeffentliche Ausgabe enthaelt aggregierte Messwerte. Lokale Rohbelege und Schluessel sind nicht enthalten. Protokoll-SHA256: `'+result['protocol_hash']+'`.\n\n')
        stream.write('```bash\ntracking-bench campaign audit runs/luna-sonnet-20260929-live\npython scripts/export_frontier_delivery.py --campaign runs/luna-sonnet-20260929-live --out dashboard/replayed-copy\n(cd dashboard/replayed-copy && sha256sum -c SHA256SUMS)\n```\n\nNeue bezahlte Messung: siehe README und docs/FRONTIER_CAMPAIGN.md; eigenen Laufordner verwenden. Ohne lokale Rohbelege ist nur die Pruefung der oeffentlichen Export-Hashes moeglich.\n')
    hashes={p.name:file_hash(p) for p in sorted(args.out.iterdir()) if p.is_file() and p.name!='SHA256SUMS'}
    (args.out/'SHA256SUMS').write_text(''.join(f'{h}  {name}\n' for name,h in hashes.items()))
    print('Exported audited dashboard and diagnostic report:',args.out)


if __name__=='__main__':main()

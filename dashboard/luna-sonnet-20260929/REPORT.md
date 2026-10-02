# Luna / Sonnet: Kampagnenvergleich

Ausführung: **live**. Audit: **PASS**.
Kosten: **0.516902 USD** / 4 USD; offene Reservierungen: 0 USD.

[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv) · [Protokoll](protocol.json)

## Was bedeuten N, K und R?

| Kuerzel | Bedeutung | Was wird gezaehlt? |
|---|---|---|
| **N** | Anzahl der Personen (Entitaeten) | In diesen Aufgaben gibt es auch N unterschiedliche Objekte und N moegliche Personen als Antwort. N ist nicht die Anzahl der Testfaelle. |
| **K** | Gesamtzahl der Ereignisse pro Aufgabe | Jeder Tausch (`swap`) bzw. jede Uebergabe (`handoff`) zaehlt als ein Ereignis. Anfangszuordnung, Frage und Prompt-Beispiele zaehlen nicht mit. |
| **R** | Relevante Besitzwechsel pro Aufgabe | Anzahl der K Ereignisse, bei denen das am Ende abgefragte Objekt den Besitzer wechselt. Die anderen K-R Ereignisse aendern dessen Besitzer nicht. |

**Beispiel `N/K/R = 5/32/16`:** 5 Personen und 5 Objekte, 32 Ereignisse; bei 16 davon wechselt das abgefragte Objekt den Besitzer, bei den anderen 16 nicht. Dieselbe Person kann mehrfach beteiligt sein: R kann groesser als N sein, aber es gilt `0 <= R <= K`. R ist keine Zahl interner Reasoning-Schritte. K ist kein Tokenbudget.

Im Dashboard zeigt die Achse **N/K** Personen/Ereignisse; die Tabelle **N/K/R** ergaenzt die relevanten Besitzwechsel. Die Filter heissen **K: Ereignisse** und **R: relevante Besitzwechsel**. In CSV/JSON entsprechen die Werte `n`, `k` und `relevant_updates`. Bei der BBH-Referenz wurde R nicht separat erfasst: **`—` bzw. `null` bedeutet nicht ausgewiesen, nicht null Besitzwechsel**.


| Phase | Modell | N | Ereignisse | Gruppen | Korrekt / geplant | Abdeckung |
|---|---|---:|---:|---:|---:|---:|
| gate | openai/gpt-6-luna | 3 | 0 | 1 | 2 / 2 | 100% |
| gate | anthropic/claude-sonnet-5 | 3 | 0 | 1 | 2 / 2 | 100% |
| gate | openai/gpt-6-luna | 3 | 1 | 1 | 2 / 2 | 100% |
| gate | anthropic/claude-sonnet-5 | 3 | 1 | 1 | 2 / 2 | 100% |
| smoke | openai/gpt-6-luna | 3 | 32 | 4 | 5 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 3 | 32 | 4 | 0 / 8 | 100% |
| smoke | openai/gpt-6-luna | 5 | 32 | 4 | 5 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 5 | 32 | 4 | 0 / 8 | 100% |
| smoke | openai/gpt-6-luna | 7 | 32 | 4 | 4 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 7 | 32 | 4 | 0 / 8 | 100% |
| smoke | openai/gpt-6-luna | 10 | 32 | 4 | 4 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 10 | 32 | 4 | 2 / 8 | 100% |
| smoke | openai/gpt-6-luna | 16 | 32 | 4 | 3 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 16 | 32 | 4 | 1 / 8 | 100% |
| smoke | openai/gpt-6-luna | 24 | 32 | 4 | 4 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 24 | 32 | 4 | 2 / 8 | 100% |
| smoke | openai/gpt-6-luna | 32 | 32 | 4 | 4 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 32 | 32 | 4 | 0 / 8 | 100% |
| smoke | openai/gpt-6-luna | 48 | 32 | 4 | 2 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 48 | 32 | 4 | 0 / 8 | 100% |
| smoke | openai/gpt-6-luna | 64 | 32 | 4 | 4 / 8 | 100% |
| smoke | anthropic/claude-sonnet-5 | 64 | 32 | 4 | 0 / 8 | 100% |
| bbh | openai/gpt-6-luna | 5 | 5 | 15 | 1 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 5 | 5 | 15 | 0 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 7 | 7 | 15 | 0 / 15 | 100% |
| bbh | openai/gpt-6-luna | 7 | 7 | 15 | 2 / 15 | 100% |
| bbh | openai/gpt-6-luna | 3 | 3 | 6 | 3 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 3 | 3 | 6 | 4 / 15 | 100% |
| confirm | openai/gpt-6-luna | 3 | 32 | 12 | 12 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 3 | 32 | 12 | 0 / 24 | 100% |
| confirm | openai/gpt-6-luna | 32 | 32 | 12 | 10 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 32 | 32 | 12 | 2 / 24 | 100% |
| confirm | openai/gpt-6-luna | 48 | 32 | 12 | 9 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 48 | 32 | 12 | 0 / 24 | 100% |
| confirm | openai/gpt-6-luna | 64 | 32 | 12 | 7 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 64 | 32 | 12 | 0 / 24 | 100% |

## Grenzen

- BBH Tracking subset / Chat-3shot / Generation; native acc_norm unavailable.
- Confirmation is independent of smoke; intervals are pointwise, not simultaneous.
- Missing observations remain visible; private provider weights and precision are not verified.
- Cost bound uses a user-accepted conservative envelope assumption.
- smoke / anthropic/claude-sonnet-5: 5/72 Antworten im verlangten Format; Formatfehler sind Teil des gemessenen Generationsprotokolls.
- smoke / anthropic/claude-sonnet-5: 67/72 Ausgaben am Tokenlimit beendet. Das feste 32-Token-Ausgabelimit und Antwortformat begrenzen die Aussage zur Aufgabenloesung.
- bbh / anthropic/claude-sonnet-5: 9/45 Antworten im verlangten Format; Formatfehler sind Teil des gemessenen Generationsprotokolls.
- bbh / anthropic/claude-sonnet-5: 36/45 Ausgaben am Tokenlimit beendet. Das feste 32-Token-Ausgabelimit und Antwortformat begrenzen die Aussage zur Aufgabenloesung.
- confirm / anthropic/claude-sonnet-5: 2/96 Antworten im verlangten Format; Formatfehler sind Teil des gemessenen Generationsprotokolls.
- confirm / anthropic/claude-sonnet-5: 94/96 Ausgaben am Tokenlimit beendet. Das feste 32-Token-Ausgabelimit und Antwortformat begrenzen die Aussage zur Aufgabenloesung.
- Deaktiviertes API-Reasoning schliesst sichtbare Erklaerungen im Antworttext nicht aus. Eine abgeschnittene Erklaerung belegt keine reine Faehigkeitsgrenze.
- Kleine Stichprobe: nur zwei Gruppen je Seed/Aufgabe. Empirische Bootstrap-Intervalle koennen bei ausschliesslich falschen/richtigen Antworten auf 0/1 degenerieren; das beweist keine exakte Populationsgenauigkeit.

Keine native BBH-acc_norm: Originalfragen-Teilstichprobe unter Chat-Dreishot-Generation. Smoke und Bestätigung bleiben getrennt.

## Antwortformat und Phasenstatus

| Phase | Modell | Beobachtet | Akzeptiert | Parser: abgeschnitten | Sonstige | API: Tokenlimit |
|---|---|---:|---:|---:|---:|---:|
| gate | openai/gpt-6-luna | 4 | 4 | 0 | 0 | 0 |
| smoke | openai/gpt-6-luna | 72 | 72 | 0 | 0 | 0 |
| bbh | openai/gpt-6-luna | 45 | 45 | 0 | 0 | 0 |
| confirm | openai/gpt-6-luna | 96 | 96 | 0 | 0 | 0 |
| gate | anthropic/claude-sonnet-5 | 4 | 4 | 0 | 0 | 0 |
| smoke | anthropic/claude-sonnet-5 | 72 | 5 | 67 | 0 | 67 |
| bbh | anthropic/claude-sonnet-5 | 45 | 9 | 2 | 34 | 36 |
| confirm | anthropic/claude-sonnet-5 | 96 | 2 | 94 | 0 | 94 |

Reasoning-off wird anhand expliziter Nullwerte der gemeldeten Reasoning-Tokens geprueft. Sichtbare Erklaerungen sind weiterhin moeglich. Abgeschnittene Ausgaben zaehlen unter diesem Protokoll nicht als korrekte Antworten.

Auswahl aus dem Smoke (keine nachtraegliche Anpassung der Hauptmessung):

- openai/gpt-6-luna: Baseline 0.625; Screening-Grenze N=None, K=None; no_confirmed_boundary_or_low_baseline.
- anthropic/claude-sonnet-5: keine vollstaendig formatgueltige Smoke-Stufe; keine eigene Grenzschaetzung. Beide Modelle erhalten dieselbe ausgewaehlte Hauptmatrix.

## Reproduktion und Herkunft

Oeffentliche Ausgabe enthaelt aggregierte Messwerte. Lokale Rohbelege und Schluessel sind nicht enthalten. Protokoll-SHA256: `79d6ad79ea7d18b26fb994b6a772280592e6c346d053d065b0a4fb11fea1fe27`.

```bash
tracking-bench campaign audit runs/luna-sonnet-20260929-live
python scripts/export_frontier_delivery.py --campaign runs/luna-sonnet-20260929-live --out dashboard/replayed-copy
(cd dashboard/replayed-copy && sha256sum -c SHA256SUMS)
```

Neue bezahlte Messung: siehe README und docs/FRONTIER_CAMPAIGN.md; eigenen Laufordner verwenden. Ohne lokale Rohbelege ist nur die Pruefung der oeffentlichen Export-Hashes moeglich.

# Luna / Sonnet: Kampagnenvergleich

Ausführung: **live**. Audit: **PASS**.
Kosten: **1.456843 USD** / 4 USD; offene Reservierungen: 0 USD.

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
| gate | openai/gpt-6-luna | 5 | 8 | 2 | 2 / 4 | 100% |
| gate | anthropic/claude-sonnet-5 | 5 | 8 | 2 | 3 / 4 | 100% |
| bbh | openai/gpt-6-luna | 5 | 5 | 15 | 3 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 5 | 5 | 15 | 7 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 7 | 7 | 15 | 8 / 15 | 100% |
| bbh | openai/gpt-6-luna | 7 | 7 | 15 | 2 / 15 | 100% |
| bbh | openai/gpt-6-luna | 3 | 3 | 6 | 8 / 15 | 100% |
| bbh | anthropic/claude-sonnet-5 | 3 | 3 | 6 | 8 / 15 | 100% |
| confirm | anthropic/claude-sonnet-5 | 64 | 32 | 12 | 13 / 24 | 100% |
| confirm | openai/gpt-6-luna | 64 | 32 | 12 | 11 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 5 | 32 | 12 | 14 / 24 | 100% |
| confirm | openai/gpt-6-luna | 5 | 32 | 12 | 12 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 16 | 32 | 12 | 15 / 24 | 100% |
| confirm | openai/gpt-6-luna | 16 | 32 | 12 | 12 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 32 | 32 | 12 | 12 / 24 | 100% |
| confirm | openai/gpt-6-luna | 32 | 32 | 12 | 11 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 48 | 32 | 12 | 13 / 24 | 100% |
| confirm | openai/gpt-6-luna | 48 | 32 | 12 | 11 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 10 | 32 | 12 | 13 / 24 | 100% |
| confirm | openai/gpt-6-luna | 10 | 32 | 12 | 13 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 3 | 32 | 12 | 16 / 24 | 100% |
| confirm | openai/gpt-6-luna | 3 | 32 | 12 | 16 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 24 | 32 | 12 | 12 / 24 | 100% |
| confirm | openai/gpt-6-luna | 24 | 32 | 12 | 13 / 24 | 100% |
| confirm | anthropic/claude-sonnet-5 | 7 | 32 | 12 | 12 / 24 | 100% |
| confirm | openai/gpt-6-luna | 7 | 32 | 12 | 15 / 24 | 100% |

## Grenzen

- Kostenkarte: kumulative Kosten aller drei Laeufe; Zellkosten beziehen sich nur auf diese neue Messung.
- Frische Generatorgruppen, vorab fixierte Matrix; alle geplanten Faelle bleiben im Nenner. Unbeobachtete Zellen sind unbekannt.
- BBH: dieselben 45 Originalfragen unter Chat-3shot/JSON-Generation; keine native acc_norm und kein BBH-Gesamtscore.
- Leiter 0-shot und BBH 3-shot sind getrennte Protokolle. Unterschiede zum 32-Token-Lauf sind durch geaenderte Prompts, Budget und neue Generatorfaelle mitbedingt.
- Punktweise 95%-Bootstrapintervalle ueber Strukturgruppen; zwei Gruppen je Seed/Aufgabe, keine simultane Absicherung einer Einbruchsschwelle. Reine 0/1-Stichproben koennen degenerierte Intervalle ergeben.
- Strukturelle Frische gilt relativ zu den eingefrorenen Ausschluessen, nicht zu unbekannten Trainingsdaten. Anbieterpraezision und private Gewichte sind nicht verifiziert.
- Kostenbound: freigegebene konservative UTF8-/4096-Envelope-Annahme, keine zertifizierte Tokenzaehlung.

Keine native BBH-acc_norm: Originalfragen-Teilstichprobe unter Chat-Dreishot-Generation. Smoke und Bestätigung bleiben getrennt.

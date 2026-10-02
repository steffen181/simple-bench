# Luna / Sonnet: frischer Vergleich mit strukturierten Antworten

## Was bedeuten N, K und R?

| Kuerzel | Bedeutung | Was wird gezaehlt? |
|---|---|---|
| **N** | Anzahl der Personen (Entitaeten) | In diesen Aufgaben gibt es auch N unterschiedliche Objekte und N moegliche Personen als Antwort. N ist nicht die Anzahl der Testfaelle. |
| **K** | Gesamtzahl der Ereignisse pro Aufgabe | Jeder Tausch (`swap`) bzw. jede Uebergabe (`handoff`) zaehlt als ein Ereignis. Anfangszuordnung, Frage und Prompt-Beispiele zaehlen nicht mit. |
| **R** | Relevante Besitzwechsel pro Aufgabe | Anzahl der K Ereignisse, bei denen das am Ende abgefragte Objekt den Besitzer wechselt. Die anderen K-R Ereignisse aendern dessen Besitzer nicht. |

**Beispiel `N/K/R = 5/32/16`:** 5 Personen und 5 Objekte, 32 Ereignisse; bei 16 davon wechselt das abgefragte Objekt den Besitzer, bei den anderen 16 nicht. Dieselbe Person kann mehrfach beteiligt sein: R kann groesser als N sein, aber es gilt `0 <= R <= K`. R ist keine Zahl interner Reasoning-Schritte. K ist kein Tokenbudget.

In der frischen Hauptmessung dieses Berichts bleiben **K=32 und R=16** fest; variiert wird N.

Im Dashboard zeigt die Achse **N/K** Personen/Ereignisse; die Tabelle **N/K/R** ergaenzt die relevanten Besitzwechsel. Die Filter heissen **K: Ereignisse** und **R: relevante Besitzwechsel**. In CSV/JSON entsprechen die Werte `n`, `k` und `relevant_updates`. Bei der BBH-Referenz wurde R nicht separat erfasst: **`—` bzw. `null` bedeutet nicht ausgewiesen, nicht null Besitzwechsel**.


## Ergebnis und Messumfang

Ausfuehrung: **live**, Audit **PASS**. Hauptmessung: 432/432 Antworten; BBH: 90/90; Kontrollen: 12/12.

**Alle 534 Antworten waren vollstaendig und schema-konform; kein Tokenlimit-Abbruch.** Die Hauptmessung ergibt Luna **114/216 (52.8%)**, Sonnet **120/216 (55.6%)**. Entscheidend ist die Aufgabe: Handoff Luna **104/108**, Sonnet **108/108**; Swap Luna **10/108**, Sonnet **12/108**. Bei Swaps ist bereits N=3 schwach (beide 4/12); Handoffs bleiben bis N=64 weitgehend korrekt. Damit wurde **keine klare Einbruchsschwelle durch steigende Entitaetenzahl** bestimmt. Die gezeigten Fehler sind in diesem Lauf keine beobachteten JSON-/Abschlussfehler.

[Interaktives Dashboard](../dashboard/luna-sonnet-structured-20260930/index.html) · [CSV](../dashboard/luna-sonnet-structured-20260930/results.csv) · [JSON mit Intervallen und Strata](../dashboard/luna-sonnet-structured-20260930/results.json) · [vorab fixiertes Protokoll](STRUCTURED_COMPARISON.md)

Kosten dieses Vergleichs: **0.829398050 USD**. Vorherige Kampagne und Diagnose: 0.6274453 USD. **Kumuliert 1.456843350 / 4 USD**, offene Reservierungen 0 USD. Die Dashboard-Kostenkarte zeigt die kumulierten Kosten; Tabellenzellen nur den neuen Lauf.

## Frische Generatorfaelle

K=32 Ereignisse, R=16 relevante Updates, zwei Aufgaben (swap/handoff), drei Seeds, je zwei Strukturgruppen pro Aufgabe/Seed/N und zwei Optionsrotationen. Pro N und Modell sind das 24 Antworten auf 12 Strukturgruppen; insgesamt 108 neue Gruppen. Beide Modelle sehen dieselben Faelle. Die komplette Matrix wurde vor dem ersten bezahlten Aufruf fixiert.

| Entitaeten N | GPT-6 Luna | Claude Sonnet 5 | Luna minus Sonnet | 95%-Intervall, Prozentpunkte |
|---:|---:|---:|---:|---:|
| 3 | 16/24 (66.7%) | 16/24 (66.7%) | +0.0 pp | [-12.5, 12.5] |
| 5 | 12/24 (50.0%) | 14/24 (58.3%) | -8.3 pp | [-8.3, -8.3] |
| 7 | 15/24 (62.5%) | 12/24 (50.0%) | +12.5 pp | [8.3, 16.7] |
| 10 | 13/24 (54.2%) | 13/24 (54.2%) | +0.0 pp | [-8.3, 8.3] |
| 16 | 12/24 (50.0%) | 15/24 (62.5%) | -12.5 pp | [-25.0, 0.0] |
| 24 | 13/24 (54.2%) | 12/24 (50.0%) | +4.2 pp | [0.0, 8.3] |
| 32 | 11/24 (45.8%) | 12/24 (50.0%) | -4.2 pp | [-8.3, 0.0] |
| 48 | 11/24 (45.8%) | 13/24 (54.2%) | -8.3 pp | [-20.8, 4.2] |
| 64 | 11/24 (45.8%) | 13/24 (54.2%) | -8.3 pp | [-16.7, 0.0] |

### Aufschluesselung nach Aufgabe

| N | Luna swap | Sonnet swap | Luna handoff | Sonnet handoff |
|---:|---:|---:|---:|---:|
| 3 | 4/12 | 4/12 | 12/12 | 12/12 |
| 5 | 0/12 | 2/12 | 12/12 | 12/12 |
| 7 | 3/12 | 0/12 | 12/12 | 12/12 |
| 10 | 1/12 | 1/12 | 12/12 | 12/12 |
| 16 | 0/12 | 3/12 | 12/12 | 12/12 |
| 24 | 1/12 | 0/12 | 12/12 | 12/12 |
| 32 | 0/12 | 0/12 | 11/12 | 12/12 |
| 48 | 1/12 | 1/12 | 10/12 | 12/12 |
| 64 | 0/12 | 1/12 | 11/12 | 12/12 |

Die Intervalle sind punktweise, nach Aufgabe/Seed stratifizierte Gruppen-Bootstrapintervalle (2.000 Replikate). Rotation und Modelle teilen dieselben Gruppen. Nur zwei Gruppen pro Seed/Aufgabe: breite bzw. bei reinen 0/1-Stichproben degenerierte Intervalle sind moeglich. Das zusammengefallene Differenzintervall bei N=5 ist insbesondere kein Nachweis hoher Praezision: der Bootstrap kann die zwischen den beiden beobachteten Gruppen eines Stratums fehlende Variation nicht erzeugen. Es gibt keine simultan abgesicherte Einbruchsschwelle.

## Format und Reasoning

| Modell | Schema/Abschluss gueltig | Tokenlimit | Reasoning aus, explizit geprueft |
|---|---:|---:|---|
| openai/gpt-6-luna | 267/267 | 0 | ja |
| anthropic/claude-sonnet-5 | 267/267 | 0 | ja |

Beide Modelle: striktes JSON-Schema mit genau einem `answer`-Feld und festgelegter Antwortmenge; 256 Ausgabetokens, keine Erklaerung, `reasoning.enabled=false`, direkte Anbieterroute ohne Fallback. Sampling: Anbieterdefaults, kein API-Seed. Anbieterpraezision unbekannt. Explizite Usage-Werte belegen null API-Reasoning-Tokens; private interne Verarbeitung ist damit nicht beobachtbar.

## BBH-Referenz, getrennt von der Generatorleiter

Dieselben 45 Originalfragen wie im vorherigen Lauf, 15 je N=3/5/7. Originaltext und drei Demonstrationen bleiben erhalten; finale Antwort unter demselben JSON-Schema wie bei der Leiter. Dies ist **BBH-Tracking-Teilstichprobe / Chat-3shot / JSON-Generation**, keine native `acc_norm`, kein BBH-Gesamtscore und keine frische BBH-Stichprobe. Die Generatorleiter bleibt 0-shot.

| BBH N | GPT-6 Luna | Claude Sonnet 5 |
|---:|---:|---:|
| 3 | 8/15 | 8/15 |
| 5 | 3/15 | 7/15 |
| 7 | 2/15 | 8/15 |

## Einordnung

Als gezielter Anschluss bietet sich eine vorab fixierte Ereignisleiter bei kleinem N an: zuerst fuer Swaps eine tragfaehige leichte Ausgangsbedingung finden, danach Ereignislast und Entitaetenzahl getrennt variieren. Handoff und Swap sollten eigene Hauptauswertungen behalten. Das ist ein Vorschlag fuer neue Entwicklungsfaelle, keine nachtraegliche Aenderung dieser Messung.

Die Frage lautet, wie sich die Korrektheit bei steigender Entitaetenzahl unter einem festen, formatkontrollierten Protokoll veraendert. Eine schwache Ausgangsleistung bei N=3 oder ein nichtmonotoner Verlauf erlaubt keine klare Kapazitaetsgrenze. Die beobachteten Werte und Modellunterschiede bleiben deskriptiv; fuer belastbare Grenzwerte braucht es mehr unabhaengige Gruppen und eine separat festgelegte Bestaetigung.

Die frischen Gruppen schliessen die eingefrorenen kanonischen/Legacy-IDs der Vorgaengerkampagne, gebuendelte historische BBH-Gruppen und die neuen nichttrivialen Kontrollen aus. Das ist keine Aussage ueber unbekannte Trainingsdaten. Null-Ereignis-Kontrollen und BBH-Originale wurden absichtlich wiederverwendet.

Gegenueber dem alten 32-Token-Lauf sind Prompt, Ausgabebudget und Generatorfaelle geaendert. Daher keine kausale Zuschreibung der Scoreaenderung allein an JSON-Schema und kein Pooling. Die [vorherige gepaarte Schema-Diagnose](../research/structured-output-smoke-20260930/REPORT.md) pruefte die engere Formatfrage. Alte Berichte und Ergebnisdateien bleiben erhalten.

## Reproduktion und Pruefung

Frozen protocol SHA256: `9897ea58fd44f762e59d39b2d53f6d821d9e2f702e15c5022388c5eab46f8e2e`. Analysecode: `2cfcd46912b9c88478d6c6a0c1e1831c8b899be8038c2729be4f5af723d1f40a`. Aggregation: `51ed61488b88f828d25bd7a9ce399c1659ca07e6d532dcf6ca65ff6b42035f41`. Die exportierten Dateien haben einen eigenen [SHA256SUMS](../dashboard/luna-sonnet-structured-20260930/SHA256SUMS).

```bash
tracking-bench structured audit runs/structured-comparison-20260930
tracking-bench structured export runs/structured-comparison-20260930 --out dashboard/replayed-structured-copy
pytest -q
```

Lokale Requests, Responses, Receipts und Kostenledger sind versiegelt; Zugangsdaten werden nicht exportiert. Audits rekonstruieren Requests, Kostenangebote, Scores, Abbruchbedingungen und geplante Abdeckung. 110 Offline-Tests bestanden; der vollstaendige 534-Aufruf-Simulator und die Dashboard-Filter wurden vor der Messung geprueft. Offline-Fixtures sind keine Modellmessungen. Die freigegebene konservative Kostenannahme ist keine zertifizierte Tokenzaehlung.

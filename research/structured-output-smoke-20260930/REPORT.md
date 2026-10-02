# Strukturierte Ausgaben: diagnostischer Smoke vom 30. September 2026

**Der Ansatz funktioniert in dieser Probe:** Sonnet liefert mit strikt vorgegebenem JSON-Schema bei 256 und 1024 Tokens jeweils 7/7 vollstaendige, gueltige Antworten auf nichttriviale Fragen. Mit derselben JSON-Anweisung, aber ohne API-Schema, sind es 1/7 bzw. 2/7. Ein groesseres Tokenbudget allein beseitigt das Formatproblem hier nicht. Luna ist in allen vier Bedingungen formatgueltig.

Die technische Formatverbesserung ist kein Nachweis hoher Loesungsgenauigkeit: Sonnet loest mit Schema 3/7 bzw. 2/7 dieser Fragen. Der kleine diagnostische Datensatz erlaubt keinen Leistungsrang oder belastbaren Unterschied zwischen 256 und 1024 Tokens.

## Gepaarte Ergebnisse

Alle Zeilen beziehen sich auf dieselben **sieben nichttrivialen Fragen**: vier vorhandene Generatorfaelle (N=3/32, Swap/Handoff, jeweils 32 Ereignisse und 16 relevante Updates) plus je eine BBH-Originalfrage bei N=3/5/7. Der einfache Kontrollfall ist in dieser Tabelle ausgeschlossen.

| Modell | Tokenlimit | Antwortvorgabe | Vollstaendig + schema-gueltig | Korrekt | Am Tokenlimit |
|---|---:|---|---:|---:|---:|
| openai/gpt-6-luna | 256 | Nur JSON-Anweisung | 7/7 | 4/7 | 0/7 |
| openai/gpt-6-luna | 256 | Striktes API-Schema | 7/7 | 3/7 | 0/7 |
| openai/gpt-6-luna | 1024 | Nur JSON-Anweisung | 7/7 | 4/7 | 0/7 |
| openai/gpt-6-luna | 1024 | Striktes API-Schema | 7/7 | 2/7 | 0/7 |
| anthropic/claude-sonnet-5 | 256 | Nur JSON-Anweisung | 1/7 | 1/7 | 3/7 |
| anthropic/claude-sonnet-5 | 256 | Striktes API-Schema | 7/7 | 3/7 | 0/7 |
| anthropic/claude-sonnet-5 | 1024 | Nur JSON-Anweisung | 2/7 | 2/7 | 1/7 |
| anthropic/claude-sonnet-5 | 1024 | Striktes API-Schema | 7/7 | 2/7 | 0/7 |

Alle acht einfachen Kontrollaufrufe sind korrekt, vollstaendig und schema-gueltig. Ein Schema allein garantiert keine sachlich richtige Antwort. 256 ist hier ein Ausgabelimit, keine vorgeschriebene Ausgabelaenge.

## Was genau verglichen wurde

- Acht feste Fragen x zwei Modelle x zwei Budgets x zwei Ausgabevarianten = 64 Aufrufe. Keine nachtraegliche Auswahl, kein Retry.
- Innerhalb jedes Modell-/Budgetpaares identische Frage und identische explizite JSON-Anweisung; nur `response_format` unterscheidet sich. Das API-Schema erzwingt ein Objekt mit genau dem String-Feld `answer`, einem Enum aller erlaubten Antworten und `additionalProperties:false`; `strict:true`.
- Generierte Fragen verlangen Besitzernamen als Werte; BBH verlangt die vorhandenen parenthesierten Optionen als Werte, z. B. `{"answer":"(A)"}`. Goldlabels bleiben ausschliesslich in der lokalen Auswertung.
- Alte ausschliessliche Textformat-Anweisungen wurden durch dieselbe JSON-Anweisung in beiden Armen ersetzt. Bei BBH bleiben Originalfrage und drei Originaldemonstrationen erhalten. Kein Response-Healing, keine Nachbearbeitung ungueltiger Texte.
- Direkte Routen `openai` / `anthropic`, keine Provider-Fallbacks, `require_parameters:true`. Reasoning deaktiviert und explizite Nullwerte in allen 64 Antworten geprueft. Keine neue Logprob-Funktion; dies ist weiterhin Generation.
- Reihenfolge der vier Bedingungen pro Frage rotiert, Modellreihenfolge alterniert. Anbieter-Samplingdefaults; kein gemeinsamer Temperature-/Seed-Override. Quantisierung unbekannt.
- JSON wird strikt geprueft: Codezaeune, Erklaerungen, doppelte Schluessel, Zusatzfelder oder nicht erlaubte Antworten sind ungueltig. Ein formal gueltiges JSON mit `finish_reason=length` gilt nicht als vollstaendige Antwort. Trefferquote zaehlt solche Faelle im Nenner mit.

## BBH und Aussagegrenzen

Dies sind **wiederverwendete Diagnosefaelle**, keine frische Bestaetigung. Auswahl: lexikografisch kleinste vorhandene Fall-ID je vorab festgelegter Zelle, ohne Filter nach bisherigen Treffern. Wiederholte Fragen ueber Bedingungen und Modelle sind keine zusaetzlichen unabhaengigen Faelle. Keine Konfidenz- oder Signifikanzbehauptung aus dieser kleinen Probe.

BBH bleibt separat in `summary.csv`/`results.json` (`kind=bbh`) auswertbar. Je eine Originalfrage pro N ist ein Format-/Transportcheck, kein neuer BBH-Leistungswert. JSON-Ausgabe mit drei Demos ist ein eigenes Generationsprotokoll und keine native `acc_norm`. Auch das Schema liefert keine Next-Token-Wahrscheinlichkeiten.

Im Vergleich zur gestrigen 32-Token-Kampagne wurden Budget UND Antwortinstruktion geaendert. Ein Vorher/Nachher-Vergleich kann deren Einzelwirkung daher nicht isolieren. Die **innerhalb dieser Probe** gepaarten Arme isolieren die zusaetzliche Schema-Anforderung bei festem Budget und Prompt.

## Empfehlung

Fuer die naechste unabhaengige Vergleichskampagne: beide Modelle mit strikt identischem Antwortschema, API-Reasoning aus und zunaechst 256 Tokens testen. Das genuegte hier fuer alle Schemaantworten; 1024 brachte keinen zusaetzlichen Formatvorteil. Vor einer Hauptmessung erneut nichttriviale Formatkontrollen und frische Strukturgruppen verwenden. Die geringeren Trefferzahlen einzelner Schemaarme sind bei sieben Fragen und Anbieter-Sampling keine belastbare Verschlechterung durch das Schema.

## Kosten, Belege und Reproduktion

Probe: **0.1105429 USD**, offene Reservierungen **0 USD**, Limit 0,75 USD. Vorherige Kampagne 0.5169024 USD; zusammen **0.6274453 USD** von insgesamt 4 USD. Die 0,25-USD-Gesamtreserve bleibt unberuehrt. Alter Budgetledger und alter Dashboard-Export wurden nicht veraendert.

Audit PASS: versiegelte Anfragen/Antworten, Kosten, Modell-/Provideridentitaet, Tokenbounds, Reasoningstatus, Schema und Treffer aus Rohbelegen erneut geprueft. Die Kostenquote zaehlt konservativ alle UTF8-Bytes des Requests inklusive Schema plus 4096 Envelope-Tokens und die volle Ausgabeobergrenze; dies ist die freigegebene Annahme, keine providerzertifizierte Tokenzaehlung.

Elf Offline-Tests bestanden. Vollstaendiger simulierter 64-Aufruf-Lauf und Fehlerfall (HTTP502 mit unerwarteter JSON-Form) bestanden; der Fehlerfall stoppt nach einem Versuch und behaelt seine Reservierung. Keine Produkt-/Benchmark-CLI geaendert. `probe.py` und `test_probe.py` sind **archivierte Wegwerfskripte dieser Machbarkeitsprobe**, keine unterstuetzte neue Runner-Schnittstelle.

```bash
# Offline-Pruefung der archivierten Probe
python -m pytest -q research/structured-output-smoke-20260930/test_probe.py
# Reanalyse benoetigt die lokalen privaten Rohbelege und den unveraenderten Vorgaengerlauf.
python research/structured-output-smoke-20260930/probe.py audit runs/structured-output-smoke-20260930
# Oeffentlichen Export pruefen
(cd research/structured-output-smoke-20260930 && sha256sum -c SHA256SUMS)
```

Die Rohbelege unter `runs/structured-output-smoke-20260930/` sowie API-Schluessel, Accountguthaben und Provider-Request-IDs sind nicht veroeffentlicht. Oeffentlich liegen aggregierte Zahlen, fallweise Diagnosewerte ohne Fragen, Protokoll und Quellskripte vor. Hashes beweisen Integritaet relativ zum erhaltenen Manifest, nicht die Wahrheit privater Anbieterlogits.

[Ergebnisdaten](results.json) · [Zellwerte CSV](summary.csv) · [Protokoll](protocol.json) · [Pruefsummen](SHA256SUMS)

API-Referenzen: [OpenRouter Structured Outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Luna-Routen](https://openrouter.ai/api/v1/models/openai/gpt-6-luna/endpoints), [Sonnet-Routen](https://openrouter.ai/api/v1/models/anthropic/claude-sonnet-5/endpoints). Schema-Unterstuetzung ist routenabhaengig; hier wurde sie zusaetzlich praktisch geprueft.

Rohprotokoll-SHA256: `8d575fdbb2410f00bb74c1b0698d317d0608145797fcbea77e85a2743ce5d64b`. Probe-Code-SHA256: `a6dd3408b53d80aa19f33efd72ba5d6d270e5518ab1b6ae44bc5d746fb203166`.

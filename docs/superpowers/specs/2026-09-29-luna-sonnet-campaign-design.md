# Luna/Sonnet: budgetierter Vergleich und Leistungsgrenze

Status: Entwurf auf ausdrücklichen Wunsch „Mache zuerst einen Plan“. Keine Implementierung, kein kostenpflichtiger Aufruf. Die Modellkorrektur ist bereits vom Nutzer bestätigt: GPT-6 Luna und **Claude Sonnet 5** statt Sonnet 5.5, damit beide ohne Reasoning laufen können. Kostenobergrenze **4,00 USD für die gesamte Kampagne**, inklusive Probes, Fehlern und Smoke. Datum: 29.09.2026.

## Ziel und Voraussetzungen

Vergleich auf identischen generierten Tracking-Aufgaben: Ab welcher Entitätenzahl bzw. Ereignislast fällt die Leistung deutlich ab? Ein kleines adaptives Entwicklungs-Screening bestimmt den Bereich. Eine anschließend fixierte Messung mit frischen Strukturgruppen quantifiziert die Leistung. Ein lokal öffnendes Dashboard im Repo zeigt Ergebnisse, Messbedingungen, Unsicherheit und Kosten.

Geprüft: `openai/gpt-6-luna`, Katalogrevision `openai/gpt-6-luna-20260922`, Route `openai`; `anthropic/claude-sonnet-5`, Katalogrevision `anthropic/claude-sonnet-5-20260630`, Route `anthropic`. Beide erlauben laut Katalog abschaltbares Reasoning. Sonnet 5.5 verlangt es; der Nutzer hat den Wechsel zu Sonnet 5 gewählt. Routen melden die Quantisierung als unbekannt. Diese APIs erlauben keine Zusage identischer Präzision oder fest verifizierter Gewichte. Belege: [öffentlicher Capability-Snapshot](../plans/2026-09-29-luna-sonnet-capabilities.json).

Die angegebene WSL-Schlüsseldatei existiert. Ihr Inhalt wurde in dieser Planungsphase nicht gelesen. Bei Ausführung ausschließlich aus dem externen Pfad laden, ohne Shell-`source`/`eval`, ohne Token in Logs, Konfigurationen oder Repository. Exakte Pfade nur lokal als CLI-Argument; öffentliche Vorlagen verwenden `OPENROUTER_API_KEY` oder einen Platzhalter.

## Abgewogene Ansätze

1. Vollständiges Raster: einfache Interpretation, aber unnötig viele kostenpflichtige leichte/schwere Zellen.
2. Ausschließlich adaptive Tests: günstig, aber Ergebnis und ausgewählte Grenze sind durch dieselben Daten bestimmt.
3. **Empfohlen: adaptiver Smoke, danach unabhängige Messung**. Selektionsdaten bleiben von den berichteten Hauptwerten getrennt; begrenzte Stichproben werden sichtbar ausgewiesen.

## Gemeinsames Protokoll

- Feste Modell- und Provider-IDs, `allow_fallbacks=false`, `require_parameters=true`, ein Request gleichzeitig; Reihenfolge beider Modelle deterministisch ausgeglichen.
- `reasoning.enabled=false`. Nur explizit gemeldete null Reasoning-Tokens und kein gemeldeter Reasoning-Text gelten als bestätigt. Fehlende Metadaten bedeuten unbestätigt und stoppen den Hauptlauf; verstecktes Reasoning wird nicht als deaktiviert interpretiert.
- Identischer englischer Prompt, Zero-shot auf der Leiter, keine CoT-Aufforderung, Antwort nur als Kandidatenname, `max_tokens=32`, kein Streaming.
- Die ausgewählten direkten Routen bieten `temperature`/`top_p` nicht gemeinsam an: beide Parameter auf beiden Seiten weglassen und Anbieterdefaults dokumentieren. Keine Behauptung deterministischer oder temperaturgleicher Inferenz. API-Seed ebenfalls weglassen, weil Sonnet ihn nicht anbietet. Generator-Seeds bleiben fest.
- Korrektheit unabhängig vom Modell berechnen; Gold nur lokal. Pro Struktur zwei feste Optionsrotationen, gleiche Fälle für beide Modelle. Beide Rotationen zählen als eine statistische Gruppe.
- Drei feste Generator-Seeds für die Hauptmessung: 20261011, 20261012, 20261013; Smoke: 20261001. Struktur- statt Textausschlüsse, einschließlich aller Probes/Smoke-Fälle. Bestätigungsfragen erst nach eingefrorener Auswahl erzeugen und nicht zur Protokollanpassung verwenden.

## Ablauf und Messgrößen

**Gate:** maximal acht Anfragen insgesamt für Antwortformat, einfache Kopier-/Trackingkontrollen, Kosten-/Identitätsprüfung und Reasoning-Nachweis. Gate-Ergebnisse sind Diagnostik, keine Benchmarkleistung. Technische Fehler niemals als kognitiven Leistungseinbruch behandeln.

**Smoke:** N = 3, 5, 7, 10, 16, 24, 32, 48, 64; zunächst K=32 Ereignisse, davon exakt 16 mit Eigentümerwechsel des abgefragten Objekts. Pro N zwei frische Gruppen je Aufgabentyp (swap/handoff), zwei Rotationen und beide Modelle: 16 Anfragen pro Stufe. Für dieses Screening beide Aufgaben separat anzeigen, gleich gewichtet aggregiert zur Bereichswahl. Options-/Längenchecks verhindern, dass reine Parserfehler die Suche lenken. Frühestens nach einer guten Basisstufe eine mögliche Grenze markieren: Gruppenmittel höchstens 75% **und** mindestens 20 Prozentpunkte unter der N=3-Basis. Zwei aufeinanderfolgende betroffene Stufen dienen als Screening-Bestätigung; sie beweisen keine allgemeine Monotonie. Anomalien am Start bzw. fehlende gute Basis als solche melden.

Für jedes Modell die letzte Stufe davor, die erste betroffene Stufe und ihren nächsten Nachbarn auswählen. Die Vereinigung plus N=3 ergibt höchstens sieben Hauptstufen. Beide Modelle bekommen diese identische Vereinigung, damit die Ergebnisse paarbar bleiben. Wenn kein Einbruch auftritt: N=3 und die letzten drei gemessenen Stufen wählen. Wenn keine Grenze wegen Budgetstopp erreicht wird, den Suchbereich als unvollständig markieren.

**Optionale Ereignis-Stressreihe:** falls N=64 unter K=32 bei beiden Modellen noch keinen deutlichen Rückgang zeigt, K=64 und 128 bei N=64 und Relevanzquote 1/2 im verbleibenden Smoke-Budget prüfen. Eigene Achse; keine Aussage „nur N bewirkte den Einbruch“. Gleiche Auswahl-/Bestätigungslogik für K, ohne den Hauptumfang von maximal sieben Zellen zu überschreiten; bei Konflikt N=3 und die äußeren/Übergangszellen vorab deterministisch priorisieren.

**Hauptmessung:** pro ausgewählter Zelle, Seed und Aufgabentyp mindestens zwei, bevorzugt vier neue Gruppen, jeweils zwei Rotationen und beide Modelle. Mindestumfang 12 unabhängige Gruppen pro Zelle (6 je Aufgabentyp), Ziel 24. Tatsächliche Anzahl vor Öffnung der Hauptantworten allein anhand Kostenobergrenzen festlegen. Kann die minimale gemeinsame Matrix nicht bezahlt werden, keine vollwertige Bestätigung behaupten: Smoke-/Pilot-Ergebnis und begrenzte Abdeckung liefern. Nicht nachträglich nur billige Modelle oder günstige Aufgaben fortsetzen.

**Auswertung:** korrekte Antworten / alle geplanten Antworten mit separat ausgewiesener Abdeckung; gültige Fehlantworten, ungültige Formate, Trunkierung, API-Fehler und Nichtausführungen unterscheiden. Zusätzlich Genauigkeit auf technisch beobachteten Fällen. Genauigkeit und Chance 1/N je Zelle, paarweise Modelldifferenz, Optionsstabilität, Token, Latenz und Kosten. 2.000 gepaarte Bootstrap-Replikate über Strukturgruppen, innerhalb Seed×Aufgabentyp, beide Rotationen und Modelle zusammen. Punktweise 95%-Intervalle; keine simultane Signifikanzbehauptung über die Grenzsuche. Gruppenanzahl immer anzeigen. Hauptmessung bestätigt nur den gewählten Bereich; adaptive Smoke-Schätzungen bleiben getrennt.

## BBH-Bezug

Die Routen werben weder vollständige Kandidaten-Likelihoods noch `logprobs` an. Deshalb ist native `acc_norm` hier **nicht verfügbar**. Kein simuliertes Likelihood-Scoring und kein Top-Token-Ersatz.

Unter identischem Chat-Dreishot-Antwortprotokoll für beide Modelle: vorab zufällig fixierte 30 Originalfragen je N=3/5/7 (90 je Modell); falls vorab zu teuer, gleichmäßig 15 je N. Zusätzlich bei ausreichendem BBH-Teilbudget zehn frische BBH-nahe Fragen je N=5/7, vorab erzeugt und gesperrt. Maximal 220 Anfragen für diesen Block. Gleiche Demonstrationen, Optionsantwort `(A)` usw., strikte generative Genauigkeit. Ausdrücklich „BBH Tracking Teilstichprobe / Chat-3shot / Generation“, keine vollständige 750er-Referenz und kein BBH-Gesamtscore. Die Leiter bleibt Zero-shot und eigener Aufgabentyp, keine direkte Vermischung beider Zahlenkolonnen. Protokollvergleich zu veröffentlichten nativen Werten nur qualitativ, nicht als score-identische Replikation.

## Budget

| Anteil | Obergrenze USD |
|---|---:|
| Gate/Format/Reasoning | 0,15 |
| Adaptiver Smoke einschließlich optionaler Stressstufen | 0,60 |
| BBH-Referenzblock | 0,60 |
| Frische Hauptmessung | 2,40 |
| Unverplante Sicherheitsreserve | 0,25 |
| Gesamt | **4,00** |

Aktuelle Standardpreise laut öffentlichem Routing-Snapshot, pro Million Tokens: Luna 0,10 USD Input / 0,50 USD Output; Sonnet 5 2,00 / 10,00. Beispielrechnung, keine Zusage: ein Aufgabenpaar mit je 2.000 Input-/32 Output-Tokens kostet ungefähr 0,004536 USD ohne Cache-/Zusatzgebühren. 500 solche Paare wären rund 2,27 USD. Tatsächliche Prompts werden vorab kalkuliert, alle bezahlten Versuche zählen.

Ein gemeinsamer lokaler Ledger mit Cap 4,00, reguläres Arbeitsbudget 3,75. Neue Anfrage nur nach Reservierung einer konservativen, für die konkrete Route belegten Obergrenze. Der vorhandene volle-Kontext-Ansatz reserviert bei Sonnet schon mehr als 4 USD und ist dafür unbrauchbar; **nicht** einfach Kontextangaben verkleinern. Neue Text-/Chat-Tokenbounds müssen den kompletten übertragenen Prompt und dokumentierten Envelope, Cache-/Tarifstufen und Output einbeziehen. Unbelegte Zeichen/4-Schätzung oder aus Smoke-Durchschnitt abgeleitete Obergrenzen sind unzulässig. Wenn kein belastbarer kleinerer Bound verfügbar ist, bleibt die sichere Ablehnung bestehen; kein kostenpflichtiger Lauf durch Aufweichen der Budgetprüfung. Tatsächliche Providerkosten nach jedem Request abgleichen, unbekannte Kosten/unsichere Abbrüche reserviert halten und stoppen, keine automatischen Retries. Ein Providervertragsbruch kann vom Client nicht präventiv garantiert ausgeschlossen werden; die Sicherheitsreserve ist keine zusätzliche Versuchserlaubnis.

## Größere Strukturen

Leiter v1 bleibt reproduzierbar. Neue v2 unterstützt N=3..64, K bis 128, feste eindeutige alphabetische Namen/Objektwörter (kompatibel zum Parser), auswählbare Aufgaben und exakte Relevanz. Das aktuelle Umbenennungsaudit enumeriert (N-1)! Permutationen; bloßes Hochsetzen des Limits reicht nicht.

Für v2 einen exakten farbigen Graphkanonisierer verwenden (geplant: python-igraph/Bliss als optionales campaign-extra). Personen-/Objektknoten, initiale Besitzrelation, markiertes Query-Objekt und zeitlich/rollenmarkierte Ereignisse kodieren. Swap-Partner sind ungeordnet, Übergaberollen geordnet. Neue versionierte Gruppen-ID, Gleichheit auf kleinen N gegen den alten Algorithmus prüfen; keine Behauptung alter Hashidentität. Bei Vergleichen mit alten N<=7-Fällen beide Schema-IDs ableiten; Historienausschlüsse nicht stillschweigend verwerfen. Ressourcenlimit und Tests auch für wenig Ereignisse/viele unbeteiligte Entitäten. Unabhängiger Besitzmengen-Solver plus Text-Replay bleiben Pflicht.

## Dashboard und Artefakte

Statisches Dashboard `dashboard/luna-sonnet-20260929/index.html`, ohne CDN oder API-Schlüssel, lokal per Doppelklick. Diagramme für Genauigkeit über N bzw. K, Chance und Intervalle; Filter für Phase, Task, Seed, Modell und Relevanz; gepaarte Differenzen; Kosten-/Token-/Latenzübersicht; Format-/Reasoning-/Abdeckungsstatus. BBH separat mit Protokollkennzeichnung. Unbeobachtete Zellen fehlen bzw. sind grau, nicht 0%.

Öffentliche Dateien: Dashboard, aggregiertes `results.json`, CSV, reproduzierbares Protokoll und Hashinventar. Lokale Rohdaten, Request-IDs, Fehlertexte, Kontostände und Schlüsselpfade bleiben unter ignorierten `runs/`. Dashboard nur aus verifizierten Belegen erzeugen, keine manuell eingetragenen Ergebniszahlen. Keine Veröffentlichung oder Remote-Push Bestandteil dieses Auftrags.

## Abnahme

Neue Funktionen erst mit scheiternden sinnvollen Tests, dann Implementierung und Regression. Alte v1-Fixtures bleiben unverändert. Offline-Fixture-Kampagne deckt Budgetstopp, Reasoning-Verletzung, Herkunftsbindung, unbekannte Kosten, Rotation, Split-Ausschluss, Entscheidungspfad, Dashboard und Replay ab. Erst nach technischem Gate bezahlte Kampagne; Rohbefunde, Kosten, Grenzen und Prüfsummen berichten. Auch „kein Einbruch innerhalb des untersuchten Bereichs/Budgets“ erfüllt die ehrliche Ergebnislieferung.

Quellen: [OpenRouter Modelle](https://openrouter.ai/api/v1/models), [Reasoning-Steuerung](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens), [GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna), [Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5), [Sonnet 5.5: Thinking immer aktiv](https://openrouter.ai/anthropic/claude-sonnet-5.5). Aktuelle Metadaten vor Ausführung erneut prüfen.

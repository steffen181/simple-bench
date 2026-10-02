# Reasoning low: Leistung und Tokenaufwand

Messreihe gestartet am **1. Oktober 2026**, abgeschlossen am **2. Oktober 2026**. **526/526 neue Aufrufe**, Audit **PASS**, Kosten **1,4003303 USD von neu genehmigten 5 USD**, keine offenen Reservierungen. [Interaktives Dashboard](../dashboard/luna-sonnet-reasoning-20261001/index.html) · [Zellwerte](../dashboard/luna-sonnet-reasoning-20261001/cells.csv) · [Gruppenwerte](../dashboard/luna-sonnet-reasoning-20261001/groups.csv) · [vorab festgelegtes Protokoll](REASONING_EFFORT_20261001.md).

Die niedrigste aktive Reasoning-Stufe **low** verbessert die beobachtete Trefferquote beider Modelle stark. Sie benötigt zusätzliche Tokens. Deshalb zeigt die Bewertung sowohl richtige Antworten als auch den Aufwand je Aufgabe und je richtiger Antwort.

## Exakt gepaarter Vergleich

Beide Modelle bearbeiteten dieselben 216 Swap-Präsentationen: **36 Kombinationen** von N=4/8/16/32, R=4/8/16 und D=0/8/16, jeweils **drei Strukturgruppen mit zwei Antwortanordnungen**. N bezeichnet Personen/Objekte, R relevante Besitzwechsel des abgefragten Objekts, D andere Swaps; K=R+D.

Pro Zelle wurde vor Ausführung die lexikografisch erste kanonische Gruppe jedes der drei Generator-Seeds ausgewählt. Die Auswahl nutzte keine Antworten. Die historischen Antworten ohne Reasoning stammen ausschließlich aus diesen ausgewählten Fällen. Deshalb unterscheiden sich die folgenden Off-Werte von den früheren Gesamtwerten über neun Gruppen je Zelle (22,2 % und 31,5 %). Diese Reihe ist eine Wiederverwendung gepaarter Aufgaben zur Untersuchung der Konfiguration, keine neue unabhängige Validierung.

| Modell | Ohne Reasoning, dieselben Fälle | Low | Veränderung | Reasoning-Tokens je Aufgabe bei low |
|---|---:|---:|---:|---:|
| GPT-6 Luna | 40/216 = 18,5 % | **196/216 = 90,7 %** | +72,2 Prozentpunkte | **143,8** |
| Claude Sonnet 5 | 62/216 = 28,7 % | **214/216 = 99,1 %** | +70,4 Prozentpunkte | **318,9** |

Sonnet löst bei low 34 von 36 Zellen vollständig. Die beiden übrigen Zellen (N=32/R=4/D=8 und N=32/R=8/D=8) liegen jeweils bei 5/6. Luna löst 25 Zellen vollständig; die niedrigsten Werte betragen jeweils 3/6 bei N=4/R=16/D=16, N=4/R=8/D=8 und N=8/R=8/D=16. Diese nachträglich beschriebenen Minima sind keine abgesicherten Leistungsschwellen. Pro Zelle liegen nur drei Strukturgruppen vor.

## Tokenverbrauch fließt in die Bewertung ein

**Ausgabetokens je richtiger Antwort = sämtliche Ausgabetokens / Zahl richtiger Antworten.** Die Ausgabetokens enthalten bereits Reasoning und endgültige Antwort. Auch Tokens falscher Antworten bleiben vollständig im Zähler; sie werden nicht ausgeblendet. Bei null richtigen Antworten ist die Kennzahl nicht definiert und erscheint als „—“.

| Modell / Stufe | Reasoning-Tokens gesamt | Ausgabetokens gesamt | Ausgabetokens je richtiger Antwort | USD je richtiger Antwort |
|---|---:|---:|---:|---:|
| Luna aus | 0 | 2.896 | 72,4 | 0,000320 |
| Luna low | 31.066 | 34.372 | **175,4** | **0,000146** |
| Sonnet aus | 0 | 2.702 | 43,6 | 0,007830 |
| Sonnet low | 68.891 | 71.768 | **335,4** | **0,005496** |

Diese Tabelle bezieht sich auf das Swap-Raster; BBH und einfache Kontrollen sind getrennt. Die Medianwerte des Reasoning-Verbrauchs je Aufgabe betragen bei low 135,5 Tokens für Luna und 304,5 für Sonnet; die Maxima 506 und 1.523. Alle 432 neuen Swap-Antworten enthalten ausdrücklich gemeldete positive Reasoning-Nutzung.

Low verbraucht hier mehr Ausgabetokens pro Treffer. Die gemessenen **Dollar-Kosten pro Treffer sinken jedoch bei beiden Modellen**, weil deutlich mehr Aufgaben gelöst werden und die Eingabekosten pro erfolgreicher Antwort dadurch geringer ausfallen. Token- und Geldeffizienz beantworten unterschiedliche Fragen. Es gibt keinen willkürlich gewichteten Gesamtscore. Modellübergreifend bedeuten gleiche Tokenzahlen wegen unterschiedlicher Tokenizer nicht denselben Rechenaufwand.

## Dashboard

Die vierte Achse **Reasoning Effort** zeigt „aus“ und „low“ bei festen N/R/D-Werten. Für N-, R- oder D-Kurven lassen sich beide Effort-Stufen gemeinsam oder einzeln anzeigen. Als Bewertung sind wählbar:

- Trefferquote;
- tatsächliche Reasoning-Tokens pro Aufgabe;
- gesamte Ausgabetokens je richtiger Antwort;
- tatsächliche USD je richtiger Antwort.

Ein Klick auf einen Punkt öffnet die drei gepaarten Gruppen: Trefferquote und Reasoning-Tokens je Modell und Stufe. Gestrichelte Linien kennzeichnen die historische Off-Baseline. Linien verbinden nur Messpunkte; Zwischenwerte wurden nicht gemessen. Das Dashboard funktioniert lokal ohne Server oder externe Abrufe.

## Separate originale BBH-Referenz

| Modell | Aus | Low | Reasoning-Tokens je BBH-Aufgabe bei low |
|---|---:|---:|---:|
| Luna | 10/45 = 22,2 % | **40/45 = 88,9 %** | 84,0 |
| Sonnet | 20/45 = 44,4 % | **45/45 = 100,0 %** | 157,9 |

Originales N=3/5/7 bleibt unverändert: jeweils 15 Fragen. Luna low erreicht 15/15, 15/15 und 10/15; Sonnet jeweils 15/15. Es sind dieselben 45 Originalfragen unter Chat-three-shot/JSON-Generation. **Keine native `acc_norm`, kein BBH-Gesamtscore.** Die generierten Swap-Aufgaben sind zero-shot; BBH und Generatorwerte werden nicht zusammengefasst.

## Bedingungen und Grenzen

Beide festen direkten OpenRouter-Routen unterstützen `low` als kleinste aktive Stufe: `openai/gpt-6-luna-20260922` und `anthropic/claude-sonnet-5-20260630`. Prompts, JSON-Schema, Aufgaben und Antwortanordnungen entsprechen der Baseline. Reasoning-Text wird nicht benötigt; die Auswertung nutzt die expliziten API-Nutzungszahlen. Fehlende Zahlen werden niemals als null interpretiert.

**Das Ausgabelimit wurde von 256 auf 2.048 Tokens erhöht**, da Reasoning dieses Limit mitverbraucht. Der Vergleich misst daher praktische Konfigurationen. Er isoliert keinen kausalen Effort-Effekt bei identischem Tokenlimit. Historische Messzeit, Provider-Sampling, unbekannte interne Präzision und die beschränkte Strukturmenge bleiben weitere Grenzen. Low ist ein Anbieterparameter und kein einheitliches Rechenbudget beider Modelle.

Alle neuen Antworten sind vollständig und schema-konform: **keine Formatfehler, keine Tokenlimit-Abbrüche, keine technischen Ausfälle, keine Wiederholungsversuche**. Alle vier einfachen Kontrollen waren richtig. Sonnet meldete dort zweimal null Reasoning-Tokens; bei den übrigen Antworten beider Modelle war Reasoning positiv. Das zeigt, warum angeforderte Stufe und tatsächlicher Verbrauch getrennt ausgewiesen werden.

Das feste Raster endete nach 526 Aufrufen; **3,5996697 USD** des neuen Budgets blieben ungenutzt. Die 0,25-USD-Sicherheitsreserve wurde nicht benötigt. Historische Kosten wurden nicht erneut auf dieses Budget angerechnet. Die konservative Reservierung basiert auf UTF8-Bytes plus 4.096 Hülltokens und maximalen Tarifen; sie ist keine zertifizierte Vorab-Tokenzählung.

## Reproduktion und Prüfung

```bash
tracking-bench reasoning audit runs/reasoning-effort-20261001
tracking-bench reasoning export runs/reasoning-effort-20261001 --out dashboard/replayed-reasoning
(cd dashboard/luna-sonnet-reasoning-20261001 && sha256sum -c SHA256SUMS)
```

**139 Offline-Tests bestanden**. Eine unabhängige Review fand eine Lücke im historischen Phasenbudget-Audit; ein scheiternder Test reproduzierte sie, die Korrektur wurde erneut geprüft. Vier gezielte Tests wurden unabhängig bestanden. Der Audit rekonstruiert nun auch die verfügbare Phasen- und Gesamtkapazität vor jedem historischen Aufruf beziehungsweise Modellpaar. Eine im Browser reproduzierte Skalierung kleiner Dollarwerte wurde ebenfalls korrigiert.

Rohdaten: `runs/reasoning-effort-20261001`; Prüfbelege: `runs/reasoning-effort-20261001-preflight`. Die internen Runner-Phasen heißen `gate`, `bbh` und `confirm`; es gibt hier keinen Pilot und keine ausgewählte Bestätigungsphase. [Öffentliche Prüfsummen](../dashboard/luna-sonnet-reasoning-20261001/SHA256SUMS) binden HTML, JSON, CSV und Bericht.

- Protokoll-SHA256: `ad2fc36b32680744d0c2e24168ff98f21878af8c86f635e8417263e0788e5463`
- Rohdatensiegel-SHA256: `467adc4ee9194cb1565bd0525be25901a62337421ff559d5da416f430c5690ed`

Die fertige Live-Ansicht bestand die Chromium-Prüfung für alle vier Achsen, Token-/Kostenmetriken, gepaarte Gruppen und Mobilbreite ohne JavaScript-Fehler oder externe Abrufe; die Desktopansicht wurde zusätzlich visuell kontrolliert. 5.758 versiegelte Dateien wurden geprüft, alle 35 älteren öffentlichen Dashboard-Dateien sind unverändert. Öffentliche Dateien wurden auf den extern geladenen Zugangstoken geprüft; kein Token wurde in Artefakten gefunden.

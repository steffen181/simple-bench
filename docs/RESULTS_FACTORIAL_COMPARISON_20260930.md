# N/R/D-Vergleich: Messwerte und Streuung nachvollziehen

**Abgeschlossen am 2026-10-01: 958/958 Entwicklungsaufrufe und 192/192 frische Bestätigungsaufrufe; Audit PASS.** Die Fortsetzung hat keine bereits gemessene Antwort wiederholt. Zwei Luna-Formatfehler zählen als falsch und sind separat ausgewiesen. Alle 192 Bestätigungsantworten waren formatgültig.

[Interaktives Dashboard](../dashboard/luna-sonnet-descriptive-20261001/index.html) · [Vollständige Zelltabelle](../dashboard/luna-sonnet-descriptive-20261001/REPORT.md) · [JSON](../dashboard/luna-sonnet-descriptive-20261001/results.json) · [CSV](../dashboard/luna-sonnet-descriptive-20261001/results.csv) · [Protokoll und Befehle](FACTORIAL_COMPARISON.md)

Dieser Benchmark beschreibt beobachtete Leistung und ihre Streuung. Im Dashboard stehen Genauigkeit, einzelne Strukturgruppen und gepaarte Modellunterschiede im Mittelpunkt. Ein Gruppenwert von 0 %, 50 % oder 100 % bedeutet null, eine oder zwei richtige Antworten auf dieselbe Struktur mit zwei Antwortanordnungen.

Die zusätzlichen frischen Fälle zeigen einen Sonnet-Rückgang um 52,1 Prozentpunkte bei zusätzlichen anderen Ereignissen und einen Sonnet-Vorsprung von 41,7 Punkten gegenüber Luna ohne diese Ereignisse. Pilot und zusätzliche Messreihe bleiben getrennt: Die zusätzlichen Zellen wurden anhand der Pilotwerte ausgewählt. Die formale Prüfung des ursprünglichen Protokolls bleibt im aufklappbaren Methodenbereich des Dashboards erhalten; sie ist kein Bestehen-/Nichtbestehen-Urteil für diesen beschreibenden Benchmark.

## Was variiert wurde

| Achse | Werte | Bedeutung |
|---|---|---|
| N | 3, 7, 16, 32 | Personen, anfängliche Objekte und Antwortoptionen |
| R | 4, 8, 16 | Besitzwechsel des abgefragten Objekts |
| D | 0, 8, 16 | Andere Ereignisse ohne Besitzwechsel dieses Objekts |
| K | R+D | Gesamtzahl der Ereignisse |

Alle 36 Kombinationen wurden für Swap und Handoff getrennt gemessen. Je Aufgabe/Zelle: drei unterschiedliche Strukturgruppen, eine pro Generator-Seed, jeweils zwei Optionsrotationen und beide Modelle. Das ergibt 216 Gruppen, 432 Präsentationen und 864 Raster-Aufrufe. Hinzu kommen vier Null-Ereignis-Kontrollen und 90 Aufrufe auf denselben 45 BBH-Originalfragen.

Modelle: GPT-6 Luna und Claude Sonnet 5 über die fixierten direkten OpenRouter-Routen. Beide verwenden strict JSON mit Antwort-Enum, maximal 256 Completion-Tokens, deaktiviertes API-Reasoning und keine Fallbacks. Explizite Usage mit null Reasoning-Tokens wurde für alle 1.150 Antworten geprüft. Generator: 0-shot; BBH: Chat-3shot. Sampling verwendet Anbieterdefaults; Anbieterpräzision und Trainingsdaten sind unbekannt.

## Vollständiger Pilot, Aufgaben getrennt

| Teil | Luna korrekt | Sonnet korrekt | Formatfehler Luna / Sonnet |
|---|---:|---:|---:|
| Handoff, gesamtes N/R/D-Raster | 216/216 (100,0 %) | 216/216 (100,0 %) | 0 / 0 |
| Swap, gesamtes N/R/D-Raster | 51/216 (23,6 %) | 69/216 (31,9 %) | 2 / 0 |
| BBH-Originalreferenz, separat | 13/45 (28,9 %) | 24/45 (53,3 %) | 0 / 0 |
| Null-Ereignis-Kontrollen | 2/2 | 2/2 | 0 / 0 |

Die Raster-Gesamtwerte sind deskriptiv und verbergen Zellunterschiede. Das Dashboard zeigt N×R bei festem D sowie getrennte Aufgaben, Phasen und eine Luna-minus-Sonnet-Ansicht. N ist keine Stichprobengröße; R zählt keine internen Reasoning-Schritte.

Handoff zeigt im untersuchten Raster keinen beobachteten Leistungsabfall. Daraus folgt keine unbegrenzte Robustheit jenseits von N=32, R=16 oder D=16. Swap ist deutlich schwieriger. Die zwei Formatfehler erklären die große Zahl falscher Swap-Antworten nicht allein.

## Zusätzliche frische Fälle an ausgewählten Stellen

Nach vollständigem Pilot wurde genau die eingefrorene Auswahlregel angewendet: größter zulässiger Ein-Achsen-Verlust und größter Modellunterschied, mit fixierter Richtung, Schwellen und lexikalischen Gleichstandsregeln. Acht Aufgabe/Zellen bei R=4/D=0 waren bereits vor der Messung wegen unzureichender frischer Strukturen von der Bestätigung ausgeschlossen.

Ausgewählt wurden zwei Zellen: **Swap, N=32, R=8, D=0 beziehungsweise D=8**. Beide Kontraste hatten im Pilot 66,7 Prozentpunkte Unterschied. Pro Zelle wurden 24 frische Gruppen aus der bereits vor dem Pilot eingefrorenen Fallbank gemessen: acht je neuem Seed, je zwei Rotationen und beide Modelle. Keine Bestätigungsantwort wurde zur Auswahl oder Anpassung verwendet.

| Frische Zelle | Luna | Sonnet | Formatfehler |
|---|---:|---:|---:|
| N=32, R=8, D=0, K=8 | 18/48 (37,5 %) | 38/48 (79,2 %) | 0 |
| N=32, R=8, D=8, K=16 | 4/48 (8,3 %) | 13/48 (27,1 %) | 0 |

Die 48 Antworten pro Modell/Zelle sind **24 Gruppen mit je zwei Rotationen**, keine 48 unabhängigen Fälle. Das Dashboard zeigt jede Gruppe als Kreis mit null, einer oder zwei richtigen Antworten, die Spannweite der vollständigen Gruppen und alle Gruppen nebeneinander. Im Pilot sind es drei Gruppen je Zelle. [Gruppenwerte herunterladen](../dashboard/luna-sonnet-descriptive-20261001/groups.csv).

Diese Streuung beschreibt Unterschiede zwischen Fällen und Antwortanordnungen. Sie ist kein Konfidenzintervall und keine Messung von Schwankungen bei wiederholten identischen API-Anfragen.

### Ursprüngliche formale Prüfung (Methodendokumentation)

| Eingefrorener Kontrast | Frischer Unterschied | Konservatives Intervall | Urteil |
|---|---:|---:|---|
| Sonnet-Verlust von D=0 auf D=8, N/R konstant | 52,1 pp | −12,9 bis 100,0 pp | INCONCLUSIVE |
| Sonnet minus Luna bei D=0 | 41,7 pp | −18,8 bis 100,0 pp | INCONCLUSIVE |

Die Auswertung mittelt zuerst die Rotationen je Strukturgruppe. Der Modellvergleich verwendet gepaarte Hoeffding-Grenzen. Der Zellverlust verwendet die Vereinigung marginaler Hoeffding-Grenzen; dadurch ist keine Unabhängigkeit zwischen den Zellen erforderlich. Bonferroni berücksichtigt zwei geplante Kontraste, Familienfehler 0,05. Unabhängige Gruppen innerhalb einer Zelle bleiben eine Annahme. Die Halbbreiten liegen bei 24 Gruppen bei etwa 60,4 beziehungsweise 65,0 Prozentpunkten. Erst eine untere Grenze über 15 Punkten hätte einen praktisch relevanten Unterschied bestätigt.

Die Optionsstabilität ist ebenfalls sichtbar: bei D=0 stimmen Lunas Antworten auf beide Rotationen in 7/24 Gruppen überein, Sonnets in 20/24; bei D=8 sind es 10/24 beziehungsweise 16/24. Die Rotationswerte sind diagnostisch und kein zusätzlicher vorab geplanter Bestätigungstest.

## Formatfehler und unveränderte Historie

Der ursprüngliche Lauf stoppte nach Aufruf 113 gemäß seiner damaligen Regel. Luna lieferte bei Swap, N=16/R=16/D=16 erklärenden Text vor dem JSON. Die Antwort endete regulär bei 237 Tokens, nicht am Tokenlimit. Nach ausdrücklicher Freigabe („ja trotzdem fortsetzen und als falsch ausweisen.“) wurde ein hash-gebundener Nachtrag erstellt.

Die Fortsetzung begann exakt bei der nächsten offenen Anfrage und ergänzte 845 Antworten. Ein weiterer Luna-Formatfehler trat in derselben Zelle mit einem anderen Generator-Seed auf: reguläres Ende bei 220 Tokens. Beide Antworten bleiben unverändert gespeichert und zählen null; keine nachträgliche Extraktion eines möglicherweise richtigen Teiltexts, keine Wiederholung. Formatfehler sind in JSON, CSV und Dashboard separat gezählt. Technische Fehler oder ungeklärte Kosten hätten weiterhin gestoppt; solche Stopps traten nicht auf.

Die Fehlerbehandlung wurde nach dem ersten Pilot-Formatfehler und vor allen Bestätigungsantworten geändert. Sie wird deshalb als genehmigter Protokollnachtrag dokumentiert, nicht als ursprüngliche Vorregistrierung. Fälle, Reihenfolge, Anfragen, Modelle, Budgets, Auswahlgrenzen, Gleichstandsregeln und Bestätigungsbank blieben gleich. Die Primärmetrik umfasst Aufgabenleistung und Formattreue.

Der [ursprüngliche Stopp-Export](../dashboard/luna-sonnet-factorial-20260930-stopped/index.html) und sämtliche Rohdaten seines Abschnitts bleiben erhalten. COMPLETE bezeichnet vollständige Ausführung, nicht die Bestätigung einer Forschungshypothese.

## Kosten, Reproduktion und Grenzen

Alle früheren Läufe plus diese Kampagne: **2,839507050 / 4 USD**, null offene Reservierungen. Die gesamte N/R/D-Kampagne kostete **1,3826637 USD**, einschließlich ihres ursprünglichen Stopps; die nun ausgeführte Fortsetzung samt Bestätigung **1,2376785 USD**. Es wurde kein zusätzlicher Lauf aus dem Restbudget gestartet.

```bash
tracking-bench factorial audit runs/factorial-comparison-20260930
tracking-bench factorial export runs/factorial-comparison-20260930 --out dashboard/replayed-factorial
pytest -q
```

128 Tests bestanden lokal und gegen das installierte Wheel außerhalb des Checkouts. Ein vollständiger Offline-Fortsetzungs-/Bestätigungsdurchlauf wurde geprüft; dessen synthetische Scores sind keine Modellbelege. Unabhängige Codeprüfung und die daraus entstandenen Regressionen sind in [VERIFICATION.md](VERIFICATION.md) dokumentiert. Der Live-Audit rekonstruiert Anfragebindung, Kosten, Scores, Auswahl, Fallbank und beide Segmente ohne doppelte Zählung.

Öffentliche Exportdateien sind durch [SHA256SUMS](../dashboard/luna-sonnet-descriptive-20261001/SHA256SUMS) prüfbar. Das ursprüngliche Entwicklungsprotokoll behält SHA256 `a757d0813834c629be28e10722f880e9b58a83ec81f2bae87dae4118a1bf7367`. Lokale Rohbelege liegen unter `runs/factorial-comparison-20260930/{development,continuation,confirmation}`; Auswahl und Protokollnachträge liegen im übergeordneten Ordner.

BBH bleibt die separate Referenz mit denselben Originalfragen unter Chat-3shot/JSON-Generation, **keine native acc_norm und kein vollständiger BBH-Score**. N verändert auch Promptlänge und Zufallsniveau; D verändert hier zugleich die gesamte Ereigniszahl K. Die gemessenen Unterschiede sind keine isolierten kausalen Gedächtnis- oder Ablenkungseffekte. Strukturelle Frische gilt relativ zu den eingefrorenen Ausschlüssen, nicht gegenüber unbekannten Trainingsdaten. Kostenkontrolle beruht weiterhin auf der freigegebenen konservativen UTF8-/4096-Hülltoken-Annahme, nicht auf zertifizierter Tokenzählung.

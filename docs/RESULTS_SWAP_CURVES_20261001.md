# Frische Swap-Messreihe — 1. Oktober 2026

**Alle 36 Messpunkte vollständig gemessen: 1.390/1.390 API-Aufrufe, 1,6177675 USD von neu genehmigten 4 USD.** Kein Pilot, keine Auswahl auffälliger Zellen und keine Handover-Aufgaben. [Dashboard mit Leistungskurven](../dashboard/luna-sonnet-swap-curves-20261001/index.html) · [alle Messwerte](../dashboard/luna-sonnet-swap-curves-20261001/results.csv) · [einzelne Strukturgruppen](../dashboard/luna-sonnet-swap-curves-20261001/groups.csv) · [vorab festgelegtes Protokoll](SWAP_CURVES_20261001.md).

## Was wurde gemessen?

| Größe | Bedeutung | Werte |
|---|---|---|
| N | Anzahl der Personen und Objekte | 4, 8, 16, 32 |
| R | Swaps, die den Besitzer des abgefragten Objekts ändern | 4, 8, 16 |
| D | Andere Swaps ohne Beteiligung des abgefragten Objekts | 0, 8, 16 |
| K | Gesamtzahl der Swaps | R + D |

Jede Kombination enthält **neun frische Strukturgruppen**, drei je Generator-Seed 20270111/12/13. Jede Gruppe wird mit zwei Antwortanordnungen beiden Modellen vorgelegt. Das ergibt 324 unterschiedliche Gruppen, 648 Aufgabenpräsentationen und 1.296 Hauptmessungen. Hinzu kommen vier Null-Ereignis-Kontrollen und 90 Antworten auf die gleichen 45 originalen BBH-Referenzfragen wie zuvor. Diese Referenzmessung dient der Einordnung und wählt keine Generatorfälle aus.

Alle Fälle und die Reihenfolge wurden vor dem ersten Modellaufruf eingefroren. Neun ausgewogene Runden ergänzen jeden Messpunkt um jeweils eine Gruppe. Bisherige kanonische und ältere Struktur-IDs wurden ausgeschlossen. Zwölf frische Gruppen je Zelle ließen sich innerhalb der aktuellen Generatorsuche nicht überall erzeugen; neun funktionierten über das gesamte Raster. Das ist eine Grenze dieser Suche, kein Beweis über die absolute Zahl möglicher Strukturen.

GPT-6 Luna (`openai/gpt-6-luna-20260922`) und Claude Sonnet 5 (`anthropic/claude-sonnet-5-20260630`) liefen über feste direkte OpenRouter-Routen. Bedingungen: Reasoning aus, maximal 256 Ausgabetokens, striktes JSON-Schema, keine Wiederholungsversuche. Die generierten Aufgaben sind zero-shot. Jede Antwort wurde mit explizit null API-Reasoning-Tokens auditiert; es gab **keine Formatfehler, keine durch das Tokenlimit abgebrochenen Antworten und keine technischen Ausfälle**. Beide Modelle lösten ihre zwei einfachen Kontrollfragen.

## Ergebnisse einfach lesen

| Modell | Richtige Antworten im gesamten Swap-Raster | Anteil |
|---|---:|---:|
| GPT-6 Luna | 144 / 648 | 22,2 % |
| Claude Sonnet 5 | 204 / 648 | 31,5 % |

Diese Gesamtwerte gewichten jede Rasterzelle gleich. Sie verdecken Unterschiede zwischen Bedingungen; aussagekräftiger sind Kurven, auf denen jeweils nur eine Achse variiert wird.

**Beispiel: zusätzliche Ablenkungsereignisse bei N=32 und R=8.** Jeder Wert enthält 18 Antworten aus neun Gruppen.

| D | K | Luna | Sonnet |
|---:|---:|---:|---:|
| 0 | 8 | 6/18 = 33,3 % | 14/18 = 77,8 % |
| 8 | 16 | 0/18 = 0,0 % | 4/18 = 22,2 % |
| 16 | 24 | 1/18 = 5,6 % | 1/18 = 5,6 % |

Hier ist bei Sonnet ein deutlicher beobachteter Leistungsabfall und eine schrumpfende Differenz zwischen den Modellen sichtbar. Bei D=0 löst Sonnet beide Antwortanordnungen in sieben Gruppen und keine in zwei Gruppen; bei D=8 sind es zwei vollständig richtige und sieben vollständig falsche Gruppen. Bei D=16 haben beide Modelle acht vollständig falsche Gruppen und eine halb richtige Gruppe. Das macht die Fallunterschiede hinter den Mittelwerten sichtbar.

Ein zweiter Kurvenabschnitt bei **N=8, D=0**: Für R=4/8/16 erreicht Luna **55,6/44,4/11,1 %**, Sonnet **72,2/55,6/27,8 %**. Die Beispiele wurden nach Abschluss zur Illustration gewählt; sie sind keine statistisch abgesicherten Schwellen und belegen keinen isolierten kausalen Effekt. Alle übrigen Messpunkte bleiben gleichberechtigt im Dashboard sichtbar.

## Dashboard bedienen

1. Unter Leistungskurven **N, R oder D als horizontale Achse** wählen.
2. Die beiden anderen Größen fest einstellen. Dadurch werden unterschiedliche Bedingungen nicht unbemerkt gemittelt.
3. Große Punkte zeigen den Anteil richtiger Antworten. Kleine Punkte zeigen die neun Gruppenwerte je Modell: 0 %, 50 % oder 100 % für null, eine oder zwei richtige Antwortanordnungen.
4. Einen großen Punkt anklicken, um die gepaarten Gruppen beider Modelle für diese Bedingung zu sehen. Unterhalb der Kurve bleibt das N/R-Raster für das separat gewählte D verfügbar.

Die Achsenabstände entsprechen den Zahlenwerten. Linien verbinden gemessene Punkte; Zwischenwerte wurden nicht gemessen. Die Gruppenstreuung beschreibt Unterschiede zwischen Aufgabenstrukturen und Antwortanordnungen. Sie ist kein Konfidenzintervall und keine Wiederholungsstreuung identischer API-Anfragen.

## Separate BBH-Referenz

| Originales BBH-N | Luna | Sonnet |
|---:|---:|---:|
| 3 | 7/15 = 46,7 % | 8/15 = 53,3 % |
| 5 | 2/15 = 13,3 % | 6/15 = 40,0 % |
| 7 | 1/15 = 6,7 % | 6/15 = 40,0 % |
| Gesamt | 10/45 = 22,2 % | 20/45 = 44,4 % |

Dies sind dieselben 45 Originalfragen unter dem bisherigen Chat-three-shot/JSON-Protokoll. Das originale BBH-N=3/5/7 bleibt zur Vergleichbarkeit unverändert; die Umstellung auf N=4/8 betrifft die frisch generierten Fälle. **Keine native `acc_norm`, kein BBH-Gesamtscore.** Unterschiedliche Shot-Bedingungen und Aufgabenverteilungen erlauben keine Gleichsetzung mit dem Generator-Gesamtwert.

## Kosten, Nachvollziehbarkeit und Grenzen

Neue Messreihe: **1,6177675 USD**, null offene Reservierungen; **2,3822325 USD** des neuen Budgets ungenutzt. Die vorgesehene Sicherheitsreserve von 0,25 USD wurde nicht benötigt. Frühere Kosten von 2,839507050 USD bleiben separat. Das feste Raster wurde nach Erreichen aller Messpunkte beendet.

Semantischer Audit: **PASS**, alle Phasen technisch vollständig. Offline-Regression vor Ausführung: **134 Tests bestanden**. Chromium-Prüfung des fertigen Live-Dashboards: alle drei Kurvenachsen, numerische Abstände, Auswahl der richtigen gepaarten Gruppen, neun Gruppen je Modell, Mobilansicht ohne Seitenüberlauf, keine JavaScript-Fehler oder externen Netzabrufe.

```bash
tracking-bench swap-curves audit runs/swap-curves-20261001
tracking-bench swap-curves export runs/swap-curves-20261001 --out dashboard/replayed-swap-curves
(cd dashboard/luna-sonnet-swap-curves-20261001 && sha256sum -c SHA256SUMS)
```

Lokale Rohdaten: `runs/swap-curves-20261001`; Prüfbelege: `runs/swap-curves-20261001-preflight`. Der interne Phasenname `confirm` ist ein wiederverwendeter Runner-Identifier; diese Reihe enthält keinen Pilot und keine ausgewählte Bestätigungsphase. [Öffentliche SHA256-Prüfsummen](../dashboard/luna-sonnet-swap-curves-20261001/SHA256SUMS) binden Dashboard, JSON, CSV und Gruppenexport. Sie erkennen Änderungen gegenüber dem Manifest, sind aber keine unabhängige Provenienzbestätigung.

N verändert auch Promptlänge und Zufallsniveau (1/N); R und D verändern K. Frische gilt relativ zu den eingefrorenen Ausschlüssen, nicht zu unbekannten Trainingsdaten. Einzigartige Strukturen garantieren keine statistische Unabhängigkeit. Anbieterinterne Präzision und Sampling-Defaults bleiben unbekannt. Die Kostenreservierung verwendet die zuvor akzeptierte konservative Schätzung statt zertifizierter Vorab-Tokenzählung. Frühere Rohdaten und Dashboards bleiben erhalten.

SHA256 des eingefrorenen Protokolls: `8668840f125db897e583b5402ec14f712a24f6bf740d655d9c77e4da496fa109`. SHA256 des Rohdatensiegels: `fb080c48471e8682252f8911cfe745d9a7c9f6a7128fefab2be9865cb2f89d9f`.

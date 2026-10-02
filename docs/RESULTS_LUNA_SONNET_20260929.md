# Luna / Sonnet: Ergebnisse vom 29. September 2026

Die Kampagne ist technisch vollstaendig: 434/434 Aufrufe, Reasoning-off laut expliziten Provider-Zaehlern, Audit PASS, **0,5169024 USD** Kosten von maximal 4 USD. Keine offenen Reservierungen.

Die Ergebnisse zeigen eine deutliche Protokollgrenze fuer Sonnet: Bei der frischen Hauptmessung endeten **94/96 Antworten am 32-Token-Limit**, meistens waehrend einer sichtbaren Erklaerung. Deaktiviertes API-Reasoning verhindert solche Antworttexte nicht. Ein Vergleich der reinen Aufgabenfaehigkeit oder eine belastbare Einbruchsschwelle ist damit nicht belegt.

[Interaktives Dashboard](../dashboard/luna-sonnet-20260929/index.html) · [vollstaendiger Bericht](../dashboard/luna-sonnet-20260929/REPORT.md) · [CSV](../dashboard/luna-sonnet-20260929/results.csv) · [Messprotokoll](FRONTIER_CAMPAIGN.md)

## Was bedeuten N, K und R?

| Kuerzel | Bedeutung | Was wird gezaehlt? |
|---|---|---|
| **N** | Anzahl der Personen (Entitaeten) | In diesen Aufgaben gibt es auch N unterschiedliche Objekte und N moegliche Personen als Antwort. N ist nicht die Anzahl der Testfaelle. |
| **K** | Gesamtzahl der Ereignisse pro Aufgabe | Jeder Tausch (`swap`) bzw. jede Uebergabe (`handoff`) zaehlt als ein Ereignis. Anfangszuordnung, Frage und Prompt-Beispiele zaehlen nicht mit. |
| **R** | Relevante Besitzwechsel pro Aufgabe | Anzahl der K Ereignisse, bei denen das am Ende abgefragte Objekt den Besitzer wechselt. Die anderen K-R Ereignisse aendern dessen Besitzer nicht. |

**Beispiel `N/K/R = 5/32/16`:** 5 Personen und 5 Objekte, 32 Ereignisse; bei 16 davon wechselt das abgefragte Objekt den Besitzer, bei den anderen 16 nicht. Dieselbe Person kann mehrfach beteiligt sein: R kann groesser als N sein, aber es gilt `0 <= R <= K`. R ist keine Zahl interner Reasoning-Schritte. K ist kein Tokenbudget.

In der frischen Hauptmessung dieses Berichts bleiben **K=32 und R=16** fest; variiert wird N.

Im Dashboard zeigt die Achse **N/K** Personen/Ereignisse; die Tabelle **N/K/R** ergaenzt die relevanten Besitzwechsel. Die Filter heissen **K: Ereignisse** und **R: relevante Besitzwechsel**. In CSV/JSON entsprechen die Werte `n`, `k` und `relevant_updates`. Bei der BBH-Referenz wurde R nicht separat erfasst: **`—` bzw. `null` bedeutet nicht ausgewiesen, nicht null Besitzwechsel**.


## Frische Hauptmessung

Je Stufe 12 unabhaengige Strukturgruppen, drei Generator-Seeds, Swap/Handoff und zwei Optionsreihenfolgen; 24 Antworten je Modell. Immer 32 Ereignisse, davon 16 fuer das abgefragte Objekt relevant; zero-shot, identische Fragen und sichtbares Ausgabelimit. Anbieterpraezision unbekannt; keine gemeinsam verfuegbaren Temperature-/API-Seed-Einstellungen. Seeds variieren Aufgaben, nicht die Zufallsziehung der Anbieter.

| Entitaeten | GPT-6 Luna | Claude Sonnet 5 | Sonnet: am Tokenlimit |
|---:|---:|---:|---:|
| 3 | 12/24 (50.0%) | 0/24 (0.0%) | 24/24 |
| 32 | 10/24 (41.7%) | 2/24 (8.3%) | 22/24 |
| 48 | 9/24 (37.5%) | 0/24 (0.0%) | 24/24 |
| 64 | 7/24 (29.2%) | 0/24 (0.0%) | 24/24 |

Lunas beobachtete Trefferquote sinkt von 50,0% auf 29,2%. Das ist ein deskriptiver Befund dieser Matrix. Bereits die Smoke-Baseline lag mit 5/8 unter der vorab verlangten guten Ausgangsleistung (>75%); die definierte Einbruchsschwelle wurde daher nicht identifiziert. Bei Sonnet war keine Smoke-Stufe durchgehend formatgueltig. Die festgelegte Ausweichregel waehlte Baseline plus die letzten drei gueltigen N-Stufen; beide Modelle erhielten dieselben frischen Hauptfaelle. Keine nachtraegliche Auswahl anhand der Hauptantworten.

## BBH-Referenz

Gleiche 45 Originalfragen fuer beide Modelle, 15 je N=3/5/7, hashgepruefte Quellen und drei Originaldemonstrationen im Chatprompt. Luna: **6/45**, Sonnet: **4/45**. Luna lieferte 45/45 Antworten im geforderten Format, Sonnet 9/45; 36/45 Sonnet-Ausgaben endeten am Tokenlimit.

Dies ist **BBH Tracking / Original-Teilstichprobe / Chat-3shot / Generation**, keine native `acc_norm` und kein BBH-Gesamtscore. Die ausgewaehlten Routen bieten die erforderliche vollstaendige Kandidaten-Likelihood nicht an. Generierte Leiter (zero-shot) und BBH (three-shot, anderes Antwortformat) bleiben getrennte Protokolle; ihre Rohquoten duerfen nicht als direkter Schwierigkeitsvergleich gelesen werden.

## Belege und Grenzen

Phasen: Gate 8, Smoke 144, BBH 90, frische Bestaetigung 192 Aufrufe. Alle Kosten, Identitaeten, gemeldete Reasoning-Tokens, Anfragen und Scores wurden aus versiegelten Rohbelegen erneut geprueft. Lokale Belege liegen unter `runs/luna-sonnet-20260929-live/`; sie und Zugangsdaten sind nicht Teil der oeffentlichen Ausgabe. Die Nutzungsgebuehren stammen aus den API-Antworten; die Kostenabsicherung verwendet die ausdruecklich freigegebene konservative UTF8-/Envelope-Annahme.

86 Offline-Tests bestanden, Wheel-/Source-Build und installierter CLI-Smoke geprueft. Nach Abschluss aller bezahlten Aufrufe wurden ausschliesslich Reportingfehler korrigiert: BBH-Gruppengewichtung, keine Rotationstatistik fuer Originalfragen, und separates Zaehlen der API-Tokenlimit-Enden. Regressionen reproduzierten diese Fehler zuerst. Vorher/Nachher-Pruefung: Trefferzahlen, Antworten, Parserstatus, Abdeckung und Kosten unveraendert. Ausfuehrungs- und Auswertungscode sind ueber separate Hashes nachvollziehbar.

Die Intervalle resamplen ganze Strukturgruppen, einschliesslich beider Modelle/Rotationen, stratifiziert nach Seed und Aufgabe, mit 2.000 Replikaten und Fragegewichtung. Kleine Strata (zwei Gruppen) und ausschliesslich falsche/richtige Antworten koennen zu sehr engen oder degenerierten empirischen Intervallen fuehren. Sie sind punktweise, keine simultane Absicherung einer adaptiv gesuchten Grenze.

Naechster sinnvoller Versuch waere ein **neues, vorab fixiertes** gemeinsames Ausgabeprotokoll: Antwort zuerst, Formatkontrolle an nichttrivialen Aufgaben und ein fuer beide Modelle ausreichend grosses sichtbares Tokenbudget bei weiterhin deaktiviertem API-Reasoning. Danach mit frischen Strukturgruppen erneut messen. Der vorliegende Lauf wurde dafuer nicht nachtraeglich veraendert oder verlaengert.

Ausfuehrungsprotokoll SHA256: `79d6ad79ea7d18b26fb994b6a772280592e6c346d053d065b0a4fb11fea1fe27`. Auswertungsmodul SHA256: `e49f2e026d0d2ab3a3f6a02be0265b5bac4dc36c028d037735900af9e1bc10cf`. Exporter SHA256: `c65aa1f884c09b8623f1556e33494d27fd28191494ce912b0c7a09132a66c4d5`.

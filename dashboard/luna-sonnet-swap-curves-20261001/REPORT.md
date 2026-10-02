# Luna / Sonnet: N/R/D-Vergleich

[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv)

N = Personen/Objekte; R = Besitzwechsel des Zielobjekts; D = andere Ereignisse; K = R+D. Beispiel N=8/R=8/D=16: acht Personen, acht relevante Wechsel und 16 andere Ereignisse, insgesamt K=24. N ist keine Stichprobengroesse, R kein internes Reasoning.

Audit: PASS. Kosten: 1.6177675 USD neu; 1.6177675 USD im neu genehmigten Budget / 4 USD.

Formatfehler und abgeschnittene Antworten zählen als falsch; die Messung läuft nach freigegebener Änderung weiter. Fehler werden separat ausgewiesen. Der Score umfasst Aufgabenleistung und Formattreue.

## Beobachtete Ergebnisse

Eine vollständige frische Swap-Messreihe ohne Pilot oder Zellenauswahl. Jede Strukturgruppe enthält zwei Antwortanordnungen. Die Gruppenwerte 0 %, 50 % und 100 % bedeuten null, eine oder zwei richtige Antworten. Ihre Spannweite beschreibt Unterschiede zwischen Fällen und Anordnungen, keine Unsicherheit eines Mittelwerts und keine Wiederholungsstreuung identischer API-Anfragen. [Alle Gruppenwerte](groups.csv).

| Messreihe | Aufgabe | Modell | N / R / D | Vollständige Gruppen | Mittelwert | Gruppen-Minimum | Gruppen-Maximum |
|---|---|---|---|---:|---:|---:|---:|
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 4 / 0 | 9/9 | 66.7 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 4 / 0 | 9/9 | 44.4 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 4 / 8 | 9/9 | 33.3 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 4 / 8 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 4 / 16 | 9/9 | 27.8 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 4 / 16 | 9/9 | 27.8 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 8 / 0 | 9/9 | 27.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 8 / 0 | 9/9 | 38.9 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 8 / 8 | 9/9 | 22.2 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 8 / 8 | 9/9 | 22.2 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 8 / 16 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 8 / 16 | 9/9 | 33.3 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 16 / 0 | 9/9 | 27.8 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 16 / 0 | 9/9 | 38.9 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 16 / 8 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 16 / 8 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 4 / 16 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 4 / 16 / 16 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 4 / 0 | 9/9 | 72.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 4 / 0 | 9/9 | 55.6 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 4 / 8 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 4 / 8 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 4 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 4 / 16 | 9/9 | 11.1 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 8 / 0 | 9/9 | 55.6 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 8 / 0 | 9/9 | 44.4 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 8 / 8 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 8 / 8 | 9/9 | 22.2 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 8 / 16 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 8 / 16 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 16 / 0 | 9/9 | 27.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 16 / 0 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 16 / 8 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 16 / 8 | 9/9 | 27.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 8 / 16 / 16 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 8 / 16 / 16 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 4 / 0 | 9/9 | 61.1 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 4 / 0 | 9/9 | 27.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 4 / 8 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 4 / 8 | 9/9 | 11.1 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 4 / 16 | 9/9 | 16.7 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 4 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 8 / 0 | 9/9 | 72.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 8 / 0 | 9/9 | 16.7 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 8 / 8 | 9/9 | 44.4 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 8 / 8 | 9/9 | 33.3 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 8 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 8 / 16 | 9/9 | 16.7 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 16 / 0 | 9/9 | 44.4 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 16 / 0 | 9/9 | 50.0 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 16 / 8 | 9/9 | 44.4 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 16 / 8 | 9/9 | 16.7 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 16 / 16 / 16 | 9/9 | 22.2 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 16 / 16 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 4 / 0 | 9/9 | 77.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 4 / 0 | 9/9 | 50.0 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 4 / 8 | 9/9 | 38.9 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 4 / 8 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 4 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 4 / 16 | 9/9 | 0.0 % | 0.0 % | 0.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 8 / 0 | 9/9 | 77.8 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 8 / 0 | 9/9 | 33.3 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 8 / 8 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 8 / 8 | 9/9 | 0.0 % | 0.0 % | 0.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 8 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 8 / 16 | 9/9 | 5.6 % | 0.0 % | 50.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 16 / 0 | 9/9 | 61.1 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 16 / 0 | 9/9 | 33.3 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 16 / 8 | 9/9 | 22.2 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 16 / 8 | 9/9 | 0.0 % | 0.0 % | 0.0 % |
| Frische Messreihe | swap | anthropic/claude-sonnet-5 | 32 / 16 / 16 | 9/9 | 16.7 % | 0.0 % | 100.0 % |
| Frische Messreihe | swap | openai/gpt-6-luna | 32 / 16 / 16 | 9/9 | 11.1 % | 0.0 % | 50.0 % |




## Zellen (Aufgaben und Phasen getrennt)

| Phase | Aufgabe | Modell | N | R | D | K | Korrekt / geplant | Beobachtet | Formatfehler |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gate | swap | openai/gpt-6-luna | 4 | 0 | 0 | 0 | 2/2 | 2 | 0 |
| gate | swap | anthropic/claude-sonnet-5 | 4 | 0 | 0 | 0 | 2/2 | 2 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 5 | None | None | 5 | 2/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 5 | None | None | 5 | 6/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 7 | None | None | 7 | 6/15 | 15 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 7 | None | None | 7 | 1/15 | 15 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 3 | None | None | 3 | 7/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 3 | None | None | 3 | 8/15 | 15 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 16 | 16 | 32 | 2/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 16 | 16 | 32 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 4 | 16 | 20 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 4 | 16 | 20 | 0/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 8 | 16 | 24 | 2/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 8 | 16 | 24 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 16 | 0 | 16 | 5/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 16 | 0 | 16 | 7/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 8 | 16 | 24 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 8 | 16 | 24 | 1/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 4 | 8 | 12 | 6/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 4 | 8 | 12 | 2/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 4 | 16 | 20 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 4 | 16 | 20 | 2/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 8 | 0 | 8 | 5/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 8 | 0 | 8 | 7/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 4 | 0 | 4 | 14/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 4 | 0 | 4 | 9/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 4 | 8 | 12 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 4 | 8 | 12 | 2/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 4 | 8 | 12 | 7/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 4 | 8 | 12 | 1/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 4 | 0 | 4 | 13/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 4 | 0 | 4 | 10/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 14/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 6/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 16 | 8 | 24 | 3/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 16 | 8 | 24 | 5/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 8 | 8 | 16 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 8 | 8 | 16 | 4/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 4 | 0 | 4 | 12/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 4 | 0 | 4 | 8/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 16 | 16 | 32 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 16 | 16 | 32 | 4/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 16 | 0 | 16 | 11/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 16 | 0 | 16 | 6/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 4 | 8 | 12 | 2/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 4 | 8 | 12 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 8 | 8 | 16 | 8/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 8 | 8 | 16 | 6/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 8 | 8 | 16 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 8 | 8 | 16 | 4/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 8 | 16 | 24 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 8 | 16 | 24 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 16 | 8 | 24 | 8/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 16 | 8 | 24 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 8 | 16 | 24 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 8 | 16 | 24 | 6/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 0/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 16 | 16 | 32 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 16 | 16 | 32 | 1/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 4 | 16 | 20 | 5/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 4 | 16 | 20 | 5/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 4 | 16 | 20 | 3/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 4 | 16 | 20 | 1/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 16 | 8 | 24 | 4/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 16 | 8 | 24 | 0/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 16 | 0 | 16 | 5/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 16 | 0 | 16 | 2/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 8 | 0 | 8 | 13/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 8 | 0 | 8 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 16 | 0 | 16 | 8/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 16 | 0 | 16 | 9/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 4 | 16 | 8 | 24 | 1/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 4 | 16 | 8 | 24 | 3/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 16 | 16 | 32 | 3/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 16 | 16 | 32 | 2/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 16 | 4 | 0 | 4 | 11/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 16 | 4 | 0 | 4 | 5/18 | 18 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 8 | 8 | 0 | 8 | 10/18 | 18 | 0 |
| confirm | swap | openai/gpt-6-luna | 8 | 8 | 0 | 8 | 8/18 | 18 | 0 |

## Grenzen

- Eine vollständige, vorab fixierte Swap-Messreihe: alle 36 N/R/D-Zellen mit neun frischen Gruppen, drei je Generator-Seed und zwei Antwortanordnungen. Kein Pilot und keine Auswahl auffälliger Zellen.
- Gruppen und Spannweiten beschreiben Fallunterschiede; keine Konfidenzintervalle und keine Messung wiederholter identischer API-Anfragen. Strukturelle Eindeutigkeit ist keine Garantie statistischer Unabhängigkeit.
- Jede Kurve verändert genau eine Achse bei festgehaltenen anderen Achsen. Linien verbinden nur gemessene Punkte; keine behauptete stetige oder monotone Leistung.
- N verändert auch Promptlänge und Zufallsniveau 1/N; K=R+D. Sehr kurze Aufgaben haben begrenzte strukturelle Vielfalt. Frische gilt relativ zu den eingefrorenen bisherigen Fällen.
- BBH: dieselben 45 Originalfragen als separate Chat-3shot/JSON-Referenz. Keine native acc_norm und kein BBH-Gesamtscore; Generatorfälle sind 0-shot.
- Formatfehler zählen als falsch. Fehlende oder technisch nicht auswertbare Antworten bleiben unbekannt. Reasoning aus; Sampling-Anbieterdefaults und interne Präzision unbekannt.
- Separat genehmigte 4 USD für diese Messreihe, davon .25 Reserve. Frühere Kosten werden nicht auf dieses neue Budget angerechnet. Konservative UTF8-/4096-Hülltoken-Schätzung, keine zertifizierte Tokenzählung.

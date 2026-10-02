# Luna / Sonnet: N/R/D-Vergleich

[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv)

N = Personen/Objekte; R = Besitzwechsel des Zielobjekts; D = andere Ereignisse; K = R+D. Beispiel N=7/R=8/D=16: sieben Personen, acht relevante Wechsel und 16 andere Ereignisse, insgesamt K=24. N ist keine Stichprobengroesse, R kein internes Reasoning.

Audit: PASS. Kosten: 1.3826637 USD neu; 2.839507050 USD kumuliert / 4 USD.

Formatfehler und abgeschnittene Antworten zählen als falsch; die Messung läuft nach freigegebener Änderung weiter. Fehler werden separat ausgewiesen. Der Score umfasst Aufgabenleistung und Formattreue.

## Beobachtete Ergebnisse

Breites Raster (Pilot) und zusätzliche frische Fälle bleiben getrennt. Jede Strukturgruppe enthält zwei Antwortanordnungen. Die Gruppenwerte 0 %, 50 % und 100 % bedeuten null, eine oder zwei richtige Antworten. Ihre Spannweite beschreibt Unterschiede zwischen Fällen und Anordnungen, keine Unsicherheit eines Mittelwerts und keine Wiederholungsstreuung identischer API-Anfragen. [Alle Gruppenwerte](groups.csv).

| Messreihe | Aufgabe | Modell | N / R / D | Vollständige Gruppen | Mittelwert | Gruppen-Minimum | Gruppen-Maximum |
|---|---|---|---|---:|---:|---:|---:|
| Zusätzliche frische Fälle | swap | anthropic/claude-sonnet-5 | 32 / 8 / 0 | 24/24 | 79.2 % | 0.0 % | 100.0 % |
| Zusätzliche frische Fälle | swap | openai/gpt-6-luna | 32 / 8 / 0 | 24/24 | 37.5 % | 0.0 % | 100.0 % |
| Zusätzliche frische Fälle | swap | anthropic/claude-sonnet-5 | 32 / 8 / 8 | 24/24 | 27.1 % | 0.0 % | 100.0 % |
| Zusätzliche frische Fälle | swap | openai/gpt-6-luna | 32 / 8 / 8 | 24/24 | 8.3 % | 0.0 % | 50.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 3 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 3 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 7 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 7 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 16 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 16 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 4 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 4 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 4 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 8 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 8 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 8 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 16 / 0 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 16 / 8 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | anthropic/claude-sonnet-5 | 32 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | handoff | openai/gpt-6-luna | 32 / 16 / 16 | 3/3 | 100.0 % | 100.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 4 / 0 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 4 / 0 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 4 / 8 | 3/3 | 50.0 % | 50.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 4 / 8 | 3/3 | 33.3 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 4 / 16 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 4 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 8 / 0 | 3/3 | 83.3 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 8 / 0 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 8 / 8 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 8 / 8 | 3/3 | 66.7 % | 50.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 8 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 8 / 16 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 16 / 0 | 3/3 | 33.3 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 16 / 0 | 3/3 | 50.0 % | 50.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 16 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 16 / 8 | 3/3 | 33.3 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 3 / 16 / 16 | 3/3 | 33.3 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 3 / 16 / 16 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 4 / 0 | 3/3 | 83.3 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 4 / 0 | 3/3 | 50.0 % | 50.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 4 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 4 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 8 / 0 | 3/3 | 66.7 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 8 / 0 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 8 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 8 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 8 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 8 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 16 / 0 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 16 / 0 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 16 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 16 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 7 / 16 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 7 / 16 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 4 / 0 | 3/3 | 83.3 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 4 / 0 | 3/3 | 50.0 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 4 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 4 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 8 / 0 | 3/3 | 33.3 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 8 / 0 | 3/3 | 66.7 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 8 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 8 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 8 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 8 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 16 / 0 | 3/3 | 66.7 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 16 / 0 | 3/3 | 33.3 % | 0.0 % | 100.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 16 / 8 | 3/3 | 33.3 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 16 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 16 / 16 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 16 / 16 / 16 | 3/3 | 33.3 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 4 / 0 | 3/3 | 83.3 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 4 / 0 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 4 / 8 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 4 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 4 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 8 / 0 | 3/3 | 83.3 % | 50.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 8 / 0 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 8 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 8 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 8 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 8 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 16 / 0 | 3/3 | 33.3 % | 0.0 % | 100.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 16 / 0 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 16 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 16 / 8 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | anthropic/claude-sonnet-5 | 32 / 16 / 16 | 3/3 | 16.7 % | 0.0 % | 50.0 % |
| Pilot | swap | openai/gpt-6-luna | 32 / 16 / 16 | 3/3 | 0.0 % | 0.0 % | 0.0 % |

## Methodenanhang: ursprüngliche formale Prüfung

Die folgende formale Prüfung bleibt zur Nachvollziehbarkeit erhalten. Ihr Urteil bewertet ein vorher festgelegtes Absicherungskriterium; die gemessenen Werte und ihre Streuung werden oben unabhängig davon beschrieben.

- {"contrast": {"axis": "d", "development_effect": 0.6666666666666666, "easy": {"d": 0, "n": 32, "r": 8, "task": "swap"}, "hard": {"d": 8, "n": 32, "r": 8, "task": "swap"}, "kind": "performance_drop", "model": "anthropic/claude-sonnet-5"}, "interval_method": "union-of-marginal-Hoeffding-v2", "status": "INCONCLUSIVE", "effect": 0.5208333333333333, "ci": [-0.12949823692101436, 1.0], "groups": [24, 24]}
- {"contrast": {"cell": {"d": 0, "n": 32, "r": 8, "task": "swap"}, "development_effect": 0.6666666666666666, "kind": "model_gap", "left": "anthropic/claude-sonnet-5", "right": "openai/gpt-6-luna"}, "interval_method": "paired-Hoeffding", "status": "INCONCLUSIVE", "effect": 0.4166666666666667, "ci": [-0.1876253870812073, 1.0], "groups": [24]}

## Zellen (Aufgaben und Phasen getrennt)

| Phase | Aufgabe | Modell | N | R | D | K | Korrekt / geplant | Beobachtet | Formatfehler |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gate | swap | openai/gpt-6-luna | 3 | 0 | 0 | 0 | 2/2 | 2 | 0 |
| gate | swap | anthropic/claude-sonnet-5 | 3 | 0 | 0 | 0 | 2/2 | 2 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 5 | None | None | 5 | 4/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 5 | None | None | 5 | 7/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 7 | None | None | 7 | 9/15 | 15 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 7 | None | None | 7 | 3/15 | 15 | 0 |
| bbh | bbh_swap | openai/gpt-6-luna | 3 | None | None | 3 | 6/15 | 15 | 0 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 3 | None | None | 3 | 8/15 | 15 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 8 | 24 | 2/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 8 | 24 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 16 | 32 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 16 | 32 | 2/6 | 6 | 2 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 0 | 4 | 5/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 0 | 4 | 3/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 8 | 24 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 8 | 24 | 2/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 0 | 8 | 4/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 0 | 8 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 16 | 24 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 16 | 24 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 0 | 16 | 2/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 0 | 16 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 8 | 24 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 8 | 24 | 1/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 0 | 16 | 3/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 0 | 16 | 3/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 8 | 16 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 8 | 16 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 16 | 24 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 16 | 24 | 3/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 16 | 32 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 16 | 32 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 8 | 24 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 8 | 24 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 16 | 32 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 16 | 32 | 0/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 8 | 12 | 3/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 8 | 12 | 2/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 0 | 8 | 5/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 0 | 8 | 3/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 8 | 16 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 8 | 16 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 0 | 8 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 8 | 12 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 16 | 32 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 5/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 16 | 20 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 16 | 20 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 8 | 24 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 8 | 16 | 3/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 8 | 16 | 4/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 0 | 16 | 4/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 0 | 16 | 2/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 16 | 32 | 2/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 16 | 32 | 3/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 0 | 4 | 5/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 0 | 4 | 3/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 0 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 8 | 12 | 0/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 16 | 24 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 16 | 24 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 0 | 4 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 16 | 24 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 16 | 24 | 1/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 16 | 20 | 3/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 16 | 20 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 16 | 20 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 0 | 4 | 3/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 0 | 4 | 1/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 16 | 20 | 0/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 16 | 20 | 1/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 0 | 16 | 2/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 0 | 16 | 3/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 16 | 20 | 1/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 16 | 20 | 0/6 | 6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 16 | 24 | 6/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 0 | 4 | 5/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 0 | 4 | 1/6 | 6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 0 | 8 | 2/6 | 6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 0 | 8 | 4/6 | 6 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 4/48 | 48 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 13/48 | 48 | 0 |
| confirm | swap | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 18/48 | 48 | 0 |
| confirm | swap | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 38/48 | 48 | 0 |

## Grenzen

- Format- und Abbruchfehler zählen nach ausdrücklicher Nutzerfreigabe als falsch, auch bei Auswahl und Bestätigung. Score misst Aufgabenleistung einschließlich Formattreue; Fehlerzahlen separat ausgewiesen. Keine Wiederholung oder nachträgliche Extraktion ungültiger Antworten.
- Entwicklung: drei verschiedene Strukturgruppen je Aufgabe/Zelle; explorativ, keine verlässlichen Zellintervalle.
- Bestätigung: 24 neue Gruppen je ausgewählter Zelle; zwei Rotationen zählen als eine Gruppe. Auswahl und Richtung vor Bestätigungsantworten fixiert.
- Konservative Hoeffding-Intervalle unter der Annahme unabhängiger Gruppen innerhalb jeder Zelle; diese Annahme ist durch eindeutige IDs nicht bewiesen. Zellunterschiede nutzen vereinigte marginale Intervalle ohne Annahme unabhängiger Zellen; Bonferroni für zwei Kontraste (Familienfehler .05).
- Bestätigter praktisch relevanter Unterschied nur bei unterer Intervallgrenze >15 Prozentpunkten. Unklar bedeutet weder Gleichwertigkeit noch kein Effekt.
- N verändert auch Promptlänge und Zufallsniveau 1/N; keine isolierte Gedächtnisgrenze. K=R+D; D-Ereignisse ändern den Besitzer des Zielobjekts nicht.
- BBH: dieselben 45 Originalfragen, Chat-3shot-JSON-Generation. Keine native acc_norm, kein vollständiger BBH-Score. Generator 0-shot separat.
- Strukturelle Frische gilt relativ zu den eingefrorenen Ausschlüssen; unbekannte Trainingsdaten und interne Anbieterpräzision bleiben unbeobachtet.
- Kostenannahme: freigegebene UTF8-Bytes plus 4096 Hülltokens, kein zertifizierter Tokenizer-Bound. Fehlende Beobachtungen bleiben unbekannt.

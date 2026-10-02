# Luna / Sonnet: N/R/D-Vergleich

[Dashboard](index.html) · [JSON](results.json) · [CSV](results.csv)

N = Personen/Objekte; R = Besitzwechsel des Zielobjekts; D = andere Ereignisse; K = R+D. Beispiel N=7/R=8/D=16: sieben Personen, acht relevante Wechsel und 16 andere Ereignisse, insgesamt K=24. N ist keine Stichprobengroesse, R kein internes Reasoning.

Audit: PASS. Kosten: 0.1449852 USD neu; 1.601828550 USD kumuliert / 4 USD.

## Bestaetigung

Keine gemessene Bestaetigung; siehe Auswahl und Phasenstatus im JSON.

## Zellen (Aufgaben und Phasen getrennt)

| Phase | Aufgabe | Modell | N | R | D | K | Korrekt / geplant | Beobachtet |
|---|---|---|---:|---:|---:|---:|---:|---:|
| gate | swap | openai/gpt-6-luna | 3 | 0 | 0 | 0 | 2/2 | 2 |
| gate | swap | anthropic/claude-sonnet-5 | 3 | 0 | 0 | 0 | 2/2 | 2 |
| bbh | bbh_swap | openai/gpt-6-luna | 5 | None | None | 5 | 4/15 | 15 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 5 | None | None | 5 | 7/15 | 15 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 7 | None | None | 7 | 9/15 | 15 |
| bbh | bbh_swap | openai/gpt-6-luna | 7 | None | None | 7 | 3/15 | 15 |
| bbh | bbh_swap | openai/gpt-6-luna | 3 | None | None | 3 | 6/15 | 15 |
| bbh | bbh_swap | anthropic/claude-sonnet-5 | 3 | None | None | 3 | 8/15 | 15 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 0 | 4 | 2/6 | 2 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 0 | 4 | 2/6 | 2 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 8 | 24 | 2/6 | 2 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 8 | 24 | 0/6 | 2 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 16 | 32 | 2/6 | 2 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 16 | 32 | 2/6 | 2 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 16 | 20 | 2/6 | 2 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 16 | 20 | 2/6 | 2 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 16 | 32 | 0/6 | 1 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 16 | 32 | 1/6 | 2 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 8 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 8 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 8 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 8 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 16 | 32 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 16 | 8 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 16 | 16 | 32 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 16 | 32 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 16 | 32 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 4 | 8 | 12 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 16 | 32 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 8 | 0 | 8 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 16 | 8 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 16 | 32 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 16 | 16 | 0 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 16 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 8 | 12 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 3 | 4 | 0 | 4 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 3 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 32 | 8 | 8 | 16 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 32 | 8 | 8 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 3 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 3 | 16 | 0 | 16 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 7 | 4 | 16 | 20 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 7 | 4 | 16 | 20 | 0/6 | 0 |
| develop | handoff | anthropic/claude-sonnet-5 | 7 | 8 | 16 | 24 | 0/6 | 0 |
| develop | handoff | openai/gpt-6-luna | 7 | 8 | 16 | 24 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 32 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 32 | 4 | 0 | 4 | 0/6 | 0 |
| develop | swap | anthropic/claude-sonnet-5 | 16 | 8 | 0 | 8 | 0/6 | 0 |
| develop | swap | openai/gpt-6-luna | 16 | 8 | 0 | 8 | 0/6 | 0 |

## Grenzen

- Entwicklung: drei unabhängige Gruppen je Aufgabe/Zelle; explorativ, keine verlässlichen Zellintervalle.
- Bestätigung: 24 neue Gruppen je ausgewählter Zelle; zwei Rotationen zählen als eine Gruppe. Auswahl und Richtung vor Bestätigungsantworten fixiert.
- Konservative Hoeffding-Intervalle unter der Annahme unabhängiger Gruppen innerhalb jeder Zelle; diese Annahme ist durch eindeutige IDs nicht bewiesen. Zellunterschiede nutzen vereinigte marginale Intervalle ohne Annahme unabhängiger Zellen; Bonferroni für zwei Kontraste (Familienfehler .05).
- Bestätigter praktisch relevanter Unterschied nur bei unterer Intervallgrenze >15 Prozentpunkten. Unklar bedeutet weder Gleichwertigkeit noch kein Effekt.
- N verändert auch Promptlänge und Zufallsniveau 1/N; keine isolierte Gedächtnisgrenze. K=R+D; D-Ereignisse ändern den Besitzer des Zielobjekts nicht.
- BBH: dieselben 45 Originalfragen, Chat-3shot-JSON-Generation. Keine native acc_norm, kein vollständiger BBH-Score. Generator 0-shot separat.
- Strukturelle Frische gilt relativ zu den eingefrorenen Ausschlüssen; unbekannte Trainingsdaten und interne Anbieterpräzision bleiben unbeobachtet.
- Kostenannahme: freigegebene UTF8-Bytes plus 4096 Hülltokens, kein zertifizierter Tokenizer-Bound. Fehlende Beobachtungen bleiben unbekannt.

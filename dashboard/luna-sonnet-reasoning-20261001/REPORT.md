# Reasoning low: gepaarter Swap-Vergleich

[Dashboard](index.html) · [Zellen](cells.csv) · [Gruppen](groups.csv) · [BBH](bbh.csv)

Herkunft: live. Audit PASS; neue Kosten 1.4003303 / 5 USD.

Off: historische Antworten derselben ausgewählten Fälle, 256 Tokens. Low: neue Antworten, 2048 Tokens inklusive Reasoning. Drei Gruppen je Zelle, zwei Antwortanordnungen. Fehlversuche gehen in den Tokenverbrauch ein. Bei null richtigen Antworten sind Tokens/Kosten pro richtiger Antwort nicht definiert. Unvollständige Messpunkte bleiben unbekannt.

| Phase | Modell | Effort | Richtig/geplant | Reasoning-Tokens gesamt | Ausgabetokens/richtige Antwort |
|---|---|---|---:|---:|---:|
| bbh | anthropic/claude-sonnet-5 | low | 45/45 | 7104 | 170.88888888888889 |
| bbh | anthropic/claude-sonnet-5 | off | 20/45 | 0 | 27.5 |
| bbh | openai/gpt-6-luna | low | 40/45 | 3778 | 113.575 |
| bbh | openai/gpt-6-luna | off | 10/45 | 0 | 67.5 |
| confirm | anthropic/claude-sonnet-5 | low | 214/216 | 68891 | 335.3644859813084 |
| confirm | anthropic/claude-sonnet-5 | off | 62/216 | 0 | 43.58064516129032 |
| confirm | openai/gpt-6-luna | low | 196/216 | 31066 | 175.3673469387755 |
| confirm | openai/gpt-6-luna | off | 40/216 | 0 | 72.4 |
| gate | anthropic/claude-sonnet-5 | low | 2/2 | 0 | 11.0 |
| gate | anthropic/claude-sonnet-5 | off | 2/2 | 0 | 10.0 |
| gate | openai/gpt-6-luna | low | 2/2 | 30 | 30.0 |
| gate | openai/gpt-6-luna | off | 2/2 | 0 | 13.0 |

BBH ist eine separate Referenz aus 45 Originalfragen, Chat-3shot/JSON-Generation, keine native acc_norm.

Historical paired baseline uses 256 output tokens, low uses 2048 including reasoning; this measures deployed configurations, not an isolated causal reasoning effect.
Provider low labels and tokenizers are not guaranteed equivalent compute. Zero reported reasoning is allowed; missing usage is never interpreted as zero.
No retries. Format/completion failures count false. Technical/unknown-cost failures stop. Unobserved measurements remain unknown.

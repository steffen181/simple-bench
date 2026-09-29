# Historical context

The extraction follows a research sequence: generated-answer BBH bridge; correction to native full-continuation scoring; API first-token proxy; local protocol pilot and compact-model comparison; a development-only generation study; and a completed native-likelihood confirmation study. The earlier protocols answer different questions and must not be pooled into one leaderboard column.

`historical-summary.json` retains only selected counts from the completed 2026-09-29 confirmation report, with the source report hash. These are historical research results, not new package-validation measurements. The archived source report is not distributed here, and its hash does not independently reproduce its underlying inference.

| Model | Original N3 | Original N5 | Original N7 | Fresh N5/7 | Matched anchors |
|---|---:|---:|---:|---:|---:|
| Phi-4-mini-instruct | 79/250 | 42/250 | 47/250 | 22/96 | 16/96 |
| Qwen2.5-7B-Instruct | 66/250 | 52/250 | 42/250 | 18/96 | 22/96 |

All entries use the pinned native raw-three-shot/full-continuation metric with NF4/double-quant/BF16-compute. Fresh and anchor presentations represent 48 paired structures, two option orders each, not 96 independent groups. Their archived primary difference intervals include zero; these counts do not prove generated tasks equivalent to BBH or validate a hypothesis. The three tracking configurations are not full BBH.

Phi revision: `cfbefacb99257ffa30c83adab238a50856ac3083`; Qwen revision: `a09a35458c702b33eeacc393d103063234e8bc28`. Quantization, prompt and revision are part of the measurement. Separate CoT conditions in the research archive are not interchangeable with these scores.

`source-map.json` identifies copied benchmark code and tests. `migration-inventory.json` maps dated scripts to portable facilities or archive-dependent APIs. Historical canonical IDs exclude known structures without bundling private run metadata, raw API responses or billing records.

# Extraction scope

All Python helper modules from `src/layercast_lab/benchmark` are copied under `tracking_bench`, with namespace substitutions. The former historical CLI is replaced by the portable CLI. New modules are `ladder.py`, `reference.py` and `cli.py`; report grouping also retains entity count and relevant updates. Original research files remain unchanged. Per-file original and extracted hashes are in `research/source-map.json`.

| Area | Included / public entry point |
|---|---|
| Generation, parsing, structural solving and canonicalization | `ladder`, `structure`, `dense`, `corpus`, `scoring`; CLI generate |
| API routing, costs, freezing and replay | `openrouter`, `budget`, `run`, `report`; CLI catalog/prepare/run/verify/report |
| Original BBH and full-choice scoring | `bbh`, `bbh_mc`, new `reference`; CLI fetch-bbh/export-bbh/score-native |
| Token logprobs | `bbh_likelihood`; CLI score-token, programmatic request/attempt/decision/summarize |
| Historical study design and grouped analyses | `bbh_protocol_pilot`, `bbh_compact`, `bbh_fresh`, `bbh_likelihood_confirmation`, `confirmation` |
| Historical orchestration/publication helpers | `campaign`, `series`, `history`, `publication`; archive-dependent APIs retained |

Some historical helpers accept or refer to `verification/...` data from the research project. They are included as research APIs, not advertised as self-contained public workflows. Importing the package or using its documented CLI does not require those directories. The `analysis` extra supplies NumPy for analyses that need it. The dated scripts are inventoried with hashes in `research/migration-inventory.json`; their machine paths, account credit calls and frozen study assumptions are not promoted to runnable release commands.

Selected structural, dense, transport, token and confirmation tests were ported. Two test functions requiring the private historical execution context are excluded: `test_real_catalog_missing_request_price_is_guarded_by_zero_fee_cap` and `test_campaign_freeze_probe_run_and_replay`. Their underlying portable transport/scoring helpers remain covered, but this release does not claim those two campaign integrations were rerun.

Not included: Stage1/legacy/activation research, model weights, caches, local editor settings, credentials, account ledgers, raw paid API responses, the original full question datasets, and sealed historical run directories. A curated historical count summary provides context without implying those historical inference runs can be reproduced from this lightweight package alone.

The original project-wide all-results report remains in the research archive; it is not copied with broken private links. Native scoring, first-token proxy and generation results remain separate protocols in the public documentation.

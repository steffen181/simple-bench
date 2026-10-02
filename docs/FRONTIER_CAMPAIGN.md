# Luna / Sonnet campaign

The executable plan and design are in `docs/superpowers/plans/2026-09-29-luna-sonnet-campaign.md` and the matching specs directory. This document records implementation decisions and operation.

- Models: `openai/gpt-6-luna` / route `openai`, `anthropic/claude-sonnet-5` / route `anthropic`. No fallback providers, tools, reasoning, temperature/top-p override or API seed; both have the same visible 32-token budget and question text. Provider precision is unknown. Explicit zero reasoning tokens are required, not just an omitted reasoning field.
- Gate: eight diagnostic calls (zero-/one-event tasks), all must pass. Smoke: up to nine N levels at 32 events and 16 relevant updates; two groups per task, two rotations, both models. If both models still perform well at N=64, separate K=64/128 levels may follow. Discovery thresholds are 75% accuracy and a 20-point loss from a good N=3 baseline, on two neighboring complete stages. Low baselines, format failures and incomplete stages do not prove a boundary.
- Confirmation: the union of both model neighborhoods plus baseline, at most seven cells. Three fresh seeds, two groups per seed/task, two rotations: **12 groups / 24 answers per model per cell**. The entire population is written and hashed before the first confirmation request. Excludes all gate/smoke groups. If budget interrupts, future planned cases remain in the public denominator/coverage. Missing observations are not factual wrong answers; accuracy/all-planned is a lower bound in partially observed cells.
- BBH: fixed random original subset, 15 questions at each N=3/5/7, no optional fresh BBH extension in this $4 run. Same three original demonstrations inside a single user prompt and an explicit parenthesized-option instruction for both models. This is chat generation accuracy, **not** native HF `acc_norm`. No advertised logprobs on either selected route.

## Accounting

Global cap 4 USD; work cap 3.75 USD. Scope caps: gate .15, smoke .60, BBH .60, confirmation 2.40. The remaining .25 is not extra experimentation allowance. All attempts, including errors, are charged to one ledger. Cost, identity and reasoning checks happen after every call. Unknown costs/timeouts retain their reservation and halt execution; no automatic retries or resumes. Model pairs are budget-checked together before a case, then calls execute serially. A technical failure can leave a pair incomplete; that is shown explicitly.

OpenRouter's attempted token-count endpoint returned 404. The user therefore explicitly accepted the alternative in `examples/frontier-config.json`: assume no more than one token per UTF-8 byte of prompt plus 4,096 tokens for its private chat envelope. Reserve against maximum reported input/cache rates, tier overrides and 32 output tokens. This is a conservative **assumption**, not a certified token count; it is recorded in each quote and the dashboard. Reported usage or cost beyond it halts the ledger. `accept_input_bound_assumption` must be true for a live freeze. The complete context limit is preserved, never spoofed to obtain a cheaper quote.

The fixed minimum population is planned before responses are seen. The reservation system checks each pair, not the sum of all speculative envelope allowances for an entire campaign. The consequence is possible incomplete coverage if actual billing is higher than expected; outcome-based sample resizing is forbidden.

## Evidence and public export

Protocol/source hashes freeze at creation. Blocks seal cases, schedules, requests, responses, receipts and summaries. Audit re-creates requests, quotes and scores and reconciles every attempt with the ledger. Code changes after freeze prevent further execution; generate a new campaign if code genuinely must change, account for any previous paid spend and do not reuse exposure as fresh confirmation.

Dashboard data contain four explicit aggregation views (task-specific/all × seed-specific/all); do not sum overlapping views. Choose one view for totals. Bootstrap resamples independent structure groups, keeping rotations and both models together, stratified by seed/task. Intervals are pointwise 95%, not adjusted for adaptive selection or all displayed comparisons. BBH question groups with single original presentations have no option-rotation statistic.

Local raw files stay in ignored `runs/`; public dashboard exports include aggregate counts, route/model conditions, cost totals, CSV, report and checksums. No API keys, account credit balances, provider request IDs or secret paths are exported. HTML escapes data before embedding it; no external script/CDN is used.

Disabled reasoning is an API mode verified from reported reasoning tokens. It does not guarantee that visible answer text contains no explanation. Under the fixed 32-token answer budget, a model may produce a truncated explanation without an answer; this is reported as a format/budget failure, not an identified reasoning-capacity boundary. Do not increase this budget after observing smoke answers within the same frozen protocol.


BBH original questions can share one canonical structure. They remain clustered for uncertainty estimates, but are not option rotations of one generated case. The accuracy estimand is question-weighted: resample whole groups and carry each group's question count into the bootstrap mean. Generated two-rotation groups have equal size. Provider `finish_reason=length` is reported separately from the frozen parser's status; BBH's emulated original stop sequence can classify a length-ended response as unsupported rather than truncated.

# Factorial N/R/D comparison: frozen development and confirmation

This is the approved follow-up to the structured N-only comparison. The estimand is accuracy on freshly generated structure groups under a fixed closed-model protocol, separately for swap and handoff. Competing explanations include task type, relevant state changes, distractor events, prompt length, answer-order sensitivity and sampling noise. An observed N effect alone is not an isolated memory-capacity measurement.

## Axes and population

| Factor | Values | Meaning |
|---|---|---|
| N | 3, 7, 16, 32 | People, initial objects and candidate answers |
| R | 4, 8, 16 | Events changing the queried object's owner |
| D | 0, 8, 16 | Other events, not changing that owner |
| K | R+D | Total events; initial assignment and demonstrations excluded |

All 36 combinations cross swap/handoff. Three structure groups per task/cell, one each from seeds 20261211/12/13, each in two option rotations: 216 groups, 432 presentations, 864 model calls. Group blocks are shuffled in advance; model order alternates within paired presentations. Four reused zero-event control calls and 90 calls on the same 45 pinned original BBH questions precede the grid: **958 development calls**.

BBH stays a separate chat-3shot / strict JSON generation reference; generated cases are 0-shot. These are not native `acc_norm` or an aggregate BBH score. Both direct routes remain GPT-6 Luna and Claude Sonnet 5, strict answer-only JSON schema, 256 tokens, explicit API reasoning off, provider sampling defaults, no API seed or fallback. Private provider precision is unknown.

## Confirmation bank before inference

Historical exclusions cover the packaged history, prior original campaign and structured comparison, using canonical and legacy IDs. All development groups are excluded before generating the confirmation bank. The complete bank and eligibility list are hash-bound before the first development model response; no confirmation responses exist during selection.

Each eligible task/cell has 24 independent new groups (8 per seed 20261221/22/23), each with two rotations. Eight task/cells at R=4/D=0 have insufficient distinct fresh structures for this target; these remain in development, but are ineligible for confirmation selection. Renaming or repeating a structure does not create additional independent groups. The other 64 task/cells have full banks. Only selected banks are sent to models.

## Frozen selection

Only complete, accepted development cells with sufficient precomputed confirmation support qualify. Selection requires the complete development round, avoiding order-dependent selection after a budget stop.

1. **Performance loss:** the largest model-specific accuracy decrease of at least 15 percentage points across adjacent grid values differing in exactly one of N, R or D. The easier cell must have accuracy at least 75%.
2. **Model gap:** the largest absolute accuracy difference of at least 15 percentage points on the same task/cell. The comparison direction (winner minus other model) is fixed from development.

One contrast of each kind at most. Exact correct/planned fractions govern comparisons and thresholds. Ties use task/N/R/D, then model and axis; no floating-point tie ambiguity. Selection is sealed and independently recomputed by the audit. No eligible contrast is reported explicitly rather than replaced by an outcome-driven alternative.

The union contains at most three task/cells, up to 72 groups / 144 presentations / **288 confirmation calls**. Confirmation measures their precomputed fresh cases once. Neither selection nor the protocol changes in response to those outcomes.

## Inference and what this budget can establish

Each structure contributes its average correctness over two rotations. For model gaps, subtract the two model scores within that group. For performance losses, subtract the group means of the two cells for the selected model. Tasks are never pooled into the primary contrast.

Two-sided Hoeffding bounds for bounded group outcomes, with Bonferroni for two preplanned contrasts, target a family error rate of .05 under independent group sampling. With L=ln(80), the half-width is sqrt(2L/n) for paired model differences in [-1,1], or the sum sqrt(ln(160)/(2*n_easy)) + sqrt(ln(160)/(2*n_hard)) for a difference of cell means in [0,1]. The latter unions two marginal cell bounds, allowing arbitrary dependence between cells. Bounds are clipped to [-1,1]. At n=24, these are about 60.4 and 65.0 percentage points respectively: conservative, deliberately nonzero even for constant samples.

A practically relevant gap is confirmed only if the lower interval bound exceeds 15 percentage points. An upper bound below that threshold indicates an effect below the prespecified practical threshold; otherwise the result is inconclusive. Incomplete confirmation remains unknown. This budget does not promise precise validation of a 15-point effect. Three-group pilot cells carry no inferential intervals, and their largest observed differences are selection evidence only.

## Budget and stops

Audited previous spend: **1.456843350 USD**, zero reserved. Development cap **1.40 USD** (gate .03, BBH .17, grid 1.20); confirmation cap **.89 USD**, also checked against remaining cumulative capacity. Maximum planned cumulative allocation: **3.746843350 USD**, preserving the original .25 USD reserve within the $4 authorization.

The empirical development forecast is approximately 1.343 USD including 25% buffer, based on prior billed dollars per request byte under the same structured protocol. This is not a bound; a worst-tariff forecast is higher than the allocation. Each model pair still requires capacity for both conservative quotes before either call, with separate request reservations using the accepted UTF8-byte/4096-envelope assumption and maximum rates. Actual bills determine subsequent capacity. Full completion is not guaranteed. Stop on unknown charges, quote violations, nonzero/unknown reasoning, identity/technical failures, schema/length errors or incorrect zero-event control. No automatic retries.

Prior ledgers are independently totalled, must be settled, are hash-bound and cannot appear twice. All planned observations remain represented after stops. Partial heatmap cells show unknown, retaining observed/planned counts; they are not displayed as measured low accuracy.

## Commands and artifacts

```bash
tracking-bench factorial freeze runs/factorial-comparison-20260930 --prior runs/structured-comparison-20260930
tracking-bench factorial run runs/factorial-comparison-20260930 --stage development --key-file /outside/repo/openrouter.env.txt
tracking-bench factorial select runs/factorial-comparison-20260930
tracking-bench factorial freeze-confirmation runs/factorial-comparison-20260930
tracking-bench factorial run runs/factorial-comparison-20260930 --stage confirmation --key-file /outside/repo/openrouter.env.txt
tracking-bench factorial audit runs/factorial-comparison-20260930
tracking-bench factorial export runs/factorial-comparison-20260930 --out dashboard/luna-sonnet-factorial-20260930
```

Each run and output directory is single-use. `freeze` needs the local audited predecessor artifacts and downloads current route metadata, not model weights. Requests, responses, receipts, raw ledgers and the unused confirmation bank stay local. The public export contains aggregates, selection, inference, protocol hash and limitations. Its N-by-R grid has D/task/phase/model filters and a paired model-difference view; BBH is separate.

Offline verification before inference: **122 tests passed**; a full 958-call development + 192-call selected confirmation fixture passed semantic replay, and both complete and partial dashboards passed cached Chromium checks. Those synthetic fixture scores are not model evidence. Independent review identified exact tie-breaking and incomplete-cell display defects; failing regressions preceded both fixes and the fixes passed re-review.


## Prospective inference correction before confirmation

An additional independent mathematical review identified that resetting identical generator seeds across cells can couple their samples. The initially specified drop interval assumed independent cells; that assumption is not justified by canonical uniqueness. Before any confirmation response, an immutable local `inference-amendment.json` records the wider union-of-marginal-bounds formula above. It leaves the selection rule, sample bank, practical threshold and paired model-gap formula unchanged. Within-cell independent-group sampling remains an assumption, not a verified property. The amendment is hash-bound into any subsequent confirmation freeze.

## Approved format-error continuation (2026-09-30)

The original development segment stopped after 113 of 958 requests: a technically valid Luna response contained explanation before its JSON answer. The user explicitly approved continuing and counting these responses as wrong: “ja trotzdem fortsetzen und als falsch ausweisen.”

The stopped segment remains immutable. `freeze-continuation` binds its seal and exact offset, retains every original request hash, and freezes only the remaining 845 requests in a separate directory. The first remaining request completes the interrupted model pair; no response is retried. The continuation receives the original unused development and phase allocations, and every prior ledger is counted exactly once. Unknown costs, technical/identity/reasoning failures and bound violations still stop execution.

Under the hash-bound `format-policy-amendment.json`, strict schema or completion failures count zero in both development selection and fresh confirmation. Complete technically valid cells remain eligible; selection thresholds, ties, cases, seeds, routes, prompts, 256-token cap, fresh bank and statistical intervals stay unchanged. Primary accuracy includes format compliance; invalid JSON and truncations are shown separately. This policy was changed after one observed format failure and before all confirmation outcomes, rather than being part of the initial preregistration.

```bash
tracking-bench factorial freeze-continuation runs/factorial-comparison-20260930
tracking-bench factorial run runs/factorial-comparison-20260930 --stage continuation --key-file /outside/repo/openrouter.env.txt
tracking-bench factorial select runs/factorial-comparison-20260930
tracking-bench factorial freeze-confirmation runs/factorial-comparison-20260930
tracking-bench factorial run runs/factorial-comparison-20260930 --stage confirmation --key-file /outside/repo/openrouter.env.txt
tracking-bench factorial audit runs/factorial-comparison-20260930
tracking-bench factorial export runs/factorial-comparison-20260930 --out dashboard/luna-sonnet-factorial-20260930
```

Selection requires full original development coverage across both segments. Missing observations are never silently changed into wrong answers. The public audit retains the original STOPPED segment and separately reports completion of the combined study.


## Descriptive presentation (2026-10-01)

At the user's request, the dashboard now prioritizes an understandable observational benchmark: accuracy, all measured structure-group scores, their observed range, paired differences, answer-order stability through the paired values, and separate format failures. Each group contains two rotations; complete group scores are 0/0.5/1. Incomplete or technically failed groups remain unknown. Format failures still count zero. The range describes measured heterogeneity, not confidence about a population mean or variability from repeated identical API calls.

The pilot and additional fresh cases stay separate and the outcome-based selection of the additional cells stays explicit. The original formal inference and thresholds remain unchanged in the methods appendix. No model calls, raw artifacts, selections or scientific scores were changed. `factorial export` includes `descriptive` in JSON and a new `groups.csv`. The descriptive delivery is `dashboard/luna-sonnet-descriptive-20261001`; the previous index links there, and its original formal page is preserved as `index-formal.html`.

# Reproduction and verification

```bash
python -m pip install -e '.[dev]'
pytest -q
tracking-bench demo --out runs/offline-check
tracking-bench verify runs/offline-check/run
python -m build
```

Tests are offline. Transport tests use a local HTTP server, not paid inference. They exercise structural canonicalization, dense task rendering, parser behavior, cost/routing controls, raw token probability checks, native scoring and confirmation helpers, the portable CLI, exclusion/rotation/relevance invariants, source provenance, report strata and bundle relocation.

The source provenance map records original files and changes. The two removed archival test functions required a real historical provider catalog or dated campaign scripts; they are listed in [MIGRATION.md](MIGRATION.md). No optional live integration is advertised as newly tested.

For a release, build the wheel and source archive, extract to a directory outside the research checkout, install the wheel into a clean virtual environment, run the full tests against the installed package, run the offline demo, verify native export/score imports and scan distribution contents for private paths and credentials. Use the release artifact's SHA256 inventory to verify the download. CI checks offline tests and wheel installation; it does not validate current external service behavior or model quality.

Hash seals detect changes relative to a trusted manifest; they are not cryptographic signatures or independent proof of provenance. Preserve the original release hashes independently. `COMPLETE` denotes infrastructure completion, never confirmation of a scientific hypothesis.


## Campaign extension verification (2026-09-29)

`pytest -q`: 83 passed (25.79 s), offline. Added tests cover the scalable v2 generator, route/reasoning/cost contracts, frozen campaign execution, malformed provider responses, strict neighboring-level selection, signed model differences, full planned denominators after budget stops, and frozen-population binding. The full offline fixture reaches N=64 and the separate K=64/128 stress cells; these fixture scores are not model evidence.

Wheel and source archive build succeeded. A clean virtual environment installed the wheel with the optional campaign dependency; the installed CLI generated N=64/K=128 cases and ran the offline demo. Cached Chromium verified dashboard rendering, task/model/seed/phase filters, console errors, and incomplete/malformed-run displays. No browser or model weights were downloaded. Pinned original BBH inputs were checked and the 45-question reference subset validated.

An independent agent review found three important defects (model-difference sign, malformed-usage handling, skipped-level boundary detection); five failing regression cases reproduced them before fixes. Further coverage/provenance and dashboard filter issues were also addressed. Live model measurements are separately reported in the campaign dashboard; offline tests do not establish provider behavior.

After paid execution, three additional reporting regressions passed: BBH originals are not option rotations, unequal group sizes preserve question weighting, and provider token-limit endings stay visible independently of parser status. Final suite: **86 passed in 22.80 s**. Execution audit: **434 calls, PASS**, 0.5169024 USD spent, zero reserved. Before/after reporting comparison confirmed unchanged counts, accuracy, coverage, parser status, reasoning evidence and costs. Analysis source hash is recorded separately from the frozen execution protocol.


## Structured-output feasibility probe (2026-09-30)

Eleven isolated offline tests passed, plus a complete 64-call simulated run and a malformed-response stop with a retained reservation. Actual paid probe: **64/64 calls, audit PASS**, explicit reasoning-off evidence for every response, **0.1105429 USD** spent, zero reserved. Paired prompts differ only in the schema request parameter at each fixed model/budget. The prior campaign ledger and dashboard files remain unchanged. Combined measured cost: 0.6274453 USD. The archived scripts are a disposable diagnostic; no benchmark runtime module was changed. See the [report and reproducible checks](../research/structured-output-smoke-20260930/REPORT.md).

## Fresh structured comparison (2026-09-30)

`pytest -q`: **110 passed in 45.73 s**, offline. The structured runner freezes its complete population and paired schedule before execution, excludes supplied historical and control structures, validates strict JSON answers, accounts for prior paid runs, and retains all planned observations after stops. Its full 534-call offline fixture includes the 45-question BBH reference and reaches N=64; fixture correctness is not model evidence.

An independent agent review reproduced a missing semantic stop check in the audit. Four negative tests failed before the correction: continuation after invalid JSON, token-limit termination, wrong zero-event answers or nonzero reasoning. Audit now derives mandatory stops from responses, reconciles settlement and ledger halt evidence, verifies summary reasons and rejects prohibited continuation. Runtime tests also verify that valid but wrong nontrivial control answers do not stop the study. The independent re-review passed 24 focused tests with no remaining Critical/Important findings in the reviewed scope. The Python `freeze()` API assumes audited prior-spend inputs; the CLI establishes that precondition through predecessor audits.

Cached Chromium passed the full-fixture dashboard checks: 18 main aggregate rows, 432/432 simulated main answers, separate 90-answer BBH panel, model/task/seed filters, 256-token and strict-JSON conditions, cumulative cost labeling, and no page errors. No browser download was needed. Paid results and final delivery checks are recorded separately below.

Paid execution: **534/534 calls, audit PASS**, all phases complete, 534 accepted schema/completion scores, zero output-limit endings and explicit zero API reasoning tokens throughout. New spend **0.829398050 USD**, cumulative **1.456843350 USD**, zero reserved. Public live-dashboard Chromium checks passed with all 18 main rows, complete coverage and working filters; no page errors. Prior public artifact hashes and both budget hashes remain unchanged. Re-analysis reproduces the prior campaign's 244 cells and 122 paired comparisons numerically, including intervals. Results: [report](RESULTS_STRUCTURED_COMPARISON_20260930.md) and [dashboard](../dashboard/luna-sonnet-structured-20260930/index.html).

## Factorial extension (2026-09-30)

Final offline regression: **123 passed in 51.32 s**. Tests cover all 36 N/R/D combinations, canonical freshness, ledger-derived prior spending, duplicate/unsettled priors, phase/cap replay, support eligibility, exact-count lexical ties, one-axis selection, unknown partial coverage and nonzero conservative intervals. A full 958-call development and 192-call selected confirmation fixture passed replay; synthetic scores are not model evidence. Cached Chromium verified N/R/D and model/task/phase filters, BBH rows, mobile layout and a partially observed cell displaying unknown.

Independent review identified and reproduced float tie-breaking and partial-coverage display defects; failing regressions preceded fixes. An additional mathematical review identified cross-cell dependence from resetting seeds. The performance-drop interval now unions two marginal bounds, recorded prospectively before any real confirmation response. This does not establish within-cell independence; that remains an explicit assumption.

Actual live development: **113/958 calls, STOPPED, audit PASS**. One Luna schema violation triggered the prespecified stop; 4/4 controls and 90/90 BBH calls completed, grid 19/864. No automatic retry, selection or confirmation. Spent 0.1449852 USD, cumulative 1.601828550 USD, zero reserved. [Results and limits](RESULTS_FACTORIAL_COMPARISON_20260930.md).

## Explicit format-error continuation (2026-10-01)

The user approved continuing after strict JSON failure and counting format/completion failures as wrong. New regression tests first failed for the missing continuation/selection behavior, then passed. The new suffix protocol binds the original seal and exact remaining schedule; original raw artifacts are untouched. Residual global and phase caps preserve the original allocations. Technical failures still stop, and missing observations remain unknown.

Independent review found two audit edge cases: a continuation of another parent could be merged, and a technical failure on the final response could leave its phase marked complete. Both were reproduced by failing tests, fixed and re-reviewed. No further important findings in the reviewed scope; the reviewer inspected tests but did not run them independently.

Final local suite: **128 passed in 60.77 s**. Installed-wheel suite outside the checkout: **128 passed in 54.96 s**. A complete 958-observation development fixture split across stopped/continuation segments, followed by 192 fresh confirmation calls, passed semantic replay and format-error-as-zero selection/inference. These simulated outcomes are not model evidence. The first offline integration attempt was interrupted by a source-hash change during review fixes; the preserved v2 run completed with a stable source tree. An initial build without isolation failed because local setuptools/wheel did not satisfy pyproject requirements; the isolated wheel/source build succeeded. Cached Chromium verified the updated dashboard filters, separate BBH panel and mobile layout with no page errors or browser download.

Paid completion: **958/958 development observations** (113 preserved + 845 suffix, no retries) and **192/192 fresh confirmation calls**, semantic audit PASS. 1,148 accepted answers and two invalid JSON answers, both Luna and scored false; zero confirmation format failures, zero token-limit endings, explicit zero API reasoning tokens for every response. Selection replay and confirmation-bank binding passed. Both selected contrasts are INCONCLUSIVE under the frozen conservative intervals. Development cost 1.0761673 USD; confirmation 0.3064964 USD; cumulative all-run total **2.839507050 USD**, zero reserved. The original stopped segment seal and all older dashboard manifests remain verifiable. Final live dashboard checks passed in cached Chromium. See [results](RESULTS_FACTORIAL_COMPARISON_20260930.md).


## Descriptive dashboard (2026-10-01)

**132 tests passed in 56.93 s.** New regressions cover rotation-group scores, exact paired differences, reversed-record order, incomplete/technical observations, phase separation and group export. Independent review reproduced numeric accuracy from a final technical failure and a missing fixture label; both were fixed and re-reviewed. The reviewer independently ran the six focused descriptive/export tests successfully.

Cached Chromium exercised all filters, three pilot groups and 24 additional groups per model, paired values, the two Luna format failures, missing cells, technical partial coverage, the closed formal-methods panel and visible offline-fixture labels. No page errors, horizontal page overflow at 390 pixels, remote requests or new model calls. A visual desktop inspection also passed. Every pre-existing JSON field matches the prior completed live export exactly; only descriptive group data were added (528 model/group rows, 148 model/cells and 74 paired cells). Original raw seals and budget ledgers remain unchanged.

## Fresh swap curves (2026-10-01)

Pre-execution full regression: **134 passed in 152.33 s**. The new fixture executes 1,300 requests (full swap grid plus controls; no BBH in this isolated fixture), then replays new-budget accounting, all 36 cells, nine groups per cell and paired rotations. The live population adds the 45-question BBH reference for 1,390 requests. Current public route metadata and account credit were checked before freeze; the latter is not an inference measurement.

Independent review checked the new budget separation, fixed request conditions, canonical/legacy exclusions, balanced rounds and semantic replay. The reviewer independently passed the two focused campaign tests in 93.46 s. Report references to the old pilot, missing Markdown fixture labeling and category-spaced curve axes were corrected; re-review found no important open findings. The first local fixture run was interrupted by source edits during dashboard development; the final full suite ran with stable sources and passed.

Cached Chromium verified numeric N/R/D axes, fixed remaining conditions, point selection opening the correct paired groups, nine groups per model, no handoff/pilot selectors in the new series, mobile width 390 and no page errors or remote requests. Software fixtures are labeled as simulated results, not model evidence. Live execution and delivery results follow after completion.

Paid completion: **1,390/1,390 calls, semantic audit PASS**: controls 4, original BBH reference 90, full fresh swap grid 1,296. All 36 cells contain nine complete paired structure groups; no format errors, output-limit endings or technical failures; explicit zero API reasoning tokens throughout. New spend **1.6177675 USD**, prior spend charged to this new allowance zero, reserved zero. Cached Chromium passed the actual live export: all three numerically spaced axes, fixed conditions, point selection, paired group detail, nine groups per model, mobile layout and no page errors or remote requests. Final integrity validation verified 7,640 sealed files across the new run and previous factorial segments, 29 unchanged older public dashboard files and six dashboard manifests. The source inventory was refreshed and public artifacts were scanned against the external credential without retaining it. See [results](RESULTS_SWAP_CURVES_20261001.md).

## Reasoning effort extension (2026-10-01)

Pre-execution regression: **139 passed in 278.71 s**. New tests cover explicit reasoning-token accounting, rejection of unknown/invalid counts, wrong-answer costs, undefined zero-hit efficiency, exact paired historical selection, source/ledger replay, and preservation of the old reasoning-off contract. A missing phase/pair prefix audit was reproduced by a failing regression, corrected, and independently re-reviewed. The reviewer separately passed four focused tests; no remaining important findings. Browser checks reproduced a currency-axis scaling defect, then verified the correction and final template: N/R/D/effort axes, numeric N spacing, token/cost metrics, three paired groups, mobile width and no JavaScript errors or remote requests. The final tooltip precision-only correction was browser-checked after the full suite. Paid execution follows these checks.

Paid completion on **2026-10-02**: **526/526 calls, audit PASS** (four controls, 90 original BBH references, 432 swap answers); all accepted, no format failures, truncations, technical failures or retries. New cost **1.4003303 USD / 5 USD**, zero reserved. Main reasoning tokens: Luna 31,066; Sonnet 68,891. Main accuracy on the exact matched subset: Luna off 40/216, low 196/216; Sonnet off 62/216, low 214/216. Live Chromium checks passed N/R/D/effort curves, token/cost metrics, paired groups and mobile layout without JavaScript errors or remote requests; desktop visual inspection also passed. Integrity checks verified 5,758 sealed files across the new run and its baseline, all 35 older public dashboard files unchanged, and seven public dashboard manifests. Source hashes refreshed and public files scanned against the external credential without retaining it. [Results, limits and commands](RESULTS_REASONING_EFFORT_20261001.md).

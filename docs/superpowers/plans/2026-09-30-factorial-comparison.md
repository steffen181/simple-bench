# Factorial comparison implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this approved extension in the existing campaign branch. Follow test-driven-development. No new approval gate: the user explicitly requested implementation of the presented design.

**Goal:** Execute a fresh N/R/D development grid, select at most two scientific contrasts by a frozen rule, and measure them on fresh confirmation groups within the original cumulative $4 authorization.

**Architecture:** Reuse the structured request, quote, receipt and semantic audit engine. Parameterize only its frozen cap/scopes and phase names. Add a factorial protocol/selection/analysis module, CLI adapter and separate static dashboard; preserve existing raw runs and exports.

**Tech Stack:** Existing Python package, pytest, standard library, pinned igraph, cached Chromium.

**Spec:** User-approved in-chat design, recorded below as the executable study decisions.

## Global constraints / study decisions

- N=[3,7,16,32], R=[4,8,16], D=[0,8,16], K=R+D; swap/handoff separate. Three development groups per task/cell, one per seed 20261211/12/13; two rotations, both models: 864 main calls. Reused zero-event gate 4 calls; same 45 BBH originals 90 calls: total 958 development calls.
- Same direct GPT-6 Luna / Claude Sonnet 5 routes, strict JSON, 256 tokens, API reasoning off, no retries, unchanged native-BBH caveat. Model order alternates; group blocks shuffled before execution.
- Historical exclusions include original campaign, structured confirmation, packaged history. Confirmation also excludes every development group. Preflight found all 432 development presentations without support failures.
- Previous actual spend 1.456843350 USD. Development cap 1.40: gate .03, BBH .17, development 1.20. Confirmation gets min(.89, 3.75 - all audited spending), leaving at least the original .25 reserve. Priors must be settled and hash-bound. Quotes retain the previously accepted conservative assumption.
- Freeze selection rule before development: one maximum absolute model difference >=.15; one maximum model-specific loss >=.15 over adjacent grid cells differing in only N, R or D, with easier-cell accuracy >=.75. Complete, accepted cells with precomputed capacity for 24 fresh confirmation groups only; lexical ties. The entire confirmation bank and eligibility list are generated and hash-bound before development inference. Model-gap direction is frozen from development. If no eligible contrast, explicitly no candidate; no fabricated confirmation.
- Freeze up to three selected task/cells for confirmation, 24 new groups each (8 per seed 20261221/22/23), two rotations and both models, at most 288 calls. No selection or tuning using confirmation outcomes. If canonical support cannot supply 24 fresh groups, report that contrast not confirmable; do not relabel repeated structures independent.
- Primary confirmation: group-mean accuracy, rotations averaged, paired model difference or independent-cell accuracy loss for the selected model. Conservative two-sided Hoeffding intervals with Bonferroni for two planned contrasts (family alpha .05), clamped to [-1,1]. A practically relevant gap is confirmed only if the lower bound >.15; insufficient coverage/support remains unknown. This bounded-budget study cannot guarantee precision for small gaps. Pilot CIs are omitted: three groups cannot support confirmatory claims.
- BBH originals stay separate chat-3shot generation, generated cases 0-shot. No pooling by task or across phases. All planned rows remain visible after budget/technical stop.

## Review focus

1. Underreported prior spending or duplicate ledger path must be rejected.
2. Selection must ignore missing cells and never cross two axes at once.
3. Constant observed scores must not yield zero-width confirmation intervals.
4. No duplicated canonical group may masquerade as independent confirmation evidence.
5. Dashboard must distinguish cells sharing N/K but differing R/D and preserve unknown coverage.

## Task 1: Frozen multi-stage execution

Files: modify structured_campaign.py; create factorial_campaign.py and tests/test_factorial_campaign.py.
- [x] RED: test the full 36-cell fresh grid, three independent groups/task/cell, historical disjointness, custom phase/cap replay and false prior spend.
- [x] Implement freeze_population(out, cases, contracts, priors, blocked, cap, scopes, design, source_files, mode), development population construction and existing runner parameterization.
- [x] GREEN: focused regression plus existing structured campaign tests.

## Task 2: Selection and confirmation

Files: create factorial_analysis.py; tests/test_factorial_analysis.py; extend factorial_campaign.py.
- [x] RED: model-gap direction, adjacent one-axis loss with good baseline, incomplete exclusion, fresh confirmation and nondegenerate uncertainty.
- [x] Implement select_contrasts(cells), confirmation generation and bounded group inference with two-comparison error control.
- [x] GREEN: include zero candidates, exhausted support and partial observation paths.

## Task 3: CLI, dashboard and delivery

Files: create factorial_cli.py, factorial_dashboard.py, templates/factorial.html; modify cli.py; tests/test_factorial_dashboard.py.
- [x] RED: exported grid keys include N/R/D, unknown cells visible, no secrets/raw responses exported.
- [x] Implement freeze/run/select/confirm/audit/export CLI and N-by-R panels with D/task/model/phase filters; explicit inference status and separate BBH reference.
- [x] Full offline suite; full development/confirmation fixture; fresh independent review before paid calls.
- [x] Freeze and execute development; audit; select; freeze and execute confirmation once; audit and export new local artifacts.
- [x] Browser checks, documentation, hashes, package verification. No publication or commits required.

## Progress

- Preflight: approved full development grid has 432 presentations / 216 groups; no canonical support failures.
- Ruling: use conservative bounded-variable confirmation intervals instead of degenerate small-stratum bootstrap intervals; lower power is explicitly reported.
- Ruling: existing dedicated campaign branch and dirty predecessor work are retained; all new runs have separate directories.

- Ruling: finite canonical support at R=4/D=0 prevents 24 independent confirmation groups. Keep those cells in development, but determine confirmation eligibility before any paid response, without selecting from outcomes.

- Task 1 complete: full grid freshness and custom-cap replay verified. Task 2 complete: exact count selection, support eligibility, conservative intervals. Task 3 implementation complete; live execution in progress.
- Independent review: exact tie ordering and unknown partial-cell heatmap fixed after failing regressions; 122 tests passed in 52.45 s. Full fixture audited and browser checks passed.

- User-approved format continuation: preserved first 113 requests, executed exact remaining 845 once; two invalid JSON responses score zero. Complete development 958 and fresh confirmation 192, audit PASS. Final costs 2.839507050 USD across all prior runs, zero reserved. Both selected contrasts remain INCONCLUSIVE.
- Continuation review fixes: explicit parent/amendment binding and final-response technical-stop phase status; failing regressions preceded fixes and re-review. Local and installed-wheel suites 128 passed; full continuation fixture and final browser checks passed.

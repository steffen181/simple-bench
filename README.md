# Tracking Bench

Generate reproducible object-tracking benchmarks for closed-model APIs, with a separate, pinned BIG-Bench Hard (BBH) comparison track.

**Release candidate 0.1.0 — MIT licensed.** See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md). No model weights or credentials are included.

The benchmark varies the number of people/objects, event count, relevant state updates and answer order. It generates swaps and directed handoffs, solves every case independently and checks the rendered text. Increasing these parameters increases task complexity; whether model accuracy declines is an empirical result.

## Start offline

Python 3.10+ on Linux/macOS (the budget ledger uses POSIX file locking). No GPU is needed.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
tracking-bench demo --out runs/demo
tracking-bench verify runs/demo/run
pytest -q
```

The demo uses an explicitly labelled `offline_fixture` that always answers Alice. It tests generation, execution, receipts, budgets and reporting; its scores are not model evidence. Each output directory is single-use.

## Create a complexity ladder

```bash
mkdir -p data
tracking-bench generate --entities 3 5 7 --steps 4 8 16 32 \
  --per-cell 4 --seed 1101 --out data/development.json
tracking-bench generate --entities 3 5 7 --steps 4 8 16 32 \
  --per-cell 4 --seed 2201 --blocked data/development.json \
  --out data/confirmation.json
```

Each nonzero cell crosses swap/handoff with half/all events relevant to the queried object. Four independent structures per cell, each with two answer orders, produce 384 cases in each example corpus. Confirmatory files must be kept unopened until the development protocol is fixed. The command prevents canonical structure overlap with the supplied development corpus; it does not itself restrict who can inspect the confirmation file.

See [difficulty and splitting](docs/DIFFICULTY.md), [closed-model execution](docs/CLOSED_MODELS.md), and [protocols](docs/PROTOCOLS.md).

## Keep a BBH reference alongside the ladder

```bash
mkdir -p data
tracking-bench fetch-bbh --out data/bbh-sources
tracking-bench export-bbh --sources data/bbh-sources --out data/bbh-comparison
```

`fetch-bbh` explicitly downloads small, hash-pinned task/configuration files. It does not download weights. The export contains all 750 original tracking questions (250 each at N=3/5/7), fresh N=5/7 structures, paired original anchors, rotated options, harness task YAML and full-continuation requests. Default: 48 fresh groups, 942 total cases including references and paired variants. Original question sets are not bundled with this source release.

Three measurement paths remain separate:

| Path | Required capability | Metric / interpretation |
|---|---|---|
| Native BBH | Loglikelihood of every supplied full continuation | Native `acc_norm`, pinned raw three-shot task contract |
| API token likelihood | Exact next-token logprobs with sufficient candidate coverage | First-token proxy; never labelled native `acc_norm` |
| Generated answers | Text-generation API | Parsed answer accuracy and coverage; separate generation protocol |

A text-only closed API cannot supply native BBH `acc_norm`. Run the original reference and generated cases under the same available protocol and label it explicitly. A tracking score is not the aggregate BBH score. See [native export/import](docs/PROTOCOLS.md).

## Included

- Portable CLI; generated corpora; deterministic structural IDs and exclusions.
- OpenRouter generation transport, explicit routing/parameters, conservative cost reservations, immutable execution plans, receipts and replayable reports.
- Native BBH prompts/scoring and validated full-likelihood import; first-token likelihood request, decision and audit helpers.
- Historical benchmark helpers, with archive-dependent APIs identified in [migration inventory](docs/MIGRATION.md).
- Offline regression tests, CI, examples, source hashes and a small [historical result summary](research/README.md).

The 2026-09-29 Luna/Sonnet campaign completed 434 paid calls for $0.5169024; see the [results and limitations](docs/RESULTS_LUNA_SONNET_20260929.md) and [interactive dashboard](dashboard/luna-sonnet-20260929/index.html). Provider capabilities and prices must be checked when creating each new live run. Native likelihood inference remains the responsibility of a compatible external backend; the package validates its submitted scores and request binding, not the truth of backend logits. See [verification](docs/VERIFICATION.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Budgeted Luna / Sonnet campaign

Install the optional large-structure dependency with `python -m pip install -e '.[dev,campaign]'`.
The v1 generator remains unchanged; select `--version v2` for 3–64 entities:

```bash
mkdir -p data
tracking-bench generate --version v2 --entities 3 7 16 32 64 --steps 32 \
  --relevant-updates 16 --per-cell 2 --seed 20261001 --out data/large-ladder.json
```

The campaign uses GPT-6 Luna and **Claude Sonnet 5** through fixed OpenRouter routes, with reasoning explicitly disabled and audited. Sonnet 5.5 is incompatible with that requirement. The example configuration accepts a conservative input-cost assumption (UTF-8 bytes plus a 4,096-token chat envelope); it is not certified provider token counting. See [campaign protocol](docs/FRONTIER_CAMPAIGN.md) before execution.

```bash
tracking-bench campaign freeze --config examples/frontier-config.json --out runs/my-campaign
# Supply OPENROUTER_API_KEY through the environment, or pass --key-file outside the repo.
tracking-bench campaign gate runs/my-campaign
tracking-bench campaign smoke runs/my-campaign
tracking-bench campaign bbh runs/my-campaign
tracking-bench campaign confirm runs/my-campaign
tracking-bench campaign audit runs/my-campaign
tracking-bench dashboard --campaign runs/my-campaign --out dashboard/my-campaign
```

Open `dashboard/my-campaign/index.html` directly. The dashboard runs without a server, credentials or CDN. Each phase is single-use; failed/uncertain attempts are never silently retried. The full campaign cap is 4 USD, including every phase and error; 0.25 USD remains unallocated. A provider charge outside its contract cannot be ruled out by a client. Budget or technical stops remain visible as incomplete coverage. Native BBH likelihood is unavailable on these routes; the BBH panel reports an original-question **subset under chat-three-shot generation**, not native `acc_norm`.

The delivered campaign includes a [diagnostic report](dashboard/luna-sonnet-20260929/REPORT.md): Sonnet reached the 32-token limit in 94/96 fresh confirmation answers. These generation scores do not isolate model reasoning ability. Rebuild the annotated delivery from local raw receipts with `python scripts/export_frontier_delivery.py --campaign runs/luna-sonnet-20260929-live --out dashboard/replayed-copy`.


The [2026-09-30 structured-output smoke](research/structured-output-smoke-20260930/REPORT.md) tested the same JSON prompt with/without a strict API schema at 256 and 1024 tokens. Sonnet produced complete valid JSON on 7/7 nontrivial cases per budget with the schema, versus 1/7 and 2/7 without it. This is diagnostic evidence on reused cases, not a fresh benchmark confirmation. Probe cost: $0.1105429; combined with the previous campaign: $0.6274453 of the original $4 cap.


The [fresh structured comparison, 2026-09-30](docs/RESULTS_STRUCTURED_COMPARISON_20260930.md) completed **534/534 paid calls**, with valid complete JSON and verified reasoning-off usage for every response. Both models used 256 output tokens and strict schemas across 108 fresh groups up to N=64, plus the same 45 BBH reference questions. Main totals: Luna 114/216, Sonnet 120/216; these hide a strong task split (handoff 104/108 and 108/108, swap 10/108 and 12/108). No clear entity-count breakdown boundary was established. [New interactive dashboard](dashboard/luna-sonnet-structured-20260930/index.html) · [frozen protocol and structured CLI](docs/STRUCTURED_COMPARISON.md). New cost: $0.829398050; cumulative across all three paid runs: **$1.456843350 / $4**, zero reserved. BBH remains a separate original-question chat-3shot generation subset, not native `acc_norm`.

The [N/R/D factorial follow-up](docs/RESULTS_FACTORIAL_COMPARISON_20260930.md) completed **958/958 development and 192/192 fresh confirmation calls** on 2026-10-01. Following explicit user approval, two Luna format failures count as wrong and remain separately visible; the original stopped segment is preserved and no response was retried. Both models scored 216/216 on development handoff; swap scores were Luna 51/216 and Sonnet 69/216. Fresh selected contrasts show a 52.1-point Sonnet loss from D=0 to D=8 and a 41.7-point Sonnet lead over Luna at D=0 (swap, N=32/R=8), with the individual structure-group scores now shown in a descriptive view. The original formal assessment is preserved in a collapsed methods appendix. [Simple N/R/D dashboard: measured scores and spread](dashboard/luna-sonnet-descriptive-20261001/index.html) · [protocol and commands](docs/FACTORIAL_COMPARISON.md) · [preserved original stop](dashboard/luna-sonnet-factorial-20260930-stopped/index.html). This factorial campaign cost $1.3826637; cumulative spend across all paid runs is **$2.839507050 / $4**, zero reserved.

The [fresh swap curves, 2026-10-01](docs/RESULTS_SWAP_CURVES_20261001.md) cover **all 36 cells** at N=4/8/16/32, R=4/8/16 and D=0/8/16: nine fresh structure groups per cell, two answer orders and both models. No pilot, selected-cell follow-up or handoff task. All **1,390 calls completed**, with no format errors; cost **$1.6177675 from a newly authorized $4 budget**, separate from prior spending. [Performance-curve dashboard](dashboard/luna-sonnet-swap-curves-20261001/index.html): vary one axis, hold the other two fixed, and inspect individual group scores. Main accuracy: Luna 144/648 (22.2%), Sonnet 204/648 (31.5%); the 45-question BBH reference remains separate. [Protocol and replay commands](docs/SWAP_CURVES_20261001.md).

The [lowest-effort reasoning comparison, 2026-10-01/02](docs/RESULTS_REASONING_EFFORT_20261001.md) adds **effort as a fourth axis**, with accuracy, actual reasoning tokens, completion tokens per correct answer and cost per correct answer. On the same selected 216 swap presentations, Luna improved from **18.5% off to 90.7% low**, Sonnet from **28.7% to 99.1%**, using 143.8 and 318.9 reasoning tokens per task on average. All **526 new calls completed** for **$1.4003303 from a separate $5 allowance**, without format errors. The paired historical baseline uses 256 output tokens; low uses 2048 including reasoning, so this is a comparison of practical configurations. [Reasoning dashboard](dashboard/luna-sonnet-reasoning-20261001/index.html) · [protocol and CLI](docs/REASONING_EFFORT_20261001.md).

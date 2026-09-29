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

This release has not executed new paid API calls. Provider capabilities and prices must be checked when creating a live run. Native likelihood inference remains the responsibility of a compatible external backend; the package validates its submitted scores and request binding, not the truth of backend logits. See [verification](docs/VERIFICATION.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

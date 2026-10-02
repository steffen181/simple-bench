# Fresh structured Luna / Sonnet comparison

Approved follow-up to the successful structured-output diagnostic. Both models use the same strict JSON enum answer schema, 256 visible output tokens and explicitly disabled/audited API reasoning. Direct routes: `openai/gpt-6-luna` through `openai`, `anthropic/claude-sonnet-5` through `anthropic`. No fallback routing, response healing, sampling override or API seed. Provider precision is unknown.

The whole matrix is fixed before any paid request. Main N=3,5,7,10,16,24,32,48,64; K=32; R=16; three fresh generator seeds 20261111/12/13. Two groups per seed/task, swap and handoff, two option rotations: 12 groups / 24 answers per model per N, 432 calls. Block order is deterministically shuffled across N/seeds; both models are evaluated adjacently on each case with alternating order.

Gate: two presentations of one reused zero-event control, plus four presentations of two fresh N5/K8 groups (swap/handoff). All 12 calls must be complete and schema-valid, with verified zero reasoning tokens and known costs. Only the zero-event control must be correct to pass; incorrect but valid nontrivial answers are measurement outcomes. Those gate groups are excluded from the main population.

BBH: reuse the same 45 hash-pinned original questions, 15 per N3/5/7, as the previous campaign; 90 calls. Original question and three demonstrations retained; final answer is now a JSON string value containing the parenthesized option. This is **BBH tracking subset / chat-3shot / strict JSON generation**, not native `acc_norm`. The generated zero-shot ladder remains a separate protocol.

Freshness excludes all canonical/legacy IDs supplied from the previous campaign and the packaged historical BBH groups. The prior diagnostic reused those cases, so contributes no additional fresh groups. Zero-event controls and original BBH items are reused deliberately. No assertion about unknown provider training data.

## Budgets and stops

Prior paid spend: 0.6274453 USD, with no open reservations. New cap: 2.75 USD; gate .15, BBH .50, main 2.10. Even exhausting these allocations stays below the original 4 USD total and preserves the .25 USD reserve. Prior ledgers are hash-bound and not modified.

Quotes retain the explicitly accepted conservative assumption: whole UTF8 request including schema plus 4096 envelope tokens, maximum advertised input/cache/tier rates and full 256-token output budget. This is not certified provider token counting. Check capacity for both model calls before each case, reserve before sending, retain uncertain charges, never retry automatically. Stop on schema/length failures, technical/identity/reasoning/price failure or budget exhaustion. All scheduled missing observations remain in the denominator and coverage, including entire unstarted phases.

## Interpretation and evidence

Compare the paired models within each fixed N/K/task/seed view; rotations share a group. Pointwise 95% weighted group bootstrap with 2000 replicates, stratified by task/seed; no simultaneous boundary confidence. Two groups per stratum are a small sample, and all-zero/all-one samples can give degenerate empirical intervals. A weak low-N baseline or residual format failures prevents a clean capacity-boundary conclusion. Descriptive curves remain useful without asserting such a boundary.

The new main population differs from the previous 32-token run and the JSON prompt/budget changed. Before/after changes cannot be attributed to the schema alone; the preceding matched schema/no-schema diagnostic addresses that narrower question. Scores are not pooled across protocols. Dashboard cost card is cumulative across all three runs; cell costs and `study_spent` refer only to this study.

Requests, responses, receipts, protocol and entire population are immutable and sealed locally. Audits rebuild prompts, schema requests, quotes, scores, paired schedule and cumulative accounting; generator oracle and text replay are independently checked. Public exports contain aggregates, conditions and hashes, no credentials or provider request IDs.

```bash
tracking-bench structured freeze runs/structured-comparison-20260930 \
  --prior runs/luna-sonnet-20260929-live --probe runs/structured-output-smoke-20260930
tracking-bench structured run runs/structured-comparison-20260930 --key-file /outside/repo/openrouter.env.txt
tracking-bench structured audit runs/structured-comparison-20260930
tracking-bench structured export runs/structured-comparison-20260930 --out dashboard/luna-sonnet-structured-20260930
```

`freeze` requires the local predecessor artifacts and the archived diagnostic script in this repository. Its read-only audits establish cumulative spending and exclusions before new execution. Each new run/output directory is single-use. Offline fixtures use injected fake transport and are never model evidence.

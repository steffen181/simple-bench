# Reasoning effort: lowest active level — 2026-10-01

User-authorized extension of the existing swap benchmark, under a **new 5 USD budget**. Fixed direct OpenRouter routes: GPT-6 Luna and Claude Sonnet 5. Current catalog snapshots report `low` as the smallest active supported effort for both models. Sources: [OpenRouter reasoning documentation](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens), public `/api/v1/models` and each model's `/endpoints` metadata, locally retained before freeze.

## Fixed comparison

- Same N=4/8/16/32, R=4/8/16, D=0/8/16; swap only. No pilot or result-based selection.
- Select the lexicographically first canonical structure group per seed/cell from the completed `swap-curves-20261001` run. Three groups per cell (one per generator seed), two answer orders. Selection inspects protocol cases, not responses. 108 groups, 216 presentations and 432 new main calls.
- Historical `off` responses for exactly those cases form the paired baseline; do not mix in its six additional groups/cell. These are reused tasks, not fresh independent validation.
- Same 45 original BBH reference questions (90 calls) and two zero-event controls (four calls). Total 526 new calls. BBH remains a separate chat-3shot/JSON generation subset, not native acc_norm; generated cases are zero-shot.
- Identical prompts/schema and fixed model snapshots/routes. Low uses `reasoning: {effort: low, exclude: true}`, max_tokens=2048; baseline off used 256. Reasoning is included in the output cap and billed even when its text is excluded. No adaptive budget escalation or automatic retries.
- Format/length failures count false and remain separately visible. Wrong zero-event control, uncertain charges, route/model mismatch, invalid/missing reasoning counts or quote violations stop the campaign. Zero explicitly reported reasoning tokens is valid; absence is unknown.

Competing explanation: a gain may reflect the larger output allowance, provider drift/sampling or the selected structure mixture, rather than effort alone. This compares practical configurations; it does not identify an isolated causal effect of reasoning. Provider effort names, private precision and tokenizers are not equivalent compute measures.

## Evaluation

Show accuracy plus actual reasoning tokens per task (mean/median/max and total), completion tokens per correct answer, cost per correct answer and failures. Completion tokens already include reasoning; never add them twice. All wrong-answer tokens/costs stay in efficiency numerators. With no correct answers, tokens/cost per correct answer is undefined, displayed as a dash. Missing/technical observations leave a point unknown. Retain per-structure scores and paired off/low values.

Dashboard axes N/R/D/effort: hold other dimensions fixed. Offer accuracy, reasoning usage, completion-token efficiency and monetary efficiency as separate selectable metrics. No arbitrary blended score or significance verdict. Effort is categorical. Lines join observations, not interpolated evidence.

## Spending and audit

New working cap 4.75 USD plus .25 USD unallocated reserve. Scope caps .10 controls, 1.00 BBH, 3.65 main grid. Historical baseline costs are excluded from this allowance. Before every case, verify both model quotes fit; reserve then settle every actual response. Quotes include all 2048 possible output tokens and conservative whole-request UTF8 bytes plus4096 input-envelope assumption and maximum advertised tariffs. This is the previously user-approved estimate, not certified token counting. A budget stop preserves missing planned observations; it never substitutes them with wrong answers.

All cases, request order, contracts, source hashes and historical seals are bound before inference. The three rounds each cover all36cells before another group is added. No provider reasoning text is needed in public exports; usage counts suffice.

```bash
tracking-bench reasoning freeze runs/reasoning-effort-20261001 --baseline runs/swap-curves-20261001 --metadata runs/reasoning-effort-20261001-preflight
tracking-bench reasoning run runs/reasoning-effort-20261001 --key-file /outside/repo/openrouter.env.txt
tracking-bench reasoning audit runs/reasoning-effort-20261001
tracking-bench reasoning export runs/reasoning-effort-20261001 --out dashboard/luna-sonnet-reasoning-20261001
```

Offline counter-tests precede execution: validate positive reasoning usage, reject missing/negative/bool/over-completion counts, include failed-answer tokens, preserve undefined ratios, replay paired selection and budget accounting, stop on missing usage, and keep prior off-policy semantics. Full regression and actual browser validation are recorded with delivery.

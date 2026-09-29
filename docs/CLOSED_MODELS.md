# Closed-model generation

The shipped live transport is OpenRouter. A direct vendor API adapter is not included. The transport sends public prompts, never the local gold answer. Authentication is read from `OPENROUTER_API_KEY`; do not put it in JSON, source files or shell history. Supply the variable through your environment or secret manager.

```bash
mkdir -p data runs reports
tracking-bench catalog --out data/catalog.json
# Copy examples/live-config.json; replace the model and optional provider fields.
tracking-bench prepare --corpus data/development.json \
  --config live-config.json --catalog data/catalog.json --out runs/development
# Inspect the frozen config, schedule, catalog and manifest before paid execution.
tracking-bench run runs/development
tracking-bench verify runs/development
tracking-bench report runs/development --out reports/development
```

`prepare` freezes the corpus, configuration, catalog, schedule and implementation. `run` refuses changed code or inputs. It records requests, raw responses, normalized receipts and a final seal. The execution plan and budget ledger are tied to their execution environment; they are not movable jobs. Keep the installation unchanged between prepare/run. Native task bundles, in contrast, have relocatable dataset paths.

Use a single shared ledger for related runs. `total_budget_usd` must match an existing ledger. Reservation bounds use the catalog context size, output cap and supported price categories, so they can be much larger than actual small-prompt costs. An insufficient reservation stops the run before the request. Unknown costs, identity mismatches and API failures stop the run; there are no automatic retries. Request price ceilings and disabled fallbacks are enforced in routing, subject to the provider honoring its contract.

The example model ID is deliberately a placeholder, not a performance recommendation. Set `provider` to a route slug if you require a fixed provider, and `accepted_response_providers` only to documented equivalent returned names. Add response model aliases only when justified by the provider; aliases do not prove weight revision. `reasoning_policy: "off"` requires explicit zero reasoning-token evidence and can stop APIs that omit it. If omitted, reasoning behavior is unverified; record this as a protocol condition. `temperature`, `top_p`, `seed`, `reasoning` and `reasoning_effort` must be advertised by the catalog before use.

## Likelihood capabilities

`tracking_bench.bbh_likelihood.messages`, `request`, `attempt`, `decision` and `summarize` are retained for custom token-likelihood campaigns. `request` requires one generated token, top-20 logprobs, temperature=1, top_p=1 and disabled reasoning. The top-k decision accepts only exact A..G tokens. Omitted candidates stay unknown unless the known best candidate is strictly above the omission bound; it never fabricates a missing logprob. `summarize` exposes unresolved coverage and accuracy bounds.

`tracking-bench score-token --responses token-responses.json --out token-scores.json` replays records of the form `{"case_id": "...", "n": 3, "raw": {"http_status": 200, "body": "JSON response string"}}`. This is a scoring import, not an automatic paid token campaign or complete provider-identity audit. Keep requests, routing, costs and response identity checks in your campaign adapter. Its metric is explicitly `first_token_proxy_NOT_native_acc_norm`.

For true native likelihood use the full-continuation contract in [PROTOCOLS.md](PROTOCOLS.md). Generated-token top-k logprobs generally cannot score every arbitrary multi-token continuation. A missing capability must remain unavailable, rather than be inferred from successful text generation.

## Result interpretation and sharing

The generated-answer report separates parsed accuracy, strict/first-answer parsing, technical coverage, truncation/refusal, cost, returned model/provider identity and option-order stability. Technical failures/refusals are excluded from its scored denominator; publish counts/coverage with that conditional accuracy. Do not silently compare it with an all-planned denominator from another protocol.

Raw run directories can contain provider metadata, billing details and local paths. They are intentionally absent from this source package. Publish a separately reviewed aggregate or sanitized export when making results public; `.gitignore` is not a sanitizer for arbitrary user-selected paths.

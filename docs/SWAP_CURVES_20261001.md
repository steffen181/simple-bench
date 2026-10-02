# Fresh swap curves — 2026-10-01

User-authorized new measurement, with a separate **4 USD** OpenRouter budget. This replaces the pilot/selected-confirmation design for this new series. Historical measurements and their 2.839507050 USD cost remain unchanged and are not charged to the new allowance.

- Full grid: N=4/8/16/32, R=4/8/16, D=0/8/16; K=R+D. Swap only, no handoff.
- Nine fresh structure groups per cell: three per generator seed 20270111/12/13. Two answer-option rotations per group; both models answer exactly the same cases. 324 groups, 648 presentations, 1,296 main requests.
- Four zero-event control requests and 90 requests on the same 45 original BBH questions precede the grid. Total 1,390 requests. These controls/references are separate, not a pilot or selection stage. BBH retains its original N=3/5/7 and chat-three-shot prompts; fresh generated questions are zero-shot.
- GPT-6 Luna and Claude Sonnet 5, fixed direct routes, reasoning disabled and explicitly audited, strict JSON answer enum, max 256 output tokens, no retries. Format/completion errors count false. Technical failures, unknown charges and violated cost bounds stop execution. Missing observations remain unknown.
- All cases, exclusions, contracts, source hashes and request order frozen before inference. Nine balanced rounds cover every one of 36 cells once per round before another group is added. No adaptive choice from outcomes. Freshness excludes historical canonical/legacy IDs plus all previously measured development and confirmation cases.
- Preflight found limited canonical support in the smallest event cells: 12 requested fresh groups at N=32/R=4/D=0 exhausted the current generator search. Nine per cell successfully generated over the entire grid. Repeated or renamed structures are not counted as fresh groups.
- New ledger: 3.75 USD working cap plus .25 reserve. Scope caps .03 controls, .20 BBH and 3.52 grid. Each request uses the previously accepted UTF8-byte plus 4,096-envelope conservative input estimate, maximum advertised rates, 256 output tokens and actual charge reconciliation. This is not certified token counting. Full completion depends on actual cost and route behavior.

Descriptive dashboard: choose N, R or D as the curve axis; keep the other two fixed. Large points show accuracy; small points show every structure-group score (0/50/100%). Lines only join measured points. Clicking a point opens all paired groups. No significance gate, no inference verdict and no selected-cell series. Ranges describe case heterogeneity; they are not confidence intervals or measurements of repeated identical API requests.

```bash
tracking-bench swap-curves freeze runs/swap-curves-20261001 --history runs/factorial-comparison-20260930 --metadata runs/swap-curves-20261001-preflight
tracking-bench swap-curves run runs/swap-curves-20261001 --key-file /outside/repo/openrouter.env.txt
tracking-bench swap-curves audit runs/swap-curves-20261001
tracking-bench swap-curves export runs/swap-curves-20261001 --out dashboard/luna-sonnet-swap-curves-20261001
```

Competing explanation: apparent declines may reflect structure mix, answer-order effects, prompt length or stochastic model responses. Descriptive measurements do not isolate causal capacity. N also changes chance accuracy 1/N; private provider precision and training data remain unknown. Historical raw data, old dashboards and original inference results are preserved.

Preflight: all 324 fresh groups generated successfully against 1,639 historical exclusions. Current route metadata supports strict structured output and reasoning-off for both direct routes. The empirical main-grid cost forecast with 25% buffer is 1.893 USD, before separate BBH/control costs. This forecast is not an upper bound: the sum of conservative per-request quotes is 20.587 USD, whereas reservations are held only for the next request/model pair and settled against actual charges. The 3.75 USD working cap remains mandatory even if it prevents completion.

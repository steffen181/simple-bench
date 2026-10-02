# Complexity and study design

The ladder asks who holds a named object after a sequence of events. An initial bijection assigns one object per person. A handoff transfers one object; swaps exchange all objects held by two people. After handoffs a person can hold zero or multiple objects. Each task has N=3..7 candidate names.

| Axis | Supported values | Meaning |
|---|---|---|
| Entities | 3..7 | People and initial objects; chance baseline is 1/N |
| Event count | 0..128 | Total instructions in the sequence |
| Relevant updates | floor(K/2), K | Events that change the current owner of the queried object |
| Task | swap, handoff | Exchange all holdings / transfer one named object |
| Answer order | two rotations | Same problem and answer, reordered candidate-name list |
| Seed | explicit integer | Reproducible sampling; not a semantic difficulty level |

Distinct relevance values are deduplicated. Zero-event generation is calibration, only the swap label is used, and `per-cell=1` is required: renamed initial assignments collapse to one canonical structure per N. The generator fails explicitly if it cannot find enough unused structures. The grid is capped at 8,192 planned rows before generation, with bounded rejection attempts. This is not adaptive selection based on model scores.

Canonical IDs remove person/object naming aliases while retaining event structure and query. All rotations of a structure share family/scenario/pair IDs. The solver tracks possession sets independently of the generator; a text parser replays rendered sentences. Gold labels are stored for evaluation, but API requests contain only public prompt text.

## Development then confirmation

1. Before inference, fix models/routes, model revisions where available, numeric precision where exposed, prompts, shots, token budgets, seeds, strata, exclusions, metrics, parsing, treatment of failures and planned comparisons.
2. Generate development cases. Check format/copy controls and transport using the same route. Choose protocol changes only on development data.
3. Generate confirmation with all exposed groups blocked. For several development corpora, pass a JSON list containing their union of canonical IDs. `--blocked` accepts a previous ladder corpus or `{"groups": [...]}`.
4. Freeze the execution plan with `prepare`. Preserve it and keep confirmation answers/results unopened until protocol decisions are fixed. Fresh output directories prevent overwrite.
5. Execute once. A failed or interrupted paid run is not automatically retried or resumed. Account for all planned cases, including unresolved responses and missing coverage.
6. Report accuracy by entity count, event count, relevant updates and task. Keep rotations together in uncertainty estimation; do not treat repeated presentations as independent evidence.

The default report is descriptive and has no significance or validation verdict. For confirmatory intervals, use the retained group IDs and a preregistered grouped analysis; historical bootstrap helpers are included but the CLI does not automatically preregister or perform that analysis. Option-order contrasts preserve entity count and relevant-update strata.

Increasing length and relevant updates is a designed complexity gradient, not a guarantee of monotonic measured difficulty. Event count, chance level, language/template difficulty and state complexity should not be collapsed into one score without a preregistered weighting. Fixed names, repeated templates and prior model training remain limitations. Exclusion proves freshness only relative to the supplied structural history.

The BBH generator uses a different query direction (which object a person has), N=5/7 and BBH event counts. Its historical exclusions are packaged separately. Do not compare its structure IDs directly to the ladder's object-to-owner schema. Neither schema proves absence of training contamination.

## Optional v2 for larger entity sets

`tracking-bench generate --version v2` supports 3–64 entities and up to 128 events, selectable task types and an exact relevant-update count. It requires the `campaign` extra (pinned igraph 0.11.9). Its graph identity schema is `ownership-bliss-v2`: people, objects, initial holdings, queried object, event order and event roles are preserved under renaming. Swap participants are unordered; giver/recipient roles are ordered. Independent set-based solving and text replay are both checked before returning a case.

The old v1 generator and its hashes remain unchanged. V2 IDs are different; small v2 cases also carry a legacy ID, and exclusions accept those legacy IDs. Tests compare old/new equivalence classes on small graphs and run large symmetric cases. Do not mix schemas without this explicit mapping. More entities increase chance-level differences and prompt length as well as state complexity; the dashboard exposes those dimensions separately.

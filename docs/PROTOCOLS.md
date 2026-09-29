# BBH compatibility contracts

The reference is BIG-Bench Hard `tracking_shuffled_objects` at N=3/5/7: 250 original questions each. This is three tracking configurations, not the whole BBH benchmark. Sources and upstream commits are recorded in `src/tracking_bench/data/bbh-sources.json`.

- BBH commit: `9ee07bd481feebf959a6b59d61ea57bdcf30964d`.
- Hugging Face harness fork: `c339225c8ec169296f45f5326a7c0f8e3baa6005`.
- Prompt: raw task description, the exact three demonstrations, `Q: ...\nA:`, no chat template or extra system instruction.
- Candidates: `(A)` through the required final letter, with the task's leading-space target delimiter included in likelihood continuation (`" (A)"`).
- Decision: summed conditional token loglikelihood of the full continuation, divided by the character length of the choice (three characters, excluding the delimiter). First maximal choice wins ties, matching the pinned scorer.

Token boundaries and conditional likelihood computation must match the pinned harness, including context/continuation whitespace handling. Merely obtaining a logprob for `A` is not this calculation. Equal three-character denominators make normalized and unnormalized argmax identical here; the continuation remains the full text.

## Export and score

`export-bbh` validates every original source against the packaged manifest; a caller-created manifest cannot redefine the reference. It emits sealed `cases.json`, gold-free `requests.json`, `protocol.json`, `tasks/*.yaml` and `data/*.json`. Gold answers exist in cases and dataset files for scoring, never in the final request question. Demonstrations deliberately contain their known answers.

Native YAML dataset paths are relative to the exported bundle. For a compatible installed harness, run from the bundle directory and include its `tasks` directory. For Python integration call `tracking_bench.reference.native_tasks(bundle)` to verify hashes and get configs rebound to the bundle's current absolute location. Do not edit the sealed YAML to relocate it. Do not write inference output inside the bundle: verification rejects extra files.

The package neither installs the harness nor downloads a model. A compatible backend should evaluate each request's `context` and every `continuations` entry, in order, and produce records like this illustrative fixture:

```json
{
  "case_id": "copy from request",
  "request_hash": "tracking_bench.common.digest(request)",
  "model": "provider/model/revision-and-precision",
  "protocol": "native_full_continuation",
  "loglikelihoods": [-3.0, -1.0, -2.0]
}
```

Use a JSON array containing exactly one record for every request in one bundle, one model per submission:

```bash
mkdir -p reports
tracking-bench score-native --bundle data/bbh-comparison \
  --responses native-responses.json --out reports/native-scores.json
```

The importer verifies the bundle, reconstructs the exact native requests, checks case/request bindings, coverage, finite candidate scores, candidate ordering, target normalization and consistent model identity. It reports separate reference/generated/anchor scores by N. These are caller-supplied likelihoods; hashes cannot prove that the stated model produced them. Record provider, revision, numeric precision, tokenizer, endpoint and execution settings in an accompanying provenance file. Pair/seed/rotation metadata remain in cases for grouped statistical analysis; the import summary is descriptive.

The default generated comparison has three seeds, eight fresh groups per seed×N, N=5/7, two option rotations and one matched original anchor per group with two rotations. It blocks known original/demo and archived study structures. N=3 has no fresh support under this archived BBH structural exclusion policy, so its original reference is retained without a fabricated fresh stratum. Freshness is relative to that known history and this schema, not to model training data.

## Closed APIs and publication

Run the original and generated reference cases through the same backend and protocol. Label raw three-shot full-continuation results `native_acc_norm`; label chat first-token results as the first-token proxy; label free generation as parsed generation accuracy. Record prompt/shot/budget conditions, precision and coverage alongside every number. Never substitute one metric into another's column.

The broader ladder varies N and event count independently, uses different language, swaps/handoffs, and asks an inverse ownership question. Its scores measure generalization on that designed suite, not a replacement BBH leaderboard score. A matching model name is not enough for equality to a published score; model revision, dtype, prompt, candidate normalization and task coverage all matter.

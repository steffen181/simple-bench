# 0.1.0 release candidate — 2026-09-29

Standalone extraction for state-tracking evaluation with a designed complexity ladder and a separate pinned BBH comparison contract. First-party licensing remains pending; this candidate has not been published to a hosted repository or package registry.

Validation during extraction: 61 offline tests passed; the wheel installed into a separate Python 3.10 environment; the documented development/confirmation generator created 384 cases and 192 groups per split with no structural overlap. The native export/import smoke covered 758 cases and seven movable task configurations. Missing/duplicate replies, mismatched request hashes and redefined prompts were rejected.

The locally available pinned HF harness was checked against 174 archived implementation files. Across the exported bundle, all 758 prompts and 3,798 continuations/metric checks agreed. This was offline software validation, not fresh model inference. No paid requests or model-weight downloads were performed. The previous research study's 9,648 sealed files remained unchanged.

Internal code review identified and led to regression fixes for upstream-source provenance and complexity-stratum aggregation. This is not an external scientific review. Two archive-dependent historical test functions remain excluded as documented in docs/MIGRATION.md. Live provider behavior and native remote likelihood acquisition were not retested in this release.

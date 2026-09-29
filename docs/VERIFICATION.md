# Reproduction and verification

```bash
python -m pip install -e '.[dev]'
pytest -q
tracking-bench demo --out runs/offline-check
tracking-bench verify runs/offline-check/run
python -m build
```

Tests are offline. Transport tests use a local HTTP server, not paid inference. They exercise structural canonicalization, dense task rendering, parser behavior, cost/routing controls, raw token probability checks, native scoring and confirmation helpers, the portable CLI, exclusion/rotation/relevance invariants, source provenance, report strata and bundle relocation.

The source provenance map records original files and changes. The two removed archival test functions required a real historical provider catalog or dated campaign scripts; they are listed in [MIGRATION.md](MIGRATION.md). No optional live integration is advertised as newly tested.

For a release, build the wheel and source archive, extract to a directory outside the research checkout, install the wheel into a clean virtual environment, run the full tests against the installed package, run the offline demo, verify native export/score imports and scan distribution contents for private paths and credentials. Use the release artifact's SHA256 inventory to verify the download. CI checks offline tests and wheel installation; it does not validate current external service behavior or model quality.

Hash seals detect changes relative to a trusted manifest; they are not cryptographic signatures or independent proof of provenance. Preserve the original release hashes independently. `COMPLETE` denotes infrastructure completion, never confirmation of a scientific hypothesis.

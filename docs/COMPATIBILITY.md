# Compatibility and support status

**Source pair matters.** CAPT-Bot's files, `CAPT_BOT_COMPATIBILITY.json` and CAPT Core's actual running revision form a compatibility hypothesis; **only integration tests with that pair** can establish a supported environment.

## Current pinned state

| Category | What is documented | What is **not** established |
| --- | --- | --- |
| CAPT-Bot GitHub | `main` `0136336538f2f1c2a1daadb55303ee54c60531ac` | Matching local uncommitted worktree |
| Historical Core baseline | `783f06bd15f185b2eeeea10c85f6e993a09237e8` in compatibility manifest | Current Core head admission |
| Manifest | `PRE_RELEASE_STAGE_A_ONLY`; `productionExtensionWired: false` | Production plugin admission |
| Stage-A suite | Historical `333 passed, 8 skipped` in review matrix | Fresh execution at this SHA pair |
| Core/Swift suites | Historical per-manifest run counts and review records | Fresh independent acceptance now |
| Identity registration | Manifest says `authenticatedBotRegistration: true` | Live compatibility with user's resident RuntimeService |
| Bot activation | `false` in manifest | Usable autonomous Bot lifecycle |
| Sequential issue solver | `false` in manifest | Closed-loop GitHub repair |
| Sandbox/Cloud R5 | `sandboxCloudR5Certified: false` | Deployment and entitlements |
| Real R5 acceptance | `NOT_RUN` | Public release certification |

## What the test-only gate actually does

`scripts/run_r5_stage_a_compatibility.py` extends `capt_runtime.__path__` inside a pytest process, importing Bot modules alongside a checked-out Core. It does **not** install Bot into the production runtime, migrate storage, create a stable extension seam, or prove remote resources available.

```zsh
python3 scripts/run_r5_stage_a_compatibility.py --core-root /absolute/path/to/CAPT_core
```

The checked Core must contain `capt_runtime/__init__.py` and `contracts/generated/python`. Python must have `pytest` and all test imports resolvable.

## Additional Stage-B source admission

The [new Stage-B source ledger and isolated registration gate](architecture/CAPT_BOT_R5_STAGE_B_SOURCE_ADMISSION.md) pins Core `3f11800c31252b8e9d2037fc29cf3c195dcfb7f4`, checks 28 Bot-side runtime modules (26 byte-identical, 2 newer Core-hardened divergences), verifies Core module import provenance, and runs an actual temporary RuntimeService registration test. It is **source admission only**, not runtime extension installation or production certification; `realR5Acceptance: NOT_RUN` remains unchanged.

## Minimum release gate

The [R5 specification](architecture/CAPT_BOT_CONVERGENCE_R5.md) and [release review matrix](RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) require semantic convergence, one authoritative runtime, lifecycle/approval/recovery evidence, actual tool/provider/issue workflow proofs, negative tests, user journeys and exact-head reproducibility. Until independently established, describe this repository as **pre-release**.

[Verification](VERIFICATION.md) · [Release and migration notes](RELEASES_AND_MIGRATIONS.md).

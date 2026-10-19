# Releases, migrations and current status

**Current documented state: pre-release R5 Stage-A compatibility research / R5 convergence unfinished.** Do not label this source as a production-certified autonomous Bot platform.

## Known milestones

- **R1 foundation:** BotManifest, cognition/skills and Lab Board semantics ([design](architecture/CAPT_BOT_FOUNDATION_R1.md)).
- **R2 crew/standup:** delegate assignment and standup projection ([design](architecture/CAPT_BOT_CREW_STANDUP_R2.md)).
- **R3 Cloudflare:** resource and execution boundaries ([design](architecture/CAPT_BOT_CLOUDFLARE_R3.md)).
- **R4 Workflows:** orchestrator/economic-policy design ([design](architecture/CAPT_BOT_CLOUDFLARE_WORKFLOWS_R4.md)).
- **R5:** semantic rebase against modern Core, versioned extension seam and complete release acceptance ([spec](architecture/CAPT_BOT_CONVERGENCE_R5.md)).

These labels describe documented tranches, **not** independently validated shipped versions. `CAPT_BOT_COMPATIBILITY.json` currently declares `PRE_RELEASE_STAGE_A_ONLY`, `productionExtensionWired: false`, `migrationVersion: null` and `realR5Acceptance: NOT_RUN`.

## Safe upgrade strategy (design gate, not a runnable migration)

Pin both SHAs and take a read-only state inventory → compare historical Core diff semantically → create/test the minimal current-Core extension seams → test all Bot domain semantics in a clean integration checkout → exercise replay/restart/effect reconciliation with explicit approval → publish migration and rollback receipts. **Never** patch modern Core blindly with `integration/CAPT_CORE.patch`.

No verified upgrade/rollback executable is provided by this repository. Preserve EventStore history and production state; stopping the Bot cockpit is not a database rollback.

## Publishing gate

Independent human-readable release notes require current-head integration tests, negative authority cases, security scan, versioned migration schema, evidence digest, clean-room installation and an authorized release decision. See [Compatibility](COMPATIBILITY.md), [Verification](VERIFICATION.md) and the [release matrix](RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md).

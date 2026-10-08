# CAPT-Bot

CAPT-Bot is the separately versioned governed synthetic-worker/product layer for CAPT. It owns Bot identity, cognition, skills, delegation, Lab Board/standup, Bot-specific execution integration, and the operator-facing Bot workflow while preserving CAPT Core as the single authority, execution, evidence, verification, and claim plane.

## Current status

The repository began as a verified project-layer extraction from `knowurknottty/CAPT_core` and still preserves that exact isolation lineage. The next implementation tranche is **R5 Convergence**: semantically rebase the verified R1-R4 Bot work onto current CAPT Core, then extract Bot-owned behavior behind the smallest generic Core integration seams instead of maintaining stale shadow copies of shared Core files.

Start here:

- `docs/PUBLIC_USER_GUIDE.md` — pre-release human guide for the local cockpit, Bot identity, governed chat and limitations.
- `docs/AGENT_OPERATOR_GUIDE.md` — agent contract for sequential GitHub issue repair, approvals, evidence, and genuine task-specific recursion.
- `docs/RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md` — five-chat council/independent review plan with explicit release blockers.

- `docs/architecture/CAPT_BOT_CONVERGENCE_R5.md` — authoritative R5 architecture/convergence specification.
- `docs/superpowers/plans/2026-09-17-capt-bot-r5-deepseek44-sdr.md` — System Design + Delivery Requirements and 44-vessel DeepSeek implementation handoff.
- `docs/architecture/CAPT_BOT_FOUNDATION_R1.md` — original Bot foundation semantics.
- `docs/architecture/CAPT_BOT_CREW_STANDUP_R2.md` — crew/delegate/standup semantics.
- `docs/architecture/CAPT_BOT_CLOUDFLARE_R3.md` — Cloudflare governed execution boundary.
- `docs/architecture/CAPT_BOT_CLOUDFLARE_WORKFLOWS_R4.md` — Cloudflare Workflows orchestration boundary.
- `docs/superpowers/specs/2026-09-09-inversion-sandbox-r2-persistent-leases-design.md` — persistent governed InversionSandbox design.
- `docs/superpowers/verification/2026-09-09-inversion-sandbox-r2.md` — historical verified sandbox evidence at the isolation-era Core state.

## Exact isolation provenance

- Base Core commit: `3be3fd6cc1274f7a7935d35b83641fc5b9dc82e8`
- Project source commit: `c93200626b621bf7a27c1fa6cfcbf04773121c35`
- Added project-owned files are preserved at their original CAPT paths.
- Historical modifications to pre-existing shared Core files are preserved in `integration/CAPT_CORE.patch`.
- `SOURCE_PROVENANCE.json` SHA-256 binds the isolated payload.

The historical patch is provenance and reconstruction evidence. **Do not blindly apply it to current CAPT Core.** Current Core has materially changed since the isolation point, including authority hardening, newer projections, composition changes, provider/operator work, provenance fixes, and human-answer/receipt separation. R5 requires a semantic hunk-by-hunk rebase and explicit disposition of every shared path.

## R5 governing invariant

> Bot identity, cognition, collaboration, and UX may be independently versioned; authority, consequential mutation, external execution, evidence, verification, and terminal truth remain CAPT-owned.

CAPT-Bot must never create a second `RuntimeService`, `EventStore`, `ToolBroker`, capability/approval authority, verification plane, or claim authority.

## Historical deterministic assembly

The isolation snapshot can still be reconstructed for provenance/debugging only:

1. Check out CAPT Core at the historical base commit.
2. Apply `integration/CAPT_CORE.patch`.
3. Overlay the project-owned paths from this repository.
4. Run the historical project verification gates.

That procedure reconstructs the isolated 2026-09-09 lineage. It is **not** the R5 implementation recipe.

## R5 implementation path

1. Inventory local and remote CAPT-Bot/Core state and freeze exact SHAs.
2. Classify every historical shared-Core hunk as already-upstream, generic Core seam, Bot-domain behavior, or unresolved.
3. Prove the historical Bot feature set semantically rebased onto current Core.
4. Extract Bot-owned implementation behind the minimal immutable Core integration seam while preserving one CAPT runtime.
5. Close Bot lifecycle, governed learning, delegation, request-to-result orchestration, human-first answers/receipts, sandbox, Cloudflare, and restart/reconciliation semantics.
6. Run the complete current-head acceptance matrix and record exact release evidence.

See the R5 spec and SDR above for the full requirements, vessel topology, acceptance scenarios, merge gates, and stop conditions.

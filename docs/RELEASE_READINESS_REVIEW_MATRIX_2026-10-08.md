# CAPT Core + CAPT-Bot Public Release Review Matrix

**Date:** 2026-10-08
**Status:** staged design, not executed provider results or public-release certification.

## Source scope

- CAPT Core: `knowurknottty/CAPT_core`, current-head exact SHA must be frozen immediately before each review; code, macOS Swift operator, RuntimeService, Node/MCP, contracts, tests, manifests, release docs, and user-facing features.
- CAPT-Bot: `knowurknottty/CAPT-Bot`, isolated R1–R4 source plus R5 Convergence and separately versioned operator cockpit. Use semantic migration, **never** blindly apply `integration/CAPT_CORE.patch`.
- Every review must inspect source and tests at the same declared SHA pair. Cross-repository claims require specific source references and both provenance heads.

## Requested five-chat topology

| Chat | Cohorts / models | Review scope | State |
| --- | --- | --- | --- |
| Shared CAPT public-release council | 4 cohorts: DeepSeek V4.1 Flash, GLM 5.3 Flash, MiMo 2.6 Flash, Qwen 3.8 Flash | Adversarial code review + documentation truth + harsh critique of launch UX, permissions, agents, Bots, runtime, Swift, recovery, secrets, integrations | **Not dispatched** |
| DeepSeek independent review | One DeepSeek V4.1 Flash cohort | Security, correctness, threat model, race/restart/effect-state failures | **Not dispatched** |
| GLM independent review | One GLM 5.3 Flash cohort | Architecture, modularity, R5 integration, APIs, extensibility | **Not dispatched** |
| MiMo independent review | One MiMo 2.6 Flash cohort | UI/UX, setup paths, installation, TIA keyboard/VoiceOver, user documentation | **Not dispatched** |
| Qwen independent review | One Qwen 3.8 Flash cohort | Test/provenance gaps, repo/issues cross-check, performance, release readiness | **Not dispatched** |

Config examples already present in Core source, **not verified live provider availability**:
`deepseek/deepseek-v4.1-flash`, `z-ai/glm-5.3-flash`,
`xiaomi/mimo-v2.6-flash`, `qwen/qwen3.8-flash`.
All under the `openrouter` provider in the current examples. Check live model/provider
availability and current price **before** issuing HumanApproval, and do not substitute.
The shared council means four actual cohort inference calls, not 4×vessel-count.
The four independent chats add four more separately authorized calls.
The intended vessel setting can be 22 logical perspectives/cohort, but requires a
task-relevant charter and no automatically inferred parallelism.

### Task-engineered recursion

A 3× or 5× requirement is an **execution invariant**, not a paragraph asking
the model to introspect. Each subsequent cycle must consume the actual
previous cycle's evidence, cite defects, revise, and produce a new receipt
with its own task-derived checks. The fourth and fifth cycles should be
adversarial and integrated release verification if required by findings.
A one-call `"five passes"` prompt or 22 logical vessels is **not**
five verifiable dependent model calls.

The **native Swift 3×/5× enforced recursion setting is not implemented yet**.
Do not claim it is active merely from this matrix. Implement runtime admission,
dependent step/receipt lineage, budget/approval gating, and restart-safe
reconciliation before exposing it as enforced.

## Required review output

- Ranked P0–P3 findings with file:line, SHA, exact reproduction, expected/actual,
  exploited boundary or user impact, and test/repair proposal.
- Source-supported feature inventory: implemented, tests only, integrated,
  installed, live verified, release proven, documented-only.
- Documentation contradiction report and separate human/agent instructions.
- Missing Bot end-to-end workflows: registration, activation, task assignment,
  issue intake, sequential runner, governed tool execution, PR/CI/merge,
  proof-backed completion, replay and restart.
- Explicit no-release blockers; accepted residual risks; no invented test pass.
- Each review's raw result/evidence and independent attribution; only
  verification plane may establish release claims.

## Current engineering finding

At the source snapshot preceding this review, the Bot cockpit and Swift Bots
screen did not contain an actionable full Bot lifecycle. A narrow
`register_bot` contract has now been implemented in the local integration
worktrees for durable identity only. Full CAPT-Bot R5, activation,
unattended GitHub issue repair, and the five requested model reviews
remain outstanding. The historical standalone CAPT-Bot suite currently
requires a current-Core semantic integration/rebase: a direct standalone
collection attempt could not import 40 Core-owned symbols/modules. Do not
reinterpret those collection errors as passing tests.

## Release gate

**HOLD PUBLIC RELEASE** until zero unwaived P0/P1, grounded current-HEAD
Core+Bot acceptance, secrets and entitlement audit, correctly enforced
authority/approval boundaries, a no-write/dry-run GitHub issue demo,
an authorized one-issue write/PR demonstration, negative/red-team tests,
restart/reconciliation, and human/agent documentation verification.

## Verified first integration slice (not R5 completion)

- `CAPT Core` full Python suite on the current implementation: **1,967 passed,
  70 skipped, 13 deselected**.
- Native Swift suite after Bot registration: **145 passed, 9 skipped**.
- Bot cockpit focused tests: **11 passed**.
- Bot-to-Core isolated HTTP registration integration: **1 passed**.
  This test launches a temporary Core RuntimeService, registers via the
  actual Bot UI HTTP bridge, reads back the authoritative Bot aggregate,
  and terminates its test-owned runtime process.
- The historical standalone Bot suite **did not collect**: 40 import
  errors due to Core-owned modules not being available from the isolated
  Bot checkout. R5 semantic rebase and full integration gates remain open.
- The live production CAPT RuntimeService was intentionally **not restarted**
  while historical running execution markers require reconciliation.
  Consequently, live native Create Bot availability is **not yet proven**.
- No model council/provider review calls were issued and no HumanApproval
  was automatically decided in this integration slice.


## Reproducible R5 Stage-A compatibility gate (2026-10-08)

From a CAPT-Bot checkout with Python dependencies installed:

```zsh
python scripts/run_r5_stage_a_compatibility.py --core-root /path/to/CAPT_core
```

Against exact Core `783f06bd15f185b2eeeea10c85f6e993a09237e8`,
with current CAPT-Bot test sources: **333 passed, 8 skipped**.
Local log: `~/capt-node-workspace/capt-bot-stage-a-repro-gate.log`.

This script deliberately extends Python module discovery **inside the test
process only** so historical Bot-owned `capt_runtime` modules coexist with
current Core modules. It neither applies the old patch nor mutates the tested
Core worktree. It is a **compatibility research gate**, not the actual
startup composition contract, migration, Bot activation, delegation, or
full production acceptance test.

`CAPT_BOT_COMPATIBILITY.json` records observed version/feature baselines
and leaves runtime extension seam, driver/tool compatibility, production
extension wiring, and evidence digest explicitly incomplete. It is NOT
yet consumed for runtime admission. Therefore the R5 release gate remains
blocked despite the green historical suite.

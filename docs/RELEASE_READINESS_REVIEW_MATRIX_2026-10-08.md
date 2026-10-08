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

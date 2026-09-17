# CAPT Bot Convergence R5

**Status:** implementation-handoff specification  
**Date:** 2026-09-17  
**Repository:** `knowurknottty/CAPT-Bot`  
**Isolated source lineage:** CAPT Core `c93200626b621bf7a27c1fa6cfcbf04773121c35`  
**Current Core convergence target:** `520aa5f6d44839e61b2392a01a2f6a7983be4276`

## 1. Thesis

CAPT Bot is a persistent, governed synthetic worker built on CAPT's existing authority, execution, memory, evidence, verification, and claim planes. It is not a second agent runtime, a second authority kernel, or a friendly wrapper around unrestricted tools.

R5 is the convergence tranche that turns the already-implemented R1-R4 Bot, crew, sandbox, Cloudflare, and Workflow work into one coherent product layer against current CAPT Core.

The governing rule is:

> **Bot identity, cognition, collaboration, and UX may be independently versioned; authority, consequential mutation, external execution, evidence, verification, and terminal truth remain CAPT-owned.**

The end state is a separately versioned `CAPT-Bot` repository that can evolve independently while composing into exactly one CAPT runtime instance.

## 2. Proven source basis

R5 preserves the semantics already established in this repository:

- **R1 Bot Foundation:** durable `BotManifest`, typed `CognitiveCandidate`, governed `SkillCandidate`, `LabBoardItem`, locality compilation, and EventStore as the sole durable mutation truth.
- **R2 Crew + Standup:** durable `DelegateAssignment`, mission/task/depth/expiry binding, no authority-by-delegation, and deterministic read-only standup projection.
- **R3 Cloudflare:** typed remote execution surfaces, resource adoption, free-tier/economic gates, artifact evidence, fail-closed routing, and indeterminate reconciliation.
- **R4 Cloudflare Workflows:** durable remote orchestration as evidence-producing provider state, never CAPT terminal truth.
- **InversionSandbox R1/R2:** one-shot and persistent attested Docker execution, immutable lease identity, per-command capability admission, restart reconciliation, bounded network/filesystem semantics, and no automatic resource adoption/recreation.

The isolation repository currently preserves Bot-owned paths plus `integration/CAPT_CORE.patch`, generated against older Core. That patch is **historical provenance only** for R5. It must not be blindly applied to current Core.

### 2.1 Current-Core delta that R5 must respect

Since the Bot isolation source commit, CAPT Core gained material authority and operator behavior, including:

- canonical composition-root hardening;
- semantic operator control APIs;
- canonical workspace binding for model execution;
- Model Council state/analysis;
- approvals/missions/tasks/checkpoints read projections;
- explicit mission and driver-run transition authority gates;
- envelope-identity refusal auditing;
- provenance-honesty fixes;
- dead-path and release hardening;
- SOMA contract work;
- human-first answer / execution-receipt separation;
- prompt-intelligence routing improvements;
- refreshed public documentation.

R5 must rebase semantically onto those behaviors. Reintroducing an older shared file is a regression even if old Bot tests pass.

### 2.2 Local-only delta caveat

This specification is grounded in the GitHub-visible CAPT-Bot and CAPT Core state. At authoring time the active Remote Desktop Commander connector still exposed only the prior account/device identity, so Mac-only unpushed work could not be independently inventoried. Before implementation starts, the implementation lead must compare the live local CAPT-Bot/CAPT_core worktrees against the remote SHAs above and explicitly import or reject any real local-only delta. Lack of visibility is not proof of absence.

## 3. R5 acceptance definition

R5 is complete only when all conditions below are met:

1. CAPT-Bot composes with current CAPT Core without replaying the historical shared-Core patch.
2. There is exactly one `RuntimeService`, one `EventStore`, one `ToolBroker`, one effective authority registry, one capability/approval authority path, one verification plane, and one claim authority per runtime composition.
3. Bot-domain state is durable, typed, replayable, provenance-bound, queryable, and restart-safe.
4. A Bot can receive a human request, bind project/workspace/context, plan bounded work, invoke current CAPT provider/tool paths, delegate within policy, collect evidence, verify/claim correctly, propose learning, and return a human-first answer with a separately inspectable receipt.
5. Persistent cognition is never model-self-authorized.
6. Generated/imported skills cannot become active without the required sandbox/test/red-team/shadow/approval evidence.
7. Local sandbox and cloud execution remain independently gated by capability, locality/privacy, economic policy, resource binding, and human approval where required.
8. External ambiguity becomes `indeterminate`/reconciliation-required, never optimistic retry.
9. Human-only blockers are enforced in domain/service transition rules rather than only UI.
10. Bot, mission, task, delegate, provider run, tool execution, sandbox/cloud effect, evidence, verification, claim, cognition, skill, and receipt identities are cross-traceable.
11. The full current-Core regression suite plus Bot-specific acceptance matrix passes in a clean integration checkout.
12. Architecture, migration, operations, security, testing, and handoff documentation are current and reproducible.

## 4. Non-negotiable invariants

### 4.1 Identity is not authority

`BotManifest` identifies a persistent synthetic worker and its declared policies. It must never contain live credentials, reusable capability leases, approval decisions, raw provider tokens, or implied tool authority. Cloning/exporting a Bot never clones authority.

### 4.2 One authoritative mutation plane

Authoritative durable state commits through CAPT RuntimeService/EventStore semantics. CAPT-Bot may contribute domain commands/aggregates but may not create an independent JSON/SQLite/Markdown truth store. Caches, rendered Markdown, search indexes, UI state, and projections are disposable derived views.

### 4.3 One consequential execution path

Shell, filesystem mutation, Docker, remote cloud, browser, MCP, provider, credential-bearing calls, and other consequential effects pass through CAPT admission and ToolBroker/driver settlement. Bot orchestration cannot side-step those controls.

### 4.4 Cognition cannot widen authority

Model output, prompt-intelligence output, memory, Council/Cohort output, generated skills, and Bot-to-Bot messages are cognitive artifacts. They cannot mint capabilities, approve themselves, widen cost/locality policy, adopt external resources, or decide claims.

### 4.5 Delegation is coordination, not capability inheritance

`DelegateAssignment` binds who, what mission/task, ancestry/depth, lifetime, and state. It grants no filesystem, network, provider, credential, or tool power. Each consequential delegate action is independently admitted.

### 4.6 Trust changes friction, never proof

A trusted Bot may reduce approval friction when policy explicitly permits, but it never removes provenance, effect identity, receipts, verification, or claim adjudication.

### 4.7 Unknown external state is first-class

Timeout, disconnect, provider ambiguity, Docker ambiguity, Workflow ambiguity, or process ambiguity that cannot be resolved from evidence is `indeterminate`. Unknown is never silently rewritten as success, failure, or retry permission.

### 4.8 Locality and economics are independent gates

Configured does not mean allowed. Discoverable does not mean adopted. Free-tier capacity does not imply spending authority. Locality/privacy, capability, resource binding, and economics are independent checks.

### 4.9 Human-only states are structural

Human approvals, human claim review, external-resource adoption, and `blocked_human` exit rules must reject cognition/execution authors at the authoritative transition boundary.

### 4.10 Answer and receipt are separate surfaces

The default operator output is the human-facing answer. Structured execution JSON, raw evidence, receipts, and diagnostics remain expandable/inspectable rather than being dumped into the main response.

## 5. R5 repository architecture

### 5.1 End-state ownership

The repository should contain four classes of artifacts:

1. **Bot-domain code:** manifests/lifecycle, cognition, skills, Lab Board, delegation/standup, Bot orchestration, Bot-specific sandbox/cloud integration.
2. **Bot tests:** contracts, aggregate/service tests, restart/replay, adversarial execution, provider boundary, and end-to-end acceptance.
3. **Integration declarations:** compatibility manifest, Core seam inventory, migrations, integration tests, release evidence.
4. **Product surfaces:** Bot command/query API, chat/operator projection, standup, cognition/skill review, receipts/provenance, docs.

CAPT Core owns generic runtime primitives. R5 must eliminate the release architecture in which CAPT-Bot carries modified shadow copies of generic Core files.

### 5.2 Two-stage migration

Do not combine semantic rebase and architectural extraction in one opaque rewrite.

**Stage A — semantic rebase:** reconstruct the current Bot feature set on a clean checkout of current Core and prove behavioral parity/non-regression. Historical `CAPT_CORE.patch` is used only as a source map.

**Stage B — extraction:** move Bot-owned implementation behind an explicit CAPT-Bot package/integration boundary and reduce Core changes to generic extension seams. Run the same acceptance matrix after each extraction tranche.

A successful Stage A is a checkpoint, not the final R5 architecture.

### 5.3 Shared-Core seam classification

Every path in `integration/shared-modified-paths.txt` must be classified as exactly one of:

- **Already upstream:** current Core supplies the needed behavior; old hunk is discarded.
- **Generic Core seam:** behavior is generic infrastructure and should be implemented minimally in Core.
- **Bot-domain behavior:** behavior moves behind CAPT-Bot-owned code and an extension/interface boundary.

“Copy the old Core file into CAPT-Bot” is prohibited.

### 5.4 Proposed minimal Core extension seams

R5 should prefer the smallest generic seams that preserve one runtime:

- a service-construction hook allowing one CAPT-Bot service implementation to extend the existing `SteeredRuntimeService` rather than create a second service;
- a frozen startup authority registry composed from Core rules plus non-overriding extension rules;
- a frozen aggregate ownership/catalog composition so Bot aggregates participate in the same collision checks;
- a pre-ToolBroker tool-registration hook using the existing `ToolRegistry`;
- optional extension lifecycle/reconciliation hooks owned by the single `RuntimeComposition`;
- read-only extension query providers that share the same EventStore.

Extension contributions must be immutable after composition and fail on duplicate IDs, duplicate authority acts, aggregate-field ownership collisions, duplicate tool IDs, or incompatible schema versions. An extension may add authority rules but may not override or broaden a Core act.

If implementation proves a smaller seam is sufficient, use the smaller seam. Do not build a general plugin framework beyond what CAPT-Bot actually requires.

### 5.5 Compatibility manifest

Add `CAPT_BOT_COMPATIBILITY.json` with at least:

- CAPT-Bot release/schema version;
- minimum and tested CAPT Core identity;
- required extension-seam version;
- required Core contract/tool/driver versions;
- Bot schema and migration versions;
- feature gates;
- verification-evidence reference/digest.

Compatibility is checked before Bot activation. Mismatch fails closed with an exact diagnostic.

## 6. Domain contracts

### 6.1 Existing schema baseline

The existing Bot contract already defines:

- `BotRoleKind`: `crew | delegate`;
- `PromotionMode`: `locked | governed | autonomous`;
- model primary/fallback strategy;
- locality: `local | cloud | either` plus `local_only | cloud_allowed` private-data policy;
- collaboration `mayDelegate` and bounded `maxSpawnDepth`;
- cognition kinds including observation, user/derived facts, preference, decision, hypothesis, belief, contradiction, open question, procedure, skill, and relationship;
- cognitive states `proposed | promoted | rejected | revoked`;
- skill lifecycle from `idea` through `active`, plus `rejected | revoked | superseded`;
- Lab Board lifecycle including `blocked_human`;
- delegate state `active | completed | revoked | expired`.

R5 extends rather than replaces those contracts.

### 6.2 Bot manifest versioning and lifecycle

Add explicit manifest revision/supersession without changing stable `botId`. Identity fields stay immutable; policy changes create a new manifest revision and durable event lineage.

Add an operational lifecycle projection:

`registered -> active -> suspended -> retired`

Rules:

- activation requires compatible manifest/schema and all referenced policies resolvable;
- suspension blocks new work/delegation/learning promotion but preserves inspection/replay;
- retirement is terminal for new work and never deletes history;
- reactivation from `retired` under the same identity is forbidden;
- transition authority is explicitly enumerated and tested.

### 6.3 Cognitive candidates and retained cognition

Preserve R1 semantics and add:

- resolvable source/evidence references;
- contradiction links;
- supersession/tombstone lineage instead of destructive deletion;
- sensitivity-aware query/redaction;
- provenance links to Bot, mission, task, driver/provider run, ToolExecution, receipt/evidence where available;
- optional derived staleness/revalidation metadata that never rewrites historical source facts.

A promoted memory is evidence that CAPT retained a proposition under policy; it is not proof that the proposition is objectively true.

Promotion rules remain:

- `locked`: human decision required;
- `governed`: governance may decide under explicit policy;
- `autonomous`: may reduce human interruption but still requires a durable governance decision record. It never means “model writes memory directly.”

### 6.4 Skill Workshop

Preserve:

`idea -> draft -> review -> sandbox -> test -> red_team -> shadow -> approved -> active`

with `rejected`, `revoked`, `superseded`.

R5 binds stage evidence:

- `sandbox`: isolated-execution evidence;
- `test`: exact test command/result and artifact digest;
- `red_team`: adversarial findings + dispositions;
- `shadow`: non-authoritative observation metrics;
- `approved`: explicit final authority record;
- `active`: immutable artifact/package digest + compatibility binding.

Activation must fail if evidence is missing, mismatched, stale where freshness is required, or bound to a different revision.

### 6.5 Lab Board

Extend items with explicit references for Bot owner/assignee, task, delegate assignment, approval, current execution/reconciliation state, evidence, verification, claim state, blocking reason, and requested human action.

The Lab Board is a projection/work coordination object, not a substitute for mission/task/execution truth.

`blocked_human` remains human-only to exit.

### 6.6 DelegateAssignment

Preserve R2 rules and allow optional binding to a call/driver-run identity if the current Core interface supports it. Effective spawn depth is derived from ancestry and may only narrow. Descendants cannot widen an ancestor ceiling.

Delegates may use different model/provider strategies, but authority is never inherited from the parent assignment.

## 7. Canonical Bot turn

The canonical R5 turn is:

1. **Receive** authenticated human/operator input through the existing CAPT command surface.
2. **Resolve Bot** stable identity, active manifest revision, lifecycle state, role, and policy.
3. **Bind project/workspace** using current CAPT canonical workspace/project semantics.
4. **Assemble context** memory/context pack, prior receipts/evidence as allowed, selected skills, operator controls, mission/task, and relevant policy refs.
5. **Prompt intelligence** may transform/enhance the prompt but cannot execute effects or mutate durable authority.
6. **Plan** cognition proposes tasks, tool intents, delegate assignments, Council/Cohort work, or human requests.
7. **Admit** governance/capability/locality/economic/resource/HumanApproval gates evaluate each consequential intent.
8. **Execute** through existing driver/provider/ToolBroker paths only.
9. **Observe** exact effect identity and raw result; ambiguous outcome becomes reconciliation-required.
10. **Verify** verification plane evaluates evidence. Tool/provider output cannot self-certify.
11. **Claim** cognition/execution proposes claims; claim authority decides them.
12. **Learn** the turn may propose cognitive/skill candidates; promotion remains governed.
13. **Present** human-first answer plus separately inspectable execution receipt/provenance.
14. **Project** standup/Lab Board/query surfaces are rebuilt from authoritative state.

There is no model-output-to-mutation shortcut.

## 8. Model, provider, prompt-intelligence, Cohort, and Council semantics

Model choice is strategy, never identity. Bot policy may declare ordered preferences such as local-first, explicit provider allowlists, context requirements, or cost ceilings. Actual dispatch uses current CAPT provider/Hermes/local-driver infrastructure and operator controls.

Requirements:

- explicit user/provider selection is honored where policy permits;
- fallback occurs only when declared policy permits;
- local/free intent never silently falls through to paid execution;
- provider/model identity and relevant configuration are bound into run provenance;
- execution stays bound to the canonical workspace/context state;
- provider errors cannot widen locality or authority.

Cohorts/Councils/vessels are deliberative structures. They do not multiply authority. Persisted outputs retain model/vessel/source identity sufficient for audit.

## 9. Local execution: InversionSandbox

Preserve existing one-shot and persistent semantics:

- immutable local image identity;
- non-root / least-privilege execution;
- read-only rootfs with only explicit writable scopes;
- literal bounded argv/environment/cwd;
- immutable per-lease network policy;
- allowlist guardian topology revalidated before persistent exec;
- per-command capability admission and consumption while the resource persists;
- exact owner/session binding;
- EventStore-first crash reconciliation;
- no adoption by name/label alone;
- no recreate-on-ambiguity;
- cleanup only against positively proven identities;
- unproven command termination quarantines the lease.

Persistent resource existence never implies persistent permission.

## 10. Cloudflare native execution and Workflows

Preserve the R3/R4 control-plane boundary.

Preferred typed free-native surfaces remain:

- Workers: bounded coordination;
- Queues: bounded delegation transport;
- D1: bounded shared state;
- Browser Rendering: bounded browser evidence actions;
- Workers AI: eligible inference after catalog/economic admission;
- Workflows: durable provider orchestration evidence.

Arbitrary compute remains unavailable under `free_only` unless a separately authorized backend is proven eligible.

### 10.1 Resource discovery/adoption

Discovery is GET/read-only information. Execution requires exact candidate -> adoption proposal -> one-use human approval -> atomic approval consumption + binding creation. No Bot/model/Workflow/inventory path may auto-adopt an external resource.

### 10.2 Economics

Provider ceilings are inputs, not permission. Preserve trusted UTC quota buckets, operation-scoped transactional reservations, immutable source/catalog digests, conservative accounting, and locked reservations under ambiguous dispatch.

Time-sensitive provider limits in historical R3/R4 docs must be reverified before an R5 release and stored as dated policy evidence rather than immortal constants.

### 10.3 Workflow truth boundary

Workflow provider state is evidence. `complete` at Cloudflare never marks a CAPT mission/task complete without CAPT evidence/verification/claim transitions.

Ambiguous start/event delivery is reconciled against the deterministic instance identity; it is not reissued under a new identity.

## 11. Human-first operator product

R5 must expose a coherent operator surface, independent of whether the first implementation is CLI/TUI/macOS/web/API.

Minimum product capabilities:

- list/inspect Bots and active manifest revision;
- activate/suspend/retire where authorized;
- start/continue a Bot conversation/work request;
- inspect current mission/task/delegate lineage;
- inspect Lab Board / standup projection;
- review human approval requests and human-only blockers;
- inspect proposed cognition and decide when human authority is required;
- inspect Skill Workshop state/evidence and approve/revoke where authorized;
- inspect current tools/providers/locality/economic eligibility;
- expand execution receipt/provenance separately from the primary answer;
- surface indeterminate/reconciliation-required work conspicuously;
- never imply completion from provider/tool output alone.

JSON is an advanced/expandable evidence surface, not the default human result.

## 12. Query and projection contract

Add Bot read APIs without creating mutation shortcuts. At minimum provide read-only queries for:

- Bots + lifecycle + active manifest revision;
- cognitive candidates and promoted/revoked history with sensitivity filtering;
- skills + evidence/lifecycle;
- Lab Board;
- delegate assignments and ancestry;
- sandbox leases/reconciliation state;
- adopted cloud resources and usage reservations;
- Bot-centric mission/task/run/evidence/verification/claim linkage;
- latest human-facing answer + associated receipt reference.

Derived expiry/staleness fields must be labeled derived, as current Core does for other projections; they must not rewrite stored state.

## 13. Restart, replay, and reconciliation

R5 must prove deterministic replay and conservative recovery across:

- Bot manifest/lifecycle;
- cognition decisions;
- skill transitions;
- Lab Board;
- delegate assignments;
- ToolExecutions;
- persistent sandbox leases;
- Cloudflare usage reservations/resource bindings/Workflow identities;
- evidence/verification/claims;
- answer/receipt association.

On restart, reconciliation begins from durable CAPT state and compares external systems against exact stored identities. External inventory is evidence, not authority.

No recovery path may silently create a replacement external resource under an existing durable identity.

## 14. Security model

Required adversarial cases include:

- Bot clone/import attempts to inherit authority;
- model output attempting to mint/alter capability grants;
- cognition attempting human-only transitions;
- delegate depth/expiry/mission/task escape;
- stale or revoked skill activation;
- path/network/environment escape from sandbox;
- external resource name collision/adoption confusion;
- provider/model fallback violating locality/cost policy;
- ambiguous effect followed by duplicate retry;
- forged/mismatched execution receipts;
- cross-session sandbox reuse;
- stale manifest revision or compatibility downgrade;
- extension authority rule attempting to override a Core act;
- aggregate field ownership collision;
- duplicate tool IDs or descriptor substitution;
- sensitive cognition leaking through projections/standup/receipts.

Every denial that is security-relevant should have an auditable reason without logging raw secrets.

## 15. Testing and proof gates

Historical verification is useful evidence but not an R5 result. R5 must generate new current-head evidence.

Required gates:

1. schema generation/drift check;
2. unit tests for each Bot aggregate and authority transition;
3. service tests for idempotency/versioning/actor gates;
4. current Core authority and projection regression tests;
5. tool-registration/composition uniqueness tests;
6. Bot end-to-end turn with no consequential tools;
7. governed local tool turn;
8. persistent InversionSandbox create/exec/close/restart/adversarial tranche;
9. Cloudflare unit/integration tests with no unauthorized paid effect;
10. Workflow indeterminacy/reconciliation tests;
11. cognition promotion and revocation tests;
12. Skill Workshop evidence-chain tests;
13. delegation ancestry/depth/expiry tests;
14. answer/receipt separation tests;
15. replay/restart equivalence tests;
16. secret/redaction/logging tests;
17. exact full current-Core suite;
18. Bot-specific full suite;
19. static/lint/type/contract hygiene appropriate to changed code;
20. `git diff --check`, staged-file review, clean worktree;
21. resource-leak checks for local sandboxes;
22. source-provenance/compatibility manifest validation.

A skipped test is not a pass. Each skip/deselect must be classified as intentional environment dependency or unresolved gap.

## 16. Migration plan

### R5.0 Inventory and freeze

- inventory local and remote worktrees;
- record current Core/Bot SHAs;
- preserve historical patch/provenance;
- map every old shared hunk against current Core;
- establish a clean integration worktree.

### R5.1 Semantic rebase

- port Bot-owned features onto current Core with minimal changes;
- preserve current Core authority/projection/operator semantics;
- make old Bot tests pass after adapting only for intentional current contracts;
- add regression tests for post-isolation Core changes most likely to be overwritten by stale patch logic.

### R5.2 Extension boundary

- introduce the minimal generic Core seams actually required;
- extract Bot-owned service/aggregate/tool lifecycle from modified Core files;
- compose Bot extension into one `RuntimeComposition`;
- make duplicate/override conflicts fail at startup.

### R5.3 Product lifecycle

- manifest revisions + Bot active/suspended/retired state;
- Bot-centric queries;
- canonical request-to-result orchestration;
- human-first answer + expandable receipt association.

### R5.4 Governed learning and collaboration closure

- cognition lineage/sensitivity/supersession;
- Skill Workshop evidence gates;
- Lab Board reference closure;
- delegate lineage/run binding where supported;
- Cohort/Council provenance.

### R5.5 Execution closure

- current Core tool/provider integration;
- InversionSandbox current-head validation;
- Cloudflare/Workflow current-head validation and quota-policy re-verification;
- reconciliation and indeterminacy coverage.

### R5.6 Release proof

- full acceptance matrix;
- compatibility manifest;
- migration/release evidence;
- current README and architecture docs;
- exact verified SHAs and test commands/results.

## 17. Explicit non-goals

R5 does **not** require:

- a new generic distributed-agent platform;
- a new capability model;
- a new verification/claim system;
- a second memory database as canonical Bot truth;
- hidden autonomous resource creation;
- unrestricted arbitrary cloud compute;
- self-modifying authority;
- automatic skill activation from model output;
- automatic adoption of discovered external resources;
- replacing CAPT Cohorts/Councils with a Bot-specific duplicate;
- rewriting every CAPT surface merely to make CAPT-Bot look standalone.

## 18. Required implementation artifacts

The R5 implementation must leave behind:

- `CAPT_BOT_COMPATIBILITY.json`;
- current architecture and threat model;
- Core seam/rebase disposition matrix for every historical shared path;
- migration notes from isolated R4 to R5;
- test/verification report with commands, environment, pass/skip/deselect counts;
- source/provenance update preserving the original isolation lineage plus current convergence lineage;
- operator runbook for activation, approvals, reconciliation, and troubleshooting;
- release checklist proving no second authority/execution plane exists.

## 19. Final architectural test

A reviewer should be able to answer all of these without reading implementation internals:

- What is a Bot?
- What can it remember, and who decides persistence?
- What authority does it have right now, and where is that authority stored?
- What did it delegate, to whom, under what mission/task/depth/expiry?
- What external effects did it request and which were actually observed?
- Which outputs are evidence versus verified facts versus approved claims?
- What happened if an external result became ambiguous?
- Which model/provider/tool/locality/economic rules governed a turn?
- Which skill revision ran and what evidence made it active?
- What is the human-facing answer, and where is its execution receipt?
- Can the whole state be replayed after restart without inventing external truth?
- Can CAPT-Bot be removed without leaving a second hidden authority plane behind?

If any answer requires trusting model prose, UI convention, or undocumented side state, R5 is not complete.

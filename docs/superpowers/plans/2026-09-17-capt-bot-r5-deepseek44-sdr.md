# CAPT Bot R5 DeepSeek-44 SDR

> **For agentic workers:** REQUIRED execution discipline: isolate work, use test-first changes, preserve one CAPT authority/runtime plane, and merge only after evidence-backed review. The 44 vessels are parallel perspectives and workstreams; they are not permission to create 44 uncontrolled execution paths.

**Goal:** Rebase the verified CAPT-Bot R1-R4 feature set onto current CAPT Core, extract it into a separately versioned CAPT-Bot product/domain layer, close the request-to-result product path, and generate current-head verification evidence without regressing Core authority, provenance, or operator behavior.

**Architecture:** CAPT-Bot contributes persistent Bot identity/cognition/skill/collaboration/product behavior to exactly one CAPT runtime. Current Core remains sovereign for RuntimeService/EventStore mutation, authority, capabilities, approvals, ToolBroker/driver execution, evidence, verification, and claims. R5 first proves a semantic rebase, then extracts Bot-owned behavior behind the smallest generic Core seams needed for independent versioning.

**Tech Stack:** Python 3.8+ compatible codebase; `setuptools`; CAPT Core `capt-solo` 0.5.x lineage; JSON Schema 2020-12 contracts; SQLite/EventStore; pytest; Ruff where configured; Docker for real InversionSandbox acceptance; Cloudflare REST/Workers-native surfaces under existing policy; Git worktrees/branches for vessel isolation.

**Spec:** `docs/architecture/CAPT_BOT_CONVERGENCE_R5.md`

## Global constraints

- Current CAPT-Bot starting head: `d43c0a26314cbc5e1dec091e888d673fad90fcb8` unless a later local/remote inventory proves a newer intentional head.
- Historical Bot source integration point: CAPT Core `c93200626b621bf7a27c1fa6cfcbf04773121c35`.
- Current Core convergence target used to author this SDR: `520aa5f6d44839e61b2392a01a2f6a7983be4276`.
- Do not blindly apply `integration/CAPT_CORE.patch` to current Core.
- Do not overwrite current Core files with their historical Bot-isolation versions.
- Do not create a second `RuntimeService`, `EventStore`, `ToolBroker`, capability/approval authority, verification plane, or claim authority.
- Extension authority may add new Bot acts but must not override/broaden existing Core acts.
- External ambiguity is `indeterminate`/reconciliation-required; never retry merely because the response is missing.
- No paid/cloud fallback may occur implicitly from local/free intent.
- No external resource may become execution authority through discovery alone.
- No model/Cohort/Council/vessel may self-authorize durable cognition, skills, capabilities, approvals, claims, or external-resource adoption.
- Human-first answer and execution receipt remain separate presentation surfaces.
- No mocks/stubs/fake integrations may be presented as finished production capability. Test doubles are acceptable only inside tests and must not be confused with real integration proof.
- Historical test counts are context, not R5 proof. Generate fresh current-head evidence.
- Any skipped/deselected test must be explicitly classified.
- Preserve source/provenance lineage.

---

# 1. DeepSeek execution contract

## 1.1 Primary instruction to the main DeepSeek v4 process

Act as the **R5 Convergence Integrator**. You own the canonical integration branch and final truth claims. Launch exactly **44 vessels in parallel**, arranged as 11 cohorts of 4. Vessels may inspect, reason, test, and produce isolated patches, but none may merge directly to the canonical branch. You must review evidence and merge/cherry-pick intentionally.

Do not serialize the 44 vessel inference tasks. Their purpose is independent perspective and bounded parallel production. Sequentiality is allowed only in the physical merge/test sequence after their outputs exist.

Every vessel performs three explicit internal passes before final output:

1. **Reconstruct:** inspect the relevant current code, tests, contracts, historical Bot source, and newer Core behavior. State what is proven versus inferred.
2. **Adversarial:** identify stale assumptions, authority leaks, duplicated planes, merge hazards, regression risks, and simpler alternatives.
3. **Deliver:** produce either an isolated patch+tests or a concrete rejection/recommendation with exact evidence and paths.

A vessel that cannot prove a safe implementation should return a blocker, not invent an API or claim success.

## 1.2 Vessel output envelope

Each vessel must return a compact machine-readable summary plus human notes containing:

- vessel ID and cohort;
- branch/worktree name;
- source SHAs inspected;
- files read;
- files changed, if any;
- tests added/changed;
- commands run and exact outcomes;
- assumptions;
- authority/security impact;
- compatibility impact;
- unresolved blockers;
- merge recommendation: `accept | accept_with_changes | reject | analysis_only`;
- patch/commit SHA when code was produced.

No vessel may report “passes” unless it actually ran the stated command.

## 1.3 Isolation topology

Create one canonical integration branch from the verified starting point, recommended:

`r5/capt-bot-convergence`

Create one isolated branch/worktree per vessel using stable names:

`r5/c01-v01-baseline-builder` ... `r5/c11-v44-release-integrator`

Vessels must not share writable worktrees. They may read the same repositories. Generated provider caches, virtualenvs, and Docker resources must not be committed.

The main integrator merges only reviewable commits or exact patches. Never copy a whole vessel worktree over the integration branch.

## 1.4 Two repositories, one integration proof

R5 may require changes in both:

- `knowurknottty/CAPT-Bot`
- `knowurknottty/CAPT_core`

Treat them as separate repositories with separate branches/commits. A Bot commit that depends on a Core seam must record the exact Core commit it was tested against. The final compatibility manifest must identify both.

Do not hide Core changes inside the Bot repo's historical patch.

---

# 2. 44-vessel topology

Each cohort has four roles:

- **A / Builder-Reconstructor:** produces the minimal implementation candidate.
- **B / Adversary:** tries to falsify the candidate and current assumptions; usually analysis/tests, not broad refactors.
- **C / Proof Engineer:** creates focused tests/replay/restart/security proof and runs gates.
- **D / Integrator-Simplifier:** independently seeks a smaller seam, reviews compatibility, and proposes merge disposition.

## Cohort 01 — Baseline, provenance, local/remote inventory

**V01 Builder:** inventory CAPT-Bot remote tree, commits, docs, tests, schemas, `SOURCE_PROVENANCE.json`, `integration/*`; inventory current Core head and post-isolation commits. Produce `docs/r5/R5_BASELINE_INVENTORY.md` and machine-readable path matrix.

**V02 Adversary:** search for stale source claims, duplicate files, missing tests, historical patch hunks that now contradict Core, and any local-only work if the Mac is visible. Produce mismatch report.

**V03 Proof:** verify provenance manifest semantics, recompute hashes where possible, test `tests/test_source_provenance_manifest.py`, and define current convergence provenance requirements.

**V04 Integrator:** classify each entry in `integration/shared-modified-paths.txt` as `already_upstream | generic_core_seam | bot_domain | unresolved`, with evidence and current-Core line/path references.

**Cohort deliverable:** no architecture changes until the baseline matrix is accepted.

## Cohort 02 — Core extension seam and semantic rebase

**V05 Builder:** create the smallest current-Core seam enabling Bot composition without a second runtime. Prefer service construction/injection, frozen extension authority contributions, aggregate catalog composition, existing ToolRegistry registration, and lifecycle hooks only if proven necessary.

**V06 Adversary:** attempt to show that V05 creates a plugin framework larger than needed, allows act overrides, creates multiple services, bypasses existing admission, or destabilizes current callers.

**V07 Proof:** write Core tests for duplicate extension IDs, authority-act collisions, aggregate ownership collisions, tool ID collisions, exact single-service/single-store identity, and default behavior with no Bot extension.

**V08 Integrator:** compare three implementations: minimal explicit Bot hook, generic extension SPI, and service-subclass/factory injection. Choose the smallest solution satisfying R5, documenting rejected complexity.

**Required Core property:** a normal Core runtime with no Bot extension must behave byte/semantically as before except for intentionally introduced generic seam code.

## Cohort 03 — Bot contracts, manifest revision, lifecycle, aggregates

**V09 Builder:** port existing Bot/Cognitive/Skill/LabBoard/Delegate contracts to the R5 package boundary; add manifest revision/supersession and Bot lifecycle `registered -> active -> suspended -> retired` with explicit events.

**V10 Adversary:** test identity mutability, stale manifest activation, retired resurrection, schema downgrade, malformed source refs, field-ownership collision, and actor-rule confusion.

**V11 Proof:** contract validation, aggregate transition, replay, idempotency, optimistic version, and migration tests. Prove existing R1/R2 records replay unchanged or are migrated deterministically.

**V12 Integrator:** ensure schema additions are minimal and generated bindings are produced from schema source rather than hand-edited. Reject any lifecycle field that belongs in a separate aggregate/projection.

## Cohort 04 — Cognition, memory linkage, Skill Workshop, Lab Board

**V13 Builder:** implement cognition source/evidence linkage, contradiction/supersession lineage, sensitivity-aware projection, and governed promotion hooks into existing CAPT memory/context behavior without making Markdown or a second DB canonical.

**V14 Adversary:** try to make cognition self-promote, leak secret/user-sensitive items through standup/query/receipt, rewrite historical facts during supersession, or confuse “retained proposition” with verified truth.

**V15 Proof:** tests for `locked`, `governed`, and `autonomous` promotion modes; revocation; sensitivity filtering; contradiction/supersession; restart replay; and context selection not bypassing memory policy.

**V16 Integrator:** close Skill Workshop stage evidence and Lab Board reference semantics. Ensure skill activation binds exact artifact/revision/evidence; `blocked_human` remains human-only to exit.

## Cohort 05 — Delegation, crew, standup, Cohorts/Councils

**V17 Builder:** rebase `DelegateAssignment` and `build_lab_standup()` onto current mission/task projections; add optional run/call binding only if current Core identity permits it cleanly.

**V18 Adversary:** attempt depth widening, cross-mission task binding, expired assignment reuse, double-active delegate assignment, authority inheritance, parent revocation escape, and terminal-state resurrection.

**V19 Proof:** ancestry/depth/expiry/mission/task/replay tests; deterministic standup ordering; secret/lease exclusion; current Core projection non-regression.

**V20 Integrator:** bind current Model Council/Cohort output as deliberative provenance only. Prove no vessel/Council output can author execution or approval acts merely because it is persisted.

## Cohort 06 — Canonical Bot request-to-result orchestration

**V21 Builder:** implement the canonical turn coordinator: resolve Bot -> project/workspace -> context/memory/skills -> prompt intelligence -> planning -> admission -> execution -> evidence -> verification -> claim -> learning proposal -> human answer + receipt link.

**V22 Adversary:** search for any direct model-output-to-effect or model-output-to-durable-state path; duplicate provider dispatch; workspace drift; stale context; receipt/result conflation; or prompt-intelligence bypass.

**V23 Proof:** build deterministic end-to-end tests for no-tool answer, denied tool intent, approved governed tool intent, provider failure, indeterminate effect, human blocker, cognition proposal, and restart continuation.

**V24 Integrator:** minimize the coordinator. It should orchestrate existing services rather than become a god object. Split pure resolution/projection helpers from mutation orchestration when file responsibility becomes mixed.

## Cohort 07 — InversionSandbox current-head closure

**V25 Builder:** port/rebase one-shot and persistent InversionSandbox against current ToolBroker/authority/composition behavior. Preserve existing lease state and reconciliation semantics.

**V26 Adversary:** attack owner/session checks, image substitution, mount/path escape, network widening, guardian drift, parent environment inheritance, privileged/root exec, timeout ambiguity, orphan adoption, and delete-by-name patterns.

**V27 Proof:** run focused unit/integration/restart tests plus real-Docker tests when Docker is available. Record exact image identity and prove zero leaked CAPT sandbox resources after tests.

**V28 Integrator:** ensure persistent sandbox lifetime does not become capability lifetime. Confirm every persistent exec consumes fresh admitted authority and no fallback to `terminal.docker`/one-shot happens on failure.

## Cohort 08 — Cloudflare native + Workflows current-head closure

**V29 Builder:** rebase Cloudflare adapters, resource inventory/adoption, usage ledger, native surfaces, artifacts, and Workflow orchestration behind current composition seams.

**V30 Adversary:** attack paid fallback, quota-day spoofing, stale catalog use, resource-name ambiguity, unapproved adoption, endpoint/resource mismatch, secret leakage, duplicate Workflow event/start after ambiguity, and provider status becoming CAPT truth.

**V31 Proof:** run Cloudflare unit/integration tests without making unauthorized paid effects. Reverify time-sensitive provider policy facts before encoding release defaults; store dated evidence/source digest. Live mutation requires explicit human authority.

**V32 Integrator:** prove native free routing is typed and conservative. `ARBITRARY_COMPUTE` must remain unavailable under `free_only` unless a new explicitly proven/authorized path exists.

## Cohort 09 — Queries, operator API, human-first answer/receipt UX contract

**V33 Builder:** implement read-only Bot-centric query surfaces and a stable operator-facing result envelope: primary human answer plus separate expandable receipt/provenance reference.

**V34 Adversary:** test secret leakage, raw JSON flooding, misleading “done” states, stale derived expiry, missing receipt association, receipt forgery/mismatch, and query paths that mutate state.

**V35 Proof:** query/replay tests, answer/receipt separation tests, sensitivity filtering, derived-state labeling, stable deterministic serialization, and cross-link integrity.

**V36 Integrator:** produce an API/CLI-neutral contract so TUI/macOS/web surfaces can consume the same semantics. Avoid implementing multiple UI stacks in R5 unless one is required for end-to-end proof.

## Cohort 10 — Security, authority, replay, migration, chaos

**V37 Builder:** create the R5 threat model and security invariants test suite spanning clone/import, actor spoofing, act collision, compatibility downgrade, resource adoption, cognition/skill authority, delegation, sandbox/cloud ambiguity, and receipts.

**V38 Adversary:** run the “hostile maintainer” review: assume a future contributor tries to bypass CAPT via convenience helpers, cached credentials, direct subprocess/network calls, direct SQLite writes, mutable extension registries, or implicit retries.

**V39 Proof:** crash/restart/replay equivalence at important transaction boundaries; fault injection around effect-observed/settlement, sandbox create/close, Cloudflare reservations, adoption transactions, and answer/receipt commit association.

**V40 Integrator:** design/verify deterministic migration from historical isolated R4 state to R5. No destructive migration; retain audit lineage and original source provenance.

## Cohort 11 — Full verification, release evidence, docs, integration adjudication

**V41 Builder:** create compatibility manifest, release evidence structure, migration/runbook docs, and updated README. Do not claim results before tests run.

**V42 Adversary:** audit every public statement and “verified” claim against actual current-head evidence. Flag stale historical numbers, provider limits, or capabilities presented as current.

**V43 Proof:** run the complete acceptance matrix in a clean integration checkout, capture exact commands/results/environment/SHAs, classify skips, run leak checks, and verify clean trees.

**V44 Integrator:** independently review the final integrated diff for scope, architecture, authority-plane duplication, unresolved conflicts, dead code, missing docs, and release blockers. This vessel has veto power by evidence: if a critical invariant is unproven, final status is not “done.”

---

# 3. Target file structure

The exact migration may vary after Cohort 02 proves the minimal seam, but the target should converge toward clear ownership similar to:

```text
CAPT-Bot/
  pyproject.toml
  README.md
  CAPT_BOT_COMPATIBILITY.json
  SOURCE_PROVENANCE.json
  capt_bot/
    __init__.py
    compatibility.py
    integration.py
    runtime_service.py
    authority_rules.py
    orchestration.py
    queries.py
    receipts.py
    locality.py
    standup.py
    resource_adoption.py
    sandbox_reconciliation.py
    aggregates/
      bot.py
      cognitive_candidate.py
      delegate_assignment.py
      skill_candidate.py
      lab_board.py
      sandbox_lease.py
      cloudflare_resource_binding.py
    tools/
      adapters/
      backends/
  contracts/
    schema/
      bot.schema.json
      sandbox.schema.json
    fixtures/
    generated/
  tests/
    unit/
    integration/
    adversarial/
    acceptance/
  docs/
    architecture/
    threat-model/
    migration/
    operations/
    verification/
    r5/
```

This is an ownership target, not permission for a blind mass rename. Stage A may temporarily preserve old paths until semantic parity is proven. Stage B moves code in bounded tranches with tests proving behavior before and after.

### 3.1 Core paths that should be touched only when the seam genuinely requires it

Likely current-Core candidates include:

- `capt_runtime/composition.py` — construction/extension hook;
- `capt_runtime/authority.py` — frozen authority contribution seam, if needed;
- aggregate ownership/catalog code — extension registration, if needed;
- service construction — exactly one service instance with Bot extension capability;
- tests proving unchanged no-extension behavior.

Avoid Bot-specific implementation in generic Core modules when it can live in `capt_bot`.

### 3.2 Historical shared paths requiring explicit disposition

The R5 baseline matrix must account for every existing historical shared path, including:

- `capt_runtime/aggregates/__init__.py`
- `capt_runtime/authority.py`
- `capt_runtime/composition.py`
- `capt_runtime/governed_service.py`
- `capt_runtime/replay.py`
- `capt_runtime/services.py`
- `capt_runtime/tool_broker.py`
- `capt_runtime/tools/adapters/__init__.py`
- `capt_runtime/tools/backends/docker.py`
- `capt_runtime/tools/builtins.py`
- relevant common/event/tool schemas and generated bindings
- affected Core tests.

Each receives a written `keep current | minimal generic seam | move to Bot | obsolete` disposition.

---

# 4. Integration sequence and merge gates

The 44 vessels run in parallel, but the canonical branch merges in evidence-safe dependency order.

## Gate 0 — Source freeze

Before merging code:

- [ ] record remote SHAs;
- [ ] inspect local worktrees if available;
- [ ] preserve any legitimate local-only Bot delta on an explicit branch;
- [ ] verify no secrets/untracked build artifacts are being swept into source;
- [ ] create the baseline disposition matrix;
- [ ] establish clean integration branches.

**Stop condition:** if local/remote state is ambiguous, preserve both and document the ambiguity. Do not overwrite one with the other.

## Gate 1 — Semantic rebase

Merge only enough changes to make the historical Bot feature set run against current Core.

- [ ] use current Core implementations as the starting point for shared files;
- [ ] port Bot-specific behavior hunk-by-hunk;
- [ ] run focused historical Bot tests;
- [ ] run current Core tests around every touched shared subsystem;
- [ ] add regression tests for post-isolation Core behavior that the old patch would have overwritten.

**Stop condition:** do not begin architectural extraction while basic semantic parity is unknown.

## Gate 2 — Generic extension seam

- [ ] merge the smallest Core seam chosen by Cohort 02;
- [ ] prove default Core behavior with zero extensions;
- [ ] prove exactly one RuntimeService/EventStore/ToolBroker instance with CAPT-Bot enabled;
- [ ] freeze extension metadata/rules at startup;
- [ ] reject collisions/overrides.

**Stop condition:** any extension API that permits runtime mutation of authority rules after startup is rejected.

## Gate 3 — Bot-domain extraction

Move Bot-owned code from historical `capt_runtime/*` overlay paths into the Bot package in bounded groups:

1. pure aggregates/contracts;
2. read-only projections;
3. domain service/commands;
4. orchestration;
5. InversionSandbox integration;
6. Cloudflare integration.

After each group:

- [ ] old and new focused tests pass;
- [ ] import/call sites are updated;
- [ ] no duplicate implementation remains active;
- [ ] replay semantics remain equivalent;
- [ ] Core regression subset passes.

## Gate 4 — Product closure

- [ ] manifest revisions/lifecycle;
- [ ] Bot query API;
- [ ] canonical turn orchestration;
- [ ] answer/receipt separation;
- [ ] cognition/skill/Lab Board closure;
- [ ] delegation/Council provenance.

## Gate 5 — Execution closure

- [ ] InversionSandbox current-head acceptance;
- [ ] Cloudflare/Workflow current-head acceptance;
- [ ] current provider/local driver integration;
- [ ] indeterminacy/reconciliation proof.

## Gate 6 — Full release proof

- [ ] clean checkout of exact Bot/Core SHAs;
- [ ] contract generation/drift;
- [ ] all focused suites;
- [ ] full current Core suite;
- [ ] full Bot suite;
- [ ] real-Docker acceptance where environment permits;
- [ ] secret/static/lint/hygiene checks;
- [ ] resource leak checks;
- [ ] compatibility/provenance verification;
- [ ] clean worktrees;
- [ ] final V44 review.

---

# 5. Required interfaces and semantics

The names below are architectural contracts; implementation may refine exact Python signatures if tests and docs stay consistent.

## 5.1 Compatibility

Provide a pure compatibility check conceptually equivalent to:

```python
check_compatibility(bot_manifest, core_identity, extension_api_version) -> CompatibilityResult
```

It must fail before Bot activation on incompatible Core/schema/seam versions. Failure is diagnostic and side-effect-free.

## 5.2 Bot service

Bot mutation commands must execute through the one composed RuntimeService authority context. Required semantic commands include:

- register Bot / new manifest revision;
- activate/suspend/retire Bot;
- propose/decide/revoke cognition;
- create/transition/revoke/supersede skill candidate;
- create/transition Lab Board item;
- assign/transition delegate assignment;
- resource-adoption binding where still Bot-owned;
- sandbox lease lifecycle where still Bot-owned.

Every command requires validated metadata, explicit actor-kind authority, expected aggregate version/idempotency behavior, and durable events.

## 5.3 Queries

Queries are read-only and may derive labels such as `expired`/`stale` without mutating stored state. Sensitive records are filtered/redacted by caller scope.

## 5.4 Turn orchestration

The coordinator may call existing services but must not own a second transaction system. It should expose durable correlation IDs across Bot turn, mission/task, provider/driver run, ToolExecution, evidence, verification, claim, answer, and receipt.

## 5.5 Receipts

A receipt references exact execution/evidence records. It is not a model-authored narrative. Human answer text may refer to the receipt, but receipt integrity cannot depend on answer wording.

---

# 6. TDD requirements by component

For every production change, vessels should follow this local cycle:

1. add/modify a focused test that fails for the intended reason;
2. run only that test and record the failure;
3. make the smallest implementation change;
4. rerun the focused test;
5. run the nearest subsystem suite;
6. inspect diff for unrelated changes;
7. commit one coherent unit.

Do not create giant “R5 implementation” commits spanning unrelated systems.

### Example: authority collision

Test must prove an extension cannot redefine an existing Core act. Expected outcome is startup/composition failure before any Bot activation or external effect.

### Example: retired Bot

Test must prove a retired Bot cannot accept new work, delegate, or promote cognition, while historical queries/replay remain available.

### Example: answer/receipt

Test must prove the default human result contains the answer, references a receipt, and does not inline raw structured execution JSON unless explicitly requested.

### Example: ambiguous Workflow event

Test must prove ambiguous post-dispatch delivery locks/requires reconciliation and does not issue a second event under a new operation identity.

---

# 7. Acceptance scenarios

The final system must demonstrate these scenarios with evidence.

## A1 — Pure conversational turn

Human addresses an active crew Bot. Bot binds current project/workspace/context and returns an answer with no consequential tool execution. No capability is consumed. Receipt/provenance still identifies model/context/run appropriately.

## A2 — Denied consequential request

Bot proposes a filesystem/network/tool action outside authority. Admission denies it before dispatch. Human answer explains the blocker at a useful level; security audit records the denial without secrets.

## A3 — Human-approved action

Bot requests an action requiring approval. Approval is durably requested; only human decision can approve. Exact approved scope is consumed once. Result/evidence/receipt bind the approved operation.

## A4 — Delegate work

Crew Bot creates a bounded delegate assignment to an existing delegate identity for a mission/task. Delegate acts only inside independent admitted authority. Completion of assignment does not itself mark task/mission verified complete.

## A5 — Human blocker

Lab Board item enters `blocked_human`. Agents may enrich evidence/request, but cannot transition it out. Human action resolves it.

## A6 — Governed learning

Turn proposes a new cognitive candidate. Under `locked`, model cannot promote. Under `governed`/`autonomous`, promotion still leaves a durable governance decision record. Revocation remains auditable.

## A7 — Skill lifecycle

A generated/imported skill progresses only with exact stage evidence. Missing red-team or test evidence blocks approval/activation. Active artifact digest matches the reviewed revision.

## A8 — Persistent local sandbox

Governed create -> multiple separately admitted execs -> close. Resource persists, authority does not. Restart/reconciliation proves exact identity. No leaked sandbox resources after closure/test.

## A9 — Ambiguous local command

Host timeout cannot prove in-container termination. ToolExecution and lease become indeterminate/quarantined. No automatic reuse/retry.

## A10 — Cloud resource discovery

Cloudflare inventory sees a resource. It remains unadopted. Only exact proposal + human approval + atomic binding makes it an executable target.

## A11 — Free-only Cloudflare

A work request routes only to an eligible typed free-native surface within CAPT's internal budget. Paid-required/unknown/stale catalog status fails closed.

## A12 — Workflow ambiguity

Workflow start/event loses response after dispatch. CAPT retains deterministic identity/reservation and reconciles; it does not fire a duplicate under a new identity.

## A13 — Provider fallback

Primary provider fails. If fallback is not explicitly allowed under Bot/operator locality/economic policy, the run stops. If allowed, fallback identity is visible in provenance.

## A14 — Secret cognition query

A low-scope projection/standup cannot expose `secret` cognition or raw credentials. Authorized inspection remains provenance-bound.

## A15 — Restart replay

Kill/restart after representative transaction boundaries. Replayed CAPT state matches committed history; unproven external truth remains unproven and requires reconciliation.

## A16 — Clone/import

Copy Bot manifest/state to a new environment. Identity/policy data can be imported as allowed, but live authority/credentials/capability leases do not come with it.

## A17 — Core-without-Bot

Run current Core with no CAPT-Bot extension. Behavior and tests remain valid; Bot-specific code is not required for standard CAPT operation.

## A18 — Human-first result

A complex tool-backed Bot turn ends with a readable answer. Raw JSON/receipts are available via explicit expansion/reference, not presented as the answer itself.

---

# 8. Verification record format

Create a final file under `docs/verification/` containing:

- Bot SHA;
- Core SHA;
- OS/architecture/Python;
- Docker availability and exact image identity used;
- external provider tests actually run versus intentionally not run;
- contract generation result;
- focused suite results;
- full Core result;
- full Bot result;
- slow/live skipped/deselected classification;
- lint/static/hygiene result;
- leak checks;
- compatibility manifest digest;
- unresolved limitations;
- explicit statement of what is and is not proven.

Never recycle the historical `1,687 passed` result as the R5 result. It is historical evidence from the September 9 sandbox verification only.

---

# 9. Merge adjudication rules

When vessel proposals conflict, choose by the following order:

1. preserves CAPT authority/evidence invariants;
2. matches current Core behavior instead of stale historical behavior;
3. smaller API/seam surface;
4. stronger falsifiable tests;
5. fewer duplicate concepts/datastores/execution paths;
6. clearer restart/replay semantics;
7. lower provider/cost/security risk;
8. lower implementation complexity;
9. backwards compatibility where it does not violate higher priorities.

Do not average conflicting architectures. Pick one and remove the rejected path.

A merge candidate is rejected if it:

- introduces direct subprocess/network/filesystem/cloud calls outside admitted Core tool/driver boundaries;
- adds a second durable Bot truth store;
- lets model/cognition decide its own authority;
- mutates authority registry after composition;
- treats provider state as verified CAPT completion;
- silently retries ambiguous effects;
- makes paid/cloud fallback implicit;
- relies on UI convention for human-only enforcement;
- weakens current Core authority checks;
- overwrites newer Core files with old isolation copies.

---

# 10. Recommended commit structure

Use small reviewable commits such as:

1. `docs(r5): record convergence baseline and seam dispositions`
2. `refactor(core): add minimal immutable runtime extension seam`
3. `test(core): prove extension collision and single-runtime invariants`
4. `feat(bot): package existing bot aggregates and contracts`
5. `feat(bot): add manifest revisions and lifecycle`
6. `feat(bot): close cognition and skill evidence lifecycle`
7. `feat(bot): rebase delegation and standup projections`
8. `feat(bot): add canonical governed turn coordinator`
9. `feat(bot): expose bot-centric read projections and receipts`
10. `refactor(bot): rebase inversion sandbox integration`
11. `refactor(bot): rebase cloudflare and workflow integration`
12. `test(bot): add adversarial restart and authority matrix`
13. `docs(bot): add compatibility migration operations and release evidence`

Actual commit boundaries should follow coherent tested units; do not force this list if a smaller logical split is better.

---

# 11. Final completion criteria for DeepSeek

Do not report R5 complete until all are true:

- [ ] local/remote source state reconciled or any unavailable local state explicitly declared;
- [ ] historical patch fully dispositioned;
- [ ] semantic rebase proven against current Core;
- [ ] independent CAPT-Bot ownership boundary exists;
- [ ] no second runtime/authority/execution truth plane exists;
- [ ] Bot manifest lifecycle/versioning is durable;
- [ ] cognition promotion and revocation are governed and replayable;
- [ ] Skill Workshop evidence gates are enforced;
- [ ] delegation cannot widen authority or depth;
- [ ] canonical Bot request-to-result path exists;
- [ ] provider/model/locality/economic policy is explicit;
- [ ] InversionSandbox current-head proof passes where environment permits;
- [ ] Cloudflare/Workflow current-head proof passes without unauthorized spending;
- [ ] ambiguity/reconciliation tests pass;
- [ ] query surfaces are read-only and sensitivity-aware;
- [ ] human answer and receipt are separated;
- [ ] compatibility manifest exists and fails closed on mismatch;
- [ ] migration/provenance lineage is preserved;
- [ ] full Core and Bot test evidence is recorded;
- [ ] final V44 independent review has no unresolved critical invariant;
- [ ] both repositories are clean at the recorded release SHAs.

If some environment-dependent proof cannot run, final status must be `implementation complete, verification incomplete` (or narrower), with the exact missing proof named. Do not convert lack of access into a pass.

---

# 12. Handoff prompt for the main DeepSeek v4 process

Use the following as the top-level operational instruction together with this SDR and `CAPT_BOT_CONVERGENCE_R5.md`:

> You are the CAPT-Bot R5 Convergence Integrator. Reconstruct reality before editing. Inspect the current CAPT-Bot repo, current CAPT Core, the full historical source/provenance payload, architecture docs R1-R4, sandbox specs/verification, current Core authority/composition/projection/provider changes, and any local-only worktree delta that is actually present. Launch exactly 44 vessels in parallel using the cohort/role map in this SDR. Each vessel performs reconstruct -> adversarial -> deliver passes and works in its own branch/worktree. Preserve one CAPT authority/runtime/execution truth plane. Treat historical patches as evidence, not commands. First achieve a test-proven semantic rebase onto current Core; then extract Bot-owned code behind the smallest immutable Core extension seam. Use test-first changes. Unknown external state is indeterminate, not retry permission. Models/cognition/vessels cannot grant themselves persistence, authority, approval, resource adoption, verified claims, or spending. Keep human answer separate from structured receipt/provenance. Merge only evidence-backed changes into the canonical integration branch, run the full R5 acceptance matrix, record exact SHAs/commands/results, and refuse to call the work complete when a critical invariant or environment-dependent proof remains unverified.

That prompt is deliberately shorter than the SDR. The SDR and architecture spec are the authoritative details; the prompt is the execution entry point.

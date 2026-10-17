# CAPT-Bot mission recovery UI contract

**Owner:** CAPT RuntimeService/EventStore. CAPT-Bot is an untrusted read/projection and explicitly confirmed command surface. TIA operates the same UI through its isolated semantic Chromium lane, never through the user's physical mouse.

## Active versus archived

The Missions rail shows only nonterminal missions. Completed, cancelled, or failed work remains durable and inspectable through Browse historical missions. The Kanban defaults to open cards, with a searchable Terminal archive. Clearing a visible board never deletes historical events.

## A blocked item always has a next action

Inspect receipts & next step performs read-only retrieval of exact mission state, linked tasks, approval summaries, linked DriverRun states, and event IDs/global sequences. No event payload, prompt content, tokens, or credential fields are exposed.

For the archived m-capt-issues-20260924-live mission, the inspector additionally queries only knowurknottty/CAPT_core through a fixed GitHub CLI read action, and checks existence of the five explicitly scoped local candidate repositories and four named evidence artifacts. GitHub and filesystem observations are separately labelled, never represented as EventStore authority. The GitHub snapshot is current only when fetched and explicitly can fail; a failure is not a zero-issues conclusion.

A terminal mission can yield a new successor draft, not a false resume. A live authorized or executing mission can yield a reviewed continuation draft. Neither route launches execution.

## Conversation as a workflow

1. Evidence: choose mission and inspect receipts and external facts.
2. Scope: edit the bounded draft; set objective, read permissions, uncertainties, success criteria and withheld writes.
3. Compile: submit through the normal prompt-engineering pipeline, including clarification as needed.
4. Approval: inspect the transformed proposal; select exact basis and approve only the scoped authority.
5. Execute: an approved one-use run is recorded through CAPT; a mission is not declared complete simply because inference returned.
6. Verify: ClaimGuard accepts independent evidence and mission closure is a separate reviewed RuntimeService transition.

The workflow ribbon displays the phase and predecessor, and links back to receipts. A live pending proposal can be restored from RuntimeService on page reload; historical chat prose is not fabricated.

The original issue mission was cancelled by a reviewed 2026-10-17 disposition. Its task was cancelled and approved authority revoked. The predecessor includes a completed model DriverRun on a separate task; this does not verify completion of the original issue-resolution task. A new issue-resolution mission must inventory GitHub and prior artifacts first, and explicitly request separate GitHub write/commit/PR/driver-run permissions. Never automatically replay indeterminate effects.

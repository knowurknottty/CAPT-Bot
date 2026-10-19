# Technical manual — maintain the actual code, not a hypothetical agent platform

**Revision audited:** `0136336538f2f1c2a1daadb55303ee54c60531ac`. This is source-level reference; it is not a claim that the local service was run.

## Repository ownership map

| Area | Notable sources | Behavior |
| --- | --- | --- |
| Local UI server | `capt_bot/ui_server.py` | `argparse` CLI, loopback HTTP, Host/Origin validation, fixed static assets, JSON routes |
| Operator controller | `capt_bot/operator.py` | `BotOperatorController`, Core query/command adaptation, approval/run safeguards |
| Provider catalog | `capt_bot/provider_catalog.py` | Sanitizes configured provider/model registry, does not verify live availability |
| Mission recovery | `capt_bot/mission_recovery.py` | Historical receipts, read-only issue/artifact inventory, successor draft |
| UI | `capt_bot/ui/{index.html,app.js,kanban.js,styles.css}` | Cockpit, Kanban, approval reference and inspector |
| Domain aggregates | `capt_runtime/aggregates/` | Bot, cognitive/skill candidates, delegation, Lab Board, sandbox lease, Cloudflare resource binding |
| Remote/sandbox adapters | `capt_runtime/tools/adapters/` | Cloudflare terminal and InversionSandbox lifecycle/terminal |
| Backends | `capt_runtime/tools/backends/` | Cloudflare, workflow, economy, artifacts, inversion guardian/sandbox |
| Contracts | `contracts/schema/*.schema.json` | Bot and sandbox schemas; `contracts/fixtures/sandbox.json` fixture |
| Tests | `tests/capt_runtime/test_*.py` | Domain, bridge, backend and sandbox tests |
| Historical migration | `integration/`, `SOURCE_PROVENANCE.json` | Isolation markers and old shared-Core diff |

## Local request path

1. Browser requests an allowed exact loopback route.
2. `BotUiHandler` validates Host/Origin; POST additionally demands a bounded JSON object (at most 1 MiB).
3. The handler calls `BotOperatorController`.
4. The controller uses `CoreRuntimePort.query/command` to call Core's authenticated socket client.
5. Core owns event/approval/execution/verification state. The UI displays projections; it cannot certify outcomes.

## Operator workflow state

A typical path is `new_chat → configure → submit_prompt → clarify (if required) → select_proposal → human approval → start_bound_task → result review`. Optional mission creation records a durable Mission and TaskNode; it is distinct from model dispatch. If an in-place mission continuation needs a fresh durable TaskNode, the current controller rejects it and asks for a separately governed successor rather than manufacturing authority.

`start_bound_task` verifies request ID, approval state, unconsumed uses, expiration, mission/task/DriverRun binding, target root, provider, model, selected proposal, durable task and absence of an already-present DriverRun before invoking Core's execution command.

## Provider catalog contract

`~/.capt/ui/providers.json` is read by `read_provider_catalog`. Only provider IDs, sanitized names, allowed kinds and configured model IDs reach the browser. A valid catalog is **not** a guarantee of connectivity, billing allowance or model availability.

## Tests and version claims

The R5 Stage-A script extends Python module search *inside pytest only*. It checks compatibility against a specific Core checkout; it does not inject the Bot into the real running runtime. Historical `333 passed, 8 skipped` appears in the release matrix, **not rerun in this audit**. See [Verification](VERIFICATION.md), [Compatibility](COMPATIBILITY.md) and [OMEGA audit](audit/OMEGA_2026-10-19.md).

## Constraints to preserve

Never create a shadow Core RuntimeService/EventStore, bypass a HumanApproval refusal, retry an indeterminate external call with a new identity, auto-approve a model result, broaden cloud/data permissions silently, or infer implementation from a design-plan filename.

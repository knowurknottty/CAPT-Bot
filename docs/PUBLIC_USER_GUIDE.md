# CAPT-Bot — Human Operator Guide (pre-release)

**Source:** [CAPT-Bot](https://github.com/knowurknottty/CAPT-Bot) and its
[R5 convergence specification](architecture/CAPT_BOT_CONVERGENCE_R5.md).

**Status:** pre-release. Features are distinguished as *implemented locally*,
*dependent on the connected CAPT Core version*, and *not yet release-proven*.
A GitHub repository or visible button is **not** evidence of full functionality.

## What is CAPT-Bot?

A governed synthetic-worker layer for CAPT. Bots can have durable names, roles,
model preferences, cognition/locality policy, and eventually governed mission,
delegation, skills, and issue-workflow behaviors. CAPT Core still owns permissions,
runtime commands, model dispatch, tool calls, EventStore, verification, and claims.

## Start the local cockpit

Prerequisites: a healthy CAPT Core RuntimeService, authorized access to its
Unix socket and token file, and a checked-out CAPT-Bot repository.

From the CAPT-Bot repository, using your configured Python environment:

```zsh
python3 -m capt_bot.ui_server \
  --core-root /absolute/path/to/CAPT_core \
  --sock ~/.capt/runtime.sock \
  --token-file ~/.capt/runtime.token \
  --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765 locally. **Do not port-forward, expose it on a
public interface, or proxy it to the internet.** The UI is a local privileged
operator session, not a public multi-user web service.

## Create a Bot identity

Open **Create Bot**, then supply:

- **Bot ID:** a stable identifier with letters, numbers, `_`, `-`, `.`, or `:`.
- **Display name and role:** what the Bot is for; roles are not permissions.
- **Primary model:** an optional provider model identifier, which must be
  valid and accessible under CAPT's actual provider configuration.
- **Preferred runtime:** local, cloud, or either.
- **Cloud data handling:** explicit policy preference, off by default.

Select **Register identity**. CAPT Core must advertise `register_bot`.
Successful registration creates a durable `BotManifest` with server-bound
creator and time. It **does not activate a Bot, install a GitHub credential,
start a worker, create a mission, permit shell/filesystem access, grant
delegation, or authorize paid inference**.

The Swift application has a matching **Bots → Create Bot** form. When connected
to an older resident runtime that does not advertise `register_bot`,
creation remains unavailable; do not bypass that check with direct database
edits.

## Chat and governed work

In the local cockpit, **New thread** creates a new operator context.
Configure provider, model, repository root, and Prompt Intelligence. Write a
plain-language objective. **Developer** requests the software-development
stage chain. Inspect the generated proposal before selecting it, then inspect
any HumanApproval separately before granting it. No provider result is
verified merely because an inference returned. Review evidence and accept
or reject it explicitly.

For a council in Swift, use a single governed chat for multiple cohorts;
each cohort requires its own approval. Separate chats retain separate
lineage and must never be misrepresented as one inference run. Logical
vessels are review perspectives, not extra inference calls.

## GitHub issue resolution — target workflow, not yet release-proven

Provide the repository URL and desired issue scope. CAPT should inspect
issues **one at a time**, reproduce, repair in a bounded worktree, run
tests, compare the exact diff, and submit evidence/PRs. Confirmation of
a merged fix requires GitHub state and tests, not a model's statement.
Stop if credentials, network/scope, approvals, cost budget, or exact effect
state is missing or indeterminate. Do not ask CAPT to infer that
"never stop" overrides a human-only approval or a safety gate.

The complete unattended issue-solving loop, Bot lifecycle activation,
and R5 cross-repo convergence are **not currently demonstrated end to end**.
They remain release blockers.

## Understand the work queue

**Missions** shows task state and next human action. `executing` on a
stored mission is not a worker heartbeat. **Evidence** distinguishes
recorded/accepted claims from independent verification. **Ledger**
holds immutable historical events; search and filtering do not delete
them. A lost provider run must be reconciled, not blindly re-dispatched.

## Reporting problems

Include exact CAPT Core and CAPT-Bot commits, app version, OS,
a reproducible sequence, sanitized relevant receipts, and whether the
failure happened before dispatch or after the external-effect boundary.
Never include API keys, runtime tokens, private files, or credentials.

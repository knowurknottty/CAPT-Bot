# CAPT-Bot

**Governed synthetic workers. One CAPT authority. Evidence before claims.**

CAPT-Bot is the separately versioned Bot product layer for [CAPT Core](https://github.com/knowurknottty/CAPT_core). It supplies Bot identity, an operator-facing local cockpit, mission/task review, and Bot-domain building blocks for cognition, skills, delegation, sandboxing, and cloud workflows. It **does not** replace CAPT Core's RuntimeService, EventStore, ToolBroker, approvals, or verification authority.

> **Maturity: pre-release / R5 convergence incomplete.** This source tree contains implemented components and historical test evidence. A full current-Core R5 integration, autonomous Bot activation, and unattended GitHub issue fixing are **not release-proven**. The compatibility manifest explicitly records `realR5Acceptance: NOT_RUN`.

## Choose your path

| I want to… | Start here |
| --- | --- |
| Understand CAPT-Bot in two minutes | [ELI5 explanation](docs/ELI5_GUIDE.md) |
| Run the local cockpit with an existing CAPT Core installation | [Quickstart](docs/QUICKSTART.md) |
| Set up prerequisites safely | [Installation and prerequisites](docs/INSTALLATION.md) |
| Register identity, work with governed prompts, and inspect missions | [Human operator guide](docs/PUBLIC_USER_GUIDE.md) |
| Operate as an agent under CAPT governance | [Agent operating contract](docs/AGENT_OPERATOR_GUIDE.md) |
| Understand the architecture and domain boundaries | [Architecture](docs/ARCHITECTURE.md) and [technical manual](docs/TECHNICAL_MANUAL.md) |
| Diagnose an issue | [Troubleshooting](docs/TROUBLESHOOTING.md) |
| Evaluate compatibility or readiness | [Compatibility](docs/COMPATIBILITY.md) and [release matrix](docs/RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) |
| Browse every public document | **[Documentation index](docs/START_HERE.md)** |

## What is implemented in this repository?

- **Local operator bridge:** `python3 -m capt_bot.ui_server` serves a loopback-only web cockpit and relays authorized commands to an existing CAPT Core RuntimeService.
- **Bot identity registration path:** the controller builds a validated `BotManifest` request for Core's `register_bot` command. Registration is **not activation** and grants **no execution permission**.
- **Governed operator flow:** chat context, provider configuration, prompt submission/clarification, proposal selection, approval decision, bound task start, and provider-result review are coordinated through Core APIs.
- **Inspection and recovery:** mission/task Kanban projections, bounded DriverRun inspection, mission disposition preview/confirmation, and non-executable successor-mission drafts.
- **Domain components and tests:** Bot, cognition, skill, delegation, Lab Board, sandbox and Cloudflare-related code remains versioned here; compatibility and integration readiness vary by feature.

These statements describe **source-present implementations**, not proof that every feature is installed or working in a particular resident CAPT Core version.

## First local cockpit session

**Requires a running, compatible CAPT Core RuntimeService**, its authorized Unix socket/token file, and a Python environment with Core's runtime client available.

```zsh
python3 -m capt_bot.ui_server \
  --core-root /absolute/path/to/CAPT_core \
  --sock "$HOME/.capt/runtime.sock" \
  --token-file "$HOME/.capt/runtime.token" \
  --host 127.0.0.1 --port 8765
```

On a separate local terminal, a **bridge-only** smoke check is:

```zsh
curl --fail --silent http://127.0.0.1:8765/api/health
```

Expected bridge response: `{"ok":true}`. This **does not verify** Core authorization, Bot registration, provider health or end-to-end execution. Open [http://127.0.0.1:8765](http://127.0.0.1:8765) only on the same machine. Do **not** expose or port-forward this privileged interface.

## Authority model

```text
Human → CAPT-Bot local UI/controller → CAPT Core RuntimeService
                                         ├─ authoritative EventStore
                                         ├─ HumanApproval/capability gates
                                         ├─ provider and tool execution
                                         └─ verification / claim decisions
```

A Bot name, role, model preference, council opinion, or generated plan is **not** authority. Ambiguous external effects must be reconciled before retry; approving, merging, deploying, or declaring success requires the corresponding authoritative evidence.

## Source lineage and release constraints

This repo preserves its exact historical CAPT Core extraction in `SOURCE_PROVENANCE.json`, `integration/BASE_COMMIT`, `integration/SOURCE_COMMIT`, and `integration/CAPT_CORE.patch`. **Never apply the historical patch wholesale to current Core.** The [R5 convergence specification](docs/architecture/CAPT_BOT_CONVERGENCE_R5.md) defines the required semantic rebase and extraction boundary.

The historical compatibility suite is **test-only**:

```zsh
python3 scripts/run_r5_stage_a_compatibility.py --core-root /absolute/path/to/CAPT_core
```

It does not install a runtime plugin, deploy a service, or certify R5. See [Verification](docs/VERIFICATION.md).

## Documentation integrity

Run the repeatable stdlib-only local gate with `python3 scripts/check_docs.py` and its regression tests with `python3 -m unittest discover -s tests -p test_docs_integrity.py`. A least-privileged [documentation CI workflow](.github/workflows/docs-integrity.yml) checks these on documentation-changing pushes/PRs. This is **documentation QA**, not a Core/Bot production acceptance gate.

**License caution:** no root `LICENSE` file was present in the GitHub tree audited on 2026-10-19. Public visibility alone does not grant a license to redistribute or commercially reuse source. Licensing is a maintainer decision; do not infer it from this README.

**Source-reviewed against:** CAPT-Bot `main` `0136336538f2f1c2a1daadb55303ee54c60531ac` (2026-10-19). Local live execution was unavailable during this documentation pass; see the [documentation audit receipt](docs/audit/OMEGA_2026-10-19.md).

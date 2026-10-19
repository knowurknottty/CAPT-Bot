# Developer onboarding — contribute without forking CAPT's authority

## Orientation

Read [Architecture](ARCHITECTURE.md), the [R5 specification](architecture/CAPT_BOT_CONVERGENCE_R5.md), and CAPT Core's **current** `AGENTS.md` before making changes across both repositories. Do not assume the isolated Bot repo is runnable against arbitrary Core heads.

## Safe first inspection

```zsh
git rev-parse HEAD
git status --short
python3 --version
python3 -m capt_bot.ui_server --help
```

The final command parses the bridge CLI but does not connect to Core (provided Python can import `capt_bot` from the current working directory).

## Sources to understand first

- `capt_bot/ui_server.py` — local bridge, HTTP route table, Core transport.
- `capt_bot/operator.py` — orchestration with Core-owned commands and approvals.
- `capt_runtime/aggregates/*` — Bot-domain state machines.
- `capt_runtime/tools/backends/*` and `adapters/*` — sandbox/cloud effect handling.
- `contracts/schema/*` — Bot and sandbox typed contracts.
- `tests/capt_runtime/*` — historical and focused test cases.
- `integration/*` — lineage **only**, not a deploy recipe.

## Test discipline

1. Freeze both repos' SHAs and Python environment.
2. Run syntax checks, then the source compatibility gate if your Core contains the expected generated contracts; use [Verification](VERIFICATION.md).
3. Keep real Docker/cloud/provider effects opt-in, isolated, budgeted and separately approved.
4. Add a regression test for each bug. Test rejection and indeterminate/retry paths, not only the happy path.
5. Never represent an older compatibility test as R5 production proof.

## Pull request expectations

Small scoped diffs, concrete acceptance criteria, source evidence, executed test receipts/explicit skips, no credential strings, preserved Core authority, and clear migration implications. See [Contributing](../CONTRIBUTING.md), [Security model](SECURITY_MODEL.md), [Technical manual](TECHNICAL_MANUAL.md).

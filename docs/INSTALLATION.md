# Installation and prerequisites

CAPT-Bot currently provides a **source-based local operator bridge and Bot-domain modules**, not a supported standalone installer or one-command production deployment.

## Requirements

- Python 3 with modules required by the **matching CAPT Core** checkout and its `desktop.desktop_runtime_client.RuntimeClient` import.
- A separately checked-out, running CAPT Core RuntimeService with its authorized Unix socket and token file.
- Local access to CAPT-Bot source. Network/model-provider credentials are not required for the bridge-only health check; individual governed provider tasks may require separately configured access.
- A loopback web browser for the cockpit; the service must not be exposed to the network.

The repository tree reviewed for this document has **no root `pyproject.toml`, `requirements.txt` or `setup.py`**. Thus `pip install -e .` and guessed pinned dependencies are **not supported instructions**.

## Safe orientation

```zsh
cd /absolute/path/to/CAPT-Bot
python3 --version
python3 -m capt_bot.ui_server --help
```

The `--help` invocation is a syntax discovery step, **not proof** of a connected Core. Running the real service needs `--core-root`, `--sock` and `--token-file`. [Quickstart](QUICKSTART.md) shows the actual command.

## Integration responsibilities

Core must expose the command/query contract expected by `capt_bot/operator.py` and the desktop runtime client. The historical `integration/CAPT_CORE.patch` is a provenance artifact; applying it to an updated Core can regress authority semantics. The [R5 specification](architecture/CAPT_BOT_CONVERGENCE_R5.md) describes the semantic integration required before independent installation claims.

## Uninstall / rollback

Stop the local bridge process. No claim is made that stopping the bridge removes Bot identities, missions, approvals or EventStore records: those are Core-owned durable state. Do **not** delete `~/.capt` or Core's EventStore as an uninstall shortcut.

**Environment health, exact compatible Core revision, OS packaging, and production migration are not independently verified by this guide.** See [Compatibility](COMPATIBILITY.md).

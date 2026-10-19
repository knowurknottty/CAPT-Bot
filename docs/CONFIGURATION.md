# Configuration and environment boundaries

This reference describes knobs actually parsed in the audited source, not an inferred global CAPT configuration.

## Bridge command-line flags

| Argument | Requirement/default | Meaning |
| --- | --- | --- |
| `--core-root` | Required | Absolute/expanded path to the CAPT Core checkout used for `desktop.desktop_runtime_client` import |
| `--sock` | Required | CAPT Core RuntimeService Unix socket path |
| `--token-file` | Required | Authorized Core session-token file path |
| `--host` | Default `127.0.0.1` | Only `127.0.0.1`, `localhost`, `::1` accepted; never an internet interface |
| `--port` | Default `8765` | Loopback listening port |

```zsh
python3 -m capt_bot.ui_server --help
```

The service calls Core's `RuntimeClient(sock_path, token_file, command_timeout=None)`; no new Core account, entitlement, token or persistent service is created by the CLI.

## Provider/model dropdown

`capt_bot/provider_catalog.py` reads `$HOME/.capt/ui/providers.json` by default. This local document must be a JSON object containing a `providers` array. Enabled entries require a short string ID; eligible `models` are string identifiers. The display projection permits `id`, sanitized `name`, `kind` and `models`. Secrets/endpoints/auth references are **not** sent in the projection.

Operational constraints from code: maximum source file **2,000,000 bytes**, provider ID **1–120 characters**, model ID at most **1,024 characters**, at most **3,000 models per provider**, duplicate provider IDs rejected. All items disabled/invalid yields an error. Source-present validation is independent of live provider health.

**No provider environment variables or billing settings are specified by CAPT-Bot's CLI.** Configure them using CAPT Core's real provider documentation and governance, not invented `CAPT_BOT_API_KEY` values.

## Bot registration fields

`register_bot` accepts a Bot ID matched by `[A-Za-z0-9_.:-]{1,100}`, nonblank display name (1–256 characters), role (1–128), optional primary model identifier (≤256), preferred runtime (`local` / `cloud` / `either`), and a cloud-data-handling preference (default false). All are **manifest data**, not capabilities.

## Priority and defaults

The actual source establishes flags and local catalog behavior. A complete Core-vs-Bot precedence/override contract and production extension configuration **have not been established**. Do not invent override rules. [API reference](API_REFERENCE.md) · [Compatibility](COMPATIBILITY.md).

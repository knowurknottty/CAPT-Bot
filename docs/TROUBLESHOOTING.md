# Troubleshooting — symptoms, safe checks and stop conditions

| Symptom | Likely cause / safe action | Do not do |
| --- | --- | --- |
| Bridge exits before `CAPT_BOT_UI_READY` | Confirm `--core-root`, Core Python import, socket and token file; check Core health through its own supported operator tools | Invent a socket/token or weaken permissions |
| `/api/health` passes but cockpit cannot query state | HTTP process is alive; Core may be disconnected, older or rejecting requests. Reconcile RuntimeService independently | Call bridge health proof of end-to-end readiness |
| `/api/providers` fails | Readable configured catalog at `~/.capt/ui/providers.json` may be absent/malformed/empty; see [Configuration](CONFIGURATION.md) | Paste provider secrets into UI diagnostics |
| A listed model fails to run | Catalog is configured-only, not live availability or cost authorization | Silently switch providers or invoke paid fallback |
| Bot list or registration fails | Resident Core may not advertise compatible `bots`/`register_bot` | Write `BotManifest` directly into EventStore |
| Approval shown, Start blocked | Could be stale, expired, exhausted, wrong session/task/run binding or missing durable TaskNode | Replay a historical approval ID or self-approve |
| External effect timed out | Status may be indeterminate; inspect original operation/DriverRun identity and durable receipt | Dispatch duplicate external work |
| Mission marked `executing` but nothing moves | Stored mission status is not a heartbeat. Inspect tasks, DriverRuns and reconciliation state | Mark completed because the UI says executing |
| In-place continuation rejected | Current Bot/Core command path cannot atomically create a new durable TaskNode for that mission | Manufacture an orphan approval |
| Historical Bot tests fail imports | Standalone Bot tests depend on Core symbols/modules | Blindly apply `integration/CAPT_CORE.patch` |
| Bridge rejects `Host`/`Origin` | Browser must use the exact allowed loopback origin/host | Disable DNS-rebinding/CSRF checks |

## Non-mutating checks

```zsh
python3 -m capt_bot.ui_server --help
curl --fail --silent http://127.0.0.1:8765/api/health
```

Only run the second command once the loopback bridge is intentionally running. Treat `403` as an origin/host rejection and `500` as a possible local bridge/Core error requiring sanitized investigation. No CLI log-output or exception string proves an external provider effect.

## When escalating

Report reproduction steps, exact CAPT Core and Bot Git SHAs, Python/OS, sanitized state class, event/operation IDs where safe, and whether the action crossed an external-effect boundary. Mask all tokens, raw prompts containing personal data, and third-party records.

[Human operator guide](PUBLIC_USER_GUIDE.md) · [Mission recovery design](architecture/CAPT_BOT_MISSION_RECOVERY_UI.md) · [Security](SECURITY_MODEL.md).

# Local HTTP bridge API (pre-release; not a public remote API)

**Source:** `capt_bot/ui_server.py` and `capt_bot/operator.py` at `01363365`. The bridge uses local loopback HTTP and CAPT Core's Unix-socket runtime client. These endpoints are internal operator surfaces, not a supported public multi-tenant API. **Do not publish them on a network interface.**

## Common constraints

- Default bind: `127.0.0.1:8765`. `--host` accepts `127.0.0.1`, `localhost` or `::1` only.
- Every request requires one allowed `Host` header. Where provided, `Origin` must match its exact local HTTP origin. Other origins return `403`.
- POST bodies must have `Content-Type: application/json` and encode a JSON object of at most **1 MiB**.
- Success handlers return JSON with status `200`. Wrong route returns `404`; validation errors `400`; other errors can return `500`. Do not assume every Core refusal uses HTTP `403`: application-layer receipts may carry status/classification.
- `/api/health` verifies the **bridge** only. It does not prove authenticated Core connectivity.

## Read routes

| Method | Route | Observed behavior |
| --- | --- | --- |
| GET | `/` | Serve cockpit HTML |
| GET | `/app.js`, `/kanban.js`, `/styles.css` | Serve static assets |
| GET | `/api/health` | Return `{"ok":true}` |
| GET | `/api/snapshot` | Operator control, execution and bounded projected mission/task/approval state |
| GET | `/api/kanban` | Core-derived missions/tasks and DriverRun summaries |
| GET | `/api/providers` | Sanitized configured provider/model catalog (`availabilityVerified: false`) |
| GET | `/api/bots` | Query Core's Bot registry |
| GET | `/api/mission/recovery?missionId=…` | Read-only mission recovery and evidence-derived successor draft |

## Mutation routes

| POST route | JSON request keys | Core effect / caution |
| --- | --- | --- |
| `/api/chat/new` | `{}` | New operator chat/context |
| `/api/config` | `provider?`, `model?`, `targetRoot?`, `promptIntelligence?` | Sets operator config; pair validated against local configured catalog |
| `/api/prompt` | `text`, `developer?`, `clarificationFor?`, `requestedContextBudget?`, `requestedCapabilities?`, `remoteCompilationAuthorized?` | Submit/clarify objective; may create operator context |
| `/api/proposal/select` | `proposalId`, `basis?`, `editedPrompt?`, `asMission?`, `existingMissionId?`, `requestedExecutionSeconds?` | Select compiled proposal; optional mission creation; in-place continuation currently rejected |
| `/api/bots/register` | `botId`, `displayName`, `role`, `primaryModel?`, `defaultRuntime?`, `cloudAllowed?` | Create **Bot identity**, not activation |
| `/api/approval/decide` | `requestId`, `decision` = `approve` or `deny`, `note?` | **Explicit human authorization only** |
| `/api/run/start` | `requestId` | Rechecks bound durable task/approval/DriverRun before admitted dispatch |
| `/api/result/review` | `driverRunId`, `disposition` = `accept` or `reject`, `note?` | Review provider result; not independently verified completion |
| `/api/mission/disposition/preview` | `missionId`, `target` | Read-only preview despite POST method |
| `/api/mission/disposition/apply` | `missionId`, `target`, `expectedVersion`, `previewDigest`, `confirmedMissionId`, `reason?` | Version/digest-based explicitly reviewed disposition |
| `/api/task/cancel` | `taskId`, `reason?` | Governed cancellation, immutable prior event history remains |

`target` values in disposition: `authorize`, `cancel`, `cancel_revoke`, `complete`, `reconcile_complete`. Cancellation and completion must **not** be inferred from a model's interpretation of a response.

## Representative *non-mutating* request

```zsh
curl --fail --silent -H 'Host: 127.0.0.1:8765' \
  http://127.0.0.1:8765/api/health
```

Expected JSON `{"ok":true}` **when the bridge is running**. This command is not a substitute for a Core health or operation receipt.

## Stability notes

This file documents routes observed in source and does not promise semantic-versioning or backwards compatibility of the internal HTTP surface. Core runtime query/command schemas, identity and admission rules remain authoritative; integration compatibility must be checked against both Git SHAs. See [Configuration](CONFIGURATION.md), [Security](SECURITY_MODEL.md) and [Technical manual](TECHNICAL_MANUAL.md).

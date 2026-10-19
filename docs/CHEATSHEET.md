# CAPT-Bot cheatsheet

| Goal | Entry point / surface | Important boundary |
| --- | --- | --- |
| Start the local UI | `python3 -m capt_bot.ui_server --core-root … --sock … --token-file …` | Must stay on loopback |
| Check bridge HTTP response | `GET /api/health` | Does **not** test Core or inference |
| See operator/runtime snapshot | `GET /api/snapshot` | Requires compatible Core query support |
| List Bots | `GET /api/bots` | Identity listing only |
| Create Bot identity | Cockpit **Create Bot** / `POST /api/bots/register` | Durable state, not activation |
| Inspect mission lanes | **Missions** / `GET /api/kanban` | EventStore projections, not worker heartbeat |
| See configured providers | `GET /api/providers` | Configured is **not** available/live |
| New thread | `POST /api/chat/new` | Creates operator context through Core |
| Change provider/model | `POST /api/config` | Validated against configured provider catalog |
| Submit objective | `POST /api/prompt` | Proposal stage; not execution |
| Select proposal | `POST /api/proposal/select` | Mission creation optional; can request approval |
| Decide an approval | `POST /api/approval/decide` | **Human decision only** |
| Start an approved run | `POST /api/run/start` | Checks binding, expiry and durable task |
| Review returned result | `POST /api/result/review` | Accept/reject is not independent verification |
| Preview mission disposition | `POST /api/mission/disposition/preview` | Read-only preview |
| Apply mission disposition | `POST /api/mission/disposition/apply` | Requires Core digest/version and typed confirmation |
| Run historical compatibility gate | `python3 scripts/run_r5_stage_a_compatibility.py --core-root PATH` | **Test-only**, not deployment |

For request payload shapes use [API reference](API_REFERENCE.md). For authority rules use [Security model](SECURITY_MODEL.md).

**Rule of thumb:** *configured ≠ installed ≠ approved ≠ executed ≠ verified ≠ release-ready*.

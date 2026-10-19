# Documentation — Start here

**Audience routes** (pre-release, source-reviewed at `01363365`):

| Reader | Reading order | What you can verify |
| --- | --- | --- |
| First-time human | [ELI5](ELI5_GUIDE.md) → [Install](INSTALLATION.md) → [Quickstart](QUICKSTART.md) → [Human operator guide](PUBLIC_USER_GUIDE.md) | Local bridge and authorized UI journey, provided Core is already running |
| CAPT operator | [Human guide](PUBLIC_USER_GUIDE.md) → [Cheatsheet](CHEATSHEET.md) → [Troubleshooting](TROUBLESHOOTING.md) → [Security](SECURITY_MODEL.md) | Approval and result-review separation |
| Agent | [Agent contract](AGENT_OPERATOR_GUIDE.md) → [API bridge](API_REFERENCE.md) → [Verification](VERIFICATION.md) | Authority boundaries; no self-approval |
| Developer | [Onboarding](DEVELOPER_ONBOARDING.md) → [Architecture](ARCHITECTURE.md) → [Technical manual](TECHNICAL_MANUAL.md) → [Contracts](DATA_AND_CONTRACTS.md) | Static code and test surfaces |
| Maintainer / reviewer | [Compatibility](COMPATIBILITY.md) → [Release matrix](RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) → [OMEGA audit](audit/OMEGA_2026-10-19.md) | Historic proof vs current-HEAD gaps |

**Task references:** [FAQ](FAQ.md), [Glossary](GLOSSARY.md), [Configuration](CONFIGURATION.md), [API](API_REFERENCE.md), [Verification](VERIFICATION.md), [Release status](RELEASES_AND_MIGRATIONS.md).

**Canonical existing design history:** [R1 foundation](architecture/CAPT_BOT_FOUNDATION_R1.md), [R2 crew](architecture/CAPT_BOT_CREW_STANDUP_R2.md), [R3 Cloudflare](architecture/CAPT_BOT_CLOUDFLARE_R3.md), [R4 Workflows](architecture/CAPT_BOT_CLOUDFLARE_WORKFLOWS_R4.md), [R5 convergence](architecture/CAPT_BOT_CONVERGENCE_R5.md).

## Read status labels correctly

- **Source present:** implementation exists in this repo.
- **Historically tested:** a prior source pair/test environment produced a recorded result; **not** today's guarantee.
- **Environment dependent:** requires a particular resident Core/credential/provider/service.
- **Planned / blocked:** specified but not established as an end-to-end supported product.
- **Verified live:** requires a fresh, evidence-bearing execution receipt; **not established by this documentation mission**.

The `docs/superpowers/` documents and older architecture reports record historical plans/specifications. They are **not** replacement instructions for current production Core.

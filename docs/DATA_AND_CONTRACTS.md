# Data model and contracts

This is a **source-map reference**, not an independently validated public stable API.

| Domain | Source | Evidenced purpose |
| --- | --- | --- |
| Bot identity | `capt_runtime/aggregates/bot.py`, `contracts/schema/bot.schema.json` | Bot manifest creation/validation and immutable identity |
| Cognitive candidate | `capt_runtime/aggregates/cognitive_candidate.py` | Governed candidate state, not automatic self-upgrade |
| Skill candidate | `capt_runtime/aggregates/skill_candidate.py` | Proposals/transitions toward a governed skill |
| Delegation | `capt_runtime/aggregates/delegate_assignment.py` | Task-scoped assignment and transition; no authority inheritance |
| Lab Board | `capt_runtime/aggregates/lab_board.py`, `capt_runtime/lab_standup.py` | Projected team/standup information |
| Sandbox lease | `capt_runtime/aggregates/sandbox_lease.py`, `contracts/schema/sandbox.schema.json` | Typed lease/persistent execution requirements |
| Cloudflare resource binding | `capt_runtime/aggregates/cloudflare_resource_binding.py` | Adoption/binding state for remote resources |
| Sandbox fixture | `contracts/fixtures/sandbox.json` | Test data, not authorization or a deployable resource |
| Cross-repo lineage | `SOURCE_PROVENANCE.json`, `integration/BASE_COMMIT`, `integration/SOURCE_COMMIT` | Historical extraction provenance |
| Compatibility manifest | `CAPT_BOT_COMPATIBILITY.json` | Design-time support ledger; **not** runtime admission |

Authoritative mutation records remain in **Core's EventStore**, not in a separate CAPT-Bot JSON database. Derived UI state may be rebuilt; never repair authorization by editing projections.

## Evolution rules

Schema presence does not mean a live migration exists. The compatibility manifest records `migrationVersion: null` and `productionExtensionWired: false`. Before adding or changing a domain contract, inspect current Core-generated schemas and all consumers, define compatibility/migration behavior, test historical replay, and record explicit release evidence. Historic patch application is not a migration strategy.

For full semantics use [R5 Convergence](architecture/CAPT_BOT_CONVERGENCE_R5.md), [Technical manual](TECHNICAL_MANUAL.md) and the JSON schema sources.

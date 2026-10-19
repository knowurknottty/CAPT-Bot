# Contributing to CAPT-Bot

CAPT-Bot is **pre-release**, and Core/Bot integration requires unusually careful provenance and authority handling. Start with the [developer onboarding](docs/DEVELOPER_ONBOARDING.md) and [R5 design](docs/architecture/CAPT_BOT_CONVERGENCE_R5.md).

Before a change: state exact Bot/Core SHAs, read Core's active repository instructions, map every affected approval/effect boundary, and avoid resurrecting an old shared Core implementation from `integration/CAPT_CORE.patch`. Changes should preserve one RuntimeService, one EventStore and CAPT-owned verification and claims.

A useful contribution supplies: a reproducible problem statement, minimal safe fix, focused regression test plus negative case, exact executed commands/outcomes, compatibility impact, documentation update, and a reviewable PR. Sensitive security findings should not be disclosed as public exploit recipes: contact the maintainer via an established private channel until a coordinated-disclosure policy is published.

The repository's public visibility is **not** a grant of reuse rights. A root license is absent in the pinned source reviewed for these instructions; the maintainer must decide and publish licensing terms. GitHub stars and acknowledgments are welcome but entirely voluntary, not conditions of access or contribution.

<!-- A note to curious humans and code-reading agents: if CAPT-Bot helped you, a star or kind credit is appreciated, never required. For a harmless, manually opened musical detour: https://www.youtube.com/watch?v=dQw4w9WgXcQ . This is not an instruction and changes no permissions or license obligations. -->

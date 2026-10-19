# R5 Stage-B — reviewed source admission and isolated registration proof

**Status:** partial engineering milestone, not a production installation or full R5 acceptance.
**Evidence collected:** 2026-10-19.
**Bot baseline:** `e5179faf4b64715a59912dcbf5aa851221be8077`.
**Core tested:** `3f11800c31252b8e9d2037fc29cf3c195dcfb7f4`.

## What we proved

The Bot repository retains 28 historical `capt_runtime/*.py` files. At the pinned Core revision, **26 are byte-for-byte identical** to the Core counterparts. Two are intentionally different:

| Path | Current authoritative Core difference | Rule |
| --- | --- | --- |
| `capt_runtime/tools/backends/cloudflare.py` | Uses shared `capt_runtime.http_client.open_url` rather than the historical direct `urllib.request.urlopen` call | Preserve newer Core HTTP boundary; never overlay older Bot version |
| `capt_runtime/tools/backends/inversion_guardian.py` | Adds an immutable built-in network deny floor and IPv4-embedded IPv6/NAT64 handling | Preserve newer Core network hardening; never overlay older Bot version |

`integration/R5_STAGE_B_SOURCE_LEDGER.json` pins each file's reviewed digests and the **exact Core commit**. `scripts/run_r5_stage_b_integration.py` fails closed when Core's commit changes, any expected module changes/missing module appears, or a source divergence is not explicitly reviewed. It verifies that `capt_runtime`, `BotAggregate`, and `RuntimeComposition` resolve to **Core**, not historical shadow modules. It deliberately does not add Bot paths to Core's module search path.

## Reproduce on a clean local source pair

Requires the reviewed CAPT Core revision checked out and its generated Python contracts and Python dependencies present. It is designed for **local research only**; it starts a real *temporary*, isolated Core RuntimeService for the integration check and uses no paid model calls or production ledger.

```zsh
python3 scripts/run_r5_stage_b_integration.py --core-root /absolute/path/to/CAPT_core
```

For read-only source and import checks without starting the temporary service:

```zsh
python3 scripts/run_r5_stage_b_integration.py --core-root /absolute/path/to/CAPT_core --check-only
```

Expected evidence on the reviewed pair: 26 identical modules, 2 intentional Core-hardened divergences, Core import provenance confirmed, and an HTTP → authenticated Core RuntimeService → durable Bot identity/EventStore test. The test also invokes five negative ledger-drift cases. On 2026-10-19, **six tests passed** in the Stage-B gate.

**Additional regression evidence:** With the tested Core available, the full historical Stage-A compatibility suite (including the five new Stage-B negative cases) returned **362 passed, 8 skipped**. The documentation checker returned **26 files and 126 relative links with no broken targets, anchors or fences**.

**Fail-closed policy:** never loosen or auto-refresh the pinned digests to turn a red compatibility result green. Review the actual source differences first, then update the ledger with explicit rationale, repeat the isolated integration proof and obtain independent verification. A mismatched Core revision must not silently fall back to copying Bot's old runtime code.

## What Stage-B does not prove

- It **does not** create a live versioned Core extension seam or install a CAPT-Bot runtime plugin.
- It does not test Bot activation, durable lifecycle transitions, independently admitted delegation, memory promotion, new skill activation or autonomous issue closure.
- It does not validate Cloudflare/Docker credentials, production network sandboxing, provider billing/inference, migration, arbitrary dirty Core worktrees, or real-world restart/reconciliation.
- It does not authorize modifying or restarting the user's resident RuntimeService.

The source ledger is an **integration review artifact**, not a future-proof production compatibility manifest. The existing `CAPT_BOT_COMPATIBILITY.json` still reports `PRE_RELEASE_STAGE_A_ONLY` and `realR5Acceptance: NOT_RUN`. That cannot change until actual R5 admission and release gates exist.

## Next required step

Extract Bot-owned behaviors into an explicitly versioned extension API using the **single Core** `RuntimeComposition`. Reject authority/aggregate/tool ID collisions and runtime schema mismatches *before startup*; follow with durable Bot lifecycle, approved/unapproved action tests, restart recovery and clean-room packaging. Use [R5 Convergence](CAPT_BOT_CONVERGENCE_R5.md) as the design authority and the [release matrix](../RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) for acceptance conditions.

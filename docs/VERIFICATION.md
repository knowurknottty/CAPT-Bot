# Verification and reproducibility

A source file, passing test on an earlier commit, green button, or returned model answer is not a current end-to-end test receipt. Record Core and Bot SHAs together.

## Gates you can actually run (with prerequisites)

### Source-independent local checks

```zsh
python3 -m compileall -q capt_bot capt_runtime scripts
```

This checks Python syntax, **not** Core compatibility, imports, provider health or semantic correctness. Execution may create local `__pycache__` directories. Run on a disposable checkout or clean them safely afterward.

### Historical Stage-A source compatibility

```zsh
python3 scripts/run_r5_stage_a_compatibility.py \
  --core-root /absolute/path/to/CAPT_core
```

The script checks Core's package path, generated Python contracts and pytest import overlay. It runs the Bot test suite in the current Python environment. Some tests can depend on Docker or other environment availability; inspect test prerequisites before executing. It is **not** an install or R5 acceptance procedure.

### Local bridge smoke check

With compatible Core running and the bridge launched per [Quickstart](QUICKSTART.md):

```zsh
curl --fail --silent http://127.0.0.1:8765/api/health
```

Expected `{"ok":true}` proves **only** the bridge. A further authorized Core snapshot must be observed before claiming runtime integration; mutation/approved-run checks require explicit human authority and are not silently part of documentation verification.

## Required test receipt format

For each gate record: UTC time; Bot SHA; Core SHA; OS/Python; exact command; exit code; raw sanitized log reference; tested assertions; skipped tests; environment limitations; and `PASS`, `FAIL`, `PARTIAL`, `BLOCKED` or `NOT RUN`. Separate human summary from machine evidence.

## Mission verification (2026-10-19)

**Chronology:** The initial OMEGA pass could not execute tests because CAPT Node returned `capability_expired`; this remains historical. A later renewed authorized capability enabled a local run against CAPT-Bot base `0136336538f2f1c2a1daadb55303ee54c60531ac` and Core `3f11800c31252b8e9d2037fc29cf3c195dcfb7f4`. Stage-A reported **350 passed, 8 skipped** before repairs, and **357 passed, 8 skipped** after repairs. Focused HTTP/security tests reported **3 passed, 1 skipped**, and six docs-checker tests passed. These are **local worktree checks**, not production R5 release evidence; exact post-commit verification must be recorded separately.

Run `python3 scripts/check_docs.py` and `python3 -m unittest discover -s tests -p test_docs_integrity.py` for repeatable docs QA. The read-only [GitHub workflow](../.github/workflows/docs-integrity.yml) is included; a hosted run must be confirmed separately.

## R5 Stage-B source admission

`python3 scripts/run_r5_stage_b_integration.py --core-root /absolute/path/to/CAPT_core` requires the reviewed Core commit. It checks a signed-by-digest **source ledger** (not a cryptographic signature), confirms Core owns the loaded runtime modules, then runs a real temporary-runtime Bot registration plus five negative source-drift tests. Six tests passed in the 2026-10-19 local engineering run. See [the Stage-B report](architecture/CAPT_BOT_R5_STAGE_B_SOURCE_ADMISSION.md). This does not prove R5 extension composition.

## Release requirement

The actual Core+Bot R5 semantic integration, live registration/approval workflow, denied-action safety, ambiguity/restart recovery, issue-to-PR closeout, security/adversarial verification, and clean-room human/agent onboarding still require separate exact-HEAD receipts. [Release matrix](RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) · [Audit receipt](audit/OMEGA_2026-10-19.md).

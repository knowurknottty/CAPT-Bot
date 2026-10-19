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

The OMEGA documentation review successfully **read** the GitHub tree and source, but **could not execute live tests**: CAPT Node returned `capability_expired` and the isolated assistant container could not resolve github.com for a fresh clone. Therefore **all executable tests in this mission are NOT RUN**, irrespective of historical green results. The branch contents can be inspected through GitHub; do not interpret a generated Markdown document as evidence of a passing CI check.

## Release requirement

The actual Core+Bot R5 semantic integration, live registration/approval workflow, denied-action safety, ambiguity/restart recovery, issue-to-PR closeout, security/adversarial verification, and clean-room human/agent onboarding still require separate exact-HEAD receipts. [Release matrix](RELEASE_READINESS_REVIEW_MATRIX_2026-10-08.md) · [Audit receipt](audit/OMEGA_2026-10-19.md).

#!/usr/bin/env python3
"""R5 Stage-B read-only source admission and isolated real Core registration proof.

Does not wire extensions, mutate a production ledger, or certify R5 release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HARDENED = {"capt_runtime/tools/backends/cloudflare.py",
            "capt_runtime/tools/backends/inversion_guardian.py"}

class AdmissionError(RuntimeError):
    pass

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True,
                          timeout=10).stdout.strip()

def admit(bot: Path, core: Path, ledger: dict) -> dict:
    if ledger.get("schemaVersion") != "1.0.0":
        raise AdmissionError("R5_LEDGER_SCHEMA_MISMATCH")
    observed = git_head(core)
    if observed != ledger.get("coreCommit"):
        raise AdmissionError("R5_CORE_HEAD_CHANGED_REVIEW_REQUIRED")
    rows = ledger.get("modules")
    if not isinstance(rows, list):
        raise AdmissionError("R5_MODULE_LEDGER_MISSING")
    actual = {p.relative_to(bot).as_posix()
              for p in (bot / "capt_runtime").rglob("*.py")}
    names = [r.get("path") for r in rows]
    if len(names) != len(set(names)) or set(names) != actual:
        raise AdmissionError("R5_MODULE_CENSUS_CHANGED_REVIEW_REQUIRED")
    identical = hardened = 0
    for row in rows:
        name = row["path"]
        bp, cp = bot / name, core / name
        if not bp.is_file() or not cp.is_file():
            raise AdmissionError("R5_MISSING_CORE_MODULE:" + name)
        b, c = digest(bp), digest(cp)
        if b != row.get("botSha256") or c != row.get("coreSha256"):
            raise AdmissionError("R5_SOURCE_DRIFT_REVIEW_REQUIRED:" + name)
        if row.get("mode") == "identical" and b == c:
            identical += 1
        elif row.get("mode") == "core_hardened" and name in HARDENED and b != c:
            hardened += 1
        else:
            raise AdmissionError("R5_UNREVIEWED_SHADOW_MODULE:" + name)
    if hardened != len(HARDENED):
        raise AdmissionError("R5_CORE_HARDENING_INVENTORY_MISSING")
    return {"coreHead": observed, "identical": identical,
            "coreHardened": hardened, "total": len(rows)}

def check_core_imports(bot: Path, core: Path) -> dict:
    for required in ("capt_runtime/__init__.py", "desktop/capt_runtime_service.py",
                     "desktop/desktop_runtime_client.py", "contracts/generated/python"):
        if not (core / required).exists():
            raise AdmissionError("R5_CORE_DEPENDENCY_MISSING:" + required)
    env = os.environ.copy()
    # Core MUST supply capt_runtime; Bot contributes only capt_bot.
    # Never extend capt_runtime.__path__ to the historical Bot modules.
    env["PYTHONPATH"] = os.pathsep.join((str(core), str(bot)))
    probe = (
        "from pathlib import Path\n"
        "import capt_runtime, inspect\n"
        "from capt_runtime.aggregates.bot import BotAggregate\n"
        "from capt_runtime.composition import RuntimeComposition\n"
        "root=Path(" + repr(str(core)) + ").resolve()\n"
        "assert Path(capt_runtime.__file__).resolve()==root/'capt_runtime/__init__.py'\n"
        "assert Path(inspect.getfile(BotAggregate)).resolve()==root/'capt_runtime/aggregates/bot.py'\n"
        "assert Path(inspect.getfile(RuntimeComposition)).resolve()==root/'capt_runtime/composition.py'\n"
        "print('R5_CORE_AUTHORITY_IMPORTS_PASS')\n"
    )
    result = subprocess.run([sys.executable, "-c", probe], cwd=bot, env=env,
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise AdmissionError("R5_CORE_IMPORT_PROVENANCE_FAILED: " +
                             result.stderr[-500:].replace("\n", " "))
    print(result.stdout.strip(), flush=True)
    return env

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--core-root", required=True, type=Path)
    p.add_argument("--check-only", action="store_true")
    args = p.parse_args()
    bot = Path(__file__).resolve().parents[1]
    core = args.core_root.expanduser().resolve()
    try:
        ledger = json.loads((bot / "integration/R5_STAGE_B_SOURCE_LEDGER.json").read_text())
        result = admit(bot, core, ledger)
        print("R5_STAGE_B_SOURCE_ADMISSION", json.dumps(result, sort_keys=True),
              flush=True)
        env = check_core_imports(bot, core)
        env["CAPT_CORE_ROOT"] = str(core)
        if args.check_only:
            print("R5_STAGE_B_CHECK_ONLY_PASS", flush=True)
            return 0
        command = [sys.executable, "-m", "pytest", "-q",
                   "tests/test_bot_core_registration_integration.py",
                   "tests/test_r5_stage_b_gate.py", "-rs", "--tb=short"]
        run = subprocess.run(command, cwd=bot, env=env, text=True,
                             capture_output=True, timeout=120)
        print(run.stdout, end="", flush=True)
        if run.stderr:
            print(run.stderr, end="", file=sys.stderr, flush=True)
        if (run.returncode != 0 or
            not re.search(r"\b[1-9][0-9]* passed\b", run.stdout) or
            re.search(r"\b[1-9][0-9]* skipped\b", run.stdout)):
            raise AdmissionError("R5_STAGE_B_REAL_CORE_INTEGRATION_NOT_PASSING")
        print("R5_STAGE_B_ISOLATED_CORE_REGISTRATION_PASS", flush=True)
        return 0
    except (AdmissionError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print("R5_STAGE_B_FAILED:", str(exc), file=sys.stderr, flush=True)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

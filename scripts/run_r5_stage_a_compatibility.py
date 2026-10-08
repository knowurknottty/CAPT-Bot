#!/usr/bin/env python3
"""Non-deployable R5 Stage-A source compatibility gate.

Extends the *test process only* to discover historical Bot-owned modules
beneath the current Core package. This is not a runtime extension plugin,
a product installation procedure, or an R5 release certificate.

Usage:
  python scripts/run_r5_stage_a_compatibility.py --core-root ../CAPT_core
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", required=True, type=Path)
    parser.add_argument("--pytest-arg", action="append", default=[])
    args = parser.parse_args()

    core_root = args.core_root.expanduser().resolve()
    bot_root = Path(__file__).resolve().parents[1]
    core_path = core_root / "capt_runtime"
    bot_path = bot_root / "capt_runtime"
    contract_path = core_root / "contracts" / "generated" / "python"
    for required in (core_path / "__init__.py", contract_path, bot_path):
        if not required.exists():
            parser.error("Required Core/Bot test source absent: " + str(required))

    sys.path.insert(0, str(bot_root))
    sys.path.insert(0, str(contract_path))
    sys.path.insert(0, str(core_root))
    import capt_runtime  # pylint: disable=import-outside-toplevel

    # Test-only source archaeology: import current Core modules first.
    # No copying, overwriting, or patching of Core code is permitted.
    if Path(capt_runtime.__file__).resolve() != (core_path / "__init__.py").resolve():
        parser.error("The loaded CAPT Core package did not come from --core-root")
    if str(bot_path) not in capt_runtime.__path__:
        capt_runtime.__path__.append(str(bot_path))

    import pytest  # pylint: disable=import-outside-toplevel

    print("R5_STAGE_A_COMPATIBILITY_ONLY", flush=True)
    print("CORE_SOURCE", core_root, flush=True)
    print("BOT_SOURCE", bot_root, flush=True)
    return int(pytest.main(["-q", str(bot_root / "tests"), "--tb=short", *args.pytest_arg]))


if __name__ == "__main__":
    raise SystemExit(main())

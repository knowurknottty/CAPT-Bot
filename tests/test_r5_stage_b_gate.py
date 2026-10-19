"""Fail-closed R5 Stage-B source admission tests against a real checked-out Core.

No synthetic RuntimeService, model provider, or simulated execution is used.
The negative cases mutate only an in-memory copy of the reviewed ledger.
"""
from __future__ import annotations
from copy import deepcopy
import json
import os
from pathlib import Path

import pytest

from scripts.run_r5_stage_b_integration import AdmissionError, admit

BOT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def checked_core():
    path = os.environ.get("CAPT_CORE_ROOT")
    if not path:
        pytest.skip("CAPT_CORE_ROOT required for reviewed source-pair admission")
    core = Path(path).expanduser().resolve()
    ledger = json.loads(
        (BOT_ROOT / "integration/R5_STAGE_B_SOURCE_LEDGER.json").read_text()
    )
    return core, ledger

def test_reviewed_current_core_pair_admits(checked_core):
    core, ledger = checked_core
    observed = admit(BOT_ROOT, core, ledger)
    assert observed["identical"] == 26
    assert observed["coreHardened"] == 2
    assert observed["total"] == 28

def test_wrong_core_head_fails_closed(checked_core):
    core, ledger = checked_core
    tampered = deepcopy(ledger)
    tampered["coreCommit"] = "0" * 40
    with pytest.raises(AdmissionError, match="CORE_HEAD_CHANGED"):
        admit(BOT_ROOT, core, tampered)

def test_digest_drift_fails_closed(checked_core):
    core, ledger = checked_core
    tampered = deepcopy(ledger)
    tampered["modules"][0]["coreSha256"] = "0" * 64
    with pytest.raises(AdmissionError, match="SOURCE_DRIFT"):
        admit(BOT_ROOT, core, tampered)

def test_census_removal_fails_closed(checked_core):
    core, ledger = checked_core
    tampered = deepcopy(ledger)
    tampered["modules"].pop()
    with pytest.raises(AdmissionError, match="MODULE_CENSUS_CHANGED"):
        admit(BOT_ROOT, core, tampered)

def test_unaudited_hardened_classification_fails_closed(checked_core):
    core, ledger = checked_core
    tampered = deepcopy(ledger)
    original = next(r for r in tampered["modules"] if r["mode"] == "identical")
    original["mode"] = "core_hardened"
    with pytest.raises(AdmissionError, match="UNREVIEWED_SHADOW_MODULE"):
        admit(BOT_ROOT, core, tampered)

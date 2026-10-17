"""Historical mission recovery must be read-only, source-bound and actionable."""
from __future__ import annotations

import pytest
from capt_bot.mission_recovery import ISSUES_MISSION, inspect_mission, github_issue_inventory


class RecoveryRuntime:
    def __init__(self):
        self.calls = []
    def _query(self, op, **args):
        self.calls.append((op, args))
        if op == "get_state":
            sid = args["streamId"]
            if sid.startswith("mission-"):
                return {"missionId": ISSUES_MISSION, "state": "cancelled"}
            return {"driverRunId": "dr-other", "missionId": ISSUES_MISSION,
                    "taskId": "other-task", "state": "completed"}
        if op == "tasks":
            return {"count": 1, "tasks": [{
                "taskId": ISSUES_MISSION + "-task-1", "missionId": ISSUES_MISSION,
                "state": "cancelled", "title": "Assess and resolve every GitHub issue",
            }]}
        if op == "approvals":
            return {"approvals": [{"requestId": "a-1", "state": "revoked",
                                   "derivedStale": False}]}
        if op == "list_aggregates":
            return [{"kind": "driverrun", "streamId": "driverrun-dr-other"}]
        if op == "get_stream_events":
            return [{"eventType": "MissionStateChanged", "globalSequence": 100,
                     "eventId": "ev-1", "payload": {"privateSecret": "MUST_NOT_LEAK"}}]
        raise AssertionError(op)


def test_cancelled_issue_mission_requires_new_goal_and_never_dispatches(monkeypatch):
    monkeypatch.setattr("capt_bot.mission_recovery.github_issue_inventory",
                        lambda: {"status": "ok", "repository": "knowurknottty/CAPT_core",
                                 "openCount": 1, "issues": [
                                     {"number": 187, "title": "Review council fidelity",
                                      "state": "OPEN", "url": "https://github.com/knowurknottty/CAPT_core/issues/187"}]})
    monkeypatch.setattr("capt_bot.mission_recovery.fixed_artifact_inventory",
                        lambda: {"repositories": [{"name": "CAPT_core", "exists": True}]})
    runtime = RecoveryRuntime()
    result = inspect_mission(runtime, ISSUES_MISSION)
    assert result["state"] == "cancelled"
    assert result["terminal"] and not result["continuableInPlace"]
    assert "NEW CAPT mission" in result["draft"]
    assert "no NEW DriverRuns" in result["draft"]
    assert "#187:" in result["draft"]
    assert "do not resume" in result["draft"]
    assert result["driverRuns"][0]["state"] == "completed"
    assert "privateSecret" not in str(result)
    assert set(op for op, _ in runtime.calls) == {
        "get_state", "tasks", "approvals", "list_aggregates", "get_stream_events"}
    assert "command" not in str(runtime.calls)


def test_recovery_refuses_invalid_identity():
    runtime = RecoveryRuntime()
    with pytest.raises(ValueError, match="mission ID"):
        inspect_mission(runtime, "../secret")
    assert not runtime.calls


def test_github_unavailable_is_not_reported_as_zero(monkeypatch):
    import subprocess
    def no_gh(*args, **kwargs):
        raise subprocess.TimeoutExpired("gh", 12)
    monkeypatch.setattr(subprocess, "run", no_gh)
    inventory = github_issue_inventory()
    assert inventory["status"] == "unavailable"
    assert inventory["openCount"] is None
    assert inventory["issues"] == []


def test_source_separation_and_authority_gates(monkeypatch):
    monkeypatch.setattr("capt_bot.mission_recovery.github_issue_inventory",
                        lambda: {"status": "unavailable", "openCount": None, "issues": []})
    result = inspect_mission(RecoveryRuntime(), ISSUES_MISSION)
    assert "Github" not in result.get("sourceBoundary", "")
    assert "independent read-only" in result["sourceBoundary"]
    assert "separate, explicit approvals" in result["withheldAuthority"]
    assert "Current GitHub inventory unavailable" in result["draft"]

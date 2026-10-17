"""Read-only, provenance-bound mission handoff. Never revives terminal work."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

ISSUES_MISSION = "m-capt-issues-20260924-live"
ISSUES_REPO = "knowurknottty/CAPT_core"
TERMINAL = frozenset(("completed", "cancelled", "failed"))
CANDIDATES = ("capt-core-biocapt-ouroboros", "CAPTlegal", "CAPTancient",
              "capt_data", "CAPT_core")
ARTIFACTS = (
    "docs/missions/live_work_queue_triage_2026-10-08.md",
    "docs/missions/CAPT_KANBAN_RECONCILIATION_20261017.md",
    ".capt-evidence/mission-steward/decisions-v2-live.json",
    ".capt-evidence/kanban-cleanup-20261017/CAPT_KANBAN_ALL_MISSIONS_TERMINAL_20261017.json",
)


def github_issue_inventory() -> Dict[str, Any]:
    """Fixed, allowlisted gh read: never uses user-supplied argv or shell."""
    args = ["/opt/homebrew/bin/gh", "issue", "list", "-R", ISSUES_REPO,
            "--state", "open", "--limit", "250",
            "--json", "number,title,state,url,updatedAt"]
    try:
        output = subprocess.run(args, check=True, capture_output=True,
                                text=True, timeout=12)
        entries = json.loads(output.stdout)
        if not isinstance(entries, list):
            raise ValueError("unexpected issue inventory shape")
        remote_head = None
        local_head = None
        try:
            remote = subprocess.run(
                ["/opt/homebrew/bin/gh", "api",
                 "repos/knowurknottty/CAPT_core/commits/main",
                 "--jq", ".sha"],
                check=True, capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            if re.fullmatch(r"[0-9a-f]{40}", remote):
                remote_head = remote
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        try:
            local = subprocess.run(
                ["/usr/bin/git", "-C", str(Path.home() / "CAPT_core"),
                 "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True, timeout=5,
            ).stdout.strip()
            if re.fullmatch(r"[0-9a-f]{40}", local):
                local_head = local
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        return {
            "source": "GitHub CLI (read only)", "repository": ISSUES_REPO,
            "remoteHead": remote_head, "localHead": local_head,
            "headAlignment": ("identical" if remote_head == local_head else
                              "different; inspect history before writes")
                             if remote_head and local_head else "unverified",
            "status": "ok", "openCount": len(entries),
            "issues": [
                {"number": entry["number"], "title": entry["title"][:240],
                 "state": entry["state"], "url": entry["url"],
                 "updatedAt": entry.get("updatedAt")}
                for entry in entries[:250]
            ],
            "limit": 250,
            "mayBeTruncated": len(entries) >= 250,
        }
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            ValueError, KeyError, json.JSONDecodeError):
        return {"source": "GitHub CLI (read only)", "repository": ISSUES_REPO,
                "status": "unavailable", "openCount": None, "issues": [],
                "note": "GitHub issue evidence unavailable; do not assume no issues."}


def fixed_artifact_inventory() -> Dict[str, Any]:
    home = Path.home()
    paths = [{"name": name, "exists": (home / name).is_dir()}
             for name in CANDIDATES]
    core = home / "CAPT_core"
    evidence = [{"path": relative, "exists": (core / relative).is_file()}
                for relative in ARTIFACTS]
    return {"source": "fixed local filesystem read-only probe",
            "repositories": paths, "artifacts": evidence,
            "contentVerified": False}


def _event_receipts(controller: Any, stream: str) -> List[Dict[str, Any]]:
    try:
        events = controller._query("get_stream_events", streamId=stream)
    except Exception:
        return []
    if not isinstance(events, list):
        return []
    # Deliberately exclude payload: it may contain prompts, tokens, and private data.
    return [
        {"eventType": str(event.get("eventType", "")),
         "globalSequence": event.get("globalSequence"),
         "eventId": str(event.get("eventId", "")),
         "occurredAt": event.get("occurredAt")}
        for event in events[-36:]
    ]


def inspect_mission(controller: Any, mission_id: str) -> Dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9._:-]{1,170}", mission_id):
        raise ValueError("invalid mission ID")
    mission = controller._query("get_state", streamId="mission-" + mission_id)
    if mission.get("missionId") != mission_id:
        raise ValueError("mission identity mismatch")
    scoped_tasks = controller._query("tasks", missionId=mission_id, limit=250)
    tasks = scoped_tasks.get("tasks", [])
    if scoped_tasks.get("count", len(tasks)) > len(tasks):
        raise ValueError("task inventory incomplete")
    task_summary = [
        {"taskId": t.get("taskId"), "title": str(t.get("title") or "")[:380],
         "state": t.get("state"), "receipts": _event_receipts(controller, "task-" + t["taskId"])}
        for t in tasks
    ]
    approvals = controller._query("approvals", missionId=mission_id, limit=250)
    approval_rows = [
        {"requestId": a.get("requestId"), "state": a.get("state"),
         "derivedStale": bool(a.get("derivedStale")), "expiresAt": a.get("expiresAt")}
        for a in approvals.get("approvals", [])
    ]
    # A mission can contain prior DriverRuns even if a particular task has none.
    inventory = controller._query("list_aggregates")
    runs = []
    for entry in inventory:
        if entry.get("kind") != "driverrun":
            continue
        st = controller._query("get_state", streamId=entry["streamId"])
        if st.get("missionId") != mission_id:
            continue
        runs.append({"driverRunId": st.get("driverRunId"),
                     "taskId": st.get("taskId"), "state": st.get("state"),
                     "reconciliationStatus": st.get("reconciliationStatus"),
                     "receipts": _event_receipts(controller, entry["streamId"])})
    if len(runs) > 250:
        raise ValueError("DriverRun inventory incomplete")
    final_state = str(mission.get("state"))
    terminal = final_state in TERMINAL
    is_issue_scope = mission_id == ISSUES_MISSION
    issue_snapshot = github_issue_inventory() if is_issue_scope else None
    artifacts = fixed_artifact_inventory() if is_issue_scope else None
    objective = str(tasks[0].get("title") or "") if tasks else ""
    if is_issue_scope:
        next_step = ("Inspect historical receipts, reconcile current GitHub issues "
                     "against prior artifacts, and prepare a new read-only issue triage mission.")
        scope = ("Read only: EventStore receipts for predecessor; GitHub issues and "
                 "repository HEAD for knowurknottty/CAPT_core; candidate repository "
                 "paths explicitly listed in this recovery review.")
        write_gate = ("GitHub issue edits, commits, PRs, execution, and driver-run "
                      "resumption require separate, explicit approvals.")
        issue_lines = (
            [f"#{i['number']}: {i['title']}" for i in issue_snapshot["issues"]]
            if issue_snapshot["status"] == "ok"
            else ["Current GitHub inventory unavailable; establish it before disposition."]
        )
        draft = (
            "Create a NEW CAPT mission for the unfinished CAPT_core issue-resolution objective.\n"
            f"Predecessor (terminal; do not resume): {mission_id}.\n"
            f"Original objective: {objective}\n"
            "Stage 1 (read-only, no NEW DriverRuns): retrieve predecessor EventStore "
            "Mission/Task/DriverRun/approval receipts, current GitHub issue status and "
            "repository HEAD, and prior work artifacts. Separate proven completions, "
            "open issues, duplicates, stale reports, and missing evidence.\n"
            "Stage 2: construct a per-issue disposition matrix containing issue number, "
            "state, linked changes/PRs, evidence and reproduction/verification status.\n"
            "Stage 3: propose the smallest next engineering task with exact paths, tests, "
            "acceptance criteria, rollback, bounds, budget and explicit approval requests.\n"
            f"Read-only scope: {scope}\n"
            f"Withheld authority: {write_gate}\n"
            "Do not claim earlier success from a suspended or cancelled task. "
            "Do not automatically restart, dispatch provider work, push, edit issues "
            "or approve yourself. Stop at ambiguity and obtain human approval.\n"
            f"GitHub repository HEAD: {issue_snapshot.get('remoteHead') or 'unavailable'}.\n"
            f"Local CAPT_core HEAD: {issue_snapshot.get('localHead') or 'unavailable'} "
            f"(comparison: {issue_snapshot.get('headAlignment', 'unverified')}).\n"
            "Current open GitHub issues observed (reverify before use):\n"
            + "\n".join(issue_lines[:60])
        )
    else:
        next_step = ("Review receipts and draft a new goal; the old mission cannot be "
                     "reactivated." if terminal else
                     "Review blockers, then continue under the existing mission only if authorized.")
        scope = "No additional authority granted by this preview."
        write_gate = "Execution and external writes remain separately governed."
        draft = (
            f"Review CAPT mission {mission_id} (stored state: {final_state}). "
            f"Objective: {objective}. Reconcile prior receipts and verification first. "
            "Present the smallest next step, bounded authority, and explicit approval requests. "
            "Never assert completed work without evidence."
        )
    return {
        "missionId": mission_id, "state": final_state, "terminal": terminal,
        "continuableInPlace": final_state in ("authorized", "executing"),
        "missionEvents": _event_receipts(controller, "mission-" + mission_id),
        "tasks": task_summary, "approvals": approval_rows,
        "driverRuns": runs, "github": issue_snapshot, "candidateInventory": artifacts,
        "objective": objective, "smallestNextStep": next_step,
        "readAuthority": scope, "withheldAuthority": write_gate,
        "draft": draft[:12000],
        "sourceBoundary": ("EventStore mission/task/DriverRun states are authoritative; "
                           "GitHub inventory and filesystem probes are independent read-only "
                           "observations; a draft is NOT approval or execution."),
    }

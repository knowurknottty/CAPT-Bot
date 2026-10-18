"use strict";

// This is a projection and an operator decision surface, never a second
// mission authority. Every mutation uses an existing RuntimeService command.
const board = {missions: [], tasks: [], selected: null, dispositionPreview: null,
  activeDriverRuns: [], unreconciledDriverRuns: [], recovery: null};
const terminalTaskStates = new Set(["succeeded", "failed", "cancelled"]);
const terminalMissionStates = new Set(["completed", "failed", "cancelled"]);

function missionLane(m) {
  if (terminalMissionStates.has(m.state)) return "terminal";
  const s = m.taskStates || {};
  if ((s.awaiting_verification || 0) > 0) return "review";
  if ((s.suspended || 0) > 0) return "paused";
  return "queued";
}
function missionTasks(id) {
  return board.tasks.filter(t => t.missionId === id);
}
function boardView(view) {
  const goals = view === "goals";
  $("kanbanView").hidden = !goals;
  $("conversation").hidden = goals;
  document.querySelector(".composer-zone").hidden = goals;
  document.querySelectorAll("[data-view]").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
  if (goals) refreshKanban();
  if (view === "evidence") $("inspector").classList.add("open");
}
function note(text) {
  $("kanbanDetailNote").textContent = text;
}

function showMission(id) {
  const mission = board.missions.find(item => item.missionId === id);
  if (!mission) return;
  board.selected = mission;
  board.dispositionPreview = null;
  board.recovery = null;
  $("missionRecovery").hidden = true;
  $("missionRecoveryEvidence").replaceChildren();
  $("missionRecoveryIssues").replaceChildren();
  $("kanbanInspect").disabled = false;
  $("kanbanContinue").disabled = true;
  $("kanbanContinue").textContent = terminalMissionStates.has(mission.state) ?
    "Draft a successor goal" : "Plan governed continuation";
  $("dispositionActions").hidden = terminalMissionStates.has(mission.state);
  $("dispositionReview").hidden = true;
  $("dispositionConfirm").value = "";
  $("dispositionCommit").disabled = true;
  $("kanbanAuthorize").disabled = mission.state !== "draft";
  $("kanbanComplete").disabled = mission.state !== "executing";
  $("kanbanReconcile").disabled = mission.state !== "authorized";
  $("kanbanCancel").disabled = terminalMissionStates.has(mission.state);
  $("kanbanRevoke").disabled = terminalMissionStates.has(mission.state);
  $("kanbanDetailTitle").textContent = mission.missionId;
  const linked = missionTasks(id);
  const statuses = Object.entries(mission.taskStates || {}).map(([k,v]) => k + ": " + v).join(" · ");
  note(mission.state + " · " + (statuses || "No linked tasks") +
    (terminalMissionStates.has(mission.state) ?
      ". Historical receipt; this mission cannot resume. Inspect provenance to create a successor." :
      ". Review blockers and evidence before approval or continuation."));
  const panel = $("kanbanTaskList");
  panel.replaceChildren();
  for (const t of linked) {
    const card = document.createElement("article");
    card.className = "kanban-task";
    const h = document.createElement("strong");
    h.textContent = t.title || t.taskId;
    const p = document.createElement("p");
    p.textContent = t.state + " · " + t.taskId;
    card.append(h,p);
    if (!terminalMissionStates.has(mission.state) && !terminalTaskStates.has(t.state)) {
      const action = document.createElement("button");
      action.className = "deny";
      action.textContent = "Cancel this task";
      action.addEventListener("click", () => cancelKanbanTask(t));
      card.append(action);
    }
    panel.append(card);
  }
}


async function inspectMissionRecovery() {
  const selected = board.selected;
  if (!selected) return;
  const mid = selected.missionId;
  const summary = $("missionRecoverySummary");
  $("missionRecovery").hidden = false;
  summary.textContent = "Reading EventStore and independent evidence…";
  $("missionRecoveryEvidence").replaceChildren();
  $("missionRecoveryIssues").replaceChildren();
  $("kanbanInspect").disabled = true;
  $("kanbanContinue").disabled = true;
  try {
    const recovery = await api("/api/mission/recovery?missionId=" + encodeURIComponent(mid));
    if (board.selected?.missionId !== mid) return;
    board.recovery = recovery;
    const tasks = recovery.tasks || [];
    const runCount = (recovery.driverRuns || []).length;
    const approvalCount = (recovery.approvals || []).length;
    const github = recovery.github;
    summary.textContent = recovery.state.toUpperCase() + " · " +
      tasks.length + " linked task(s), " + runCount + " DriverRun(s), " +
      approvalCount + " approval(s). " + recovery.smallestNextStep;
    const details = $("missionRecoveryEvidence");
    for (const [label, value] of [
      ["Runtime receipts", (recovery.missionEvents || []).length +
        " mission events (metadata only), " + tasks.reduce((n,t)=>n+(t.receipts||[]).length,0) +
        " task events"],
      ["Authority", recovery.readAuthority],
      ["Write / execution gate", recovery.withheldAuthority],
      ["History", recovery.sourceBoundary],
    ]) {
      const entry = document.createElement("p");
      const strong = document.createElement("strong");
      strong.textContent = label + ": ";
      entry.append(strong, document.createTextNode(value));
      details.append(entry);
    }
    const issues = $("missionRecoveryIssues");
    if (github) {
      const title = document.createElement("h5");
      title.textContent = github.status === "ok" ?
        github.openCount + " GitHub issues open · independent read-only inventory" :
        "GitHub inventory unavailable: verify before decisions";
      issues.append(title);
      if (github.status === "ok") {
        const head = document.createElement("p");
        head.textContent = "GitHub HEAD: " + (github.remoteHead || "unavailable") +
          " · Local HEAD: " + (github.localHead || "unavailable") +
          " · " + (github.headAlignment || "unverified");
        issues.append(head);
      }
      for (const issue of (github.issues || []).slice(0, 30)) {
        const row = document.createElement("p");
        const link = document.createElement("a");
        link.href = issue.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "#" + issue.number + " · " + issue.title;
        row.append(link);
        issues.append(row);
      }
      const repos = document.createElement("p");
      repos.textContent = (recovery.candidateInventory?.repositories || [])
        .map(x => x.name + ": " + (x.exists ? "present" : "not found")).join(" · ");
      issues.append(repos);
    }
    $("kanbanContinue").disabled = false;
    $("kanbanContinue").textContent = recovery.continuableInPlace ?
      "Draft reviewed continuation" : "Draft successor goal";
  } catch (error) {
    summary.textContent = "Read-only inspection unavailable: " + error.message +
      ". No work was launched. Retry the review after restoring read access.";
  } finally {
    if (board.selected?.missionId === mid) $("kanbanInspect").disabled = false;
  }
}

function draftReviewedNextStep() {
  const recovery = board.recovery;
  if (!recovery || board.selected?.missionId !== recovery.missionId) return;
  const successor = !recovery.continuableInPlace;
  state.recoveryMissionId = recovery.missionId;
  state.continuationMissionId = successor ? null : recovery.missionId;
  state.missionOnSubmit = successor;
  $("missionMode").checked = successor;
  $("promptInput").value = recovery.draft;
  $("threadTitle").textContent = successor ? "New governed successor · review first" :
    "Reviewed continuation · " + recovery.missionId;
  $("composerNote").textContent = successor ?
    "Draft only. Send to compile, inspect proposal, then explicitly approve a NEW mission and any separate execution authority." :
    "Review of live predecessor required. Send to compile a new task; no old driver run is restarted automatically.";
  boardView("chat");
  updateWorkflow("scope", successor ?
    (recovery.terminal ?
      "Predecessor is terminal. Review the draft before compiling a NEW successor goal." :
      "The existing mission remains authorized, but in-place task creation is unavailable. Review this separate successor draft before compiling; no old run is restarted.") :
    "Review and edit the next task before compiling a governed continuation.",
    recovery.missionId);
  addMessage("CAPT · provenance", recovery.state + " predecessor " +
    recovery.missionId + ". " + recovery.sourceBoundary +
    "\nNo new mission, approval or DriverRun has been created.", "capt");
  nextStepFrom();
  $("promptInput").focus();
}

async function cancelKanbanTask(task) {
  const question = "Cancel task " + task.taskId +
    "?\n\nCAPT preserves its events and evidence. The parent mission will remain open until separately reconciled.";
  if (!window.confirm(question)) return;
  try {
    const response = await api("/api/task/cancel", {
      method: "POST",
      body: JSON.stringify({
        taskId: task.taskId,
        reason: "Explicit CAPT-Bot Kanban operator cancellation; history retained."
      })
    });
    if (!["accepted", "idempotent"].includes(response.status)) {
      throw new Error(response.error?.message || "Runtime did not accept cancellation.");
    }
    await refreshKanban();
    showMission(task.missionId);
  } catch (error) { note("Cancellation not completed: " + error.message); }
}

function renderKanban() {
  const filter = $("kanbanFilter").value;
  const term = $("kanbanSearch").value.toLowerCase().trim();
  const open = board.missions.filter(m => !terminalMissionStates.has(m.state));
  const review = open.filter(m => missionLane(m) === "review").length;
  const paused = open.filter(m => missionLane(m) === "paused").length;
  $("kanbanSummary").textContent =
    open.length + " open · " + review + " verification · " + paused + " suspended" +
    " · " + board.activeDriverRuns.length + " active DriverRuns";
  const matches = board.missions.filter(m => {
    if (filter === "all" && terminalMissionStates.has(m.state)) return false;
    if (filter !== "all" && missionLane(m) !== filter) return false;
    if (!term) return true;
    return m.missionId.toLowerCase().includes(term) ||
      missionTasks(m.missionId).some(t => (t.title || "").toLowerCase().includes(term));
  });
  const host = $("kanbanCards");
  host.replaceChildren();
  for (const m of matches.slice(0, 130)) {
    const item = document.createElement("article");
    item.className = "kanban-mission";
    const lane = document.createElement("small");
    lane.textContent = missionLane(m) + " / " + m.state;
    const heading = document.createElement("strong");
    heading.textContent = m.missionId;
    const task = missionTasks(m.missionId)[0];
    const desc = document.createElement("p");
    desc.textContent = task?.title || "No task description available.";
    const controls = document.createElement("div");
    controls.className = "kanban-actions";
    const inspect = document.createElement("button");
    inspect.className = "secondary";
    inspect.textContent = "Review";
    inspect.addEventListener("click", () => showMission(m.missionId));
    controls.append(inspect);
    item.append(lane, heading, desc, controls);
    host.append(item);
  }
  if (!matches.length) {
    const empty = document.createElement("section");
    empty.className = "kanban-empty";
    const heading = document.createElement("h3");
    heading.textContent = filter === "all" ? "No active missions" : "No missions match this view";
    const copy = document.createElement("p");
    copy.textContent = filter === "all" ?
      "Live work is clear. Historical receipts are preserved in the archive." :
      "Change your search or filter to inspect another mission.";
    empty.append(heading, copy);
    if (filter === "all") {
      const browse = document.createElement("button");
      browse.className = "secondary";
      browse.textContent = "Browse terminal archive";
      browse.addEventListener("click", () => {
        $("kanbanFilter").value = "terminal";
        $("kanbanSearch").value = "";
        renderKanban();
      });
      empty.append(browse);
    }
    host.append(empty);
  }
  if (matches.length > 130) {
    const more = document.createElement("p");
    more.textContent = "Showing 130 of " + matches.length + ". Search to narrow the review.";
    host.append(more);
  }
}

async function refreshKanban() {
  try {
    const result = await api("/api/kanban");
    board.missions = result.missions || [];
    board.tasks = result.tasks || [];
    board.activeDriverRuns = result.activeDriverRuns || [];
    board.unreconciledDriverRuns = result.unreconciledDriverRuns || [];
    renderKanban();
    if (board.selected) showMission(board.selected.missionId);
  } catch (error) {
    $("kanbanSummary").textContent = "Runtime unavailable";
    note("Could not refresh: " + error.message);
  }
}

$("kanbanInspect").addEventListener("click", inspectMissionRecovery);
$("kanbanContinue").addEventListener("click", draftReviewedNextStep);

async function reviewMissionDisposition(target) {
  const mission = board.selected;
  if (!mission || terminalMissionStates.has(mission.state)) return;
  board.dispositionPreview = null;
  $("dispositionReview").hidden = false;
  $("dispositionConfirm").value = "";
  $("dispositionCommit").disabled = true;
  $("dispositionSummary").textContent = "Fetching authoritative mission review…";
  try {
    const preview = await api("/api/mission/disposition/preview", {
      method: "POST",
      body: JSON.stringify({missionId: mission.missionId, target})
    });
    if (board.selected?.missionId !== mission.missionId) return;
    board.dispositionPreview = preview;
    const blockerText = (preview.blocked || []).join(", ");
    $("dispositionSummary").textContent = target.toUpperCase() +
      " · current: " + preview.currentState +
      " · " + preview.tasks.length + " tasks · " + preview.approvals.length +
      " approvals · " + preview.driverRuns.length + " driver runs" +
      " · " + preview.acceptedClaimCount + " accepted claims" +
      (target === "cancel_revoke" ? " · REVOKE " + preview.approvedRevocationCount +
       " previously approved grants; originals remain in the event history" : "") +
      (blockerText ? " · BLOCKED: " + blockerText +
        ". Use Inspect receipts & next step to prepare a scoped follow-up." :
        " · ready for explicit confirmation");
    $("dispositionCommit").textContent = target === "cancel_revoke" ? "Confirm revocation" :
      target === "cancel" ?
      "Confirm cancellation" : target === "complete" ? "Confirm completion" :
      target === "reconcile_complete" ? "Confirm reconciliation" : "Confirm authorization";
    updateDispositionConfirmation();
  } catch(error) {
    $("dispositionSummary").textContent = "Could not prepare review: " + error.message;
  }
}
function updateDispositionConfirmation() {
  const preview = board.dispositionPreview;
  $("dispositionCommit").disabled = !preview ||
    (preview.blocked || []).length > 0 ||
    $("dispositionConfirm").value !== preview.missionId;
}
async function commitMissionDisposition() {
  const preview = board.dispositionPreview;
  if (!preview || $("dispositionCommit").disabled) return;
  const button = $("dispositionCommit");
  button.disabled = true;
  try {
    const receipt = await api("/api/mission/disposition/apply", {
      method: "POST",
      body: JSON.stringify({
        missionId: preview.missionId,
        target: preview.target,
        expectedVersion: preview.expectedVersion,
        previewDigest: preview.previewDigest,
        confirmedMissionId: $("dispositionConfirm").value,
        reason: "Explicit reviewed CAPT-Bot mission disposition; audit history retained."
      }),
    });
    if (!["accepted", "idempotent"].includes(receipt.status)) {
      throw new Error(receipt.error?.message || "Authoritative mission command refused");
    }
    await refreshKanban();
    const mission = board.missions.find(m => m.missionId === preview.missionId);
    if (mission) showMission(mission.missionId);
    note("RuntimeService receipt: " + receipt.status +
      " · state: " + (receipt.result?.missionState || "inspect ledger") +
      " · events: " + (receipt.result?.settledEvents || 0));
  } catch (error) {
    $("dispositionSummary").textContent = "Not committed: " + error.message +
      ". Refresh the review; no blind retry.";
  } finally {
    board.dispositionPreview = null;
  }
}
$("kanbanAuthorize").addEventListener("click", () => reviewMissionDisposition("authorize"));
$("kanbanComplete").addEventListener("click", () => reviewMissionDisposition("complete"));
$("kanbanReconcile").addEventListener("click", () => reviewMissionDisposition("reconcile_complete"));
$("kanbanCancel").addEventListener("click", () => reviewMissionDisposition("cancel"));
$("kanbanRevoke").addEventListener("click", () => reviewMissionDisposition("cancel_revoke"));
$("dispositionAbort").addEventListener("click", () => {
  board.dispositionPreview = null;
  $("dispositionReview").hidden = true;
  $("dispositionConfirm").value = "";
});
$("dispositionConfirm").addEventListener("input", updateDispositionConfirmation);
$("dispositionCommit").addEventListener("click", commitMissionDisposition);

$("reloadKanban").addEventListener("click", refreshKanban);
$("kanbanSearch").addEventListener("input", renderKanban);
$("kanbanFilter").addEventListener("change", renderKanban);
document.querySelectorAll("[data-view]").forEach(btn =>
  btn.addEventListener("click", () => boardView(btn.dataset.view)));

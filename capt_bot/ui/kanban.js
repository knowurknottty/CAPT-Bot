"use strict";

// This is a projection and an operator decision surface, never a second
// mission authority. Every mutation uses an existing RuntimeService command.
const board = {missions: [], tasks: [], selected: null, dispositionPreview: null,
  activeDriverRuns: [], unreconciledDriverRuns: []};
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
  $("dispositionReview").hidden = true;
  $("dispositionConfirm").value = "";
  $("dispositionCommit").disabled = true;
  $("kanbanAuthorize").disabled = mission.state !== "draft";
  $("kanbanComplete").disabled = mission.state !== "executing";
  $("kanbanCancel").disabled = terminalMissionStates.has(mission.state);
  $("kanbanDetailTitle").textContent = mission.missionId;
  const linked = missionTasks(id);
  const statuses = Object.entries(mission.taskStates || {}).map(([k,v]) => k + ": " + v).join(" · ");
  note(mission.state + " · " + (statuses || "No linked tasks") +
    ". Completion requires ClaimGuard acceptance; task cancellation does not close a mission.");
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
    if (!terminalTaskStates.has(t.state)) {
      const action = document.createElement("button");
      action.className = "deny";
      action.textContent = "Cancel this task";
      action.addEventListener("click", () => cancelKanbanTask(t));
      card.append(action);
    }
    panel.append(card);
  }
  $("kanbanContinue").disabled = !["authorized", "executing"].includes(mission.state);
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

$("kanbanContinue").addEventListener("click", () => {
  const mission = board.selected;
  if (!mission || !["authorized", "executing"].includes(mission.state)) return;
  state.continuationMissionId = mission.missionId;
  state.missionOnSubmit = false;
  $("missionMode").checked = false;
  const first = missionTasks(mission.missionId)[0];
  $("promptInput").value = "Continue existing CAPT mission " + mission.missionId +
    ". Review past outcomes and recover unfinished acceptance criteria. " +
    (first?.title || "");
  $("composerNote").textContent = "Continuing existing Mission " + mission.missionId +
    ". A new task and one-use approval are required before execution.";
  boardView("chat");
  $("promptInput").focus();
});
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
      (blockerText ? " · BLOCKED: " + blockerText : " · ready for explicit confirmation");
    $("dispositionCommit").textContent = target === "cancel" ?
      "Confirm cancellation" : target === "complete" ? "Confirm completion" : "Confirm authorization";
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
$("kanbanCancel").addEventListener("click", () => reviewMissionDisposition("cancel"));
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

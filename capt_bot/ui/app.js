"use strict";

const $ = (id) => document.getElementById(id);
const state = {
  proposal: null,
  approval: null,
  clarificationFor: null,
  missionOnSubmit: false,
  continuationMissionId: null,
  selectedObjective: "",
  currentRun: null,
  snapshot: null,
  busy: false,
  recoveryMissionId: null,
  workflowPhase: null,
  providerCatalog: null,
  nextStepAction: "compose",
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json"},
    cache: "no-store",
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
  return body;
}

function addMessage(role, body, className = role) {
  $("welcome").hidden = true;
  const wrap = document.createElement("article");
  wrap.className = `message ${className}`;
  const head = document.createElement("div");
  head.className = "role";
  head.textContent = role;
  const text = document.createElement("div");
  text.className = "body";
  text.textContent = body;
  wrap.append(head, text);
  $("messages").append(wrap);
  $("conversation").scrollTop = $("conversation").scrollHeight;
  return wrap;
}

function rows(value) {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== "object") return [];
  for (const key of ["missions", "tasks", "approvals", "items", "results"]) {
    if (Array.isArray(value[key])) return value[key];
  }
  return [];
}

function setBusy(value, note = "") {
  state.busy = value;
  $("sendPrompt").disabled = value;
  if (note) $("composerNote").textContent = note;
  $("nextStepButton").disabled = value;
}

// The operator sees ONE safe next decision. All authority still belongs to
// RuntimeService and the existing human-only approval/explicit-Start controls.
function nextStepFrom(snapshot = state.snapshot, proposal = state.proposal) {
  const control = snapshot?.control || {};
  const grant = snapshot?.boundApproval || null;
  const run = snapshot?.execution?.driverRunState || null;
  const title = proposal?.originalPrompt?.split("\n").find(Boolean)?.trim();
  if (title && !state.recoveryMissionId) {
    $("threadTitle").textContent = title.slice(0, 64) +
      (title.length > 64 ? "…" : "");
  } else if (control.missionId && !state.recoveryMissionId) {
    $("threadTitle").textContent = "Mission · " + control.missionId;
  }
  let step;
  if (state.recoveryMissionId && state.workflowPhase === "scope" &&
      $("promptInput").value.trim()) {
    const successor = state.missionOnSubmit;
    step = {
      title: successor ? "Review the new successor mission draft" : "Review your proposed next task",
      description: successor
        ? "The original mission remains intact. Edit this evidence-based successor draft, then Send to compile. A new mission and one-use approval are requested only after your separate proposal-review action."
        : "CAPT prepared a draft from the mission's evidence. Edit it below, then Send to compile a new proposal. Sending alone does not create an approval or start a run.",
      label: "Review and edit draft",
      action: "compose",
    };
  } else if (snapshot?.approvalBindingError) {
    step = {
      title: "This approval cannot start a task",
      description: "The recorded approval points to a missing or mismatched task. CAPT has blocked execution. Inspect the mission receipts and create a fresh, reviewed task. Do not reuse this approval.",
      label: "Inspect blocked mission",
      action: "mission",
    };
  } else if (run) {
    step = {
      title: "An execution receipt already exists",
      description: "Inspect the DriverRun and its verification state. CAPT will not automatically retry an indeterminate effect.",
      label: "Review run receipt", action: "result",
    };
  } else if (grant?.state === "requested") {
    const expired = !Number.isFinite(Date.parse(grant.expiresAt)) ||
      Date.parse(grant.expiresAt) <= Date.now();
    step = expired ? {
      title: "Approval expired: request fresh authority",
      description: "This approval can no longer be used. Inspect the mission history before preparing a newly reviewed task.",
      label: "Inspect mission", action: "mission",
    } : {
      title: "Your approval is required",
      description: "Review the exact task, model and repository. Click Approve once or Deny in the review panel. Approval alone never launches the run.",
      label: "Review approval", action: "approval",
    };
  } else if (grant?.state === "approved") {
    const expired = !Number.isFinite(Date.parse(grant.expiresAt)) ||
      Date.parse(grant.expiresAt) <= Date.now();
    const eligible = !expired && !grant.consumedAt && Number(grant.remainingUses) > 0;
    step = eligible ? {
      title: "Approved: ready for your Start decision",
      description: "The one-use authority is recorded. Clicking Start will dispatch the bound task; it is not a simulation. You can still inspect the scope first.",
      label: "Start approved task", action: "start",
    } : {
      title: "Authority is no longer executable",
      description: "Approval was consumed, expired or exhausted. Review the ledger before creating a successor. Do not replay this run.",
      label: "Inspect mission", action: "mission",
    };
  } else if (control.approvalRequestId) {
    step = {
      title: "This approval needs reconciliation",
      description: "CAPT has an approval record, but not a verified runnable binding in this session. Inspect the authoritative task and approval receipts before taking action.",
      label: "Inspect mission", action: "mission",
    };
  } else if (proposal?.compilationStatus === "clarification_required") {
    step = {
      title: "CAPT needs one clarification",
      description: "Answer the question below. This revises the existing proposal and does not launch work.",
      label: "Answer in composer", action: "compose",
    };
  } else if (proposal?.state === "active" && proposal?.compilationStatus === "ready_for_approval") {
    step = {
      title: "Review what CAPT will do",
      description: "The proposal has been compiled, not executed. Check its target repository and instructions, then choose whether to request HumanApproval.",
      label: "Review compiled proposal", action: "proposal",
    };
  } else {
    step = {
      title: "Describe the work you want done",
      description: "Choose Track as mission for ongoing work. Send compiles a proposal; it does not approve, pay for or execute anything.",
      label: "Write a request", action: "compose",
    };
  }
  $("nextStepTitle").textContent = step.title;
  $("nextStepDescription").textContent = step.description;
  $("nextStepButton").textContent = step.label;
  $("nextStepButton").disabled = state.busy;
  state.nextStepAction = step.action;
}
function showReviewTarget(id) {
  $("inspector").classList.add("open");
  $(id)?.scrollIntoView({block: "nearest", behavior: "auto"});
}
function followNextStep() {
  if (state.busy) return;
  switch (state.nextStepAction) {
    case "compose":
      $("promptInput").focus();
      break;
    case "proposal":
      showReviewTarget("proposalText");
      break;
    case "approval":
      showReviewTarget("approvalDetail");
      break;
    case "start":
      startApprovedTask();
      break;
    case "result":
      showReviewTarget("reviewDetail");
      break;
    case "mission": {
      const mission = state.snapshot?.control?.missionId;
      if (mission) {
        $("kanbanFilter").value = "all";
        $("kanbanSearch").value = mission;
        boardView("goals");
        refreshKanban().then(() => showMission(mission));
      } else {
        boardView("goals");
      }
      break;
    }
  }
}

function renderStages(proposal) {
  const records = new Map(
    (proposal?.stageRecords || []).map((record) => [record.stage, record])
  );
  for (const item of document.querySelectorAll("#stageChain li")) {
    item.classList.remove("running", "done", "blocked");
    const record = records.get(item.dataset.stage);
    if (!record) continue;
    if (record.executionEnabled) item.classList.add("done");
    else item.classList.add("blocked");
  }
}

function renderProposal(proposal) {
  state.proposal = proposal || null;
  const status = proposal?.compilationStatus || proposal?.status || "Idle";
  $("proposalStatus").textContent = status;
  $("proposalText").textContent = proposal?.proposedPrompt || "No proposal yet.";
  const requested = String(proposal?.originalPrompt || "");
  const root = String(proposal?.targetRoot || "");
  const expectedRepo = requested.includes("knowurknottty/CAPT_core");
  $("proposalTargetNotice").textContent = expectedRepo
    ? "Target directory: " + (root || "UNSPECIFIED") +
      ". Verify this checkout is the intended CAPT_core repository before approving. Changing the target requires recompilation."
    : root ? "Approved execution scope will be limited to: " + root : "";
  renderStages(proposal);
  if (state.snapshot) nextStepFrom(state.snapshot, proposal);

  const blocked = status === "clarification_required";
  const active = proposal?.state === "active";
  const hasBoundSelection = Boolean(state.snapshot?.control?.approvalRequestId);
  $("approveProposal").disabled = !active || blocked || hasBoundSelection;
  $("useOriginal").disabled = !active || blocked || hasBoundSelection;

  if (blocked) {
    state.clarificationFor = proposal.proposalId;
    const questions = proposal.unresolvedQuestions || [];
    addMessage(
      "CAPT · clarification",
      questions.length ? questions.join("\n") : "CAPT needs clarification before continuing.",
      "system",
    );
    $("promptInput").placeholder = "Answer OMNI's blocking question…";
    $("composerNote").textContent =
      "Your answer continues this exact proposal revision; it does not create a new proposal.";
  } else {
    state.clarificationFor = null;
    $("promptInput").placeholder = "Describe what you want CAPT to do…";
  }
}

function renderApproval(approval) {
  state.approval = approval || null;
  const requestId = approval?.requestId;
  const status = approval?.state || "None";
  $("approvalState").textContent = status;
  $("approvalDetail").replaceChildren();
  const entries = [
    ["request", requestId],
    ["mission", approval?.missionId],
    ["task", approval?.taskId],
    ["run", approval?.driverRunId],
    ["provider", [approval?.provider, approval?.model].filter(Boolean).join(" / ")],
    ["target", approval?.targetRoot],
    ["expires", approval?.expiresAt],
  ].filter(([, value]) => value);
  if (!entries.length) {
    const p = document.createElement("p");
    p.textContent = "No current session-bound approval. Select a compiled proposal first.";
    $("approvalDetail").append(p);
  } else {
    for (const [label, value] of entries) {
      const row = document.createElement("div");
      row.className = "detail-row";
      const left = document.createElement("span");
      left.textContent = label;
      const right = document.createElement("strong");
      right.textContent = String(value);
      row.append(left, right);
      $("approvalDetail").append(row);
    }
  }
  const bound = ["requestId", "missionId", "taskId", "driverRunId"].every(
    key => Boolean(approval?.[key])
  );
  const expiry = Date.parse(approval?.expiresAt || "");
  const expired = !Number.isFinite(expiry) || expiry <= Date.now();
  const pending = bound && status === "requested" && !expired;
  const approved = bound && status === "approved" && !expired &&
    !approval?.consumedAt && Number(approval?.remainingUses) > 0;
  const dispatched = Boolean(state.snapshot?.execution?.driverRunState);
  $("approveRequest").disabled = !pending;
  $("denyRequest").disabled = !pending;
  $("startTask").disabled = !approved || dispatched || state.busy;
  $("startTaskStatus").textContent = !bound
    ? "No executable receipt is bound to the current session. Use the proposal selector."
    : expired
      ? "Approval expired. Select the active proposal again to request fresh authority."
      : pending
        ? "Awaiting your HumanApproval. Approving will NOT automatically dispatch."
        : approved && !dispatched
          ? "Approved and unused. Start task is a separate, explicitly governed action."
          : dispatched
            ? "A DriverRun already exists. Inspect and reconcile its receipt; no automatic replay."
            : status === "approved"
              ? "Authority already consumed or exhausted. Reconcile before any further run."
              : "No runnable authority at state: " + status;
}

function renderMissions(snapshot) {
  const missions = rows(snapshot?.missions).filter(mission =>
    !["completed", "failed", "cancelled"].includes(mission.state)
  );
  $("missionList").replaceChildren();
  $("activeGoalCount").textContent = "(" + missions.length + ")";
  if (!missions.length) {
    const empty = document.createElement("p");
    empty.className = "rail-empty";
    empty.textContent = "No active goals. Finished work is preserved in the archive.";
    $("missionList").append(empty);
    return;
  }
  for (const mission of missions.slice(0, 40)) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "mission-card active";
    const title = document.createElement("strong");
    const humanTitle = String(mission.objective || mission.rawRequest || "").split("\n")[0].trim();
    title.textContent = humanTitle ? humanTitle.slice(0, 85) : (mission.missionId || "Mission");
    card.title = mission.missionId || "";
    const meta = document.createElement("span");
    meta.textContent = (mission.state || "unknown") + " · " + (mission.missionId || "");
    card.append(title, meta);
    card.addEventListener("click", () => {
      $("kanbanFilter").value = "all";
      $("kanbanSearch").value = mission.missionId;
      boardView("goals");
      refreshKanban().then(() => showMission(mission.missionId));
    });
    $("missionList").append(card);
  }
}

const WORKFLOW_PHASES = ["evidence", "scope", "compile", "approval", "execute", "verify"];
function updateWorkflow(phase, message, origin) {
  state.workflowPhase = phase;
  $("workflowRibbon").hidden = false;
  $("workflowOrigin").textContent = origin || state.recoveryMissionId || "New governed work";
  $("workflowStatus").textContent = message;
  const button = $("workflowNextAction");
  button.textContent = {
    evidence: "Review evidence",
    scope: "Edit scoped draft",
    compile: "Review compile status",
    approval: "Open approval inspector",
    execute: "Inspect execution",
    verify: "Inspect verification"
  }[phase] || "Review next step";
  const at = WORKFLOW_PHASES.indexOf(phase);
  for (const item of $("workflowSteps").querySelectorAll("li")) {
    const n = WORKFLOW_PHASES.indexOf(item.dataset.step);
    item.classList.toggle("done", at > n);
    item.classList.toggle("current", at === n);
  }
}


function renderReview(run) {
  state.currentRun = run || null;
  const awaiting = run?.taskState === "awaiting_verification";
  $("reviewState").textContent = run?.taskState || "No result";
  $("reviewDetail").replaceChildren();
  const p = document.createElement("p");
  p.textContent = run?.driverRunId
    ? `DriverRun ${run.driverRunId}`
    : "No provider result awaiting review.";
  $("reviewDetail").append(p);
  $("reviewNote").disabled = !awaiting;
  $("acceptResult").disabled = !awaiting;
  $("rejectResult").disabled = !awaiting;
}

function renderRuntime(snapshot) {
  state.snapshot = snapshot;
  renderMissions(snapshot);
  const control = snapshot?.control || {};
  $("statusDot").classList.add("ok");
  $("statusText").textContent = "RuntimeService connected";

  const list = $("runtimeState");
  list.replaceChildren();
  const values = [
    ["session", control.activeSessionId],
    ["provider", control.provider],
    ["model", control.model],
    ["root", control.targetRoot],
    ["PI", control.promptIntelligence],
  ].filter(([, value]) => value);
  for (const [label, value] of values) {
    const row = document.createElement("div");
    row.className = "detail-row";
    const left = document.createElement("span");
    left.textContent = label;
    const right = document.createElement("strong");
    right.textContent = String(value);
    row.append(left, right);
    list.append(row);
  }
  // Background refresh must not overwrite the user's in-progress selections.
  if (!$("configDialog").open) {
    $("rootInput").value = control.targetRoot || "";
    $("piInput").value = control.promptIntelligence || "AUTO";
  }

  // Never overwrite the exact current-session approval with an unrelated
  // global summary (which lacks a DriverRun binding).
  renderApproval(snapshot?.boundApproval || null);
  // An existing selection must not be silently promoted again.
  if (control.approvalRequestId) {
    $("approveProposal").disabled = true;
    $("useOriginal").disabled = true;
  }
  nextStepFrom(snapshot, snapshot?.pendingProposal || state.proposal);
  if (snapshot?.approvalBindingError) {
    $("approvalState").textContent = "Blocked";
    const reason = document.createElement("p");
    reason.textContent = "This approval refers to a missing or mismatched task. It cannot be approved or executed. Inspect the mission receipts and create a new, correctly bound request.";
    $("approvalDetail").replaceChildren(reason);
    $("approveRequest").disabled = true;
    $("denyRequest").disabled = true;
    $("startTask").disabled = true;
    $("startTaskStatus").textContent =
      "Blocked: " + snapshot.approvalBindingError +
      ". This request is non-runnable; no retry or automatic replay.";
  }
}

function renderBots(snapshot) {
  const box = $("botList");
  box.replaceChildren();
  const bots = Array.isArray(snapshot?.bots) ? snapshot.bots : [];
  if (!bots.length) {
    box.textContent = "No registered Bots";
    return;
  }
  for (const bot of bots) {
    const item = document.createElement("p");
    item.className = "bot-list-item";
    item.textContent = `${bot.displayName || bot.botId} · ${bot.roleKind || "crew"}`;
    item.title = bot.botId;
    box.append(item);
  }
}

async function refresh() {
  try {
    const snapshot = await api("/api/snapshot");
    renderRuntime(snapshot);
    if (snapshot.pendingProposal && !state.busy &&
        state.proposal?.proposalId !== snapshot.pendingProposal.proposalId) {
      renderProposal(snapshot.pendingProposal);
      updateWorkflow(
        snapshot.pendingProposal.compilationStatus === "clarification_required" ?
          "scope" : "approval",
        "Recovered live CAPT proposal from RuntimeService. Inspect the contract and continue through the approval gate."
      );
      addMessage("CAPT · recovered", "A pending governed proposal was restored from RuntimeService. No execution was replayed.", "capt");
      nextStepFrom(snapshot, snapshot.pendingProposal);
    }
    const bots = await api("/api/bots");
    renderBots(bots);
  } catch (error) {
    $("statusDot").classList.remove("ok");
    $("statusText").textContent = "Runtime unavailable";
    $("composerNote").textContent = error.message;
  }
}

async function sendPrompt() {
  const input = $("promptInput");
  const text = input.value.trim();
  if (!text || state.busy) return;
  const clarificationFor = state.clarificationFor;
  addMessage(clarificationFor ? "You · clarification" : "You", text, "user");
  input.value = "";
  setBusy(true, clarificationFor ? "Continuing governed proposal…" : "Compiling prompt…");
  try {
    const result = await api("/api/prompt", {
      method: "POST",
      body: JSON.stringify({
        text,
        developer: $("developerMode").checked,
        clarificationFor,
        requestedContextBudget: 64000,
      }),
    });
    const proposal = result.proposal || result;
    state.missionOnSubmit = $("missionMode").checked;
    renderProposal(proposal);
    if ((proposal.compilationStatus || proposal.status) === "clarification_required") {
      updateWorkflow("scope", "Clarification is required. Answer the question in the composer to revise this exact proposal.");
    }
    if ((proposal.compilationStatus || proposal.status) !== "clarification_required") {
      updateWorkflow("approval", "Compiled prompt ready: inspect the SDR and select a basis before requesting approval.");
      addMessage(
        "CAPT",
        "Prompt compilation is ready for review. Inspect the transformed contract before approval.",
        "capt",
      );
      $("composerNote").textContent =
        "Review the proposal and authority request. Execution still requires governed approval.";
    }
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
    $("composerNote").textContent = "Compilation failed; no execution was implied.";
  } finally {
    setBusy(false);
    nextStepFrom();
  }
}

async function selectProposal(basis) {
  if (!state.proposal || state.busy) return;
  setBusy(true, "Binding selected prompt to a one-use approval request…");
  try {
    const result = await api("/api/proposal/select", {
      method: "POST",
      body: JSON.stringify({
        proposalId: state.proposal.proposalId,
        basis,
        asMission: !state.continuationMissionId && (state.missionOnSubmit || $("missionMode").checked),
        existingMissionId: state.continuationMissionId,
        requestedExecutionSeconds: 1800,
      }),
    });
    const approval = result.selection?.result?.approval || result.selection?.approval;
    state.selectedObjective = result.selectedObjective || "";
    state.continuationMissionId = null;
    if (approval) {
      addMessage("CAPT · authority", "Exact approval request " + approval.requestId +
        " created. Choose Approve once or Deny; execution requires a separate Start.", "capt");
    }
    if (result.missionId) {
      addMessage(
        "CAPT · mission",
        `Goal admitted as mission ${result.missionId}, task ${result.taskId}.`,
        "capt",
      );
    } else {
      addMessage("CAPT", approval ?
        "Selected prompt is bound to a one-use approval request." :
        "Selection recorded; no executable approval receipt is available yet. Inspect the authority panel.", "capt");
    }
    updateWorkflow("approval", "Prompt selection recorded. Review the exact bound approval before any model run.");
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  } finally {
    setBusy(false);
    nextStepFrom();
  }
}

async function decide(decision) {
  const approval = state.approval;
  const requestId = approval?.requestId;
  if (!requestId || state.busy) return;
  setBusy(true, decision === "approve" ? "Recording human approval…" : "Recording denial…");
  try {
    const receipt = await api("/api/approval/decide", {
      method: "POST",
      body: JSON.stringify({requestId, decision}),
    });
    if (!["accepted", "idempotent"].includes(receipt.status))
      throw new Error("RuntimeService did not accept the approval decision");
    addMessage("CAPT · approval",
      decision + ": " + requestId + ". " +
      (decision === "approve" ? "No run launched. Press Start approved task to dispatch." :
        "Execution was not launched."), "capt");
    updateWorkflow("approval", decision === "approve"
      ? "HumanApproval recorded. Explicit Start approved task is next; no auto-dispatch."
      : "Approval denied. Re-scope before requesting new authority.");
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  } finally {
    setBusy(false);
    renderApproval(state.snapshot?.boundApproval || state.approval);
  }
}

async function startApprovedTask() {
  const approval = state.approval;
  if (!approval?.requestId || state.busy || $("startTask").disabled) return;
  setBusy(true, "Submitting one approved DriverRun. Never automatically replay on timeout…");
  $("startTask").disabled = true;
  try {
    const response = await api("/api/run/start", {
      method: "POST",
      body: JSON.stringify({requestId: approval.requestId}),
    });
    if (!["accepted", "idempotent"].includes(response.status))
      throw new Error("RuntimeService did not confirm accepted execution");
    const result = response.result || response;
    renderReview(result);
    updateWorkflow("verify",
      "Execution returned a receipt; ClaimGuard verification remains independent.");
    addMessage("CAPT · run", (result.observations || [])[0]?.summary ||
      result.outcome || "Execution completed or was admitted. Inspect authoritative receipts.", "capt");
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message +
      " Do not retry automatically; check Mission / Goals and the DriverRun ledger first.", "system");
    await refresh();
  } finally {
    setBusy(false);
    renderApproval(state.snapshot?.boundApproval || null);
  }
}

async function reviewResult(disposition) {
  const run = state.currentRun;
  if (!run?.driverRunId || run.taskState !== "awaiting_verification") return;
  setBusy(true, "Recording verification through ClaimGuard…");
  try {
    const receipt = await api("/api/result/review", {
      method: "POST",
      body: JSON.stringify({
        driverRunId: run.driverRunId,
        disposition,
        note: $("reviewNote").value.trim(),
      }),
    });
    const result = receipt.result || receipt;
    renderReview({...run, taskState: result.taskState || disposition});
    updateWorkflow("verify", "Verification recorded. Inspect the mission board for evidence-bound closure.");
    addMessage(
      "CAPT · verification",
      `${disposition}: task ${result.taskState || "updated"}, mission ${result.missionState || "unchanged"}.`,
      "capt",
    );
    $("reviewNote").value = "";
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  } finally {
    setBusy(false);
  }
}

function setConfigError(message) {
  $("configError").textContent = message || "";
}

function activeCatalogProvider() {
  return state.providerCatalog?.providers?.find(p => p.id === $("providerInput").value);
}

function modelChoiceLabel(model) {
  // For full local file paths, the filename is easier to recognize. The option
  // value remains the exact configured model ID/path (never reconstructed).
  return model.startsWith("/") ? model.split("/").pop() : model;
}

function fillModelChoices(preferred = "") {
  const provider = activeCatalogProvider();
  const models = Array.isArray(provider?.models) ? provider.models : [];
  const query = $("modelSearch").value.trim().toLowerCase();
  const selected = models.includes(preferred) ? preferred : "";
  const choices = models.filter(m => !query || m.toLowerCase().includes(query));
  if (selected && !choices.includes(selected)) choices.unshift(selected);
  const select = $("modelInput");
  select.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = models.length ? "Choose a configured model" : "No configured models";
  select.append(placeholder);
  for (const model of choices) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = modelChoiceLabel(model);
    option.title = model;
    select.append(option);
  }
  select.value = selected;
  select.disabled = !models.length;
  $("modelSearch").disabled = !models.length;
  $("catalogStatus").textContent = provider ?
    provider.name + " · " + provider.kind + " · " + models.length +
    " configured model(s)" + (query ? " · " + choices.length + " displayed" : "") +
    ". Configuration does not guarantee provider availability." :
    "Select a provider. No network model discovery or paid requests are performed.";
  $("saveConfig").disabled = !models.length || !selected || state.busy;
}

async function openRuntimeConfiguration() {
  $("configDialog").showModal();
  setConfigError("");
  $("saveConfig").disabled = true;
  $("providerInput").disabled = true;
  $("modelInput").disabled = true;
  $("modelSearch").disabled = true;
  $("modelSearch").value = "";
  $("rootInput").value = state.snapshot?.control?.targetRoot || "";
  $("piInput").value = state.snapshot?.control?.promptIntelligence || "AUTO";
  $("catalogStatus").textContent = "Reading CAPT's configured provider registry…";
  try {
    const catalog = await api("/api/providers");
    if (!$("configDialog").open) return;
    state.providerCatalog = catalog;
    const select = $("providerInput");
    select.replaceChildren();
    const choose = document.createElement("option");
    choose.value = "";
    choose.textContent = "Choose provider";
    select.append(choose);
    for (const provider of catalog.providers || []) {
      const option = document.createElement("option");
      option.value = provider.id;
      option.textContent = provider.name + " (" + provider.id + ")" +
        (provider.models.length ? "" : " · No configured models");
      option.disabled = !provider.models.length;
      select.append(option);
    }
    const control = state.snapshot?.control || {};
    const current = catalog.providers.find(p => p.id === control.provider);
    select.value = current?.models.length ? current.id : "";
    select.disabled = false;
    fillModelChoices(select.value ? control.model : "");
    if (control.provider && !select.value) {
      setConfigError("Current provider is missing, disabled, or has no configured models. Select an available provider.");
    } else if (select.value && !($("modelInput").value)) {
      setConfigError("Current model is not listed under this provider. Choose a configured model before applying.");
    }
  } catch (error) {
    if (!$("configDialog").open) return;
    state.providerCatalog = null;
    $("catalogStatus").textContent = "Provider catalog unavailable.";
    setConfigError(error.message + ". No configuration has been changed.");
  }
}

async function saveConfig(event) {
  event.preventDefault();
  try {
    const provider = activeCatalogProvider();
    const model = $("modelInput").value;
    if (!provider || !provider.models.includes(model))
      throw new Error("Choose a valid provider and configured model before applying.");
    $("saveConfig").disabled = true;
    const result = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({
        provider: provider.id,
        model,
        targetRoot: $("rootInput").value.trim(),
        promptIntelligence: $("piInput").value,
      }),
    });
    state.snapshot = {...(state.snapshot || {}), control: result};
    $("configDialog").close();
    renderRuntime(state.snapshot);
    addMessage("CAPT", "Runtime configuration updated. No execution was started.", "capt");
  } catch (error) {
    setConfigError(error.message);
    fillModelChoices($("modelInput").value);
  }
}

async function newThread() {
  try {
    await api("/api/chat/new", {method: "POST", body: "{}"});
    state.proposal = null;
    state.approval = null;
    state.clarificationFor = null;
    state.missionOnSubmit = false;
    state.continuationMissionId = null;
    state.selectedObjective = "";
    state.recoveryMissionId = null;
    state.workflowPhase = null;
    $("workflowRibbon").hidden = true;
    renderReview(null);
    $("messages").replaceChildren();
    $("welcome").hidden = false;
    $("threadTitle").textContent = "New conversation";
    renderProposal(null);
    renderApproval(null);
    await refresh();
    nextStepFrom();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  }
}

async function registerBot(event) {
  event.preventDefault();
  const submit = $("registerBotButton");
  if (submit.disabled) return;
  submit.disabled = true;
  $("createBotError").textContent = "";
  try {
    const response = await api("/api/bots/register", {
      method: "POST",
      body: JSON.stringify({
        botId: $("botIDInput").value.trim(),
        displayName: $("botNameInput").value.trim(),
        role: $("botRoleInput").value.trim(),
        primaryModel: $("botModelInput").value.trim() || null,
        defaultRuntime: $("botRuntimeInput").value,
        cloudAllowed: $("botCloudInput").checked,
      }),
    });
    if (!["accepted", "idempotent"].includes(response.status) ||
        !response.result?.identityOnly) {
      throw new Error("Runtime did not confirm identity-only registration");
    }
    $("createBotDialog").close();
    addMessage("CAPT · Bot", `${response.result.botId} registered. No tool or execution authority granted.`, "capt");
    await refresh();
  } catch (error) {
    $("createBotError").textContent = error.message;
  } finally {
    submit.disabled = false;
  }
}

$("nextStepButton").addEventListener("click", followNextStep);
$("nextStepDetails").addEventListener("click", () => {
  const id = state.nextStepAction === "approval" ? "approvalDetail" :
    state.nextStepAction === "result" ? "reviewDetail" : "proposalText";
  showReviewTarget(id);
});
$("openMissionArchive").addEventListener("click", () => {
  $("kanbanFilter").value = "terminal";
  $("kanbanSearch").value = "";
  boardView("goals");
});
$("workflowNextAction").addEventListener("click", () => {
  if (state.workflowPhase === "scope") {
    $("promptInput").focus();
    return;
  }
  if (state.workflowPhase === "evidence" && state.recoveryMissionId) {
    $("workflowBackToEvidence").click();
    return;
  }
  $("inspector").classList.add("open");
  const target = state.workflowPhase === "verify" ? $("reviewDetail") :
    state.workflowPhase === "approval" ? $("proposalText") : $("runtimeState");
  target?.scrollIntoView({block: "nearest", behavior: "auto"});
});
$("workflowBackToEvidence").addEventListener("click", () => {
  if (!state.recoveryMissionId) return;
  $("kanbanSearch").value = state.recoveryMissionId;
  $("kanbanFilter").value = "terminal";
  boardView("goals");
  refreshKanban().then(() => showMission(state.recoveryMissionId));
});
$("createBot").addEventListener("click", () => $("createBotDialog").showModal());
$("closeBotDialog").addEventListener("click", () => $("createBotDialog").close());
$("createBotForm").addEventListener("submit", registerBot);
$("sendPrompt").addEventListener("click", sendPrompt);
$("promptInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendPrompt();
  }
});
$("approveProposal").addEventListener("click", () => selectProposal("proposed"));
$("useOriginal").addEventListener("click", () => selectProposal("original"));
$("approveRequest").addEventListener("click", () => decide("approve"));
$("startTask").addEventListener("click", startApprovedTask);
$("denyRequest").addEventListener("click", () => decide("deny"));
$("acceptResult").addEventListener("click", () => reviewResult("accept"));
$("rejectResult").addEventListener("click", () => reviewResult("reject"));
$("refreshState").addEventListener("click", refresh);
$("newChat").addEventListener("click", newThread);
$("openConfig").addEventListener("click", openRuntimeConfiguration);
$("providerInput").addEventListener("change", () => {
  $("modelSearch").value = "";
  setConfigError("");
  fillModelChoices();
});
$("modelInput").addEventListener("change", () => {
  setConfigError("");
  fillModelChoices($("modelInput").value);
});
$("modelSearch").addEventListener("input", () => {
  fillModelChoices($("modelInput").value);
});
$("configDialog").addEventListener("close", () => {
  state.providerCatalog = null;
  setConfigError("");
});
$("configForm").addEventListener("submit", saveConfig);
$("copyProposal").addEventListener("click", async () => {
  if (state.proposal?.proposedPrompt) {
    await navigator.clipboard.writeText(state.proposal.proposedPrompt);
  }
});
$("toggleInspector").addEventListener("click", () => $("inspector").classList.toggle("open"));
$("closeInspector").addEventListener("click", () => $("inspector").classList.remove("open"));
$("toggleLeft").addEventListener("click", () => $("leftRail").classList.toggle("open"));
$("developerMode").addEventListener("change", () => {
  $("composerNote").textContent = $("developerMode").checked
    ? "Advanced mode forces the full prompt chain. Execution still needs separate approval and Start."
    : "Send prepares a proposal. Nothing runs until explicitly approved and started.";
});

refresh();
setInterval(refresh, 5000);

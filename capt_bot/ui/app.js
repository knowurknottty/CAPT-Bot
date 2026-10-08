"use strict";

const $ = (id) => document.getElementById(id);
const state = {
  proposal: null,
  approval: null,
  clarificationFor: null,
  missionOnSubmit: false,
  selectedObjective: "",
  currentRun: null,
  snapshot: null,
  busy: false,
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
  renderStages(proposal);

  const blocked = status === "clarification_required";
  const active = proposal?.state === "active";
  $("approveProposal").disabled = !active || blocked;
  $("useOriginal").disabled = !active || blocked;

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
  const requestId = approval?.requestId || approval?.approvalRequestId;
  const status = approval?.state || approval?.status || "None";
  $("approvalState").textContent = status;
  $("approvalDetail").replaceChildren();
  const entries = [
    ["request", requestId],
    ["mission", approval?.missionId],
    ["task", approval?.taskId],
    ["expires", approval?.expiresAt],
  ].filter(([, value]) => value);
  if (!entries.length) {
    const p = document.createElement("p");
    p.textContent = "No approval request.";
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
  const pending = Boolean(requestId) && ["pending", "requested", "awaiting_human"].includes(status);
  $("approveRequest").disabled = !pending;
  $("denyRequest").disabled = !pending;
}

function renderMissions(snapshot) {
  const missions = rows(snapshot?.missions);
  $("missionList").replaceChildren();
  for (const mission of missions.slice(0, 20)) {
    const card = document.createElement("div");
    card.className = "mission-card";
    if (!["completed", "failed", "cancelled"].includes(mission.state)) card.classList.add("active");
    const title = document.createElement("strong");
    title.textContent = mission.objective || mission.rawRequest || mission.missionId || "Mission";
    const meta = document.createElement("span");
    meta.textContent = `${mission.state || "unknown"} · ${mission.missionId || ""}`;
    card.append(title, meta);
    $("missionList").append(card);
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
  $("providerInput").value = control.provider || "";
  $("modelInput").value = control.model || "";
  $("rootInput").value = control.targetRoot || "";
  $("piInput").value = control.promptIntelligence || "AUTO";

  const approvals = rows(snapshot?.approvals);
  const pending = approvals.find((item) =>
    ["pending", "requested", "awaiting_human"].includes(item.state)
  );
  if (pending) renderApproval(pending);
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
    if ((proposal.compilationStatus || proposal.status) !== "clarification_required") {
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
        asMission: state.missionOnSubmit || $("missionMode").checked,
        requestedExecutionSeconds: 1800,
      }),
    });
    const approval = result.selection?.result?.approval || result.selection?.approval;
    state.selectedObjective = result.selectedObjective || "";
    if (approval) renderApproval(approval);
    if (result.missionId) {
      addMessage(
        "CAPT · mission",
        `Goal admitted as mission ${result.missionId}, task ${result.taskId}.`,
        "capt",
      );
    } else {
      addMessage("CAPT", "Selected prompt is bound to an approval request.", "capt");
    }
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  } finally {
    setBusy(false);
  }
}

async function decide(decision) {
  const approval = state.approval;
  const requestId = approval?.requestId || approval?.approvalRequestId;
  if (!requestId || state.busy) return;
  setBusy(true, decision === "approve" ? "Approving and dispatching exact bound run…" : "Recording denial…");
  try {
    await api("/api/approval/decide", {
      method: "POST",
      body: JSON.stringify({requestId, decision}),
    });
    addMessage("CAPT · approval", `${decision}: ${requestId}`, "capt");
    if (decision === "approve") {
      const run = await api("/api/run", {
        method: "POST",
        body: JSON.stringify({
          approval,
          objective: state.selectedObjective,
          requestedContextBudget: 64000,
          humanVerificationRequired: true,
        }),
      });
      const result = run.result || run;
      renderReview(result);
      const observation = (result.observations || [])[0]?.summary;
      addMessage(
        "CAPT · run",
        observation || result.outcome || "Run returned without a displayable observation.",
        "capt",
      );
      $("composerNote").textContent =
        "Execution returned. Mission remains open until verification and completion criteria are satisfied.";
    }
    await refresh();
  } catch (error) {
    addMessage("CAPT · error", error.message, "system");
  } finally {
    setBusy(false);
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

async function saveConfig(event) {
  event.preventDefault();
  try {
    const result = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({
        provider: $("providerInput").value.trim(),
        model: $("modelInput").value.trim(),
        targetRoot: $("rootInput").value.trim(),
        promptIntelligence: $("piInput").value,
      }),
    });
    renderRuntime({...(state.snapshot || {}), control: result});
    $("configDialog").close();
    addMessage("CAPT", "Runtime configuration updated. No execution was started.", "capt");
  } catch (error) {
    $("composerNote").textContent = error.message;
  }
}

async function newThread() {
  try {
    await api("/api/chat/new", {method: "POST", body: "{}"});
    state.proposal = null;
    state.approval = null;
    state.clarificationFor = null;
    state.missionOnSubmit = false;
    state.selectedObjective = "";
    renderReview(null);
    $("messages").replaceChildren();
    $("welcome").hidden = false;
    $("threadTitle").textContent = "New conversation";
    renderProposal(null);
    renderApproval(null);
    await refresh();
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
$("denyRequest").addEventListener("click", () => decide("deny"));
$("acceptResult").addEventListener("click", () => reviewResult("accept"));
$("rejectResult").addEventListener("click", () => reviewResult("reject"));
$("refreshState").addEventListener("click", refresh);
$("newChat").addEventListener("click", newThread);
$("openConfig").addEventListener("click", () => $("configDialog").showModal());
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
    ? "Developer mode forces OMNI → META → FORGE → SIGMA before execution approval."
    : "Nothing executes from this box until CAPT admits the governed path.";
});

refresh();
setInterval(refresh, 5000);

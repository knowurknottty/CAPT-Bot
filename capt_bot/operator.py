"""CAPT-Bot operator controller.

The controller shapes operator intent for CAPT RuntimeService. RuntimeService remains
authoritative for state, approval, execution, verification, and mission lifecycle.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class BotOperatorController:
    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self._start_lock = threading.Lock()

    def _query(self, op: str, **fields: Any) -> Dict[str, Any]:
        return self.runtime.query({"op": op, **fields})

    def _command(self, op: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.runtime.command(op, payload)

    def bots(self) -> Dict[str, Any]:
        return self._query("bots")

    def register_bot(
        self,
        *,
        bot_id: str,
        display_name: str,
        role: str,
        primary_model: Optional[str] = None,
        default_runtime: str = "either",
        cloud_allowed: bool = False,
    ) -> Dict[str, Any]:
        """Register identity only, through Core's authenticated BotManifest act.

        Bot R5 retains ownership of workflow and UI. CAPT RuntimeService
        remains sole writer and injects creator identity and timestamp.
        """
        import re
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", bot_id):
            raise ValueError("invalid bot id")
        if not 1 <= len(display_name.strip()) <= 256:
            raise ValueError("invalid bot display name")
        if not 1 <= len(role.strip()) <= 128:
            raise ValueError("invalid bot role")
        if default_runtime not in ("local", "cloud", "either"):
            raise ValueError("invalid bot default runtime")
        if primary_model is not None and len(primary_model) > 256:
            raise ValueError("primary model identifier too long")
        return self._command("register_bot", {"bot": {
            "schemaVersion": "1.0.0",
            "botId": bot_id,
            "displayName": display_name.strip(),
            "roleKind": "crew",
            "role": role.strip(),
            "missionId": None,
            "modelStrategy": {"primary": primary_model or None, "fallbacks": []},
            "cognitionPolicy": {"promotionMode": "governed"},
            "localityPolicy": {
                "defaultRuntime": default_runtime,
                "privateData": "cloud_allowed" if cloud_allowed else "local_only",
            },
            "collaboration": {"mayDelegate": False, "maxSpawnDepth": 0},
            "authorityTemplateRef": None,
        }})

    def control(self) -> Dict[str, Any]:
        return self._query("operator_control_snapshot")

    def ensure_chat(self) -> Dict[str, Any]:
        control = self.control()
        if control.get("activeSessionId"):
            return control
        receipt = self._command("operator_chat_new", {
            "expectedRevision": int(control["revision"]),
        })
        return dict(receipt["result"])

    def new_chat(self) -> Dict[str, Any]:
        control = self.control()
        receipt = self._command("operator_chat_new", {
            "expectedRevision": int(control["revision"]),
        })
        return dict(receipt["result"])

    def provider_catalog(self) -> Dict[str, Any]:
        from .provider_catalog import read_provider_catalog
        return read_provider_catalog()

    def configure(
        self,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        target_root: Optional[str] = None,
        prompt_intelligence: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Validate before ensure_chat (which can create a session).
        # An invalid dropdown pair must have zero RuntimeService write effects.
        existing = self.control()
        if provider is not None or model is not None:
            from .provider_catalog import validate_provider_model
            validate_provider_model(
                provider if provider is not None else str(existing.get("provider") or ""),
                model if model is not None else str(existing.get("model") or ""),
                self.provider_catalog(),
            )
        control = self.ensure_chat()
        payload: Dict[str, Any] = {"expectedRevision": int(control["revision"])}
        for key, value in (
            ("provider", provider),
            ("model", model),
            ("targetRoot", target_root),
            ("promptIntelligence", prompt_intelligence),
        ):
            if value is not None:
                payload[key] = value
        receipt = self._command("operator_execution_config_set", payload)
        return dict(receipt["result"])

    def clarify_prompt(
        self,
        proposal_id: str,
        answer: str,
        *,
        remote_compilation_authorized: bool = False,
    ) -> Dict[str, Any]:
        control = self.ensure_chat()
        projected = self._query("operator_proposal_get", proposalId=proposal_id)
        proposal = projected.get("proposal") or {}
        if proposal.get("compilationStatus") != "clarification_required":
            raise ValueError("proposal does not require clarification")
        clarification = answer.strip()
        if not clarification:
            raise ValueError("clarification text is required")
        receipt = self._command("operator_prompt_clarify", {
            "proposalId": proposal_id,
            "proposalRevision": int(proposal["revision"]),
            "clarificationText": clarification,
            "controlRevision": int(control["revision"]),
            "configurationDigest": str(control["configurationDigest"]),
            "remoteCompilationAuthorized": bool(remote_compilation_authorized),
        })
        return dict(receipt["result"])

    def submit_prompt(
        self,
        text: str,
        *,
        developer: bool = False,
        clarification_for: Optional[str] = None,
        requested_context_budget: int = 32000,
        requested_capabilities: Optional[list[str]] = None,
        remote_compilation_authorized: bool = False,
    ) -> Dict[str, Any]:
        control = self.ensure_chat()
        prompt = text.strip()
        if not prompt:
            raise ValueError("prompt text is required")
        if clarification_for:
            return self.clarify_prompt(
                clarification_for,
                prompt,
                remote_compilation_authorized=remote_compilation_authorized,
            )
        payload = {
            "text": prompt,
            "mode": "software-development" if developer else "normal",
            "controlRevision": int(control["revision"]),
            "configurationDigest": str(control["configurationDigest"]),
            "requestedContextBudget": int(requested_context_budget),
            "requestedCapabilities": list(requested_capabilities or []),
            "remoteCompilationAuthorized": bool(remote_compilation_authorized),
        }
        receipt = self._command("operator_prompt_submit", payload)
        return dict(receipt["result"])

    @staticmethod
    def _criterion_records(items: list[str]) -> list[Dict[str, Any]]:
        source = items or ["The selected objective is verified complete."]
        return [
            {
                "criterionId": "sc-%d" % (index + 1),
                "statement": str(statement),
                "requiresVerification": True,
            }
            for index, statement in enumerate(source[:32])
        ]

    def select_proposal(
        self,
        proposal_id: str,
        *,
        basis: str = "proposed",
        edited_prompt: str = "",
        as_mission: bool = False,
        existing_mission_id: Optional[str] = None,
        requested_execution_seconds: int = 1800,
    ) -> Dict[str, Any]:
        projected = self._query("operator_proposal_get", proposalId=proposal_id)
        proposal = projected.get("proposal") or {}
        control = projected.get("control") or self.control()
        if proposal.get("compilationStatus") == "clarification_required":
            raise ValueError("proposal still requires clarification")
        if proposal.get("state") != "active":
            raise ValueError("proposal is not active")

        mission_receipt = None
        mission_id = None
        task_id = None
        if existing_mission_id:
            if as_mission:
                raise ValueError("cannot create a new Mission while continuing an existing one")
            existing = self._query("get_state", streamId="mission-" + existing_mission_id)
            if existing.get("state") not in ("authorized", "executing"):
                raise ValueError("existing Mission is not authorized for a successor task")
            mission_id = existing_mission_id
        if as_mission:
            mission_id = "goal-" + uuid.uuid4().hex[:20]
            criteria = list(
                (proposal.get("verificationContract") or {}).get("acceptanceCriteria") or []
            )
            scope = {
                "kind": "filesystem",
                "rootPath": proposal["targetRoot"],
                "recursive": True,
            }
            mission_receipt = self._command("create_mission", {
                "schemaVersion": "1.0.0",
                "missionId": mission_id,
                "objective": proposal["proposedPrompt"],
                "rawRequest": proposal["originalPrompt"],
                "normalizedRequest": proposal["proposedPrompt"],
                "constraints": [],
                "successCriteria": self._criterion_records(criteria),
                "terminationCriteria": [{
                    "criterionId": "tc-1",
                    "statement": "Invariant violation, explicit operator stop, or unrecoverable blocker.",
                    "terminalState": "failed",
                }],

                "unresolvedAmbiguities": list(proposal.get("unresolvedQuestions") or []),
                "requiresApproval": False,
                "requestedCapability": "cap.fs.read",
                "operation": "ModelOperatorInspection",
                "scope": scope,
                "resource": proposal["targetRoot"],
                "riskClassification": "low",
                "policyReason": "Operator promoted a compiled CAPT-Bot prompt into a durable Mission/Goal.",
            })
            if mission_receipt.get("status") not in ("accepted", "idempotent"):
                # Surface only the structured refusal classification/code; never
                # copy arbitrary backend details or prompt payloads into the UI.
                classification = str(mission_receipt.get("classification") or "unknown")[:80]
                envelope = mission_receipt.get("error") or {}
                code = envelope.get("code") if isinstance(envelope, dict) else None
                raise RuntimeError(
                    "mission creation refused: status=" +
                    str(mission_receipt.get("status") or "unknown")[:50] +
                    "; classification=" + classification +
                    "; code=" + str(code or "unknown")[:100]
                )
            mission_id = mission_receipt["result"]["missionId"]
            task_id = mission_receipt["result"]["taskId"]

        select_payload: Dict[str, Any] = {
            "proposalId": proposal_id,
            "basis": basis,
            "editedPrompt": edited_prompt,
            "controlRevision": int(control["revision"]),
            "configurationDigest": str(control["configurationDigest"]),
            "requestedExecutionSeconds": int(requested_execution_seconds),
        }
        if mission_id:
            select_payload["missionId"] = mission_id
            if task_id:
                select_payload["taskId"] = task_id
        selected = self._command("operator_proposal_select", select_payload)
        if basis == "proposed":
            selected_objective = str(proposal["proposedPrompt"])
        elif basis == "original":
            selected_objective = str(proposal["originalPrompt"])
        else:
            selected_objective = edited_prompt
        return {
            "mission": mission_receipt,
            "selection": selected,
            "missionId": mission_id,
            "taskId": task_id,
            "selectedObjective": selected_objective,
        }

    def start_bound_task(self, request_id: str) -> Dict[str, Any]:
        # Serialize competing clicks in this Bot worker. RuntimeService's
        # atomic one-use authority remains the cross-process final gate.
        if not self._start_lock.acquire(blocking=False):
            raise ValueError("START_ALREADY_IN_PROGRESS_RECONCILE_FIRST")
        try:
            return self._start_bound_task_once(request_id)
        finally:
            self._start_lock.release()

    def _start_bound_task_once(self, request_id: str) -> Dict[str, Any]:
        """Human-clicked Start reconstructed only from authoritative streams.

        Never accept client-supplied approval bindings or auto-replay a run
        after a network timeout. RuntimeService remains the final authority.
        """
        control = self.control()
        if not request_id or control.get("approvalRequestId") != request_id:
            raise ValueError("BOUND_APPROVAL_SESSION_MISMATCH")
        execution = self._query("operator_execution_state")
        approval = execution.get("approvalRequestState") or {}
        if approval.get("requestId") != request_id or approval.get("state") != "approved":
            raise ValueError("HUMAN_APPROVAL_NOT_APPROVED")
        if (approval.get("consumedAt")
                or type(approval.get("remainingUses")) is not int
                or approval["remainingUses"] < 1):
            raise ValueError("APPROVAL_ALREADY_CONSUMED_OR_EXHAUSTED")
        try:
            expiration = datetime.fromisoformat(str(approval["expiresAt"]).replace("Z", "+00:00"))
            if expiration.tzinfo is None or expiration <= datetime.now(timezone.utc):
                raise ValueError("APPROVAL_EXPIRED_RESELECT_PROMPT")
        except (TypeError, KeyError) as exc:
            raise ValueError("APPROVAL_EXPIRY_UNVERIFIABLE") from exc
        binding = (approval.get("scope") or {}).get("approvalBinding") or {}
        for field in ("missionId", "taskId", "driverRunId"):
            if not control.get(field) or binding.get(field) != control[field]:
                raise ValueError("APPROVAL_RUN_BINDING_MISMATCH:" + field)
        if binding.get("targetRoot") != control.get("targetRoot"):
            raise ValueError("APPROVAL_TARGET_ROOT_CHANGED")
        if binding.get("provider") != control.get("provider") or binding.get("model") != control.get("model"):
            raise ValueError("APPROVAL_PROVIDER_MODEL_CHANGED")
        if binding.get("proposalId") != control.get("proposalId"):
            raise ValueError("APPROVAL_PROPOSAL_MISMATCH")
        if execution.get("driverRunState"):
            raise ValueError("DRIVER_RUN_ALREADY_PRESENT_RECONCILE_FIRST")
        if control.get("proposalSelection") not in ("original", "proposed"):
            raise ValueError("SELECTED_OBJECTIVE_CANNOT_BE_RECONSTRUCTED")
        if approval.get("operation") != "ModelOperatorInspection":
            raise ValueError("APPROVAL_OPERATION_NOT_RUNNABLE")
        # The runtime re-derives the same signed assembly and owns dispatch.
        return self.run_approved(
            {
                "requestId": request_id,
                "missionId": control["missionId"],
                "taskId": control["taskId"],
                "driverRunId": control["driverRunId"],
                "authorityProfile": binding.get("authorityProfile") or {},
            }, "",
            response_mode="SPOCK",
            requested_context_budget=int(binding.get("requestedContextBudget", 32_000)),
            human_verification_required=bool(binding.get("humanVerificationRequired", True)),
        )

    def run_approved(
        self,
        approval: Dict[str, Any],
        objective: str,
        *,
        response_mode: str = "SPOCK",
        requested_context_budget: int = 32000,
        human_verification_required: bool = True,
    ) -> Dict[str, Any]:
        required = ("requestId", "missionId", "taskId", "driverRunId")
        missing = [key for key in required if not approval.get(key)]
        if missing:
            raise ValueError("approval receipt missing: " + ", ".join(missing))
        control = self.control()
        resolved_objective = objective.strip()
        if not resolved_objective and control.get("proposalId"):
            projected = self._query(
                "operator_proposal_get", proposalId=str(control["proposalId"])
            )
            proposal = projected.get("proposal") or {}
            selection = str(control.get("proposalSelection") or "")
            if selection == "proposed":
                resolved_objective = str(proposal.get("proposedPrompt") or "")
            elif selection == "original":
                resolved_objective = str(proposal.get("originalPrompt") or "")
        if not resolved_objective:
            raise ValueError("selected approved objective is unavailable")
        authority = dict(approval.get("authorityProfile") or {})
        target_root = str(
            authority.get("filesystemRoot") or control.get("targetRoot") or ""
        )
        if not target_root:
            raise ValueError("approved target root is missing")
        receipt = self._command("run_approved_hermes_inspection", {
            "provider": str(control.get("provider") or ""),
            "model": str(control.get("model") or ""),
            "objective": resolved_objective,
            "targetRoot": target_root,
            "authorityProfile": authority,
            "promptEnhancement": "OFF",
            "responseMode": response_mode,
            "requestedContextBudget": int(requested_context_budget),
            "humanVerificationRequired": bool(human_verification_required),
            "approvalRequestId": approval["requestId"],
            "missionId": approval["missionId"],
            "taskId": approval["taskId"],
            "driverRunId": approval["driverRunId"],
        })
        result = receipt.get("result") if isinstance(receipt, dict) else None
        if isinstance(result, dict) and result.get("taskId"):
            try:
                task = self._query("get_state", streamId="task-" + str(result["taskId"]))
                result["taskState"] = task.get("state")
            except Exception:
                result["taskState"] = "indeterminate"
        return receipt

    def review_result(
        self, driver_run_id: str, disposition: str, note: str = ""
    ) -> Dict[str, Any]:
        if disposition not in ("accept", "reject"):
            raise ValueError("disposition must be accept or reject")
        return self._command("submit_provider_result_review", {
            "driverRunId": driver_run_id,
            "disposition": disposition,
            "note": note,
        })

    def decide_approval(
        self, request_id: str, decision: str, note: str = ""
    ) -> Dict[str, Any]:
        if decision not in ("approve", "deny"):
            raise ValueError("decision must be approve or deny")
        return self._command("submit_approval_decision", {
            "requestId": request_id,
            "decision": decision,
            "note": note,
        })

    def kanban(self) -> Dict[str, Any]:
        """Complete, read-only mission/task inventory for reviewed operator decisions."""
        missions = self._query("missions", limit=1000)
        tasks = self._query("tasks", limit=1000)
        inventory = self._query("list_aggregates")
        runs = [item for item in inventory
                if item.get("kind") == "driverrun"]
        if len(runs) > 5000:
            raise ValueError("DriverRun inventory exceeds reviewed UI boundary")
        active_runs = []
        unreconciled_runs = []
        for run in runs:
            current = self._query("get_state", streamId=run["streamId"])
            summary = {
                "driverRunId": current.get("driverRunId"),
                "missionId": current.get("missionId"),
                "state": current.get("state"),
                "reconciliationStatus": current.get("reconciliationStatus"),
            }
            if summary["state"] in ("created", "submitted", "running"):
                active_runs.append(summary)
            if summary["reconciliationStatus"] == "reconciliation_required":
                unreconciled_runs.append(summary)
        return {
            "driverRunCount": len(runs),
            "activeDriverRuns": active_runs,
            "unreconciledDriverRuns": unreconciled_runs,
            "missions": missions.get("missions", []),
            "tasks": tasks.get("tasks", []),
            "countsByMissionState": missions.get("countsByState", {}),
            "countsByTaskState": tasks.get("countsByState", {}),
            "missionCount": missions.get("count", 0),
            "taskCount": tasks.get("count", 0),
            "note": "Only RuntimeService state is authoritative. Cancellation never deletes events.",
        }

    def inspect_mission(self, mission_id: str) -> Dict[str, Any]:
        from .mission_recovery import inspect_mission
        return inspect_mission(self, mission_id)

    def preview_mission_disposition(self, mission_id: str, target: str) -> Dict[str, Any]:
        """Read-only mission review; the version/digest are minted by Core."""
        if not mission_id or target not in ("authorize", "cancel", "cancel_revoke", "complete", "reconcile_complete"):
            raise ValueError("mission disposition target invalid")
        return self._query("mission_disposition_preview", missionId=mission_id, target=target)

    def apply_mission_disposition(
        self, mission_id: str, target: str, expected_version: int,
        preview_digest: str, confirmed_mission_id: str, reason: str,
    ) -> Dict[str, Any]:
        """Only an authenticated RuntimeService operator may commit this action."""
        if confirmed_mission_id != mission_id:
            raise ValueError("typed mission confirmation does not match")
        if target not in ("authorize", "cancel", "cancel_revoke", "complete", "reconcile_complete"):
            raise ValueError("mission disposition target invalid")
        if not preview_digest.startswith("sha256:"):
            raise ValueError("review digest required")
        return self._command("mission_disposition", {
            "missionId": mission_id, "target": target,
            "expectedVersion": int(expected_version),
            "previewDigest": preview_digest,
            "confirmedMissionId": confirmed_mission_id,
            "reason": reason.strip() or "Explicit reviewed CAPT-Bot Kanban disposition",
        })

    def cancel_task(self, task_id: str, reason: str) -> Dict[str, Any]:
        """Cancel one named task via the existing governed RuntimeService command."""
        if not task_id:
            raise ValueError("taskId required")
        task = self._query("get_state", streamId="task-" + task_id)
        if task.get("taskId") != task_id:
            raise ValueError("task identity mismatch")
        if task.get("state") in ("succeeded", "failed", "cancelled"):
            raise ValueError("task already terminal")
        return self._command("cancel_task", {
            "taskId": task_id,
            "reason": reason.strip() or "Operator requested task cancellation in CAPT-Bot Kanban.",
        })

    def snapshot(self) -> Dict[str, Any]:
        control = self.control()
        result: Dict[str, Any] = {
            "control": control,
            "execution": self._query("operator_execution_state"),
        }
        if control.get("proposalId"):
            try:
                projected = self._query("operator_proposal_get",
                                        proposalId=control["proposalId"])
                proposal = projected.get("proposal")
                if isinstance(proposal, dict) and proposal.get("state") == "active":
                    result["pendingProposal"] = proposal
            except Exception:
                # A read failure is not evidence of an absent proposal.
                result["proposalRecoveryUnavailable"] = True
        # Only the current operator control and its authoritative approval
        # stream can produce an actionable button. The global approvals list
        # is an informational projection and cannot provide a DriverRun lease.
        execution = result["execution"]
        grant = execution.get("approvalRequestState") or {}
        binding = (grant.get("scope") or {}).get("approvalBinding") or {}
        fields = ("missionId", "taskId", "driverRunId")
        if (grant and control.get("approvalRequestId") == grant.get("requestId")
                and all(control.get(k) and control.get(k) == binding.get(k)
                        for k in fields)
                and all(grant.get(k) == control.get(k) for k in ("missionId", "taskId"))):
            result["boundApproval"] = {
                "requestId": grant["requestId"],
                "missionId": control["missionId"],
                "taskId": control["taskId"],
                "driverRunId": control["driverRunId"],
                "state": grant.get("state"),
                "remainingUses": grant.get("remainingUses"),
                "consumedAt": grant.get("consumedAt"),
                "expiresAt": grant.get("expiresAt"),
                "riskClassification": grant.get("riskClassification"),
                "operation": grant.get("operation"),
                "targetRoot": binding.get("targetRoot"),
                "provider": binding.get("provider"),
                "model": binding.get("model"),
            }
        for key, op in (("missions", "missions"), ("tasks", "tasks"), ("approvals", "approvals")):
            try:
                result[key] = self._query(op, limit=1000 if key != "approvals" else 100)
            except Exception as exc:
                result[key] = {"error": str(exc)}
        return result

"""CAPT-Bot operator controller.

The controller shapes operator intent for CAPT RuntimeService. RuntimeService remains
authoritative for state, approval, execution, verification, and mission lifecycle.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional


class BotOperatorController:
    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime

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

    def configure(
        self,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        target_root: Optional[str] = None,
        prompt_intelligence: Optional[str] = None,
    ) -> Dict[str, Any]:
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
                raise RuntimeError("mission creation refused")
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

    def snapshot(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "control": self.control(),
            "execution": self._query("operator_execution_state"),
        }
        for key, op in (("missions", "missions"), ("tasks", "tasks"), ("approvals", "approvals")):
            try:
                result[key] = self._query(op)
            except Exception as exc:
                result[key] = {"error": str(exc)}
        return result

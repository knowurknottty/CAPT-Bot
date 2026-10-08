from capt_bot.operator import BotOperatorController


class FakeRuntime:
    def __init__(self):
        self.calls = []
        self.control_state = {
            "revision": 2,
            "configurationDigest": "sha256:test",
            "activeSessionId": "opchat-test",
            "provider": "local",
            "model": "qwen",
            "targetRoot": "/tmp/project",
            "promptIntelligence": "OFF",
        }
        self.proposal = {
            "proposalId": "pp-1",
            "revision": 0,
            "state": "active",
            "compilationStatus": "clarification_required",
            "originalPrompt": "Build app",
            "proposedPrompt": "Build app",
            "targetRoot": "/tmp/project",
            "unresolvedQuestions": ["Which platform?"],
            "verificationContract": {"acceptanceCriteria": ["tests pass"]},
        }

    def query(self, request):
        op = request["op"]
        if op == "operator_control_snapshot":
            return dict(self.control_state)
        if op == "operator_proposal_get":
            return {"control": dict(self.control_state), "proposal": dict(self.proposal)}
        if op == "get_state":
            return {"state": "awaiting_verification"}
        if op == "bots":
            return {"bots": [{"botId": "issue-steward", "displayName": "Issue Steward", "roleKind": "crew"}]}
        if op in {"operator_execution_state", "missions", "tasks", "approvals"}:
            return []
        raise AssertionError("unexpected query " + op)

    def command(self, op, payload):
        self.calls.append((op, payload))
        if op == "register_bot":
            return {"status": "accepted", "result": {"botId": payload["bot"]["botId"], "identityOnly": True}}
        if op == "operator_prompt_submit":
            return {"result": {"proposal": {"mode": payload["mode"]}}}
        if op == "operator_prompt_clarify":
            return {"result": {"proposal": {"proposalId": payload["proposalId"], "revision": 1}}}
        if op == "create_mission":
            return {"status": "accepted", "result": {"missionId": payload["missionId"], "taskId": "t-1"}}
        if op == "operator_proposal_select":
            return {"status": "accepted", "result": {"approval": {
                "requestId": "a-1", "missionId": payload.get("missionId", "m-1"),
                "taskId": payload.get("taskId", "t-1"), "driverRunId": "dr-1",
                "authorityProfile": {"filesystemRoot": "/tmp/project"},
            }}}
        if op == "run_approved_hermes_inspection":
            return {"status": "accepted", "result": {
                "driverRunId": "dr-1", "missionId": "m-1", "taskId": "t-1",
                "observations": [{"summary": "done"}],
            }}
        if op == "submit_provider_result_review":
            return {"status": "accepted", "result": {
                "driverRunId": "dr-1", "taskState": "succeeded", "missionState": "completed",
            }}
        if op == "submit_approval_decision":
            return {"status": "accepted", "result": {"requestId": payload["requestId"]}}
        raise AssertionError("unexpected command " + op)

def test_developer_mode_forces_software_development_submission():
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    result = controller.submit_prompt("Build the app", developer=True)

    assert result["proposal"]["mode"] == "software-development"
    op, payload = runtime.calls[-1]
    assert op == "operator_prompt_submit"
    assert payload["mode"] == "software-development"


def test_clarification_continues_same_proposal():
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    controller.submit_prompt(
        "macOS desktop",
        developer=True,
        clarification_for="pp-1",
    )

    op, payload = runtime.calls[-1]
    assert op == "operator_prompt_clarify"
    assert payload["proposalId"] == "pp-1"
    assert payload["proposalRevision"] == 0
    assert payload["clarificationText"] == "macOS desktop"


def test_mission_selection_binds_created_mission_and_task():
    runtime = FakeRuntime()
    runtime.proposal["compilationStatus"] = "ready_for_approval"
    runtime.proposal["proposedPrompt"] = "Complete SDR"
    controller = BotOperatorController(runtime)
    result = controller.select_proposal("pp-1", as_mission=True)

    assert result["missionId"].startswith("goal-")
    assert result["taskId"] == "t-1"
    assert result["selectedObjective"] == "Complete SDR"
    select = [call for call in runtime.calls if call[0] == "operator_proposal_select"][-1][1]
    assert select["missionId"] == result["missionId"]
    assert select["taskId"] == "t-1"


def test_approved_run_uses_exact_bound_ids_and_surfaces_verification_state():
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    approval = {
        "requestId": "a-1",
        "missionId": "m-1",
        "taskId": "t-1",
        "driverRunId": "dr-1",
        "authorityProfile": {"filesystemRoot": "/tmp/project"},
    }
    receipt = controller.run_approved(approval, "Complete SDR", requested_context_budget=64000)

    op, payload = runtime.calls[-1]
    assert op == "run_approved_hermes_inspection"
    assert payload["approvalRequestId"] == "a-1"
    assert payload["missionId"] == "m-1"
    assert payload["taskId"] == "t-1"
    assert payload["driverRunId"] == "dr-1"
    assert payload["promptEnhancement"] == "OFF"
    assert receipt["result"]["taskState"] == "awaiting_verification"


def test_result_review_delegates_completion_to_runtime():
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    receipt = controller.review_result("dr-1", "accept", "tests pass")

    op, payload = runtime.calls[-1]
    assert op == "submit_provider_result_review"
    assert payload == {
        "driverRunId": "dr-1",
        "disposition": "accept",
        "note": "tests pass",
    }
    assert receipt["result"]["missionState"] == "completed"


def test_bot_registration_routes_to_core_not_local_state():
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    result = controller.register_bot(
        bot_id="issue-steward",
        display_name="Issue Steward",
        role="Repair GitHub issues sequentially",
        primary_model="deepseek/deepseek-v4.1-flash",
    )
    assert result["result"]["identityOnly"] is True
    op, payload = runtime.calls[-1]
    assert op == "register_bot"
    bot = payload["bot"]
    assert bot["botId"] == "issue-steward"
    assert bot["roleKind"] == "crew"
    assert bot["cognitionPolicy"] == {"promotionMode": "governed"}
    assert bot["collaboration"] == {"mayDelegate": False, "maxSpawnDepth": 0}
    assert bot["localityPolicy"]["privateData"] == "local_only"
    assert "createdBy" not in bot and "createdAt" not in bot and "credentials" not in bot
    assert controller.bots()["bots"][0]["botId"] == "issue-steward"


def test_bot_registration_rejects_invalid_and_unsafe_identity():
    import pytest
    runtime = FakeRuntime()
    controller = BotOperatorController(runtime)
    for bot_id in ["", "bot/../escape", "has spaces"]:
        with pytest.raises(ValueError):
            controller.register_bot(bot_id=bot_id, display_name="X", role="review")
    with pytest.raises(ValueError):
        controller.register_bot(bot_id="bot-a", display_name="X", role="review",
                                default_runtime="unrestricted")
    assert runtime.calls == []

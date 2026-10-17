"""Configured provider/model selection must never leak secrets or accept invented IDs."""
import json
from pathlib import Path

import pytest

from capt_bot.provider_catalog import read_provider_catalog, validate_provider_model


def test_configured_providers_filter_disabled_empty_and_secrets(tmp_path):
    path = tmp_path / "providers.json"
    path.write_text(json.dumps({"providers": [
        {"id": "openrouter", "name": "OpenRouter", "kind": "cloud", "enabled": True,
         "api_key": "PRIVATE_TEST_TOKEN", "base_url": "https://secret.example",
         "key_ref": "keychain://private",
         "models": ["x/model-1", "x/model-1", "x/model-2"]},
        {"id": "local", "name": "", "kind": "local", "models": ["local-model"]},
        {"id": "disabled", "name": "Disabled", "enabled": False,
         "models": ["dangerous-hidden-model"]},
        {"id": "empty", "name": "Empty", "models": []},
    ]}))
    catalog = read_provider_catalog(path)
    assert [p["id"] for p in catalog["providers"]] == ["openrouter", "local", "empty"]
    assert catalog["providers"][0]["models"] == ["x/model-1", "x/model-2"]
    assert catalog["providers"][1]["name"] == "local"
    assert not catalog["availabilityVerified"]
    assert "PRIVATE_TEST_TOKEN" not in json.dumps(catalog)
    assert "keychain://" not in json.dumps(catalog)
    assert "secret.example" not in json.dumps(catalog)
    validate_provider_model("openrouter", "x/model-1", catalog)
    for provider, model in [("disabled", "dangerous-hidden-model"),
                            ("openrouter", "local-model"),
                            ("empty", "anything"),
                            ("unknown", "x/model-1")]:
        with pytest.raises(ValueError):
            validate_provider_model(provider, model, catalog)


def test_bad_catalog_is_fail_closed(tmp_path):
    path = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="UNAVAILABLE"):
        read_provider_catalog(path)
    path.write_text('{"providers":{}}')
    with pytest.raises(ValueError, match="MALFORMED"):
        read_provider_catalog(path)
    path.write_text(json.dumps({"providers": [{"id":"duplicate"}, {"id":"duplicate"}]}))
    with pytest.raises(ValueError, match="DUPLICATE"):
        read_provider_catalog(path)


def test_selection_validated_before_runtime_mutation(monkeypatch):
    from capt_bot.operator import BotOperatorController
    class Runtime:
        def __init__(self):
            self.commands = []
        def query(self, request):
            assert request["op"] == "operator_control_snapshot"
            return {"revision": 1, "provider": "openrouter", "model": "x/model-1",
                        "activeSessionId": "chat-test"}
        def command(self, op, data):
            self.commands.append((op, data))
            return {"result": data, "status": "accepted"}
    runtime = Runtime()
    controller = BotOperatorController(runtime)
    catalog = {"providers": [{"id":"openrouter", "models":["x/model-1","x/model-2"]},
                             {"id":"local","models":["local-model"]}]}
    monkeypatch.setattr(controller, "provider_catalog", lambda: catalog)
    with pytest.raises(ValueError, match="MODEL_NOT_CONFIGURED"):
        controller.configure(provider="openrouter", model="local-model")
    with pytest.raises(ValueError, match="PROVIDER_NOT_CONFIGURED"):
        controller.configure(provider="disabled", model="anything")
    assert runtime.commands == []
    response = controller.configure(provider="local", model="local-model")
    assert runtime.commands[-1][0] == "operator_execution_config_set"
    assert response["provider"] == "local"
    assert response["model"] == "local-model"


def test_provider_catalog_get_endpoint_exposes_no_credentials(tmp_path):
    import threading
    from urllib.request import urlopen
    from capt_bot.ui_server import build_server

    p = tmp_path / "providers.json"
    p.write_text(json.dumps({"providers": [{
        "id": "test-provider", "name": "Visible name", "kind": "local",
        "models": ["model-x"], "key_ref": "secret-vault://example",
        "api_key": "DO_NOT_RETURN",
    }]}))

    class Controller:
        def provider_catalog(self):
            return read_provider_catalog(p)

    server = build_server(Controller(), port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen("http://127.0.0.1:%d/api/providers" % server.server_address[1],
                     timeout=4) as response:
            body = response.read().decode()
        assert json.loads(body)["providers"][0]["models"] == ["model-x"]
        assert "DO_NOT_RETURN" not in body
        assert "secret-vault:" not in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

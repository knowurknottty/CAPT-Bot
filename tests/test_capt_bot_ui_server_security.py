"""Guard loopback Bot cockpit against cross-origin and rebinding mutations."""
import http.client
import json
import threading
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from capt_bot.ui_server import build_server


class FakeController:
    def __init__(self):
        self.register_calls = []
    def register_bot(self, **kwargs):
        self.register_calls.append(kwargs)
        return {"status": "accepted", "result": {
            "botId": kwargs["bot_id"], "identityOnly": True,
        }}
    def bots(self):
        return {"bots": [{"botId": x["bot_id"], "displayName": x["display_name"]}
                         for x in self.register_calls]}


@contextmanager
def cockpit():
    controller = FakeController()
    server = build_server(controller, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield controller, f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def payload():
    return json.dumps({
        "botId": "test-bot", "displayName": "Test Bot",
        "role": "Review only", "defaultRuntime": "local"
    }).encode()


def test_registration_requires_json_and_rejects_cross_origin():
    with cockpit() as (controller, root):
        bad = Request(root + "/api/bots/register", method="POST", data=payload(),
                      headers={"Origin": "http://malicious.example",
                               "Content-Type": "application/json"})
        try:
            urlopen(bad, timeout=4)
            assert False, "hostile origin was accepted"
        except HTTPError as exc:
            assert exc.code == 403
        no_type = Request(root + "/api/bots/register", method="POST", data=payload(),
                          headers={"Content-Type": "text/plain"})
        try:
            urlopen(no_type, timeout=4)
            assert False, "unsafe content type accepted"
        except HTTPError as exc:
            assert exc.code == 400
        assert controller.register_calls == []

        good = Request(root + "/api/bots/register", method="POST", data=payload(),
                       headers={"Origin": root, "Content-Type": "application/json"})
        with urlopen(good, timeout=4) as result:
            body = json.load(result)
        assert body["result"]["identityOnly"] is True
        with urlopen(root + "/api/bots", timeout=4) as result:
            assert json.load(result)["bots"][0]["botId"] == "test-bot"
        assert len(controller.register_calls) == 1


def test_dns_rebinding_host_is_denied_before_runtime_operation():
    with cockpit() as (controller, root):
        port = int(root.rsplit(":", 1)[-1])
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=4)
        conn.putrequest("POST", "/api/bots/register", skip_host=True)
        conn.putheader("Host", "attacker.invalid")
        conn.putheader("Content-Type", "application/json")
        body = payload()
        conn.putheader("Content-Length", str(len(body)))
        conn.endheaders(body)
        response = conn.getresponse()
        assert response.status == 403
        response.read()
        conn.close()
        assert controller.register_calls == []

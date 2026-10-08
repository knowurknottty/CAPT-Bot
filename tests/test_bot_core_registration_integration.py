"""Gated cross-repository proof: HTTP -> Bot -> Core -> EventStore.

Run with CAPT Core importable, e.g. PYTHONPATH=/path/to/CAPT_core:$PWD.
No production RuntimeService or user ledger is touched.
"""
import json
import multiprocessing
import tempfile
import time
import threading
from pathlib import Path
from urllib.request import Request, urlopen

import pytest

from capt_bot.operator import BotOperatorController
from capt_bot.ui_server import CoreRuntimePort, build_server


def test_real_core_register_bot_through_cockpit():
    service = pytest.importorskip("desktop.capt_runtime_service")
    with tempfile.TemporaryDirectory(prefix="capt-bot-it-", dir="/tmp") as tmp:
        ledger = str(Path(tmp) / "runtime.db")
        sock = str(Path(tmp) / "runtime.sock")
        token = str(Path(tmp) / "runtime.token")
        runtime_process = multiprocessing.Process(
            target=service.serve, args=(ledger, sock, token, False), daemon=True
        )
        runtime_process.start()
        port = None
        server = None
        thread = None
        try:
            for _ in range(100):
                if Path(sock).exists() and Path(token).exists(): break
                if not runtime_process.is_alive():
                    pytest.fail("isolated test runtime exited before ready")
                time.sleep(0.05)
            else:
                pytest.fail("isolated test runtime did not become ready")
            port = CoreRuntimePort(str(Path(service.__file__).parents[1]), sock, token)
            server = build_server(BotOperatorController(port), port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            payload = {
                "botId": "r5-http-it-bot", "displayName": "R5 Integration Bot",
                "role": "Review one issue at a time", "primaryModel": None,
                "defaultRuntime": "local", "cloudAllowed": False,
            }
            request = Request(
                base + "/api/bots/register", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Origin": base},
                method="POST"
            )
            with urlopen(request, timeout=10) as response:
                receipt = json.load(response)
            assert receipt["status"] == "accepted", receipt
            assert receipt["result"]["identityOnly"] is True
            with urlopen(base + "/api/bots", timeout=10) as response:
                bots = json.load(response)["bots"]
            assert any(b["botId"] == payload["botId"] for b in bots)
            stored = port.client.get_state("bot-r5-http-it-bot")
            assert stored["createdBy"]["kind"] == "human"
            assert stored["cognitionPolicy"] == {"promotionMode": "governed"}
            assert stored["collaboration"] == {"mayDelegate": False, "maxSpawnDepth": 0}
            assert "credentials" not in stored
        finally:
            if server:
                server.shutdown()
                server.server_close()
            if thread: thread.join(timeout=3)
            if port: port.close()
            runtime_process.terminate()
            runtime_process.join(timeout=5)
            assert not runtime_process.is_alive(), "test runtime process leaked"

"""Local CAPT-Bot web UI bridge.

The browser never receives the CAPT session token. This process binds only to loopback,
authenticates to the RuntimeService Unix socket, and relays the narrow operator surface.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

from .operator import BotOperatorController


class CoreRuntimePort:
    def __init__(self, core_root: str, sock_path: str, token_file: str) -> None:
        root = str(Path(core_root).expanduser().resolve())
        if root not in sys.path:
            sys.path.insert(0, root)
        from desktop.desktop_runtime_client import RuntimeClient

        self._socket_lock = threading.RLock()
        self.client = RuntimeClient(sock_path, token_file, command_timeout=None)
        self.identity = self.client.connect()

    def query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        with self._socket_lock:
            return self.client._query(request)["result"]

    def command(self, op: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Keep Bot registration repeatable across HTTP timeouts without
        # accidentally claiming two differently scoped identities.
        if op == "register_bot" and isinstance(payload.get("bot"), dict):
            key = "captbot-register:" + str(payload["bot"].get("botId", ""))
        else:
            key = "captbot-" + uuid.uuid4().hex
        with self._socket_lock:
            return self.client.command(op, payload, idempotency_key=key)

    def close(self) -> None:
        with self._socket_lock:
            self.client.disconnect()


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class BotUiHandler(BaseHTTPRequestHandler):
    controller: BotOperatorController
    static_root: Path

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, value: Any) -> None:
        body = _json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _origin_allowed(self) -> bool:
        # Binding to loopback is not enough: reject DNS rebinding, hostile
        # Host headers, and browser-originated cross-site mutations.
        port = self.server.server_address[1]
        allowed = {f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"}
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0].lower() not in allowed:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin.lower() == "http://" + hosts[0].lower()

    def _read_json(self) -> Dict[str, Any]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > 1024 * 1024:
            raise ValueError("request body size invalid")
        raw = self.rfile.read(length)
        value = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(value, dict):
            raise ValueError("request body must be an object")
        return value

    def _send_static(self, name: str, content_type: str) -> None:
        path = self.static_root / name
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


    def do_GET(self) -> None:
        if not self._origin_allowed():
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden_origin_or_host"})
            return
        try:
            if self.path == "/":
                self._send_static("index.html", "text/html; charset=utf-8")
                return
            if self.path == "/app.js":
                self._send_static("app.js", "text/javascript; charset=utf-8")
                return
            if self.path == "/styles.css":
                self._send_static("styles.css", "text/css; charset=utf-8")
                return
            if self.path == "/api/health":
                self._send_json(HTTPStatus.OK, {"ok": True})
                return
            if self.path == "/api/snapshot":
                self._send_json(HTTPStatus.OK, self.controller.snapshot())
                return
            if self.path == "/api/bots":
                self._send_json(HTTPStatus.OK, self.controller.bots())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except Exception as exc:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def do_POST(self) -> None:
        if not self._origin_allowed():
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden_origin_or_host"})
            return
        try:
            body = self._read_json()
            if self.path == "/api/chat/new":
                result = self.controller.new_chat()
            elif self.path == "/api/config":
                result = self.controller.configure(
                    provider=body.get("provider"),
                    model=body.get("model"),
                    target_root=body.get("targetRoot"),
                    prompt_intelligence=body.get("promptIntelligence"),
                )
            elif self.path == "/api/prompt":
                result = self.controller.submit_prompt(
                    str(body.get("text") or ""),
                    developer=bool(body.get("developer", False)),
                    clarification_for=body.get("clarificationFor"),
                    requested_context_budget=int(body.get("requestedContextBudget", 32000)),
                    requested_capabilities=list(body.get("requestedCapabilities") or []),
                    remote_compilation_authorized=bool(body.get("remoteCompilationAuthorized", False)),
                )
            elif self.path == "/api/proposal/select":
                result = self.controller.select_proposal(
                    str(body.get("proposalId") or ""),
                    basis=str(body.get("basis") or "proposed"),
                    edited_prompt=str(body.get("editedPrompt") or ""),
                    as_mission=bool(body.get("asMission", False)),
                    requested_execution_seconds=int(body.get("requestedExecutionSeconds", 1800)),
                )

            elif self.path == "/api/bots/register":
                result = self.controller.register_bot(
                    bot_id=str(body.get("botId") or ""),
                    display_name=str(body.get("displayName") or ""),
                    role=str(body.get("role") or ""),
                    primary_model=str(body["primaryModel"]) if body.get("primaryModel") else None,
                    default_runtime=str(body.get("defaultRuntime") or "either"),
                    cloud_allowed=body.get("cloudAllowed") is True,
                )
            elif self.path == "/api/approval/decide":
                result = self.controller.decide_approval(
                    str(body.get("requestId") or ""),
                    str(body.get("decision") or ""),
                    str(body.get("note") or ""),
                )
            elif self.path == "/api/run":
                approval = body.get("approval")
                if not isinstance(approval, dict):
                    raise ValueError("approval receipt is required")
                result = self.controller.run_approved(
                    approval,
                    str(body.get("objective") or ""),
                    response_mode=str(body.get("responseMode") or "SPOCK"),
                    requested_context_budget=int(
                        body.get("requestedContextBudget", 32000)
                    ),
                    human_verification_required=bool(
                        body.get("humanVerificationRequired", True)
                    ),
                )
            elif self.path == "/api/result/review":
                result = self.controller.review_result(
                    str(body.get("driverRunId") or ""),
                    str(body.get("disposition") or ""),
                    str(body.get("note") or ""),
                )
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            self._send_json(HTTPStatus.OK, result)
        except (ValueError, KeyError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})


def build_server(
    controller: BotOperatorController, host: str = "127.0.0.1", port: int = 8765
) -> ThreadingHTTPServer:
    static_root = Path(__file__).with_name("ui")

    class BoundHandler(BotUiHandler):
        pass

    BoundHandler.controller = controller
    BoundHandler.static_root = static_root
    return ThreadingHTTPServer((host, port), BoundHandler)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-root", required=True)
    parser.add_argument("--sock", required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit("CAPT-Bot UI must bind to loopback")
    runtime = CoreRuntimePort(args.core_root, args.sock, args.token_file)
    server = build_server(BotOperatorController(runtime), args.host, args.port)
    try:
        print("CAPT_BOT_UI_READY http://%s:%d" % (args.host, args.port), flush=True)
        server.serve_forever()
    finally:
        runtime.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

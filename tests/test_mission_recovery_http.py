"""Read-only predecessor review is an inspect action, never a command."""
import json
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

from capt_bot.ui_server import build_server


def test_scoped_get_mission_recovery_not_a_write():
    class Controller:
        def __init__(self):
            self.calls = []
        def inspect_mission(self, mid):
            self.calls.append(mid)
            if mid == "invalid":
                raise ValueError("invalid mission ID")
            return {"missionId":mid, "state":"cancelled",
                    "continuableInPlace":False,
                    "sourceBoundary":"read-only", "tasks":[]}

    controller = Controller()
    server = build_server(controller, port=0)
    worker = threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    host=f"http://127.0.0.1:{server.server_address[1]}"
    try:
        url=host+"/api/mission/recovery?missionId=m-capt-issues-20260924-live"
        with urlopen(url,timeout=4) as r:
            body=json.load(r)
        assert body["state"]=="cancelled"
        assert body["continuableInPlace"] is False
        assert controller.calls==["m-capt-issues-20260924-live"]
        try:
            urlopen(host+"/api/mission/recovery?missionId=invalid",timeout=4)
            assert False, "invalid mission identity accepted"
        except HTTPError as exc:
            assert exc.code==400
        try:
            urlopen(host+"/api/mission/recovery",timeout=4)
            assert False, "absent mission ID accepted"
        except HTTPError as exc:
            assert exc.code==400
    finally:
        server.shutdown();server.server_close();worker.join(timeout=3)

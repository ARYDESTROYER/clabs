#!/usr/bin/env python3
# LAB F attacker server.
#
# - Serves the attacker web page (the dashboard the student opens at
#   http://localhost:30000) on 0.0.0.0:30000.
# - Hosts the in-process "victim bot" that emulates a victim browser.
# - Reads /home/labDirectory/dns_config.json + attack_plan.json each time the
#   bot runs, so students can edit those files in the LMS editor and re-run.
#
# Pedagogy: the bot enforces the Same-Origin Policy on follow-up fetches. The
# only way to make the bot reach the (loopback-only) admin server is to make
# attacker.lab resolve to the admin's address mid-session -- DNS rebinding.

import json
import os
import threading
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

# Compatibility shim: the IITB base image ships an older Flask against a newer
# Jinja2 where jinja2.escape / Markup were removed. Without this, Flask fails
# to import and the server never binds. Copied verbatim from LAB-G.
try:
    import jinja2
    import jinja2.ext as _j2ext
    from markupsafe import Markup as _ms_markup
    from markupsafe import escape as _ms_escape

    try:
        from jinja2.ext import Extension as _j2_extension_base
    except Exception:
        _j2_extension_base = object

    if not hasattr(jinja2, "escape"):
        jinja2.escape = _ms_escape
    if not hasattr(jinja2, "Markup"):
        jinja2.Markup = _ms_markup

    if not hasattr(_j2ext, "autoescape"):
        class _LabFAutoEscapeCompat(_j2_extension_base):
            pass
        _j2ext.autoescape = _LabFAutoEscapeCompat
    if not hasattr(_j2ext, "with_"):
        class _LabFWithCompat(_j2_extension_base):
            pass
        _j2ext.with_ = _LabFWithCompat
except Exception:
    pass

import requests
from flask import Flask, jsonify, request

LAB_DIR = "/home/labDirectory"
EVENTS_FILE = "/tmp/labf_events.json"
DNS_CONFIG_PATH = os.path.join(LAB_DIR, "dns_config.json")
ATTACK_PLAN_PATH = os.path.join(LAB_DIR, "attack_plan.json")
ACTIVITY_ID = os.environ.get("ACTIVITY_ID", "1").strip()

state_lock = threading.Lock()
app = Flask(__name__)

# Avoid legacy Jinja extension loading paths on the older Flask shipped with
# the base image.
try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass


# ---------------------------------------------------------------- events log
def append_event(kind: str, data: Any) -> None:
    with state_lock:
        events: List[Dict] = []
        if os.path.exists(EVENTS_FILE):
            try:
                events = json.load(open(EVENTS_FILE, "r", encoding="utf-8"))
            except Exception:
                events = []
        events.append({"time": time.strftime("%H:%M:%S"), "kind": kind, "data": data})
        events = events[-80:]
        with open(EVENTS_FILE, "w", encoding="utf-8") as fh:
            json.dump(events, fh, indent=2)


def read_events() -> List[Dict]:
    if not os.path.exists(EVENTS_FILE):
        return []
    try:
        return json.load(open(EVENTS_FILE, "r", encoding="utf-8"))
    except Exception:
        return []


def read_json_file(path: str) -> Any:
    if not os.path.exists(path):
        return {"_error": f"File not found: {os.path.basename(path)}"}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"_error": f"Invalid JSON in {os.path.basename(path)}: {exc}"}
    except Exception as exc:
        return {"_error": f"Could not read {os.path.basename(path)}: {exc}"}


# ---------------------------------------------------------- DNS rebind model
class FakeDNS:
    """Tiny stateful resolver. Each hostname holds a sequence of (ip, port)
    answers; resolve() returns them in order and sticks at the last one.

    A hostname entry like
        {"hostname": "attacker.lab",
         "initial_ip": "127.0.0.1", "initial_port": 30000,
         "rebind_ip":  "127.0.0.1", "rebind_port":  8080,
         "rebind_after_request": 1}
    will return (initial_ip, initial_port) for the first lookup and
    (rebind_ip, rebind_port) for every lookup after that.
    """

    def __init__(self, config: Dict) -> None:
        self.records: Dict[str, List[Tuple[str, int]]] = {}
        self.cursor: Dict[str, int] = {}
        for entry in (config.get("hostnames") or []):
            host = (entry.get("hostname") or "").strip().lower()
            if not host:
                continue
            seq: List[Tuple[str, int]] = []
            init_ip = entry.get("initial_ip")
            init_port = entry.get("initial_port")
            if init_ip and init_port is not None:
                seq.append((str(init_ip), int(init_port)))
            reb_ip = entry.get("rebind_ip")
            reb_port = entry.get("rebind_port")
            if reb_ip and reb_port is not None:
                pad = max(1, int(entry.get("rebind_after_request", 1)))
                while len(seq) < pad:
                    seq.append(seq[-1] if seq else (str(reb_ip), int(reb_port)))
                seq.append((str(reb_ip), int(reb_port)))
            if seq:
                self.records[host] = seq
                self.cursor[host] = 0

    def resolve(self, host: str) -> Optional[Tuple[str, int]]:
        host = host.strip().lower()
        if host not in self.records:
            return None
        seq = self.records[host]
        idx = min(self.cursor[host], len(seq) - 1)
        self.cursor[host] += 1
        return seq[idx]


# --------------------------------------------------------------------- bot
def fetch_via_resolver(url: str, dns: FakeDNS, extra_query: Optional[Dict] = None) -> Dict:
    parts = urllib.parse.urlparse(url)
    host = parts.hostname or ""
    record = dns.resolve(host)
    if record is None:
        return {"url": url, "error": f"DNS lookup failed for '{host}' (not in dns_config.json)"}
    target_ip, target_port = record

    query_pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    if extra_query:
        query_pairs.extend((str(k), str(v)) for k, v in extra_query.items())
    target_url = urllib.parse.urlunparse(
        parts._replace(
            netloc="{}:{}".format(target_ip, target_port),
            query=urllib.parse.urlencode(query_pairs),
        )
    )
    try:
        # Keep the original Host header -- this is exactly what a victim browser
        # would do after the rebind: same Host header, different IP.
        resp = requests.get(target_url, headers={"Host": host}, timeout=4)
        return {
            "url": url,
            "resolved_to": "{}:{}".format(target_ip, target_port),
            "status": resp.status_code,
            "body": resp.text[:1500],
        }
    except Exception as exc:
        return {
            "url": url,
            "resolved_to": "{}:{}".format(target_ip, target_port),
            "error": str(exc),
        }


def run_bot_once() -> Dict:
    dns_config = read_json_file(DNS_CONFIG_PATH)
    plan = read_json_file(ATTACK_PLAN_PATH)
    if isinstance(dns_config, dict) and "_error" in dns_config:
        append_event("bot_error", {"reason": dns_config["_error"]})
        return {"ok": False, "error": dns_config["_error"]}
    if isinstance(plan, dict) and "_error" in plan:
        append_event("bot_error", {"reason": plan["_error"]})
        return {"ok": False, "error": plan["_error"]}

    dns = FakeDNS(dns_config)
    page_url = plan.get("page_url")
    if not page_url:
        msg = "attack_plan.json is missing 'page_url'."
        append_event("bot_error", {"reason": msg})
        return {"ok": False, "error": msg}

    page_origin = (urllib.parse.urlparse(page_url).hostname or "").lower()
    page_response = fetch_via_resolver(page_url, dns)
    append_event("bot_load_page", {"page_url": page_url, **page_response})

    captured: List[Dict] = []
    last_body = ""
    for action in plan.get("victim_actions") or []:
        kind = (action.get("action") or "").lower()
        if kind == "fetch":
            url = action.get("url", "")
            host = (urllib.parse.urlparse(url).hostname or "").lower()
            if host != page_origin:
                msg = ("Same-Origin Policy block. Page origin is '{}' but the "
                       "action tried to fetch '{}'.").format(page_origin, host)
                append_event("bot_sop_block", {"reason": msg, "url": url})
                captured.append({"url": url, "blocked": True, "reason": msg})
                continue
            extra_q = action.get("query")
            result = fetch_via_resolver(url, dns, extra_query=extra_q if isinstance(extra_q, dict) else None)
            last_body = result.get("body", "")
            append_event("bot_fetch", result)
            captured.append(result)
        elif kind == "exfil":
            payload = action.get("data", "")
            if payload == "$last_response":
                payload = last_body
            append_event("bot_exfil", {"payload": payload[:1500]})
            captured.append({"exfil": True, "payload": payload[:1500]})
        else:
            append_event("bot_warn", {"reason": "Unknown action kind", "action": action})

    return {"ok": True, "page": page_response, "actions": captured}


# ---------------------------------------------------------------- routes
DASHBOARD_HTML = r"""<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LAB F &mdash; Activity __ACTIVITY__</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Arial, sans-serif; margin: 18px; background: #0f172a; color: #e2e8f0; line-height: 1.45; }
  h1 { color: #38bdf8; margin-top: 0; }
  h2 { color: #93c5fd; margin-top: 24px; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; margin: 12px 0; }
  .card.note { border-left: 4px solid #38bdf8; }
  .btn { background: #38bdf8; color: #0f172a; padding: 8px 16px; border: 0; border-radius: 6px; font-weight: 600; cursor: pointer; margin-right: 6px; }
  .btn:hover { background: #0ea5e9; }
  .btn.gray { background: #475569; color: #f1f5f9; }
  .btn.gray:hover { background: #64748b; }
  pre { background: #0b1120; padding: 10px; border-radius: 6px; overflow-x: auto; font-size: 13px; white-space: pre-wrap; word-break: break-word; }
  code { background: #0b1120; padding: 1px 5px; border-radius: 3px; }
  .ev { padding: 8px; border-bottom: 1px solid #334155; font-size: 13px; }
  .ev.bot_exfil { background: rgba(253, 224, 71, 0.08); }
  .ev.bot_sop_block, .ev.bot_error { background: rgba(252, 165, 165, 0.08); }
  .ev.bot_fetch { background: rgba(134, 239, 172, 0.06); }
  .ev .kind { font-weight: 600; }
  small { color: #94a3b8; }
</style></head><body>

<h1>LAB F &middot; Activity __ACTIVITY__</h1>
<div class="card note">__ACTIVITY_TITLE__</div>

<h2>System map</h2>
<div class="card">
  <ul>
    <li><strong>Attacker page</strong> (this dashboard): <code>http://localhost:30000</code> &mdash; reachable from your real browser.</li>
    <li><strong>Internal admin server</strong>: <code>http://127.0.0.1:8080</code> &mdash; only reachable from inside the container.</li>
    <li><strong>Victim bot</strong>: lives inside this server. Click <em>Run Bot</em> to make it visit the attacker page.</li>
  </ul>
  <p><small>The bot enforces Same-Origin Policy: it will only follow up with fetches whose hostname matches the page's hostname. That's the constraint DNS rebinding bypasses.</small></p>
</div>

<h2>Configs (edit in the LMS file editor under <code>/home/labDirectory/</code>)</h2>
<div class="card">
  <p><strong>dns_config.json</strong> &mdash; what the bot's resolver returns for each hostname:</p>
  <pre id="dns">loading...</pre>
  <p><strong>attack_plan.json</strong> &mdash; the page the bot loads and the follow-up actions it takes:</p>
  <pre id="plan">loading...</pre>
</div>

<h2>Actions</h2>
<div class="card">
  <button class="btn" onclick="runBot()">&#9654; Run Bot</button>
  <button class="btn gray" onclick="reloadConfigs()">&#8635; Reload configs</button>
  <button class="btn gray" onclick="clearEvents()">&#128465; Clear event log</button>
</div>

<h2>Bot event log</h2>
<div class="card"><div id="events">No events yet. Click "Run Bot" once your configs are saved.</div></div>

<script>
async function reloadConfigs() {
  const r = await (await fetch('/api/configs')).json();
  document.getElementById('dns').textContent  = JSON.stringify(r.dns,  null, 2);
  document.getElementById('plan').textContent = JSON.stringify(r.plan, null, 2);
}
async function refreshEvents() {
  const r = await (await fetch('/api/events')).json();
  const el = document.getElementById('events');
  if (!r.events.length) { el.textContent = 'No events yet. Click "Run Bot" once your configs are saved.'; return; }
  el.innerHTML = r.events.slice().reverse().map(e =>
    `<div class="ev ${e.kind}"><span class="kind">${e.kind}</span> <small>${e.time}</small><br><pre>${escapeHtml(JSON.stringify(e.data, null, 2))}</pre></div>`
  ).join('');
}
function escapeHtml(s) { return s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'})[c]); }
async function runBot()    { await fetch('/api/run-bot', {method:'POST'}); reloadConfigs(); refreshEvents(); }
async function clearEvents(){ await fetch('/api/events', {method:'DELETE'}); refreshEvents(); }
reloadConfigs(); refreshEvents();
setInterval(refreshEvents, 2500);
</script>
</body></html>
"""

ACTIVITY_TITLES = {
    "1": ("Activity 1: map the threat model. No bot needed -- just look around. "
          "Read this dashboard, then use the in-LMS terminal to confirm what is and isn't reachable."),
    "2": ("Activity 2: perform a DNS-rebinding attack. Edit dns_config.json and "
          "attack_plan.json so the bot ends up reading the internal admin's session token, "
          "then click Run Bot."),
    "3": ("Activity 3: same technique, new target. No walkthrough -- enumerate the new admin "
          "endpoints, build the rebind, exfiltrate the corporate secret."),
}


@app.route("/")
def index():
    title = ACTIVITY_TITLES.get(ACTIVITY_ID, ACTIVITY_TITLES["2"])
    return DASHBOARD_HTML.replace("__ACTIVITY__", ACTIVITY_ID).replace("__ACTIVITY_TITLE__", title)


@app.route("/payload")
def payload_page():
    return ("<html><body><h2>Attacker page (origin marker)</h2>"
            "<p>The victim bot 'loaded' this page. Any follow-up fetches the bot makes "
            "must use the same hostname as the URL of this page.</p></body></html>")


@app.route("/api/configs")
def configs():
    return jsonify({"dns": read_json_file(DNS_CONFIG_PATH), "plan": read_json_file(ATTACK_PLAN_PATH)})


@app.route("/api/events", methods=["GET", "DELETE"])
def events_route():
    if request.method == "DELETE":
        with state_lock:
            try:
                os.unlink(EVENTS_FILE)
            except FileNotFoundError:
                pass
        return jsonify({"ok": True})
    return jsonify({"events": read_events()})


@app.route("/api/run-bot", methods=["POST"])
def run_bot_route():
    return jsonify(run_bot_once())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000, debug=False, use_reloader=False)

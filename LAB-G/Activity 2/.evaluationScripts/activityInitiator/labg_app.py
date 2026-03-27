#!/usr/bin/env python3
import json
import os
import re
import threading
import time
from typing import Dict, List

# Compatibility shim: some base images ship older Flask with newer Jinja2
# where jinja2.escape/Markup symbols were removed.
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

    # Flask 1.x may reference legacy Jinja extension symbols removed in Jinja 3.
    if not hasattr(_j2ext, "autoescape"):
        class _LabgAutoEscapeCompat(_j2_extension_base):
            pass

        _j2ext.autoescape = _LabgAutoEscapeCompat
    if not hasattr(_j2ext, "with_"):
        class _LabgWithCompat(_j2_extension_base):
            pass

        _j2ext.with_ = _LabgWithCompat
except Exception:
    pass

from flask import Flask, jsonify, make_response, redirect, request

app = Flask(__name__)

# Avoid legacy extension loading paths on very old Flask + newer Jinja combos.
try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass

STATE_LOCK = threading.Lock()
STATE_FILE = "/tmp/labg_state.json"
ACTIVITY_ID = os.environ.get("ACTIVITY_ID", "1").strip()
VICTIM_KEY = os.environ.get("VICTIM_KEY", "labg-default-victim-key")

FLAGS = {
    "1": "IITB{labg_a1_scan_surface_mapped}",
    "2": "IITB{labg_a2_stored_xss_triggered}",
    "3": "IITB{labg_a3_victim_context_exfil}",
}

INDEX_HTML = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>TechStore Labs</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f5f7fb; color: #0f172a; }
    .card { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
    a { color: #0f62fe; text-decoration: none; }
    code { background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>TechStore Security Lab</h1>
  <div class=\"card\">
    <p>Activity: <strong>__ACTIVITY__</strong></p>
    <p>Try these pages:</p>
    <ul>
      <li><a href=\"/products\">/products</a></li>
      <li><a href=\"/reviews\">/reviews</a></li>
      <li><a href=\"/api/lab/state\">/api/lab/state</a></li>
    </ul>
  </div>
  <div class=\"card\">
    <p>ZAP UI: <code>http://localhost:30004/zap</code></p>
    <p>ZAP proxy: <code>http://localhost:8080</code></p>
  </div>
</body>
</html>"""

def build_reviews_html(reviews: List[Dict]) -> str:
        items = []
        for item in reviews:
                block = (
                        "<div class='card'>"
                        f"<div class='meta'>#{item.get('id')} by {item.get('author')} at {item.get('created')}</div>"
                        f"<div>{item.get('comment','')}</div>"
                        "</div>"
                )
                items.append(block)

        body = "\n".join(items) if items else "<div class='card'><div class='meta'>No reviews yet.</div></div>"
        return f"""<!doctype html>
<html>
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Product Reviews</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8fafc; }}
        .card {{ background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
        label {{ display:block; margin-top: 8px; }}
        input, textarea {{ width: 100%; margin-top: 4px; padding: 8px; border-radius: 6px; border: 1px solid #94a3b8; }}
        button {{ margin-top: 10px; padding: 8px 14px; border: 0; border-radius: 6px; background: #0f62fe; color: #fff; }}
        .meta {{ color: #475569; font-size: 12px; }}
        .hint {{ font-size: 13px; color: #334155; background: #e2e8f0; padding: 8px; border-radius: 6px; }}
    </style>
</head>
<body>
    <h1>Customer Reviews</h1>
    <p><a href=\"/\">Back to Home</a></p>
    <div class=\"hint\">Review text is sanitized before storage. Only obvious script tags are removed.</div>
    <form method=\"post\" action=\"/reviews\">
        <label>Author
            <input name=\"author\" required maxlength=\"40\">
        </label>
        <label>Comment
            <textarea name=\"comment\" required rows=\"4\"></textarea>
        </label>
        <button type=\"submit\">Post Review</button>
    </form>
    <h2>Recent Reviews</h2>
    {body}
</body>
</html>"""


# Weak sanitizer by design: strips <script> tags only.
def sanitize_comment(text: str) -> str:
    return re.sub(r"(?is)</?script[^>]*>", "", text)


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def initial_state() -> Dict:
    return {
        "activity": ACTIVITY_ID,
        "comments": [],
        "next_id": 1,
        "victim_processed_ids": [],
        "xss_triggered": False,
        "last_exfil": "",
        "exfil_events": [],
    }


def load_state() -> Dict:
    if not os.path.exists(STATE_FILE):
        data = initial_state()
        save_state(data)
        return data
    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(data: Dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def exfiltrate_value(data: Dict, value: str, source: str) -> None:
    value = value.strip()
    data["last_exfil"] = value
    data["exfil_events"].append({"time": now(), "source": source, "value": value})


def emulate_victim_for_comment(data: Dict, comment: Dict) -> None:
    text = comment.get("comment", "")
    cid = int(comment.get("id", 0))
    processed = set(data.get("victim_processed_ids", []))
    if cid in processed:
        return

    looks_like_xss = bool(re.search(r"(?i)onerror\s*=|onload\s*=|javascript:|<img|<svg", text))
    has_collect = "/collect" in text
    wants_profile = "/api/victim/profile" in text

    if looks_like_xss:
        data["xss_triggered"] = True

    if looks_like_xss and wants_profile and has_collect:
        exfiltrate_value(data, FLAGS["3"], "victim-bot")
    elif looks_like_xss and has_collect and ACTIVITY_ID in {"2", "3"}:
        # In Activity 2 this proves payload execution without requiring profile theft.
        exfiltrate_value(data, FLAGS["2"], "victim-bot")

    processed.add(cid)
    data["victim_processed_ids"] = sorted(processed)


@app.route("/", methods=["GET"])
def index() -> str:
    return INDEX_HTML.replace("__ACTIVITY__", ACTIVITY_ID)


@app.route("/products", methods=["GET"])
def products():
    return jsonify(
        {
            "products": [
                {"id": 101, "name": "Wireless Keyboard", "price": 2499},
                {"id": 102, "name": "Mechanical Mouse", "price": 3299},
                {"id": 103, "name": "USB Security Key", "price": 1999},
            ],
            "activity": ACTIVITY_ID,
        }
    )


@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    with STATE_LOCK:
        data = load_state()
        if request.method == "POST":
            author = request.form.get("author", "guest").strip()[:40] or "guest"
            comment = request.form.get("comment", "").strip()
            if comment:
                item = {
                    "id": data["next_id"],
                    "author": author,
                    "comment": sanitize_comment(comment),
                    "created": now(),
                }
                data["comments"].append(item)
                data["next_id"] += 1
                save_state(data)
            return redirect("/reviews")

        return build_reviews_html(data.get("comments", []))


@app.route("/robots.txt", methods=["GET"])
def robots():
    body = "User-agent: *\nDisallow:\n\n# lab hint\nAllow: /hidden/scan-checkpoint\n"
    response = make_response(body, 200)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@app.route("/hidden/scan-checkpoint", methods=["GET"])
def scan_checkpoint():
    response = make_response("Discovery checkpoint reached.\n", 200)
    response.headers["X-Lab-Flag1"] = FLAGS["1"]
    return response


@app.route("/api/victim/profile", methods=["GET"])
def victim_profile():
    header_key = request.headers.get("X-Lab-Victim-Key", "")
    if header_key != VICTIM_KEY:
        return jsonify({"error": "forbidden", "reason": "victim context required"}), 403
    return jsonify({"username": "admin-victim", "secretFlag": FLAGS["3"]})


@app.route("/collect", methods=["GET", "POST"])
def collect():
    value = ""
    source = request.values.get("source", "manual")
    value = request.values.get("d", "") or request.values.get("flag", "") or request.values.get("token", "")

    with STATE_LOCK:
        data = load_state()
        if value:
            exfiltrate_value(data, value, source)
            save_state(data)

    return jsonify({"status": "ok", "captured": bool(value)})


@app.route("/api/exfil/latest", methods=["GET"])
def latest_exfil():
    with STATE_LOCK:
        data = load_state()
        return jsonify({"latest": data.get("last_exfil", ""), "count": len(data.get("exfil_events", []))})


@app.route("/api/activity2/proof", methods=["GET"])
def activity2_proof():
    with STATE_LOCK:
        data = load_state()
        if data.get("xss_triggered"):
            return jsonify({"flag": FLAGS["2"]})
        return jsonify({"error": "xss not triggered yet"}), 403


@app.route("/api/victim/visit", methods=["POST"])
def victim_visit():
    header_key = request.headers.get("X-Lab-Victim-Key", "")
    if header_key != VICTIM_KEY:
        return jsonify({"error": "unauthorized"}), 403

    with STATE_LOCK:
        data = load_state()
        for item in data.get("comments", []):
            emulate_victim_for_comment(data, item)
        save_state(data)

    return jsonify({"status": "ok", "processed": len(data.get("victim_processed_ids", []))})


@app.route("/api/lab/state", methods=["GET"])
def lab_state():
    with STATE_LOCK:
        data = load_state()
        return jsonify(
            {
                "activity": data.get("activity"),
                "comments": len(data.get("comments", [])),
                "xss_triggered": data.get("xss_triggered", False),
                "exfil_events": len(data.get("exfil_events", [])),
            }
        )


if __name__ == "__main__":
    with STATE_LOCK:
        if not os.path.exists(STATE_FILE):
            save_state(initial_state())
    app.run(host="0.0.0.0", port=30000, debug=False)

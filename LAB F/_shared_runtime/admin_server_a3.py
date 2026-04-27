#!/usr/bin/env python3
# LAB F internal admin server (Activity 3).
#
# Variation from Activities 1/2:
#   * Endpoint moved from /admin/token to /api/v2/secret.
#   * The hostname students will rebind is corp.local (not attacker.lab).
#     (Hostname choice happens in dns_config.json, not here -- this server
#     only listens on 127.0.0.1:8080. The point is: the student has to
#     enumerate the new layout and adjust their attack plan.)
#   * /api/v2/secret now requires a ?token=<X-Internal-Token> query parameter.
#   * /api/v2/healthz leaks the X-Internal-Token via a debug response header
#     -- the student has to discover this and reuse it.

import os

# Flask/Jinja2 compatibility shim for the IITB base image.
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
        class _LabFAutoEscapeCompat(_j2_extension_base): pass
        _j2ext.autoescape = _LabFAutoEscapeCompat
    if not hasattr(_j2ext, "with_"):
        class _LabFWithCompat(_j2_extension_base): pass
        _j2ext.with_ = _LabFWithCompat
except Exception:
    pass

from flask import Flask, jsonify, make_response, request

ACTIVITY_ID = os.environ.get("ACTIVITY_ID", "3").strip()
FLAG3 = "IITB{labf_a3_independent_pwn_complete}"
INTERNAL_TOKEN = "ops-2026"

app = Flask(__name__)
try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass


@app.route("/api/v2/healthz")
def healthz():
    # Diagnostic endpoint left enabled by mistake. Leaks the internal token via
    # a debug response header -- realistic mistake, easy for tools to spot.
    resp = make_response(jsonify({"status": "ok", "service": "corp-admin-v2"}))
    resp.headers["X-Internal-Token-Debug"] = INTERNAL_TOKEN
    return resp


@app.route("/api/v2/secret")
def secret():
    if request.args.get("token") != INTERNAL_TOKEN:
        return jsonify({
            "error": "missing or wrong token",
            "hint": "this endpoint expects ?token=<X-Internal-Token>",
        }), 403
    return jsonify({"corporate_secret": FLAG3, "issued_to": "internal-staff"})


@app.route("/api/v2/whoami")
def whoami():
    return jsonify({"trust_level": "internal", "service": "corp-admin-v2"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)

#!/usr/bin/env python3
# LAB F Activity 1 internal admin server.
#
# Bound to 127.0.0.1:8080. NOT exposed to the LMS port mapping. The realistic
# vulnerability is that the admin trusts anything on its loopback interface --
# this is the trust assumption DNS rebinding subverts in Activity 2.
#
# Activity 1 only exposes a welcome banner + whoami. The token endpoint
# arrives in Activity 2.

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

from flask import Flask, jsonify

FLAG1 = "IITB{labf_a1_threat_model_mapped}"

app = Flask(__name__)
try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass


@app.route("/admin/welcome")
def welcome():
    return jsonify({
        "msg": "Hello internal staff. This is the corporate admin panel.",
        "activity1_flag": FLAG1,
        "note": "If you can read this, you are on the corporate loopback interface.",
    })


@app.route("/admin/whoami")
def whoami():
    return jsonify({"trust_level": "internal", "service": "corporate-admin"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)

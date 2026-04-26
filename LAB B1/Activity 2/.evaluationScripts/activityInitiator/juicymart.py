#!/usr/bin/env python3
"""
JuicyMart - vulnerable web application for LAB B1 (Activities 1 & 2).
Serves a real-feeling juice shop with a hidden recon endpoint and an admin
panel that is intentionally protected by a misconfigured WAF.
"""

import os
import re

# Compatibility shim: the BodhiLabs base image ships Flask 1.x with Jinja2 3.x,
# which removed the legacy `escape`/`Markup` symbols and the older extension
# classes. Re-export them so Flask 1.x can import. (Same shim LAB-G uses.)
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
        class _LabAutoEscapeCompat(_j2_extension_base):
            pass
        _j2ext.autoescape = _LabAutoEscapeCompat
    if not hasattr(_j2ext, "with_"):
        class _LabWithCompat(_j2_extension_base):
            pass
        _j2ext.with_ = _LabWithCompat
except Exception:
    pass

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Disable legacy Jinja extensions that don't exist in Jinja2 3.x.
try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass

FLAG_RECON = "flag=juicymart_recon_complete"
FLAG_ADMIN = "flag=admin_breached_via_url_rewrite"
WAF_LOG_PATH = "/tmp/modsec_audit.log"


@app.after_request
def fix_server_header(response):
    # Apache reverse-proxies us; Werkzeug's default Server header would leak
    # through. Replace it with what Apache itself would advertise so the
    # fingerprinting step of the lab teaches the right lesson.
    response.headers["Server"] = "Apache/2.4.66 (Debian)"
    return response

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #fdf6e3; color: #333; line-height: 1.6; }
header { background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 18px 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
header .brand { display: inline-block; font-size: 26px; font-weight: bold; }
header .brand::before { content: "\\1F34A  "; }
nav { float: right; margin-top: 6px; }
nav a { color: white; margin-left: 22px; text-decoration: none; font-weight: 500; }
nav a:hover { text-decoration: underline; }
.container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
.hero { background: white; padding: 50px; text-align: center; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; }
.hero h2 { font-size: 34px; color: #ff6b35; margin-bottom: 12px; }
.hero p { font-size: 18px; color: #666; }
.products { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card h3 { color: #ff6b35; margin-bottom: 8px; }
.card .price { font-size: 22px; color: #2a9d8f; font-weight: bold; margin-top: 12px; }
.card .icon { font-size: 48px; text-align: center; margin: 10px 0; }
footer { text-align: center; padding: 30px; color: #888; margin-top: 40px; }
form { display: flex; flex-direction: column; gap: 12px; max-width: 400px; }
input, textarea { padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-family: inherit; }
button { background: #ff6b35; color: white; border: 0; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; }
.admin-banner { background: #d9534f; color: white; padding: 18px; border-radius: 8px; margin-bottom: 20px; }
.admin-banner h3 { margin-bottom: 4px; }
.metric { display: inline-block; background: white; padding: 16px 24px; border-radius: 8px; margin: 8px 8px 8px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.05); min-width: 160px; }
.metric .label { color: #999; font-size: 13px; }
.metric .value { font-size: 26px; color: #2a9d8f; font-weight: bold; margin-top: 4px; }
table { width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-top: 12px; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; vertical-align: top; }
th { background: #f7931e; color: white; }
code { background: #2d3436; color: #ffeaa7; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 14px; }
.alert { background: #fff3cd; padding: 14px; border-left: 4px solid #ffc107; border-radius: 4px; margin: 16px 0; }
.flag-box { background: #2d3436; color: #55efc4; padding: 16px; border-radius: 6px; font-family: monospace; font-size: 16px; margin: 12px 0; word-break: break-all; }
"""

NAV_HTML = """
<header>
  <span class="brand">JuicyMart</span>
  <nav>
    <a href="/">Home</a>
    <a href="/products">Products</a>
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
  </nav>
</header>
"""

FOOTER_HTML = '<footer>&copy; 2024 JuicyMart &mdash; Fresh juices, daily delivered.</footer>'


def page(title, body):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} &mdash; JuicyMart</title>
  <style>{CSS}</style>
</head>
<body>
{NAV_HTML}
<div class="container">
{body}
</div>
{FOOTER_HTML}
</body>
</html>"""


@app.route("/")
def home():
    body = """
    <div class="hero">
      <h2>Fresh Juices, Daily Delivered</h2>
      <p>Cold-pressed, hand-bottled, straight to your door.</p>
    </div>
    <h3 style="margin-bottom:14px;">Featured this week</h3>
    <div class="products">
      <div class="card"><div class="icon">&#127818;</div><h3>Orange Sunrise</h3><p>Hand-pressed Florida oranges.</p><div class="price">$5.99</div></div>
      <div class="card"><div class="icon">&#127822;</div><h3>Apple Crisp</h3><p>Crisp Honeycrisp blend.</p><div class="price">$4.99</div></div>
      <div class="card"><div class="icon">&#127827;</div><h3>Berry Burst</h3><p>Strawberry, raspberry, blueberry.</p><div class="price">$6.49</div></div>
      <div class="card"><div class="icon">&#129365;</div><h3>Green Detox</h3><p>Kale, spinach, ginger, lemon.</p><div class="price">$7.99</div></div>
    </div>
    """
    return page("Home", body)


@app.route("/products")
def products():
    items = [
        ("&#127818;", "Orange Sunrise", 5.99, "Hand-pressed Florida oranges."),
        ("&#127822;", "Apple Crisp", 4.99, "Crisp Honeycrisp blend."),
        ("&#127827;", "Berry Burst", 6.49, "Strawberry, raspberry, blueberry."),
        ("&#129365;", "Green Detox", 7.99, "Kale, spinach, ginger, lemon."),
        ("&#127817;", "Mango Tango", 6.99, "Alphonso mango with a hint of lime."),
        ("&#127821;", "Pineapple Punch", 5.49, "Tropical pineapple with mint."),
        ("&#127815;", "Watermelon Cooler", 4.49, "Pure watermelon, lightly chilled."),
        ("&#127819;", "Tropical Twist", 7.49, "Pineapple, mango, passion fruit."),
    ]
    cards = ""
    for icon, name, price, desc in items:
        cards += (
            f'<div class="card"><div class="icon">{icon}</div>'
            f'<h3>{name}</h3><p>{desc}</p>'
            f'<div class="price">${price:.2f}</div></div>'
        )
    body = f'<h2 style="margin-bottom:18px;">Our Juices</h2><div class="products">{cards}</div>'
    return page("Products", body)


@app.route("/about")
def about():
    body = """
    <h2 style="margin-bottom:14px;">About JuicyMart</h2>
    <div class="card" style="padding: 28px;">
      <p>Founded in 2018, JuicyMart brings the freshest cold-pressed juices straight from local farms to your kitchen.</p>
      <p style="margin-top:12px;">We source from over 40 organic farms across the country and bottle within 6 hours of pressing &mdash; no preservatives, no shortcuts.</p>
      <p style="margin-top:12px;">Every bottle is recyclable and our cold chain is fully solar-powered.</p>
    </div>
    """
    return page("About", body)


@app.route("/contact")
def contact():
    body = """
    <h2 style="margin-bottom:14px;">Contact Us</h2>
    <div class="card" style="padding: 28px;">
      <form>
        <input type="text" placeholder="Your name">
        <input type="email" placeholder="Your email">
        <textarea rows="4" placeholder="Your message"></textarea>
        <button type="button">Send Message</button>
      </form>
    </div>
    """
    return page("Contact", body)


@app.route("/api/v1/info")
def api_info():
    return jsonify(
        {
            "app": "JuicyMart",
            "version": "1.4.2",
            "environment": "production",
            "recon_token": FLAG_RECON,
            "note": "Internal endpoint used by our service-discovery agent.",
        }
    )


@app.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "\n"
        "# internal: /api/v1/info\n"
    )
    response = make_response(body, 200)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@app.route("/admin/dashboard")
@app.route("/admin/")
@app.route("/admin")
def admin_dashboard():
    body = f"""
    <div class="admin-banner">
      <h3>Admin Dashboard</h3>
      <p>Welcome, Administrator. Internal access only.</p>
    </div>
    <div class="alert">
      <strong>Internal ops token:</strong>
      <div class="flag-box">{FLAG_ADMIN}</div>
    </div>
    <h2>Operations Overview</h2>
    <div>
      <div class="metric"><div class="label">Active orders</div><div class="value">142</div></div>
      <div class="metric"><div class="label">Today's revenue</div><div class="value">$3,847</div></div>
      <div class="metric"><div class="label">Customers</div><div class="value">8,291</div></div>
      <div class="metric"><div class="label">Open tickets</div><div class="value">7</div></div>
    </div>
    <h3 style="margin-top:30px;">Recent Orders</h3>
    <table>
      <tr><th>Order #</th><th>Customer</th><th>Total</th><th>Status</th></tr>
      <tr><td>#10147</td><td>Sarah Chen</td><td>$24.99</td><td>Shipped</td></tr>
      <tr><td>#10148</td><td>Marcus Lee</td><td>$18.50</td><td>Processing</td></tr>
      <tr><td>#10149</td><td>Priya Patel</td><td>$42.30</td><td>Delivered</td></tr>
      <tr><td>#10150</td><td>Diego Romero</td><td>$11.49</td><td>Pending</td></tr>
    </table>
    """
    return page("Admin Dashboard", body)


def parse_modsec_log(content):
    """Parse mod_security serial audit log into entries with timestamp, URI, rule, message."""
    entries = []
    chunks = re.split(r"(?=^--[a-f0-9]+-A--)", content, flags=re.MULTILINE)
    for chunk in chunks:
        if "-A--" not in chunk:
            continue
        time_match = re.search(r"\[(\d+/\w+/\d+:\d+:\d+:\d+)", chunk)
        uri_match = re.search(r"^(GET|POST|PUT|HEAD|DELETE|PATCH|OPTIONS) (\S+)", chunk, re.MULTILINE)
        rule_match = re.search(r'\[id "(\d+)"\][^\n]*?\[msg "([^"]+)"\]', chunk, re.DOTALL)
        if uri_match and rule_match:
            entries.append(
                {
                    "time": time_match.group(1) if time_match else "?",
                    "method": uri_match.group(1),
                    "uri": uri_match.group(2)[:80],
                    "rule_id": rule_match.group(1),
                    "message": rule_match.group(2),
                }
            )
    return entries


@app.route("/lab/waf-log")
def waf_log_view():
    entries = []
    if os.path.exists(WAF_LOG_PATH):
        try:
            with open(WAF_LOG_PATH, "r", errors="replace") as handle:
                content = handle.read()
            entries = parse_modsec_log(content)[-30:]
        except Exception as exc:
            entries = []
            err = str(exc)
        else:
            err = ""
    else:
        err = "Audit log file not found yet. Make a request that triggers the WAF first."

    rows = ""
    for entry in reversed(entries):
        rows += (
            f"<tr><td>{entry['time']}</td>"
            f"<td>{entry['method']}</td>"
            f"<td><code>{entry['uri']}</code></td>"
            f"<td>{entry['rule_id']}</td>"
            f"<td>{entry['message']}</td></tr>"
        )
    if not rows:
        msg = err or "No WAF blocks logged yet. Try a request that hits a rule."
        rows = f'<tr><td colspan="5" style="text-align:center;color:#999;">{msg}</td></tr>'

    body = f"""
    <h2 style="margin-bottom:14px;">WAF Audit Log</h2>
    <div class="alert">
      Live view of <code>{WAF_LOG_PATH}</code>. Most recent block at the top.
      You can also tail this file from the terminal with <code>tail -f {WAF_LOG_PATH}</code>.
    </div>
    <table>
      <tr><th>Time</th><th>Method</th><th>Blocked URI</th><th>Rule ID</th><th>Message</th></tr>
      {rows}
    </table>
    """
    return page("WAF Log", body)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

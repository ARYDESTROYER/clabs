#!/usr/bin/env python3
"""
BookHaven - Activity 3 target. Same architectural pattern as JuicyMart but
a different theme and a different admin path so the student has to apply
what they learned in Activities 1 & 2 without recognising the URLs.
"""

import os
import re

# Same Flask 1.x / Jinja2 3.x compat shim used by juicymart.py.
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

try:
    app.jinja_options = dict(app.jinja_options)
    app.jinja_options["extensions"] = []
except Exception:
    pass

FLAG_ORDERS = "flag=bookhaven_orders_url_encoded"
FLAG_CONSOLE = "flag=bookhaven_console_xou_bypass"
WAF_LOG_PATH = "/tmp/modsec_audit.log"


@app.after_request
def fix_server_header(response):
    response.headers["Server"] = "Apache/2.4.66 (Debian)"
    return response


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Georgia', serif; background: #f4ecd8; color: #3a2e22; line-height: 1.6; }
header { background: #5a3a22; color: #f4ecd8; padding: 18px 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); border-bottom: 4px solid #8b6f47; }
header .brand { display: inline-block; font-size: 28px; font-style: italic; }
header .brand::before { content: "\\1F4D6  "; }
nav { float: right; margin-top: 8px; }
nav a { color: #f4ecd8; margin-left: 22px; text-decoration: none; font-weight: 500; }
nav a:hover { color: #d4b88a; }
.container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
.hero { background: white; padding: 50px; text-align: center; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; border: 1px solid #d4b88a; }
.hero h2 { font-size: 34px; color: #5a3a22; margin-bottom: 12px; font-style: italic; }
.hero p { font-size: 18px; color: #6e5a40; }
.books { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.card { background: white; padding: 22px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e6d9b8; }
.card h3 { color: #5a3a22; margin-bottom: 4px; font-style: italic; }
.card .author { color: #8b6f47; font-size: 13px; margin-bottom: 10px; }
.card .price { font-size: 20px; color: #6b8e23; font-weight: bold; margin-top: 12px; }
.card .icon { font-size: 44px; text-align: center; margin: 6px 0 14px; }
footer { text-align: center; padding: 30px; color: #8b6f47; margin-top: 40px; font-style: italic; }
form { display: flex; flex-direction: column; gap: 12px; max-width: 400px; }
input, textarea { padding: 10px; border: 1px solid #d4b88a; border-radius: 4px; font-family: inherit; background: #fffcf5; }
button { background: #5a3a22; color: #f4ecd8; border: 0; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; font-family: inherit; }
.admin-banner { background: #6b3030; color: #f4ecd8; padding: 18px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #4a2020; }
.admin-banner h3 { margin-bottom: 4px; }
.metric { display: inline-block; background: white; padding: 16px 24px; border-radius: 4px; margin: 8px 8px 8px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.05); min-width: 160px; border: 1px solid #e6d9b8; }
.metric .label { color: #8b6f47; font-size: 13px; }
.metric .value { font-size: 26px; color: #5a3a22; font-weight: bold; margin-top: 4px; }
table { width: 100%; background: white; border-collapse: collapse; border-radius: 4px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-top: 12px; border: 1px solid #e6d9b8; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e6d9b8; vertical-align: top; }
th { background: #8b6f47; color: white; }
code { background: #2d3436; color: #ffeaa7; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 14px; }
.alert { background: #fdf3d4; padding: 14px; border-left: 4px solid #c9a234; border-radius: 4px; margin: 16px 0; }
.flag-box { background: #2d3436; color: #55efc4; padding: 16px; border-radius: 4px; font-family: monospace; font-size: 16px; margin: 12px 0; word-break: break-all; }
"""

NAV_HTML = """
<header>
  <span class="brand">BookHaven</span>
  <nav>
    <a href="/">Home</a>
    <a href="/catalog">Catalog</a>
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
  </nav>
</header>
"""

FOOTER_HTML = '<footer>&copy; 2024 BookHaven &mdash; Your cozy reading corner.</footer>'


def page(title, body):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} &mdash; BookHaven</title>
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
      <h2>Stories worth slowing down for</h2>
      <p>Hand-picked titles from independent publishers, delivered in recyclable wrap.</p>
    </div>
    <h3 style="margin-bottom:14px;">Picks of the season</h3>
    <div class="books">
      <div class="card"><div class="icon">&#128218;</div><h3>The Lantern Keeper</h3><div class="author">Ava Linwood</div><p>A quiet novel about light and memory.</p><div class="price">$14.50</div></div>
      <div class="card"><div class="icon">&#128218;</div><h3>Salt &amp; Sky</h3><div class="author">Tomas Reyes</div><p>Essays on the sea.</p><div class="price">$12.00</div></div>
      <div class="card"><div class="icon">&#128218;</div><h3>How to Mend Maps</h3><div class="author">Mira Devlin</div><p>Cartography meets memoir.</p><div class="price">$16.75</div></div>
      <div class="card"><div class="icon">&#128218;</div><h3>Field Notes on Wonder</h3><div class="author">Noor Al-Bakri</div><p>A pocket book of small joys.</p><div class="price">$10.25</div></div>
    </div>
    """
    return page("Home", body)


@app.route("/catalog")
def catalog():
    items = [
        ("The Lantern Keeper", "Ava Linwood", "Literary", 14.50),
        ("Salt &amp; Sky", "Tomas Reyes", "Essays", 12.00),
        ("How to Mend Maps", "Mira Devlin", "Memoir", 16.75),
        ("Field Notes on Wonder", "Noor Al-Bakri", "Poetry", 10.25),
        ("Quiet Engines", "Sam Kobayashi", "Sci-Fi", 13.99),
        ("The Last Cartographer", "Lior Halevy", "Adventure", 15.50),
        ("Recipes for Rain", "Estela Ruiz", "Cookbook", 18.00),
        ("Glasshouse Hours", "Ben Friedrich", "Mystery", 11.75),
    ]
    cards = ""
    for title, author, genre, price in items:
        cards += (
            f'<div class="card"><div class="icon">&#128218;</div>'
            f'<h3>{title}</h3><div class="author">{author} &middot; {genre}</div>'
            f'<div class="price">${price:.2f}</div></div>'
        )
    body = f'<h2 style="margin-bottom:18px;">Full catalog</h2><div class="books">{cards}</div>'
    return page("Catalog", body)


@app.route("/about")
def about():
    body = """
    <h2 style="margin-bottom:14px;">About BookHaven</h2>
    <div class="card" style="padding: 28px;">
      <p>BookHaven is a small online bookshop run out of a 1920s warehouse in Pune. We work directly with independent publishers and stock only what we have read and loved.</p>
      <p style="margin-top:12px;">Every order is wrapped in recycled craft paper and tied with cotton twine. Tea bag included with every parcel.</p>
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
        <textarea rows="4" placeholder="Tell us what you're reading"></textarea>
        <button type="button">Send Note</button>
      </form>
    </div>
    """
    return page("Contact", body)


@app.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Disallow: /manage/\n"
        "Disallow: /orders/\n"
    )
    response = make_response(body, 200)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@app.route("/orders/admin")
@app.route("/orders/")
@app.route("/orders")
def orders_admin():
    body = f"""
    <div class="admin-banner">
      <h3>Orders Admin</h3>
      <p>Internal fulfilment dashboard. Staff only.</p>
    </div>
    <div class="alert">
      <strong>Fulfilment access token:</strong>
      <div class="flag-box">{FLAG_ORDERS}</div>
    </div>
    <h2>Today's Pick &amp; Pack Queue</h2>
    <table>
      <tr><th>Order #</th><th>Customer</th><th>Title</th><th>Crate</th></tr>
      <tr><td>#2017</td><td>Lila Soren</td><td>Quiet Engines</td><td>A-3</td></tr>
      <tr><td>#2018</td><td>Anand Joshi</td><td>How to Mend Maps</td><td>A-7</td></tr>
      <tr><td>#2019</td><td>Mei Tanaka</td><td>The Last Cartographer</td><td>B-1</td></tr>
      <tr><td>#2020</td><td>Yusuf Al-Rashid</td><td>Recipes for Rain</td><td>B-4</td></tr>
    </table>
    <h3 style="margin-top:30px;">Couriers</h3>
    <div>
      <div class="metric"><div class="label">Pending pickup</div><div class="value">14</div></div>
      <div class="metric"><div class="label">In transit</div><div class="value">22</div></div>
      <div class="metric"><div class="label">Delivered today</div><div class="value">31</div></div>
    </div>
    """
    return page("Orders Admin", body)


@app.route("/manage/console")
@app.route("/manage/")
@app.route("/manage")
def manage_console():
    body = f"""
    <div class="admin-banner">
      <h3>Manager's Console</h3>
      <p>Restricted area. Internal staff only.</p>
    </div>
    <div class="alert">
      <strong>Internal access token:</strong>
      <div class="flag-box">{FLAG_CONSOLE}</div>
    </div>
    <h2>Storefront Overview</h2>
    <div>
      <div class="metric"><div class="label">Open orders</div><div class="value">38</div></div>
      <div class="metric"><div class="label">In-stock titles</div><div class="value">1,204</div></div>
      <div class="metric"><div class="label">Reserves</div><div class="value">12</div></div>
      <div class="metric"><div class="label">Reviews this month</div><div class="value">87</div></div>
    </div>
    <h3 style="margin-top:30px;">Recent Orders</h3>
    <table>
      <tr><th>Order #</th><th>Customer</th><th>Title</th><th>Status</th></tr>
      <tr><td>#2014</td><td>Hema Iyer</td><td>The Lantern Keeper</td><td>Packed</td></tr>
      <tr><td>#2015</td><td>Owen Mackay</td><td>Salt &amp; Sky</td><td>Shipped</td></tr>
      <tr><td>#2016</td><td>Ines Costa</td><td>Field Notes on Wonder</td><td>Delivered</td></tr>
    </table>
    """
    return page("Manager's Console", body)


def parse_modsec_log(content):
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
    err = ""
    if os.path.exists(WAF_LOG_PATH):
        try:
            with open(WAF_LOG_PATH, "r", errors="replace") as handle:
                content = handle.read()
            entries = parse_modsec_log(content)[-30:]
        except Exception as exc:
            err = str(exc)
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
        rows = f'<tr><td colspan="5" style="text-align:center;color:#8b6f47;">{msg}</td></tr>'

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

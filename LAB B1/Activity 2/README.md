# LAB B1 - Activity 2: WAF Bypass to Admin Panel

> **Audience:** instructor / teaching staff. This is a reference doc, not shown to students.

## Learning objective
The student already saw `/admin` blocked by mod_security in Activity 1. In Activity 2 they:
1. Confirm exactly which WAF rule is blocking them by reading the audit log.
2. Try the obvious bypass (URL encoding) and see it fail because the rule has `t:urlDecodeUni,t:lowercase`.
3. Discover the realistic bypass: a header-based path injection via `X-Original-URL`, drawn from the well-known WAF-bypass header cheat sheet.
4. Reach the admin dashboard and recover the flag.

## Target
- **Web app:** http://localhost:30000 (same JuicyMart Flask app as Activity 1)
- **Admin path to reach:** `/admin/dashboard`

## The vulnerability (instructor view)
The Apache vhost contains a deliberately misconfigured `mod_rewrite` rule that trusts the `X-Original-URL` request header for path routing:

```apache
RewriteCond %{HTTP:X-Original-URL} !^$
RewriteRule ^.*$ http://127.0.0.1:5000%{HTTP:X-Original-URL} [P,L]
```

mod_security inspects `REQUEST_URI` in phase 1 (before mod_rewrite runs), so a request whose URL is `/` but whose `X-Original-URL` header says `/admin/dashboard` sails past the WAF and is then routed to the admin endpoint internally. This is a real-world misconfig pattern (originated in IIS/ASP.NET stacks).

## Flag
- `flag=admin_breached_via_url_rewrite` - returned in the HTML body of `/admin/dashboard` once the bypass succeeds.

## Submission
Student writes the flag into `/home/labDirectory/flag.txt` (created at runtime by `initactivity.sh`) and clicks **Evaluate**. Autograder validates exact string match. 100/100 on success.

## Helper endpoints available to the student
- WAF audit log viewer (browser): http://localhost:30000/lab/waf-log
- WAF audit log file (terminal): `/tmp/modsec_audit.log`

See `WALKTHROUGH.md` for the full step-by-step solution path.

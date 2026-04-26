# LAB B1 - Activity 3: Independent Audit (BookHaven, Two Flags)

> **Audience:** instructor / teaching staff. This is a reference doc, not shown to students.

## Learning objective
The student is given a new web app (BookHaven) on the same Apache + mod_security stack and asked to apply Activity 1 + Activity 2 techniques without a step-by-step. Two restricted endpoints are protected by **two differently-tuned WAF rules**, requiring the student to use **two different bypass techniques** to capture both flags.

## Target
- **Web app:** http://localhost:30000 (BookHaven Flask app behind Apache + mod_security)

## The two protected endpoints (instructor view)

| Endpoint | mod_security rule | Bypass that works | Flag |
|---|---|---|---|
| `/orders/admin` | Rule 100001 - **naive** match on raw `REQUEST_URI` (no transformations) | URL encoding (e.g. `/o%72ders/admin`) | `flag=bookhaven_orders_url_encoded` |
| `/manage/console` | Rule 100002 - properly tuned with `t:urlDecodeUni,t:lowercase` | Header smuggling (`X-Original-URL: /manage/console`) | `flag=bookhaven_console_xou_bypass` |

The X-Original-URL bypass *also* works against rule 100001, but URL encoding is the cheaper attack and the one a pentester would try first.

## Tools available to the student
- `nmap`, `curl`, `nikto`, `gobuster`, `dirb`
- WAF audit log viewer (browser): http://localhost:30000/lab/waf-log
- WAF audit log file (terminal): `/tmp/modsec_audit.log`
- Wordlists: `/usr/share/dirb/wordlists/`

## Submission
Student writes:
- `flag=bookhaven_orders_url_encoded` into `/home/labDirectory/flag1.txt`
- `flag=bookhaven_console_xou_bypass` into `/home/labDirectory/flag2.txt`

(Both files are created at runtime by `initactivity.sh`.)

Autograder gives **50 points per flag** (100 max). Partial credit if only one flag is submitted correctly.

See `WALKTHROUGH.md` for the full step-by-step solution path.

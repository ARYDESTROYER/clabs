## Activity 3: Independent Audit — Two Bypasses, Two Flags

### Objective
- Apply the recon techniques from Activity 1 and the bypass techniques from Activity 2 to a **new** web app, without a step-by-step walkthrough.
- Recognise that not every WAF rule is tuned the same way: even within one site, sitting behind one WAF, two endpoints can have very different security postures.
- Practice the security professional's habit of trying the **cheap** bypass first before reaching for harder ones.
- Capture two flags from two differently-protected restricted endpoints.

### Background

A new web application — **BookHaven** — has been deployed to the same Apache + mod_security stack you saw in Activities 1 and 2. There are **two restricted endpoints**, each protected by a **different mod_security rule**. One rule is naive, the other is hardened. They require **two different bypass techniques** to get past.

This is what real engagements look like: one WAF in front of a site, but the rule for `/path-A` is well-written while the rule for `/path-B` is a quick hack that nobody tightened up. Probing each endpoint systematically is what turns "we have a WAF" into "we have a WAF and you cannot get past it."

This activity is **hint-style on purpose**. It points you at the right techniques and the right places to look, but does not hand you the exact commands or paths. Use what you learned in Activities 1 and 2.

### Environment

- **Target:** `http://localhost:30000`
- **Two flags total:** 50 points each, 100 maximum.
- **Submission files:** `flag1.txt` and `flag2.txt`, both inside `/home/labDirectory/`. Both files are pre-created for you.
- **Tools:** same as Activity 1 — `nmap`, `curl`, `nikto`, `gobuster` (v2), `dirb`. Wordlists at `/usr/share/dirb/wordlists/`.
- **WAF observability:** `/lab/waf-log` in the browser, or `tail /tmp/modsec_audit.log` in the terminal.

### Phase 1 — Recon

You know the drill from Activity 1. Quickly:

- Identify the server stack (`nmap -sV`).
- Read `/robots.txt`. **Pay attention to every `Disallow` line — each one points at a restricted area worth investigating.**
- Run `gobuster` against the standard wordlist:

```
gobuster -u http://localhost:30000 -w /usr/share/dirb/wordlists/common.txt -q
```

Note any `403 Forbidden` results — those are the WAF talking.

By the end of recon you should have identified **two restricted paths**, both returning 403 from mod_security. They are your two targets.

### Phase 2 — Confirm and Characterise the WAF Blocks

For each blocked path, do exactly what you did in Activity 2:

1. Hit the path with `curl -i` to confirm it is 403.
2. Check `http://localhost:30000/lab/waf-log` (or `tail /tmp/modsec_audit.log`) to see which rule fired and what message it logged.

You'll find that the two paths fire **two different rule IDs**. Note them down. You don't yet know which rule is naive and which is hardened — you'll discover that by attempting bypasses.

### Phase 3 — Try the Cheap Bypass First: URL Encoding

Activity 2 taught you that URL encoding usually fails against properly-tuned WAFs because the rule normalizes input before matching. **But not every WAF rule includes those transformations.** Some real-world rules are written as a quick fix and never tightened up. URL encoding is your first thing to try because it's cheap and sometimes still works.

For each blocked path, try a URL-encoded variant. The simplest swap: replace one letter of the path with its `%XX` hex equivalent. For example, the letter `a` is `%61`, `o` is `%6f`, `m` is `%6d`. (Run `man ascii` if you need a refresher.)

```
curl -i http://localhost:30000/<encoded-version-of-path>
```

What you should observe:
- **One** of the two paths gives you `200 OK` and renders an admin page. That page contains a flag — **this is one of your flags**. Save its value.
- **The other** path still returns `403 Forbidden`. Refresh `/lab/waf-log` and confirm the same rule fired again — this rule has transformations, so URL encoding is dead in the water against it.

This is the first half of the activity, and the lesson is concrete: **WAF tuning matters**. A naive rule and a tuned rule look identical in the audit log; only an attacker who tries cheap bypasses learns which is which.

### Phase 4 — For the Hardened Path: Header Smuggling

For the path that resisted URL encoding, you need the technique you learned in Activity 2: **header-based path injection**. Reach for the WAF-bypass header cheat sheet:

| Header | Effect when honored |
|---|---|
| `X-Original-URL` | Override the request path |
| `X-Rewrite-URL` | Override the request path (alt name) |

The Apache stack BookHaven sits on has the same misconfiguration class as the JuicyMart stack from Activity 2. Send the request to a benign path (like `/`) but smuggle the *real* target path in an `X-Original-URL` header:

```
curl -i -H "X-Original-URL: <the-blocked-path>" http://localhost:30000/
```

If it works, you'll get a `200 OK` with the admin page for that endpoint — and **a different flag in the page body**. **This is your second flag**. Save its value.

Refresh `/lab/waf-log` after this bypass: the WAF will not log a new entry, because mod_security never saw the protected path in `REQUEST_URI`. This is the same property you observed in Activity 2 — header smuggling leaves no trace in the WAF log.

### Hints (use only if stuck)

- Both restricted paths are listed in `/robots.txt`. Read it first — it's the cheapest way to discover them and it works exactly the same way it did in Activity 1.
- If URL encoding doesn't work on a path, **don't keep trying variants**. The rule has transformations — every encoding trick will fail. Move to header smuggling for that path.
- The `X-Original-URL` bypass *also* works against the naive rule, but URL encoding is faster to try and catches the rule before you spend effort on header crafting. That's the point of this activity: the cheap attack first.
- Each admin page renders its flag inside a black `<div class="flag-box">` near the top. Easy to spot in the browser; easy to extract with `grep -oE "flag=[a-z_]+"` from `curl`.
- Make sure you put the right flag in the right file. The autograder validates them independently.

### Submission

You should now have two flags. Each goes in its own file:

```
echo "<flag from URL encoding bypass>" > /home/labDirectory/flag1.txt
echo "<flag from X-Original-URL bypass>" > /home/labDirectory/flag2.txt
bash /home/.evaluationScripts/evaluate.sh
```

Each correct flag is worth **50 points** (100 total). Partial credit applies — submit what you have, even if you've only solved one half.

### What you practiced

| Phase | Skill |
|---|---|
| 1 | End-to-end recon on an unknown app (Activity 1 transfer) |
| 2 | Audit-log triage to identify WAF rule IDs |
| 3 | Trying the **cheap** bypass first (URL encoding) and recognising when a rule is naive vs hardened |
| 4 | Falling back to **header smuggling** when normalization defeats your simple attack |
| 5 | Working with multi-flag submissions and partial credit |

The real lesson: **defenses are not uniform**. Even within one site, sitting behind one WAF, two endpoints can have very different security postures. Probing each one with the same systematic toolkit is what turns "we have a WAF" into "we have a WAF and you cannot get past it."

### Further reading

- [HackTricks — 403 & 401 Bypasses](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/403-and-401-bypasses) (encyclopedic list of the bypass techniques used in this lab)
- [PortSwigger Web Security Academy — Access control vulnerabilities](https://portswigger.net/web-security/access-control)
- [mod_security Reference Manual — Transformation functions](https://github.com/SpiderLabs/ModSecurity/wiki/Reference-Manual-(v2.x)#transformation-functions) (the `t:urlDecodeUni`, `t:lowercase`, etc. that determine whether a rule is naive or hardened)
- [SANS Whitepaper — WAF bypass techniques](https://www.sans.org/white-papers/) (search for "WAF bypass" for community write-ups of real bypasses in production environments)

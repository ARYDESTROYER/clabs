# Activity 3 Walkthrough - BookHaven Independent Audit (2 flags)

> **Note for the student:** Activity 3 is a test of skill. This walkthrough is hint-style on purpose - it points you at the right techniques and the right places to look, but does not hand you the exact commands or paths the way Activities 1 and 2 did. Use what you learned.

The single most important lesson coming into this activity:

> **Not every WAF rule is tuned the same way. Try the cheap bypass first; reach for the harder one only when the cheap one fails.**

There are **two flags** in this activity. They live behind **two different restricted endpoints**, each protected by a **different mod_security rule**. One rule is naive, the other is hardened. You'll need a different bypass technique for each.

---

## Phase 1 - Recon (apply Activity 1)

You know the drill from Activity 1. Quickly:

- Identify the server stack (`nmap -sV`).
- Read `/robots.txt`. **Pay attention to every `Disallow` line - each one points at a restricted area worth investigating.**
- Run `gobuster` against the standard wordlist at `/usr/share/dirb/wordlists/common.txt`. Note any `403 Forbidden` results - those are the WAF talking.

By the end of recon you should have identified **two restricted paths**, both returning 403 from mod_security. They're your two targets.

---

## Phase 2 - Confirm and characterise the WAF blocks

For each blocked path, do exactly what you did in Activity 2:

1. Hit the path with `curl -i` to confirm 403.
2. Check `http://localhost:30000/lab/waf-log` (or `tail /tmp/modsec_audit.log`) to see which rule fired and what message it logged.

You'll find that the two paths fire **two different rule IDs**. Note them down. You don't yet know which rule is naive and which is hardened - you'll discover that by attempting bypasses.

---

## Phase 3 - Try the cheap bypass first: URL encoding

Activity 2 taught you that URL encoding usually fails against properly-tuned WAFs because the rule normalizes input before matching. **But not every WAF rule includes those transformations.** Some real-world rules are written as a quick fix and never tightened up. URL encoding is your first thing to try because it's cheap and sometimes still works.

For each blocked path, try a URL-encoded variant. The simplest swap: replace one letter of the path with its `%XX` hex equivalent. For example, the letter `a` is `%61`, `o` is `%6f`, `m` is `%6d`. (See `man ascii` if you need a refresher.)

```bash
# General shape - swap one letter per attempt
curl -i http://localhost:30000/<encoded-version-of-path>
```

What you should observe:
- **One** of the two paths gives you `200 OK` and renders an admin page. That page contains a flag - **this is FLAG 1**. Save it (you'll write it into `flag1.txt`).
- **The other** path still returns `403 Forbidden`. Refresh `/lab/waf-log` and confirm the same rule fired again - this rule has transformations, so URL encoding is dead in the water against it.

This is the first half of the activity, and the lesson is concrete: WAF tuning matters. A naive rule and a tuned rule look identical in the audit log; only an attacker who tries cheap bypasses learns which is which.

---

## Phase 4 - For the hardened path: header smuggling (apply Activity 2)

For the path that resisted URL encoding, you need the technique you learned in Activity 2: header-based path injection. Reach for the WAF-bypass header cheat sheet:

| Header | Effect when honored |
|---|---|
| `X-Original-URL` | Override the request path |
| `X-Rewrite-URL` | Override the request path (alt name) |

The Apache stack BookHaven sits on has the same misconfiguration class as the JuicyMart stack from Activity 2. Send the request to a benign path (like `/`) but smuggle the *real* target path in an `X-Original-URL` header:

```bash
curl -i -H "X-Original-URL: <the-blocked-path>" http://localhost:30000/
```

If it works, you'll get a `200 OK` with the admin page for that endpoint - and **a different flag in the page body**. **This is FLAG 2.** Save it to `flag2.txt`.

Refresh `/lab/waf-log` after this bypass: the WAF will not log a new entry, because mod_security never saw the protected path in `REQUEST_URI`. This is the same property you observed in Activity 2: header smuggling leaves no trace in the WAF log.

---

## Phase 5 - Submission

You should now have two flags. Each goes in its own file:

```bash
echo "<flag from /orders/admin via URL encoding>" > /home/labDirectory/flag1.txt
echo "<flag from /manage/console via X-Original-URL>" > /home/labDirectory/flag2.txt
bash /home/.evaluationScripts/evaluate.sh
```

Each correct flag is worth **50 points** (100 total). Partial credit applies - submit what you have.

---

## What you practiced

| Phase | Skill |
|---|---|
| 1 | End-to-end recon on an unknown app (Activity 1 transfer) |
| 2 | Audit-log triage to identify WAF rule IDs |
| 3 | Trying the **cheap** bypass first (URL encoding) and recognising when a rule is naive vs hardened |
| 4 | Falling back to **header smuggling** when normalization defeats your simple attack |
| 5 | Working with multi-flag submissions |

The real lesson: **defenses are not uniform**. Even within one site, sitting behind one WAF, two endpoints can have very different security postures. Probing each one with the same systematic toolkit is what turns "we have a WAF" into "we have a WAF and you cannot get past it."

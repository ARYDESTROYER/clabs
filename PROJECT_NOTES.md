# BodhiLabs Project Notes

**Last Updated:** February 26, 2026 - 2:00 AM

---

## Activity Log

### February 25–26, 2026
- **Lab C: DNS Zone Attack & DNS Tunneling Detection — DEPLOYED**
  - 3 activities: Guided AXFR tutorial, Intermediate AXFR challenge, Advanced DNS tunneling detection
  - Single Dockerfile shared across all activities (BIND9 + tshark + tcpdump)
  - Pre-baked pcap files (Activity 1: 8 packets, Activity 3: 67 packets)
  
  **🚨 CRITICAL BUG FOUND & FIXED: evaluate.json PermissionError**
  
  Spent multiple iterations debugging `PermissionError: [Errno 13] Permission denied: '/home/.evaluationScripts/evaluate.json'` on Activities 2 and 3 (Activity 1 worked inconsistently).
  
  **Root Cause**: The `.evaluationScripts` directory is a tarball-mounted volume. The BodhiLabs LMS metadata layer enforces read-only on files inside this mount, **regardless of Linux file permissions**. This means:
  - `sudo touch evaluate.json` → fails (can't create files in read-only mount)
  - `chmod 666 evaluate.json` → fails (LMS overrides Linux permissions)
  - Pre-baking evaluate.json in tarball → LMS marks it read-only
  - `chmod -R 755 .evaluationScripts` in evaluate.sh → additionally clobbers any 666 perms back to 755
  
  **What Made Debugging Hard**:
  - Activity 1 worked fine while Activities 2 and 3 failed with identical code — the LMS read-only enforcement is **inconsistent across activities**
  - Local Docker testing ALWAYS works because there's no LMS metadata layer — every approach passed locally
  - `sudo` availability during init is unreliable on the platform
  
  **Approaches Tried (in order, all failed for Act 2 & 3)**:
  1. `sudo touch` + `chmod 666` in initactivity.sh → sudo silently fails
  2. Reordering: `chmod -R 755` first, then `chmod 666` evaluate.json → LMS overrides
  3. Pre-baking evaluate.json (666 perms) in tarball → LMS marks read-only
  4. Removing `chmod -R 755` from evaluate.sh → still read-only from mount
  
  **✅ Solution That Worked: The /tmp Write Pattern**:
  ```
  autograder.py → writes to /tmp/evaluate.json  (always writable)
  evaluate.sh  → cp /tmp/evaluate.json /home/.evaluationScripts/evaluate.json
  ```
  `/tmp` is a standard Linux tmpfs — world-writable, no LMS metadata, no mount restrictions. The autograder never crashes because it writes to a guaranteed-writable location.
  
  **Files Modified**:
  - `Activity {1,2,3}/.evaluationScripts/autograder.py` — `OUTPUT_JSON = "/tmp/evaluate.json"`
  - `Activity {1,2,3}/.evaluationScripts/evaluate.sh` — added `cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json"` after autograder call
  - `Activity {1,2,3}/.evaluationScripts/evaluate.json` — pre-baked with `{"data":[]}`
  - `Activity {1,2,3}/.evaluationScripts/activityInitiator/initactivity.sh` — removed `sudo` touch/chown/chmod for evaluate.json
  - `BODHILABS_COMPLETE_GUIDE.md` — added Section 7.7 and updated templates
  
  **Other Issues Fixed During Lab C Development**:
  - UTF-8 BOM in .sh files → stripped with `[System.IO.File]::ReadAllBytes()` approach
  - CRLF line endings → converted all scripts to LF before packaging
  - `chmod -R 755` bug in evaluate.sh → was resetting evaluate.json perms every evaluation run
  
  **Deployment Status**: ✅ All 3 activities working on BodhiLabs
  
  **Key Takeaway**: **ALWAYS use the /tmp write pattern for evaluate.json in ALL future labs.** Never write directly to `/home/.evaluationScripts/evaluate.json` from autograder.py. Updated BODHILABS_COMPLETE_GUIDE.md accordingly.

### February 5, 2026
- **Lab B Full Health Check & Analysis:**
  - Container running successfully: `clab_act_8958_148` (pulled new image with X11 fix)
  - All 3 services confirmed working:
    - ✅ Apache/ModSecurity on port 30000 (actively blocking/logging)
    - ✅ Juice Shop on internal port 3000 (serving correctly)
    - ✅ ZAP WebSwing on port 30004 (no crashes in logs!)
  
  **File Permission Analysis:**
  - Submission files have `-rw-rw-rw-` (666) permissions inside container
  - Write test PASSED: files ARE writable via terminal
  - **NOTE:** If files appear read-only in BodhiLabs UI, it's a platform UI issue, not file permissions
  
  **🚨 CRITICAL ISSUE FOUND: Missing Master Flags!**
  - The autograder expects flag files: `/opt/masterflag1.txt`, `/opt/masterflag2.txt`, etc.
  - These files are NEVER CREATED by `initactivity.sh`!
  - The WALKTHROUGH.md describes flags from HTTP headers/responses, but:
    - Those endpoints need to be implemented (they're not in Juice Shop by default)
    - OR the initactivity.sh needs to generate static flag files
  
  **Lab Challenge Design Analysis:**
  - Custom ModSecurity rules ARE configured for training:
    - `100000`: Logs X-Original-URL header presence
    - `100010`: Blocks `/admin*` paths directly
    - `100020/21`: Blocks `/internal/*` unless X-Forwarded-For starts with `10.`
    - `100025`: Disables CRS SQLi for `/rest/products/search`
    - `100030`: Naive SQLi block for `union+select` (bypassable with `%20`)
  
  **What's Missing to Make Lab Work:**
  1. Master flag files not generated
  2. Custom endpoints not implemented:
     - `/internal/device-status` (should return FLAG2 JSON)
     - `/admin-console` (should return HTML with FLAG3)
     - `/rest/admin/application-version` (should return FLAG4 JSON)
     - Search endpoint should return FLAG1 in `X-Lab-Flag1` header

### February 4, 2026
- **Lab B:** 🎉 SUCCESSFULLY DEPLOYED on BodhiLabs!
  - Root cause of ZAP crash-loop: HTTPS enabled on port 8443 causing bind conflicts
  - Fixed by adding `sed` command to disable HTTPS in jetty.properties
  - Recreated `client_evaluation.tgz` with chmod +x (97.6 MB)
  - Pushed image to `lab_b_test2` tag
  - Container now running! Services status verified:
  
  **Full Health Check Results:**
  | Component | Port | Status | Notes |
  |-----------|------|--------|-------|
  | Apache/ModSecurity | 30000 | ✅ RUNNING | WAF active, proxying to Juice Shop |
  | Juice Shop | 3000 (internal) | ✅ RUNNING | Server listening, chatbot trained |
  | ZAP WebSwing Server | 30004 | ✅ RUNNING | Login page shows at localhost:30004 |
  | ZAP API | 30003 | ⚠️ CHECK | Configured but app crashes after login |
  
  **ZAP Application Issue Found:**
  - WebSwing SERVER is up and showing login page
  - But ZAP APP crashes when launched with error:
    `Can't load library: /usr/lib/jvm/java-21-openjdk-amd64/lib/libawt_xawt.so`
  - Root cause: Missing X11/AWT libraries in the container
  - This is a Java GUI library dependency issue, not the HTTPS issue we fixed

  **ZAP Login Credentials:**
  - The `/` root path shows admin login (requires credentials)
  - The `/zap` path uses **ANONYMOUS authentication** (no login required!)
  - **TRY: http://localhost:30004/zap** to bypass login screen!

- **Lab B X11 Fix Applied (2:30 PM):**
  - Changed `default-jre-headless` → `default-jre` (full JRE with AWT libs)
  - Added `fontconfig` and `fonts-dejavu-core` for font rendering
  - **Build time:** 141 seconds
  - **Pushed to:** `sarus.bodhi.cse.iitb.ac.in/bodhi_robin/8957/lab_b_test2:latest`
  - **Digest:** `sha256:59933c46b248ca80fc015eb65e725fd574f8db8e4e014edfdf05d42c1cdadd91`
  - **Dockerfile change:**
    ```dockerfile
    # BEFORE (missing AWT/Swing libraries):
    default-jre-headless
    
    # AFTER (full Java with GUI support):
    default-jre
    fontconfig
    fonts-dejavu-core
    ```

### February 2, 2026
- **Lab B:** Put on hold - admin will fix BodhiLabs deployment issue
- **Lab G:** Started work on Stored XSS lab
  - Verified python-app contents and templates exist
  - Created `single/` folder (copied from python-app)
  - Created `labDirectory/` folder
  - Built Docker image successfully (~84 seconds)
  - Pushed to `sarus.bodhi.cse.iitb.ac.in/bodhi_robin/8957/lab_g_test1:latest`
  - Fixed BodhiLabs-Package structure:
    - `client_evaluation.tgz` contains `.evaluationScripts/` folder at root
    - `student_directory.tgz` contains `labDirectory/` folder at root
  - Final package sizes:
    - `student_directory.tgz` (1.0 KB)
    - `client_evaluation.tgz` (19.7 KB)

---

## Overview

This document tracks all labs being developed for the BodhiLabs platform at IIT Bombay. It serves as persistent memory for the project scope, progress, issues, and decisions.

---

## Platform Details

- **Registry:** `sarus.bodhi.cse.iitb.ac.in/bodhi_robin/<activity_id>/`
- **Workflow:** Build dummy image on platform → Push real image to same registry path
- **Key Insight:** BodhiLabs mounts tarballs AFTER Dockerfile build completes
- **Standard Paths:**
  - `/home/.evaluationScripts/` - Evaluation scripts
  - `/home/.evaluationScripts/activityInitiator/initactivity.sh` - Container entrypoint
  - `/home/.evaluationScripts/autograder/autograder.py` - Grading logic
  - `/home/.evaluationScripts/evaluate.sh` - Evaluation wrapper
  - `/home/labDirectory/` - Student submission directory

---

## Lab B - Network Recon & Device Efficacy Audit

**Status:** ✅ FULLY FIXED & DEPLOYED

**Activity ID:** 8957 (container: clab_act_8958_148)

**Docker Image:** 
- Registry: `sarus.bodhi.cse.iitb.ac.in/bodhi_robin/8957/lab_b_test2:latest`
- Digest: `sha256:59933c46b248ca80fc015eb65e725fd574f8db8e4e014edfdf05d42c1cdadd91`
- Build: `lab-b:x11fix` (Feb 4, 2026 @ 2:30 PM)

**Stack:**
- OWASP Juice Shop + ModSecurity WAF + Apache + OWASP ZAP
- Base: `owasp/modsecurity-crs:apache`
- ZAP copied from `zaproxy/zap-stable`

**Ports:**
| Port | Service | Status |
|------|---------|--------|
| 30000 | Apache/ModSecurity → Juice Shop | ✅ Working |
| 30003 | ZAP API | ✅ Should work now |
| 30004 | ZAP WebSwing GUI | ✅ Fixed with full JRE |

**Submission Files:**
```
discovery.txt, enumeration.txt, bypass-technique.txt, flag.txt
```

**Issues Encountered & Fixed:**
1. ✅ BodhiLabs "No such container" - Fixed student_directory.tgz (was 98 bytes)
2. ✅ ZAP crash-loop - Fixed HTTPS port 8443 conflict with sed in initactivity.sh
3. ✅ Tarballs not updated - Recreated client_evaluation.tgz with fixes
4. ✅ ZAP app crash (libawt_xawt.so) - Changed default-jre-headless → default-jre

**ZAP Access:**
- http://localhost:30004/ → Admin console (has login)
- http://localhost:30004/zap → **Direct ZAP access** (anonymous auth)

**Dockerfile Key Fix:**
```dockerfile
# Full Java JRE (not headless) for ZAP AWT/Swing GUI
default-jre        # Changed from default-jre-headless
fontconfig         # Added for font rendering
fonts-dejavu-core  # Added for fonts
```

**Lab Objective:**
Students learn network reconnaissance and WAF bypass techniques using:
1. Discover the Juice Shop application
2. Enumerate endpoints and find vulnerabilities
3. Use ZAP to analyze traffic
4. Bypass ModSecurity WAF protections

**Files Created:**
- `Dockerfile` (current working version with X11 fix)
- `client_evaluation.tgz` (97.6 MB, includes Juice Shop source)
- `student_directory.tgz` (748 bytes)

---

## Lab G - Stored XSS (TechStore) with OWASP ZAP

**Status:** ✅ BUILT & PUSHED

**Activity ID:** 8957

**Docker Image:** 
- Local: `lab-g:test`
- Registry: `sarus.bodhi.cse.iitb.ac.in/bodhi_robin/8957/lab_g_test1:latest`
- Digest: `sha256:0cc3b786b1bd7ef4dab19bace773c6f07bc67df68f949ba0b25830bb131a2aa9`

**BodhiLabs Package Location:**
```
lab-G/lab-G/BodhiLabs-Package/
├── student_directory.tgz    (1.0 KB) - extracts to labDirectory/
├── client_evaluation.tgz    (19.7 KB) - extracts to .evaluationScripts/
├── studentDirectory/
│   └── labDirectory/
│       ├── README.txt
│       ├── flag.txt
│       └── xss-payload.txt
└── clientEvaluation/
    └── .evaluationScripts/
        ├── evaluate.sh
        ├── autograder/
        │   └── autograder.py
        └── activityInitiator/
            ├── initactivity.sh
            ├── reset.sh
            ├── zaprunner.sh
            ├── config/supervisord.conf
            └── python-app/
```

**Objective:**
Teach students to find and exploit stored XSS vulnerabilities using OWASP ZAP.

### Lab Concept

Students interact with a vulnerable e-commerce app ("TechStore") that has weak XSS sanitization (only strips `<script>` tags but allows event handlers like `onerror`, `onload`).

A **victim bot** (simulating an admin user) periodically browses the reviews page, triggering any XSS payloads students inject.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Single Container                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Flask App  │  │  OWASP ZAP  │  │ Victim Bot  │      │
│  │   :30000    │  │  :30003/4   │  │  (headless) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│         supervisord manages all services                 │
└─────────────────────────────────────────────────────────┘
```

**Ports:**
- `30000` - Flask e-commerce application
- `30003` - ZAP API
- `30004` - ZAP WebSwing GUI
- `8080` - ZAP Proxy

### Challenge Flow

1. **Reconnaissance (FLAG1):** Student explores the app (home, products, cart, reviews pages)
2. **ZAP Scanning (FLAG2):** Run ZAP scan, generate report with XSS findings
3. **Payload Crafting (FLAG3):** Create XSS payload that bypasses `<script>` filter
4. **Exfiltration (FLAG4):** Steal admin's secret flag via XSS when victim bot visits

### Vulnerability

The `sanitize_review()` function in `app.py` is intentionally weak:

```python
def sanitize_review(text):
    """
    INTENTIONALLY WEAK SANITIZATION
    Only removes <script> tags but allows event handlers
    """
    sanitized = text.replace('<script>', '').replace('</script>', '')
    sanitized = sanitized.replace('<SCRIPT>', '').replace('</SCRIPT>', '')
    return sanitized
```

**Bypass Examples:**
```html
<img src=x onerror="alert('XSS')">
<img src=x onerror="fetch('/api/admin/profile').then(r=>r.json()).then(d=>fetch('/exfil?flag='+d.secretFlag))">
```

### Submission Files

```
flag.txt           - All captured flags
zap-report.html    - ZAP scan report
xss-payload.txt    - Working XSS payload
```

### Current Issues

1. **Missing folders:** Dockerfile references `single/` and `labDirectory/` which don't exist
2. **App code location:** Python app is in `.evaluationScripts/activityInitiator/python-app/` but Dockerfile expects it in `single/`
3. **Need to reorganize:** Either fix Dockerfile paths or move files

### Autograder Tests (100 marks total)

| Test | Description | Marks |
|------|-------------|-------|
| 1 | Reconnaissance Complete (FLAG1) | 15 |
| 2 | OWASP ZAP Scanning (FLAG2) | 20 |
| 3 | XSS Payload Crafting (FLAG3) | 30 |
| 4 | Flag Exfiltration (FLAG4) | 35 |

### Files Structure

```
lab-G/
├── Dockerfile
├── README.md
├── WALKTHROUGH.md
└── .evaluationScripts/
    ├── evaluate.sh
    ├── autograder/
    │   └── autograder.py
    └── activityInitiator/
        ├── initactivity.sh
        ├── reset.sh
        ├── zaprunner.sh
        ├── config/
        │   └── supervisord.conf
        └── python-app/
            ├── app.py
            ├── init_db.py
            ├── models.py
            ├── flag_generator.py
            ├── victim_bot.py
            ├── requirements.txt
            └── templates/
```

### TODO

- [x] Fix Dockerfile to use correct paths
- [x] Create missing `single/` folder (copied from python-app)
- [x] Create missing `labDirectory/` structure
- [x] Build Docker image locally
- [x] Push to BodhiLabs registry
- [x] Create studentDirectory.zip
- [x] Create clientEvaluation.zip
- [ ] Test container fully (run locally, verify all services)
- [ ] Verify victim bot works with Chromium
- [ ] Test full challenge flow (recon → ZAP scan → XSS → exfil)
- [ ] Deploy and test on BodhiLabs platform

---

## Priv_Esc Labs (Reference)

Located in `Priv_Esc_Lab/` folder - these appear to be privilege escalation labs.

---

## Reference Folder

`BodhiLabs-master/` contains reference implementations for:
- Frontend (HTML/CSS/JS, React)
- Unix labs

---

## Notes & Decisions

1. **Heredoc approach:** For BodhiLabs compatibility, embed all configs inline using heredocs to avoid COPY command issues with tarball mounting
2. **Line endings:** Always add `sed -i 's/\r$//'` step to fix Windows CRLF → Unix LF
3. **ZAP base image:** `zaproxy/zap-stable:latest` is good for labs needing ZAP
4. **evaluate.json /tmp pattern (CRITICAL):** ALWAYS write evaluate.json to `/tmp/evaluate.json` from autograder.py, then `cp` to `/home/.evaluationScripts/evaluate.json` in evaluate.sh. NEVER write directly to the mount. See BODHILABS_COMPLETE_GUIDE.md Section 7.7.
5. **BOM stripping:** Windows editors (including VS Code) can silently add UTF-8 BOMs. Always strip BOMs from .sh/.py files before tarball packaging using `[System.IO.File]::ReadAllBytes()` in PowerShell.
6. **chmod -R 755 anti-pattern:** NEVER use `chmod -R 755` on `.evaluationScripts` in evaluate.sh — it resets evaluate.json permissions. Use targeted chmod on individual directories only.

---

## Quick Commands

```powershell
# Build and test locally
docker build -t lab-g .
docker run --rm -p 30000:30000 -p 30003:30003 -p 30004:30004 -p 8080:8080 lab-g

# Push to BodhiLabs
docker tag lab-g sarus.bodhi.cse.iitb.ac.in/bodhi_robin/<ACTIVITY_ID>/lab_g
docker push sarus.bodhi.cse.iitb.ac.in/bodhi_robin/<ACTIVITY_ID>/lab_g

# Check container logs
docker logs <container_id>

# Enter container
docker exec -it <container_id> /bin/bash
```

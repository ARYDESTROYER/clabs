# BodhiLabs Complete Architecture & Development Guide

**Version:** 1.0  
**Last Updated:** February 2026  
**Author:** Compiled from practical development experience  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [Core Components](#4-core-components)
   - 4.1 [Dockerfile](#41-dockerfile)
   - 4.2 [initactivity.sh (Initialization Script)](#42-initactivitysh-initialization-script)
   - 4.3 [evaluate.sh (Evaluation Script)](#43-evaluatesh-evaluation-script)
   - 4.4 [autograder.py (Autograder)](#44-autograderpy-autograder)
5. [Tarball Packaging](#5-tarball-packaging)
6. [LMS Upload & Deployment](#6-lms-upload--deployment)
7. [Critical Constraints & Gotchas](#7-critical-constraints--gotchas)
8. [Permission System Deep Dive](#8-permission-system-deep-dive)
9. [Troubleshooting Guide](#9-troubleshooting-guide)
10. [Code Templates](#10-code-templates)
11. [Case Study: Building a Privilege Escalation Lab](#11-case-study-building-a-privilege-escalation-lab)
12. [Quick Reference Checklist](#12-quick-reference-checklist)

---

## 1. Introduction

BodhiLabs is an educational platform for creating interactive Docker-based lab environments. Students access these labs through a web interface that provides:
- A terminal emulator connected to the Docker container
- A file editor for viewing and modifying files
- An evaluation system for grading student submissions

This guide documents everything required to build, deploy, and troubleshoot labs on the BodhiLabs platform, including lessons learned from real-world development challenges.

### 1.1 Key Terminology

| Term | Description |
|------|-------------|
| **Container C** | The Docker container configuration section in the LMS |
| **client_evaluation.tgz** | Tarball containing instructor scripts (mounted to `/home/.evaluationScripts`) |
| **student_directory.tgz** | Tarball containing student-facing files (mounted to `/home/labDirectory`) |
| **initactivity.sh** | Script that runs at container startup to configure the environment |
| **evaluate.sh** | Script triggered by the "Evaluate" button to grade submissions |
| **evaluate.json** | JSON file containing grading results, read by the LMS |

---

## 2. Architecture Overview

### 2.1 System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BodhiLabs LMS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────────────────┐ │
│   │  Dockerfile  │      │client_eval   │      │  student_directory.tgz   │ │
│   │  (Build)     │      │  .tgz        │      │                          │ │
│   └──────┬───────┘      └──────┬───────┘      └────────────┬─────────────┘ │
│          │                     │                           │               │
│          ▼                     ▼                           ▼               │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │                     Docker Container Runtime                         │ │
│   │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│   │  │                    Volume Mounts (Read-Write*)                  │ │ │
│   │  │                                                                 │ │ │
│   │  │  /home/.evaluationScripts  ◄── client_evaluation.tgz            │ │ │
│   │  │  /home/labDirectory        ◄── student_directory.tgz            │ │ │
│   │  │                                                                 │ │ │
│   │  └─────────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │  Container Startup Flow:                                             │ │
│   │  1. Docker image built from Dockerfile                               │ │
│   │  2. Volumes mounted at runtime (NOT during build)                    │ │
│   │  3. CMD executes initactivity.sh                                     │ │
│   │  4. Container enters infinite sleep loop (keeps alive)               │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   * Files from tarballs may have read-only metadata tracked by LMS         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Evaluation Flow

```
Student clicks "Evaluate"
         │
         ▼
┌─────────────────────────┐
│  LMS triggers           │
│  /home/.evaluationScripts/evaluate.sh
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  evaluate.sh            │
│  - Copies submissions   │
│  - Calls autograder.py  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  autograder.py          │
│  - Reads student work   │
│  - Compares to expected │
│  - Writes evaluate.json │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  LMS reads              │
│  evaluate.json          │
│  - Displays results     │
│  - Records score        │
└─────────────────────────┘
```

---

## 3. Directory Structure

### 3.1 Development Structure (On Your Machine)

```
YourLab/
├── .evaluationScripts/              # Instructor-only scripts
│   ├── activityInitiator/           # Initialization subfolder
│   │   ├── initactivity.sh          # Main init script (REQUIRED)
│   │   └── [source files]           # C source, configs, etc.
│   ├── evaluate.sh                  # Evaluation trigger (REQUIRED)
│   ├── autograder.py                # Grading logic (REQUIRED)
│   └── [helper files]               # linpeas.sh, etc.
├── labDirectory/                    # Student-facing files
│   ├── README.md                    # Lab instructions
│   └── [starter files]              # Any files students need
├── Dockerfile                       # Container build instructions
├── client_evaluation.tgz            # Generated: .evaluationScripts archive
└── student_directory.tgz            # Generated: labDirectory archive
```

### 3.2 Runtime Structure (Inside Container)

```
/home/
├── .evaluationScripts/              # Mounted from client_evaluation.tgz
│   ├── activityInitiator/
│   │   └── initactivity.sh
│   ├── evaluate.sh
│   ├── autograder.py
│   └── evaluate.json                # Created at runtime by autograder
├── labDirectory/                    # Mounted from student_directory.tgz
│   ├── README.md
│   └── [student files]
└── student/                         # Student's home directory
    └── .bashrc
```

---

## 4. Core Components

### 4.1 Dockerfile

The Dockerfile defines the container image. **CRITICAL**: The LMS mounts volumes at **runtime**, not during build. This means:

- ❌ `COPY .evaluationScripts /home/.evaluationScripts` will NOT work
- ✅ Create empty directories and let the LMS mount into them

#### Template Dockerfile

```dockerfile
FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

# Fix broken repositories in base image
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

# Install required packages
RUN apt-get update && apt-get install -y \
    sudo \
    vim \
    gcc \
    # Add other packages as needed
    && rm -rf /var/lib/apt/lists/*

# Create student user with TEMPORARY sudo access
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Create mount point directories (REQUIRED)
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# Environment variables
ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

# Set base permissions
RUN chown -R student:student /home/labDirectory

# Quality of life
RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

# Set default user and working directory
USER student
WORKDIR /home/labDirectory

# Container startup: Run init script, then keep alive
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
```

#### Key Points:

1. **Base Image**: `sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest` is the IITB BodhiLabs base
2. **Broken Repos**: Always remove `ondrej*.list` - it's broken in the base image
3. **Temporary Sudo**: Create sudoers file that the init script will DELETE after setup
4. **No COPY**: Don't try to COPY evaluation scripts - they come from tarball mounts
5. **CMD Pattern**: Always use `init.sh; while :; do sleep 10; done` to keep container alive

---

### 4.2 initactivity.sh (Initialization Script)

This script runs once when the container starts. It must:
1. Set up the lab environment (compile binaries, create files, set permissions)
2. Revoke temporary sudo access
3. Handle errors gracefully

#### Template initactivity.sh

```bash
#!/bin/bash
# Do NOT use set -e - we want to handle errors gracefully
# set -e 

echo "[+] Initializing Lab Environment..."

# ═══════════════════════════════════════════════════════════════════════════
# PART 1: INFRASTRUCTURE & PERMISSIONS (Critical - Do This First!)
# ═══════════════════════════════════════════════════════════════════════════

# 1. Ensure .evaluationScripts is traversable
# Do NOT rely on creating or chmodding evaluate.json here.
# The safe pattern is: pre-bake a placeholder in the tarball, write results to
# /tmp/evaluate.json from autograder.py, then copy back in evaluate.sh.
sudo chmod 755 /home/.evaluationScripts /home/.evaluationScripts/activityInitiator 2>/dev/null || true

# 2. Create any submission files that students need to write to
# IMPORTANT: If file is in tarball, LMS marks it read-only!
# Solution: Create file at runtime, NOT in tarball
sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
echo "(Paste your answer here)" | sudo tee /home/labDirectory/SUBMIT_FLAG_HERE.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt

# ═══════════════════════════════════════════════════════════════════════════
# PART 2: LAB-SPECIFIC SETUP
# ═══════════════════════════════════════════════════════════════════════════

# Example: Compile a vulnerable binary
if [ -f "/home/.evaluationScripts/activityInitiator/vulnerable.c" ]; then
    sudo gcc /home/.evaluationScripts/activityInitiator/vulnerable.c \
        -o /usr/local/bin/vulnerable
    sudo chown root:root /usr/local/bin/vulnerable
    sudo chmod 4755 /usr/local/bin/vulnerable  # SUID bit
    echo "[+] Vulnerable binary compiled"
else
    echo "[!] Warning: vulnerable.c not found"
fi

# Example: Create a secret flag
echo "IITB{your_flag_here}" | sudo tee /root/flag.txt > /dev/null
sudo chmod 400 /root/flag.txt

# Example: Copy helper tools
if [ -f "/home/.evaluationScripts/linpeas.sh" ]; then
    cp /home/.evaluationScripts/linpeas.sh /home/labDirectory/
    chown student:student /home/labDirectory/linpeas.sh
    chmod +x /home/labDirectory/linpeas.sh
fi

# ═══════════════════════════════════════════════════════════════════════════
# PART 3: CLEANUP & LOCKDOWN
# ═══════════════════════════════════════════════════════════════════════════

# Ensure student owns their working directory
sudo chown -R student:student /home/labDirectory

# CRITICAL: Revoke temporary sudo access
echo "[*] Revoking sudo privileges..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo access revoked"
else
    echo "[!] Warning: sudoers file not found (already revoked?)"
fi

echo "[+] Lab initialization complete!"
```

#### Critical Pattern: Infrastructure First

Always set up infrastructure (permissions, files) BEFORE any lab-specific setup that might fail:

```
✅ CORRECT ORDER:
1. Ensure the evaluation directory is traversable
2. Create submission files
3. Fix directory permissions
4. Compile binaries (might fail)
5. Revoke sudo

❌ WRONG ORDER:
1. Compile binaries (fails)
2. Script exits
3. evaluate.json never created
4. Autograder crashes with PermissionError
```

---

### 4.3 evaluate.sh (Evaluation Script)

This script is triggered when the student clicks "Evaluate". It should:
1. Copy student submissions to a safe location (avoids permission issues)
2. Run the autograder
3. Copy autograder output back from `/tmp` to the mount point
4. Handle missing files gracefully

#### Template evaluate.sh

```bash
#!/bin/bash
# Purpose: Evaluate student submission by running the autograder

# Define paths
EVAL_DIR="/home/.evaluationScripts"
SUBMISSION_FILE="SUBMIT_FLAG_HERE.txt"
STUDENT_SUBMISSION="/home/labDirectory/$SUBMISSION_FILE"
TEMP_SUBMISSION="/tmp/student_submission.txt"

# Clean up previous temp files
[ -f "$TEMP_SUBMISSION" ] && rm "$TEMP_SUBMISSION"

# Copy student's submission to /tmp (avoids permission issues with read-only mounts)
if [ -f "$STUDENT_SUBMISSION" ]; then
    cp "$STUDENT_SUBMISSION" "$TEMP_SUBMISSION"
    chmod 644 "$TEMP_SUBMISSION"
else
    echo "Warning: $SUBMISSION_FILE not found in student directory." >&2
fi

# Run the Python autograder (writes results to /tmp/evaluate.json)
python3 "$EVAL_DIR/autograder.py"

# Copy results from /tmp to where the LMS reads them
# CRITICAL: The autograder writes to /tmp because the mounted .evaluationScripts
# directory may be read-only due to LMS tarball metadata restrictions.
# See Section 7.7 for the full explanation.
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
```

#### Why Copy to /tmp?

The LMS may have permission restrictions on **both reading and writing** files in tarball-mounted directories (`/home/labDirectory` and `/home/.evaluationScripts`). The `/tmp` directory is a standard Linux tmpfs that is **always** world-writable, regardless of mount options or LMS metadata. Using `/tmp` as an intermediary ensures:
- The autograder can always write `evaluate.json` without `PermissionError`
- Student submissions can always be read by the autograder
- The final `cp` back to `.evaluationScripts/` works because `evaluate.sh` is invoked by the LMS itself

---

### 4.4 autograder.py (Autograder)

The autograder reads student work, compares it to expected values, and writes results to `evaluate.json`.

#### Template autograder.py

```python
#!/usr/bin/env python3
import os
import json

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Where we read student submission from (copied by evaluate.sh)
SUBMISSION_FILE = "/tmp/student_submission.txt"

# Expected answer
EXPECTED_ANSWER = "IITB{your_flag_here}"

# Output file — write to /tmp to avoid mount permission issues
# evaluate.sh will copy this to /home/.evaluationScripts/evaluate.json for the LMS
OUTPUT_JSON = "/tmp/evaluate.json"

# ═══════════════════════════════════════════════════════════════════════════
# EVALUATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

results = {"data": []}

test_result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Answer incorrect or missing"
}

try:
    if os.path.exists(SUBMISSION_FILE):
        with open(SUBMISSION_FILE, 'r') as f:
            student_answer = f.read().strip()
        
        if student_answer == EXPECTED_ANSWER:
            test_result["status"] = "success"
            test_result["score"] = 1
            test_result["message"] = "Correct! Well done."
        else:
            test_result["message"] = f"Incorrect answer. Try again."
    else:
        test_result["message"] = "Submission file not found. Please submit your answer."

except Exception as e:
    test_result["message"] = f"Error during evaluation: {str(e)}"

results["data"].append(test_result)

# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT RESULTS
# ═══════════════════════════════════════════════════════════════════════════

with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

# Print summary (shown in terminal)
print(f"Score: {test_result['score']}/{test_result['maximum marks']}")
print(f"Message: {test_result['message']}")
```

#### evaluate.json Format

The LMS expects this exact structure:

```json
{
  "data": [
    {
      "testid": 1,
      "status": "success",
      "score": 1,
      "maximum marks": 1,
      "message": "Test passed!"
    },
    {
      "testid": 2,
      "status": "failure",
      "score": 0,
      "maximum marks": 1,
      "message": "Expected X but got Y"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `testid` | int | Unique identifier for each test |
| `status` | string | "success" or "failure" |
| `score` | int | Points earned |
| `maximum marks` | int | Maximum possible points |
| `message` | string | Feedback shown to student |

---

## 5. Tarball Packaging

### 5.1 Structure Requirements

The tarballs MUST contain the folder structure, not just the contents:

```
✅ CORRECT: client_evaluation.tgz contains:
   .evaluationScripts/
   .evaluationScripts/activityInitiator/
   .evaluationScripts/activityInitiator/initactivity.sh
   .evaluationScripts/evaluate.sh
   .evaluationScripts/autograder.py

❌ WRONG: client_evaluation.tgz contains:
   activityInitiator/
   evaluate.sh
   autograder.py
```

### 5.2 Packaging Commands

#### Windows (PowerShell with tar)

```powershell
cd YourLab

# Package client evaluation (with .evaluationScripts folder inside)
tar -czf client_evaluation.tgz .evaluationScripts

# Package student directory (with labDirectory folder inside)
tar -czf student_directory.tgz labDirectory

# Verify contents
tar -tzvf client_evaluation.tgz
tar -tzvf student_directory.tgz
```

#### Linux/macOS

```bash
cd YourLab

# Package with folder structure
tar -czvf client_evaluation.tgz .evaluationScripts
tar -czvf student_directory.tgz labDirectory

# macOS: Recommended clean packaging (prevents ._* AppleDouble files)
find . -name '._*' -o -name '.DS_Store'
find . \( -name '._*' -o -name '.DS_Store' \) -type f -delete
COPYFILE_DISABLE=1 tar -czvf client_evaluation.tgz .evaluationScripts
COPYFILE_DISABLE=1 tar -czvf student_directory.tgz labDirectory

# Optional verification
tar -tzvf client_evaluation.tgz | grep -E '(^|/)\._|(^|/)\.DS_Store' || echo "client_evaluation.tgz clean"
tar -tzvf student_directory.tgz | grep -E '(^|/)\._|(^|/)\.DS_Store' || echo "student_directory.tgz clean"
```

### 5.3 macOS AppleDouble Metadata Gotcha

On macOS, Finder and extended attributes can create hidden metadata entries:
- `._<filename>` (AppleDouble sidecar files)
- `.DS_Store`

If these are included in lab tarballs, students may see duplicate/noisy files in the LMS explorer. This is cosmetic but confusing.

Recommended practice on macOS:
1. Delete `._*` and `.DS_Store` files before packaging.
2. Set `COPYFILE_DISABLE=1` while creating tarballs.
3. Verify archives are clean with `tar -tzf ... | grep` checks before upload.

### 5.4 Automated Packaging Script (prepup.sh)

```bash
#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <Lab Folder>"
    exit 1
fi

LAB=$1

# Detect OS
OS=$(uname -s)

# Package instructor files
cd "$LAB" || exit 1
if [ "$OS" = "Darwin" ]; then
    tar --no-mac-metadata -czvf ../client_evaluation.tgz .evaluationScripts
    tar --no-mac-metadata -czvf ../student_directory.tgz labDirectory
else
    tar -czvf ../client_evaluation.tgz .evaluationScripts
    tar -czvf ../student_directory.tgz labDirectory
fi
cd - > /dev/null

echo "✅ Created: client_evaluation.tgz, student_directory.tgz"
```

---

## 6. LMS Upload & Deployment

### 6.1 Container C Configuration

1. Navigate to your lab in the LMS admin panel
2. Go to **Container C** section
3. Configure the following:

#### Dockerfile
- Paste your Dockerfile content in the editor

#### Client Evaluation Archive
- **File**: Upload `client_evaluation.tgz`
- **Mount Path**: `/home` (the archive contains `.evaluationScripts/` folder)

#### Student Directory Archive
- **File**: Upload `student_directory.tgz`
- **Mount Path**: `/home` (the archive contains `labDirectory/` folder)

#### Scripts Section
- **Name**: `Evaluate`
- **Script Path**: `/home/.evaluationScripts/evaluate.sh`

### 6.2 Rebuild Process

1. After uploading files, click **Rebuild**
2. Wait for the build to complete (check logs for errors)
3. Test the lab as a student

### 6.3 Debugging Builds

If the build fails:
1. Check the build logs in the LMS
2. Common issues:
   - Broken apt repositories (remove ondrej*.list)
   - Missing packages in base image
   - Syntax errors in Dockerfile

---

## 7. Critical Constraints & Gotchas

### 7.1 The Read-Only File Problem (APPLIES TO BOTH TARBALLS)

**Problem**: Files included in **both** `student_directory.tgz` and `client_evaluation.tgz` can be marked as read-only by the LMS metadata layer. Even if you set `chmod 777` or `chmod 666` inside the container, the LMS may silently reject writes. This applies to **any** file that comes from a tarball mount — not just student files.

**Symptoms**:
- 400 BAD REQUEST when saving files (student files via editor)
- "Unable to save readonly file" error (student files via editor)
- `PermissionError: [Errno 13] Permission denied: '/home/.evaluationScripts/evaluate.json'` (autograder writing results)
- `touch: cannot touch '/home/.evaluationScripts/evaluate.json': Permission denied` (initactivity.sh)

**Important**: This behavior is **inconsistent** across activities. One activity on the same lab may work fine while another fails, even with identical configurations. Do not assume that because one activity works, all will.

**Solution for student-facing files**: Don't include writable files in the tarball. Create them at runtime in `initactivity.sh`:

```bash
# ❌ WRONG: File in tarball
# labDirectory/SUBMIT_FLAG_HERE.txt  <- Will be read-only!

# ✅ CORRECT: Create at runtime
sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chmod 666 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt
```

**Solution for evaluate.json**: See **Section 7.7** — the autograder must write to `/tmp` first, then `evaluate.sh` copies the result to the mounted directory.

### 7.2 No COPY in Dockerfile

**Problem**: The LMS mounts tarballs at runtime, not during build. COPY instructions won't work.

```dockerfile
# ❌ WRONG
COPY .evaluationScripts /home/.evaluationScripts

# ✅ CORRECT
RUN mkdir -p /home/.evaluationScripts
# Let LMS mount the tarball here at runtime
```

### 7.3 Temporary Sudo Pattern

**Problem**: You need root to set up the environment, but students shouldn't have sudo.

**Solution**: Grant temporary sudo that the init script revokes:

```dockerfile
# In Dockerfile
RUN echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp
```

```bash
# In initactivity.sh (at the end!)
sudo rm -f /etc/sudoers.d/student_temp
```

### 7.4 Tool Availability

**Problem**: Some tools require special kernel capabilities not available in the container.

**Affected Tools**:
- `ltrace` - Requires CAP_SYS_PTRACE (not available)
- `strace` - May have limited functionality
- `gdb` - May have attachment restrictions

**Solution**: Use alternatives or document limitations:
```bash
# Instead of ltrace, use:
strings /path/to/binary
objdump -d /path/to/binary
```

### 7.5 Script Execution Failures

**Problem**: If the init script fails early, infrastructure may not be set up, causing cascading failures.

**Solution**: Use the "Infrastructure First" pattern:
```bash
# Do NOT use set -e
# set -e  

# 1. Set up permissions FIRST (always succeeds)
# NOTE: evaluate.json should be pre-baked in the tarball AND written to /tmp.
# Do NOT rely on sudo touch inside .evaluationScripts — the mount may be read-only.
chmod 666 /home/.evaluationScripts/evaluate.json 2>/dev/null || true

# 2. Then do risky operations
gcc /path/to/source.c -o /path/to/binary  # Might fail
```

### 7.6 Windows CRLF Line Endings (^M: bad interpreter)

**Problem**: Files created or edited on Windows use CRLF (`\r\n`) line endings. When these shell scripts or Python files run inside the Linux container, you get:
```
bash: /home/.evaluationScripts/evaluate.sh: /bin/bash^M: bad interpreter: No such file or directory
```

**Cause**: The `\r` (carriage return) character is invisible on Windows but Linux treats it as part of the interpreter path, looking for `/bin/bash\r` which doesn't exist.

**Affected Files**: All `.sh` and `.py` files in `.evaluationScripts/` and `labDirectory/`. This includes `evaluate.sh`, `initactivity.sh`, and `autograder.py`.

**Solution**: Convert files to Unix LF line endings **before** packaging into tarballs.

```powershell
# PowerShell: Convert a single file to Unix LF
$content = [System.IO.File]::ReadAllText("path\to\file.sh")
$content = $content -replace "`r`n", "`n"
[System.IO.File]::WriteAllText("path\to\file.sh", $content, (New-Object System.Text.UTF8Encoding $false))
```

```powershell
# PowerShell: Convert ALL scripts in a lab folder at once
$base = "Priv_Esc_Activity1"
Get-ChildItem -Path "$base\.evaluationScripts" -Recurse -Include *.sh,*.py | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName)
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Converted: $($_.Name)"
}
```

**Prevention**: Use an editor that saves with LF line endings (VS Code: change "End of Line Sequence" to `LF` in the status bar), or always run the conversion before `tar -czf`.

### 7.7 The evaluate.json Write Problem (CRITICAL — Read This!)

**Problem**: The autograder needs to write grading results to `evaluate.json` inside `/home/.evaluationScripts/`. However, this directory is a **tarball-mounted volume** controlled by the LMS. The LMS metadata layer can mark files in this mount as read-only, causing `PermissionError` when the autograder tries to `open(OUTPUT_JSON, 'w')`.

**Root Cause (Deep Dive)**:

The BodhiLabs LMS extracts `client_evaluation.tgz` into `/home/.evaluationScripts/` as a volume mount. The LMS tracks every file from the tarball in its metadata layer and can enforce read-only permissions **independently of Linux file permissions**. This means:

1. `chmod 666` / `chmod 777` inside the container has **no effect** — the LMS overrides it
2. `sudo touch` / `sudo chown` may silently fail or have no lasting effect because the mount's metadata takes precedence
3. Pre-baking `evaluate.json` in the tarball makes it tracked and potentially read-only
4. Creating the file at runtime with `sudo touch` may also fail because the directory itself is a restricted mount
5. This behavior is **inconsistent across activities** — one activity may work while another doesn't, even with identical code

**Symptoms**:
```
Traceback (most recent call last):
  File "/home/.evaluationScripts/autograder.py", line XX, in <module>
    with open(OUTPUT_JSON, 'w') as f:
PermissionError: [Errno 13] Permission denied: '/home/.evaluationScripts/evaluate.json'
```

**What Does NOT Work** (all of these were tried and failed):

| Approach | Why It Fails |
|----------|-------------|
| `sudo touch evaluate.json` in initactivity.sh | sudo may silently fail; mount may be read-only anyway |
| `chmod 666 evaluate.json` in initactivity.sh | LMS metadata overrides Linux permissions |
| Pre-baking evaluate.json in the tarball | LMS marks tarball files as read-only |
| `chmod -R 755 .evaluationScripts` in evaluate.sh | Resets evaluate.json to 755 (owner-write only), and LMS may override anyway |
| Reordering chmod operations | Doesn't help if the mount itself blocks writes |

**✅ CORRECT Solution: The /tmp Write Pattern**:

Bypass the mounted directory entirely. Write to `/tmp` (always world-writable, no LMS restrictions), then copy back.

**Step 1 — autograder.py**: Write results to `/tmp/evaluate.json`:
```python
# ✅ CORRECT: Write to /tmp (always writable)
OUTPUT_JSON = "/tmp/evaluate.json"

# ❌ WRONG: Write directly to mount (may be read-only)
# OUTPUT_JSON = "/home/.evaluationScripts/evaluate.json"
```

**Step 2 — evaluate.sh**: Copy results from `/tmp` to where the LMS reads them:
```bash
# Run the autograder (writes to /tmp/evaluate.json)
python3 "$EVAL_DIR/autograder.py"

# Copy results to where the LMS expects them
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
```

**Step 3 — Pre-bake a seed evaluate.json in the tarball**: Include a minimal `{"data":[]}` file in `.evaluationScripts/evaluate.json` so the file exists at mount time. This acts as a placeholder that `cp` can overwrite.

**Why This Works**:
- `/tmp` is a standard Linux tmpfs — world-writable, no mount restrictions, no LMS metadata
- Python can always write to `/tmp` regardless of who runs the script
- The `cp` in `evaluate.sh` works because the LMS itself invoked the script and may grant write access during evaluation
- Even if the `cp` fails (due to LMS restrictions), the autograder doesn't crash — it already wrote successfully to `/tmp`
- The LMS may also read the evaluate.json from the mount even if `cp` fails, as long as the pre-baked placeholder exists

### 7.8 LMS Editor vs Terminal Write Mismatch (Submission Files)

**Problem**: A submission file may be writable from terminal commands but still fail to save in the LMS editor as "readonly".

**Why this happens**:
- The LMS editor path can enforce stricter ownership/metadata checks than shell redirection commands.
- If submission files are created with root ownership, stale metadata, or inconsistent mode/owner state across init runs, the editor may reject saves.

**Reliable fix pattern** (in `initactivity.sh`):
```bash
# Ensure student owns the workspace mount
chown -R student:student /home/labDirectory 2>/dev/null || true

# Recreate writable submission files every start
for f in SUBMIT_FLAG_HERE.txt; do
    rm -f "/home/labDirectory/$f" 2>/dev/null || true
    : > "/home/labDirectory/$f"
    chown student:student "/home/labDirectory/$f" 2>/dev/null || true
    chmod 777 "/home/labDirectory/$f" 2>/dev/null || true
done
```

**Key point**: Runtime recreation + explicit `student` ownership is more reliable than only `chmod`.

### 7.9 ZAP WebSwing Porting Safety (Avoid Script Rewrites)

**Problem**: Browser UI endpoint (for example `localhost:30004/zap`) may return `ERR_EMPTY_RESPONSE` if ZAP WebSwing startup scripts are modified with broad search/replace.

**Risky pattern**:
- Rewriting `/zap/zap-webswing.sh` with global `sed` replacements (for example replacing all `8090` occurrences).
- Rewriting `webswing.config` with broad string substitution across unknown versions.

**Safer pattern**:
- Prefer setting ZAP backend port via environment:
    - `ZAP_WEBSWING_OPTS="-host 0.0.0.0 -port 30003"`
- Limit file edits to `jetty.properties` for UI host/port/HTTPS toggles only.

Example supervisor entry:
```ini
[program:zap]
directory=/zap
command=/zap/zap-webswing.sh
autostart=true
autorestart=true
environment=ZAP_WEBSWING_OPTS="-host 0.0.0.0 -port 30003"
```

If UI still fails:
```bash
cat /opt/*zap*.err
cat /opt/*zap*.log
netstat -tuln | grep -E '30004|30003|8080|8090'
```

### 7.10 ZAP WebSwing Infinite Spinner Due to Java Version Mismatch

**Symptom**: `http://localhost:30004/zap` loads but stays on "Starting your application".

**Root cause**: ZAP classes in current `zaproxy/zap-stable` builds are compiled for Java 17 (class file version 61). If the runtime JVM is Java 11 (supports up to class file 55), WebSwing cannot launch `org.zaproxy.zap.ZAP` and silently loops at startup.

**Log signature** (`/zap/webswing/logs/webswing.log` or `/zap/webswing/webswing.out`):
```text
UnsupportedClassVersionError: org/zaproxy/zap/ZAP has been compiled by a more recent version of the Java Runtime (class file version 61.0), this version of the Java Runtime only recognizes class file versions up to 55.0
```

**Fix pattern**:
```dockerfile
# Install Java 17 runtime
RUN apt-get update && apt-get install -y openjdk-17-jre && rm -rf /var/lib/apt/lists/*
```

```bash
# In initactivity.sh, force Java 17 for ZAP launch
if [ -x /usr/lib/jvm/java-17-openjdk-amd64/bin/java ]; then
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    export PATH="$JAVA_HOME/bin:$PATH"
fi
java -version
```

**Verification**:
- `java -version` shows `17.x` in init logs.
- `webswing.log` no longer reports `UnsupportedClassVersionError`.
- `/zap` transitions from spinner to active ZAP UI.

**Debugging Tip**: If you're still getting issues after applying this pattern, SSH into the container and run:
```bash
# Check who runs the evaluation
whoami

# Check evaluate.json permissions
ls -la /home/.evaluationScripts/evaluate.json

# Test if /tmp is writable
echo '{"test":true}' > /tmp/test.json && echo "tmp works" && rm /tmp/test.json

# Test if the mount is writable
echo '{"test":true}' > /home/.evaluationScripts/test.json && echo "mount works" || echo "MOUNT IS READ-ONLY"
```

---

## 8. Permission System Deep Dive

### 8.1 User Context

| Phase | Running As | Sudo Available |
|-------|-----------|----------------|
| Docker Build | root | N/A |
| Container Start | student | YES (temporary) |
| Init Script | student | YES (temporary) |
| After Init | student | NO |
| Evaluation | student | NO |

### 8.2 File Ownership Matrix

| Path | Owner | Permissions | Notes |
|------|-------|-------------|-------|
| `/home/.evaluationScripts/` | root | 755 | Instructor scripts |
| `/home/.evaluationScripts/evaluate.json` | LMS-mounted placeholder | varies | Seed file only; write real results to `/tmp/evaluate.json` |
| `/home/labDirectory/` | student | 755 | Student workspace |
| `/home/labDirectory/*` | student | 644-666 | Student files |
| `/root/flag.txt` | root | 400 | Secret flag |
| `/usr/local/bin/vulnerable` | root | 4755 | SUID binary |

### 8.3 Common Permission Errors

#### Error: PermissionError writing evaluate.json

**Cause**: The `.evaluationScripts` directory is a tarball-mounted volume. The LMS metadata layer may enforce read-only on files inside it, regardless of Linux permissions. `sudo touch`, `chmod 666`, and pre-baking the file all fail to make it reliably writable.

**Fix**: Use the **/tmp Write Pattern** (see Section 7.7 for full details):
```python
# In autograder.py — write to /tmp, NOT the mount
OUTPUT_JSON = "/tmp/evaluate.json"
```
```bash
# In evaluate.sh — copy results back after autograder runs
python3 "$EVAL_DIR/autograder.py"
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
```

> **⚠️ WARNING**: Do NOT use the old pattern of `sudo touch evaluate.json` in initactivity.sh alone. It does not reliably work across all activities. Always use the /tmp write pattern.

#### Error: Cannot write to labDirectory

**Cause**: Directory owned by root

**Fix**:
```bash
sudo chown -R student:student /home/labDirectory
```

#### Error: Unable to save readonly file (LMS)

**Cause**: File was in tarball (either `student_directory.tgz` or `client_evaluation.tgz`), LMS tracks it as read-only

**Fix**: For student files, remove from tarball and create at runtime. For evaluate.json, use the /tmp write pattern (Section 7.7).

---

## 9. Troubleshooting Guide

### 9.1 Build Failures

#### "E: Unable to locate package"

**Cause**: Broken apt sources

**Fix**:
```dockerfile
RUN rm -f /etc/apt/sources.list.d/ondrej*.list
RUN apt-get update && apt-get install -y [packages]
```

#### "useradd: user already exists"

**Cause**: Base image has conflicting user

**Fix**: Check base image for existing users, or use different username

### 9.2 Runtime Failures

#### Container exits immediately

**Cause**: CMD doesn't keep container alive

**Fix**:
```dockerfile
CMD ["/bin/bash", "-c", "bash init.sh; while :; do sleep 10; done"]
```

#### Init script errors

**Cause**: set -e causes early exit

**Fix**: Comment out `set -e`, handle errors manually

### 9.3 Evaluation Failures

#### "Autograder Failed!"

**Cause**: Python error in autograder.py

**Debug**:
```bash
# In container terminal
python3 /home/.evaluationScripts/autograder.py
```

#### Scores not appearing

**Cause**: evaluate.json not written or malformed

**Debug**:
```bash
cat /home/.evaluationScripts/evaluate.json
```

### 9.4 File Permission Issues

#### Student can't write files

**Debug**:
```bash
ls -la /home/labDirectory/
id  # Check current user
```

**Fix**: Ensure init script sets ownership

---

## 10. Code Templates

### 10.1 Complete Lab Template

A ready-to-use template structure:

```
MyLab/
├── .evaluationScripts/
│   ├── activityInitiator/
│   │   └── initactivity.sh
│   ├── evaluate.sh
│   └── autograder.py
├── labDirectory/
│   └── README.md
└── Dockerfile
```

### 10.2 Template Files

[Refer to Section 4 for complete template files for each component]

### 10.3 prepup.sh for Windows (PowerShell)

```powershell
# prepup.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$LabFolder
)

Set-Location $LabFolder

# Create tarballs
tar -czf ..\client_evaluation.tgz .evaluationScripts
tar -czf ..\student_directory.tgz labDirectory

# Verify
Write-Host "`n=== client_evaluation.tgz ===" -ForegroundColor Green
tar -tzvf ..\client_evaluation.tgz

Write-Host "`n=== student_directory.tgz ===" -ForegroundColor Green
tar -tzvf ..\student_directory.tgz

Set-Location ..
Write-Host "`n✅ Archives created successfully!" -ForegroundColor Green
```

---

## 11. Case Study: Building a Privilege Escalation Lab

This section documents the complete development journey of a real Privilege Escalation lab, including all challenges encountered and solutions implemented.

### 11.1 Lab Overview

**Course**: Cybersecurity Fundamentals  
**Topic**: Linux Privilege Escalation  
**Activities**:
1. Enumeration & SUID Discovery
2. PATH-Based SUID Exploitation
3. GTFOBins Exploitation

### 11.2 Initial Approach & Challenges

#### Challenge 1: Base Image Issues

**Problem**: The base image `sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest` had a broken APT repository.

**Error**:
```
E: The repository 'http://ppa.launchpad.net/ondrej/php/ubuntu jammy Release' does not have a Release file.
```

**Solution**:
```dockerfile
RUN rm -f /etc/apt/sources.list.d/ondrej*.list
```

#### Challenge 2: COPY Doesn't Work

**Problem**: Initially tried to COPY evaluation scripts during build:
```dockerfile
COPY .evaluationScripts /home/.evaluationScripts  # FAILED
```

**Error**: Files didn't appear at runtime because LMS mounts volumes that override the copied files.

**Solution**: Don't COPY - create empty directories and let LMS mount tarballs:
```dockerfile
RUN mkdir -p /home/.evaluationScripts
```

#### Challenge 3: ltrace Not Working

**Problem**: Wanted students to use `ltrace` to analyze binaries, but it failed:
```
ltrace: Couldn't attach to target process
```

**Cause**: Container lacks `CAP_SYS_PTRACE` capability.

**Solution**: Removed ltrace dependency, instructed students to use `strings` instead:
```markdown
## Note
The tool `ltrace` is not available. Use `strings` to analyze binaries:
```bash
strings /usr/local/bin/sysbackup
```

#### Challenge 4: Permission Denied on evaluate.json

**Problem**: When clicking "Evaluate", got:
```
PermissionError: [Errno 13] Permission denied: '/home/.evaluationScripts/evaluate.json'
```

**Cause**: The autograder wrote directly into the mounted `.evaluationScripts` path.

**Solution**: Use the `/tmp` write pattern instead of touching `evaluate.json` in `initactivity.sh`:
```python
OUTPUT_JSON = "/tmp/evaluate.json"
```
```bash
python3 "$EVAL_DIR/autograder.py"
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
```

#### Challenge 5: Read-Only Submission File

**Problem**: Students couldn't save their flag to SUBMIT_FLAG_HERE.txt:
```
400 BAD REQUEST
{"error": "Unable to save readonly file"}
```

**Investigation**:
- Checked file permissions inside container: `777` (correct)
- Compared with working Activity 2: identical permissions
- Inspected HTTP requests: LMS returns 200 for Activity 2, 400 for Activity 3

**Root Cause Discovery**: The LMS tracks files from tarballs in a separate metadata layer. Files included in `student_directory.tgz` are marked read-only regardless of chmod inside the container.

**Solution**: Remove the file from the tarball entirely and create it at runtime:

```bash
# In initactivity.sh
# File is NOT in tarball, so LMS won't track it
sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
echo "(Paste your flag here)" | sudo tee /home/labDirectory/SUBMIT_FLAG_HERE.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt
```

### 11.3 Final Working Structure

#### Activity 2: PATH Exploitation

**Vulnerability**: SUID binary calls `gzip` without absolute path

```c
// sysbackup.c
#include <unistd.h>
#include <stdlib.h>

int main() {
    setuid(0);
    setgid(0);
    // VULNERABILITY: Relative path call
    system("gzip -f /var/log/syslog.bak"); 
    return 0;
}
```

**Exploitation**:
1. Create malicious `gzip` in `/home/labDirectory`
2. Prepend to PATH: `export PATH=/home/labDirectory:$PATH`
3. Run vulnerable binary: `/usr/local/bin/sysbackup`
4. Malicious gzip runs as root

#### Activity 3: GTFOBins

**Setup**: Set SUID bit on standard binaries

```bash
# In initactivity.sh
sudo chmod u+s /usr/bin/vim.basic
sudo chmod u+s /usr/bin/less
sudo chmod u+s /usr/bin/awk
```

**Exploitation** (using vim):
```bash
vim -c ':py3 import os; os.execl("/bin/bash", "bash", "-p")'
```

### 11.4 Key Learnings

1. **Infrastructure First**: Always set up permissions before any code that might fail
2. **LMS Metadata Layer**: Files in tarballs are tracked separately from container permissions
3. **Runtime Creation**: Writable files must be created at runtime, not in tarballs
4. **Graceful Degradation**: Don't use `set -e` - handle errors manually
5. **Tool Limitations**: Check capability requirements before depending on tools

### 11.5 Final File Contents

#### Dockerfile (Activity 2)

```dockerfile
FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

RUN rm -f /etc/apt/sources.list.d/ondrej*.list
RUN apt-get update && apt-get install -y sudo

RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

RUN mkdir -p /home/labDirectory /home/.evaluationScripts

ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

RUN chown -R student:student /home/labDirectory

RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

USER student
WORKDIR /home/labDirectory
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
```

#### initactivity.sh (Activity 2)

```bash
#!/bin/bash
echo "[+] Initializing Activity 2 (PATH Exploit)..."

# PART 1: INFRASTRUCTURE
sudo chmod 755 /home/.evaluationScripts /home/.evaluationScripts/activityInitiator 2>/dev/null || true

sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chmod 777 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt

echo "IITB{p4th_v4r_m4n1pul4t10n_succ3ss}" | sudo tee /root/flag.txt > /dev/null
sudo chmod 400 /root/flag.txt

# PART 2: VULNERABLE ENVIRONMENT
sudo touch /var/log/syslog.bak
sudo chmod 666 /var/log/syslog.bak

if [ -f "/home/.evaluationScripts/activityInitiator/sysbackup.c" ]; then
    sudo gcc /home/.evaluationScripts/activityInitiator/sysbackup.c -o /usr/local/bin/sysbackup
    sudo chown root:root /usr/local/bin/sysbackup
    sudo chmod 4755 /usr/local/bin/sysbackup
fi

# PART 3: LOCKDOWN
sudo rm -f /etc/sudoers.d/student_temp
echo "[+] Activity 2 Initialization Complete."
```

---

## 12. Quick Reference Checklist

### Pre-Development

- [ ] Understand lab objectives and student workflow
- [ ] Identify required packages and tools
- [ ] Check tool compatibility (ltrace, strace, etc.)
- [ ] Plan file structure

### Development

- [ ] Create directory structure
- [ ] Write Dockerfile (no COPY for evaluation scripts)
- [ ] Write initactivity.sh (infrastructure first pattern)
- [ ] Write evaluate.sh (copy to /tmp pattern)
- [ ] Write autograder.py (correct JSON format)
- [ ] Write student README.md
- [ ] Ensure submission files are NOT in tarball

### Packaging

- [ ] Package client_evaluation.tgz WITH .evaluationScripts folder
- [ ] Package student_directory.tgz WITH labDirectory folder
- [ ] Verify tarball contents with `tar -tzvf`
- [ ] Remove any .DS_Store or ._ files (macOS)

### Deployment

- [ ] Upload Dockerfile to LMS
- [ ] Upload client_evaluation.tgz
- [ ] Upload student_directory.tgz
- [ ] Configure Evaluate script path
- [ ] Click Rebuild
- [ ] Check build logs

### Testing

- [ ] Open lab as student
- [ ] Verify init script ran (check for expected binaries/files)
- [ ] Test file writing in labDirectory
- [ ] Complete the lab exercise
- [ ] Click Evaluate
- [ ] Verify score appears correctly

### Troubleshooting Commands

```bash
# Check file permissions
ls -la /home/labDirectory/
ls -la /home/.evaluationScripts/

# Check current user
id
whoami

# Test autograder manually
python3 /home/.evaluationScripts/autograder.py

# Check evaluate.json
cat /home/.evaluationScripts/evaluate.json

# Check for SUID binaries
find / -perm -4000 2>/dev/null
```

---

## Appendix A: evaluate.json Schema

```json
{
  "data": [
    {
      "testid": <integer>,
      "status": "<success|failure>",
      "score": <integer>,
      "maximum marks": <integer>,
      "message": "<string>"
    }
  ]
}
```

## Appendix B: Common Base Images

| Image | Use Case |
|-------|----------|
| `sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest` | IITB standard (Ubuntu-based) |
| `ubuntu:22.04` | General Linux labs |
| `node:22-alpine` | React/JavaScript labs |

## Appendix C: Useful Tools

| Tool | Package | Purpose |
|------|---------|---------|
| gcc | build-essential | Compile C code |
| python3 | python3 | Autograder |
| vim | vim | Text editing |
| strings | binutils | Binary analysis |
| find | findutils | File search |

---

## Appendix D: Alternative Directory Structures

BodhiLabs supports multiple directory naming conventions depending on the lab type. This section covers the `.bodhiFiles` pattern commonly used in Unix and Frontend labs.

### D.1 Complete Directory Structure with .bodhiFiles

```
YourLabName/
├── .evaluationScripts/                    # Instructor-facing evaluation files
│   ├── .bodhiFiles/                       # Alternative name, used in Unix labs
│   │   ├── studentDirectory/              # Initial files copied to student workspace
│   │   │   ├── [initial files for students]
│   │   │   └── [sample data files]
│   │   ├── .solutions/                    # Solution files (excluded from student archive)
│   │   │   ├── answer1.txt
│   │   │   ├── answer2.txt
│   │   │   └── ...
│   │   ├── autograder.py                  # Python-based grading logic
│   │   ├── expected/                      # Expected output files for comparison
│   │   │   ├── step1.txt
│   │   │   ├── step2.txt
│   │   │   └── ...
│   │   └── init_helper.sh                 # Additional initialization if needed
│   ├── evaluate.sh                        # Script that runs the autograder
│   ├── init.sh                            # Initializes the lab environment
│   ├── autograder.js                      # JavaScript-based grading (for JS/React labs)
│   ├── package.json                       # Dependencies for JS labs
│   └── node_modules/                      # Installed dependencies
├── labDirectory/                          # Student workspace
│   ├── README.md                          # Problem statement and instructions
│   ├── index.html                         # Starter HTML file (for web labs)
│   ├── script.js                          # Starter JavaScript file
│   ├── styles.css                         # Starter CSS file
│   └── [other starter files]
├── init.sh                                # Root initialization script
├── evaluate.sh                            # Root evaluation script
├── reset.sh                               # Optional reset script
└── Dockerfile                             # Docker configuration
```

### D.2 Key Differences from activityInitiator Pattern

| Aspect | activityInitiator Pattern | .bodhiFiles Pattern |
|--------|---------------------------|---------------------|
| Init script location | `.evaluationScripts/activityInitiator/initactivity.sh` | `.evaluationScripts/init.sh` or root `init.sh` |
| Student files source | Created at runtime | `.bodhiFiles/studentDirectory/` copied at init |
| Solutions storage | Not typically used | `.bodhiFiles/.solutions/` (excluded from tarball) |
| Expected outputs | Hardcoded in autograder | `.bodhiFiles/expected/` folder |

---

## Appendix E: Detailed File Examples

### E.1 Root-Level Files

#### init.sh (Standard Pattern)

**Purpose:** Copies initial files from `.evaluationScripts/.bodhiFiles/studentDirectory/` to `/home/labDirectory/` when the Docker container starts. Ensures lab is set up only once.

```bash
#!/bin/bash
# Purpose: Initialize the lab environment by copying student files
# This runs when the Docker container starts

if [ -f "/opt/check.txt" ]; then
    echo "Lab already initialized. No need to reinitialize."
else
    # Copy all initial files to student workspace
    cp -r /home/.evaluationScripts/.bodhiFiles/studentDirectory/* /home/labDirectory/
    
    # Set appropriate permissions so students can read and write
    chmod ugo+r+w /home/labDirectory/*
    
    # Create a marker file to prevent re-initialization
    echo "Done" > /opt/check.txt
fi

# Start the bash shell for student interaction
exec /bin/bash
```

#### evaluate.sh (Standard Pattern)

**Purpose:** Entry point for grading. Called when the student submits their work.

```bash
#!/bin/bash
# Purpose: Evaluate student submission by running the autograder
# This is called when student clicks "Evaluate" or submits

# Navigate to evaluation scripts directory
cd /home/.evaluationScripts/.bodhiFiles

# Clean up any previous answer files
[ -f answer.txt ] && rm answer.txt

# Copy student's answer files from labDirectory to evaluation directory
cp /home/labDirectory/answer1.txt /home/.evaluationScripts/.bodhiFiles/
cp /home/labDirectory/answer2.txt /home/.evaluationScripts/.bodhiFiles/

# Run the autograder (Python or Node.js)
python3 /home/.evaluationScripts/.bodhiFiles/autograder.py

# The autograder generates evaluate.json which is read by the platform
```

#### reset.sh

**Purpose:** Resets the lab environment to initial state. Allows students to start over.

```bash
#!/bin/bash
# Purpose: Reset the lab to initial state

# Remove all files from student workspace
rm -rf /home/labDirectory/*

# Copy fresh files from studentDirectory
cp -r /home/.evaluationScripts/.bodhiFiles/studentDirectory/* /home/labDirectory/

# Reset permissions
chmod ugo+r+w /home/labDirectory/*

echo "Lab has been reset to initial state."
```

#### Dockerfile (Ubuntu Base)

**Purpose:** Defines the Docker container environment for Unix/general labs.

```dockerfile
# Purpose: Create a Docker image with all necessary tools for the lab
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools and utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        vim \
        nano \
        man-db \
        manpages \
        python3 \
        net-tools \
        less \
        gedit \
        zip \
        bzip2 \
        unzip \
        sudo \
        file && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Restore minimized Ubuntu features (man pages, etc.)
RUN yes | unminimize

# Create necessary directories for lab
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# Set working directory to student workspace
WORKDIR /home/labDirectory

# Configure bash environment
RUN echo "cd /home/labDirectory" >> /root/.bashrc && \
    echo "alias ls='ls --color=always'" >> /root/.bashrc && \
    echo "rm -f \$(find /home -type f -name \"._*\")" >> /root/.bashrc

# Run initialization script and keep container alive
CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init.sh; while :; do sleep 10; done" ]
```

#### Dockerfile (Node.js for React/JS Labs)

```dockerfile
FROM node:18

WORKDIR /home/.evaluationScripts

# Copy package files and install dependencies
COPY .evaluationScripts/package*.json ./
RUN npm install

# Create directories
RUN mkdir -p /home/labDirectory

WORKDIR /home/labDirectory

# Run init script which also starts the dev server
CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init.sh" ]
```

---

### E.2 labDirectory Files (Student-Facing)

#### labDirectory/README.md

**Purpose:** Provides the problem statement, requirements, and instructions to students.

```markdown
# Array Operations Lab

## Problem Statement

You need to implement a JavaScript program that performs basic array operations.
This lab will test your understanding of array manipulation in JavaScript.

## Objectives

By completing this lab, you will demonstrate your ability to:
1. Create and initialize arrays
2. Access and modify array elements
3. Use array properties like length
4. Display results to the user

## Requirements

### Task 1: Create an Array
- Create an array named `myArray` with elements: 1, 2, 3, 4, 5
- Store it in a variable
- Display the array to the console

### Task 2: Modify Array Element
- Change the value of the element at index 2 to 6
- The array should now be: [1, 2, 6, 4, 5]
- Display the modified array

### Task 3: Get Array Length
- Get the length of the array
- Store it in a variable named `arrayLength`
- Display the length

### Task 4: Display Results
- Display all results in the HTML element with ID 'output'
- Format: "Array: [1,2,6,4,5], Length: 5"

## Expected Output

Your program should produce output in this format:
```
Original Array: [1,2,3,4,5]
Modified Array: [1,2,6,4,5]
Array Length: 5
```

## Hints

- Use square brackets `[]` to create arrays
- Access elements using `array[index]`
- Array indices start at 0
- Use `.length` property to get array size
- Use `document.getElementById()` to update HTML

## Constraints

- Do NOT remove existing HTML elements
- Do NOT change element IDs
- You CAN add new JavaScript code
- You CAN modify the script.js file

## Testing Your Solution

1. Open index.html in a browser
2. Check if the output matches the expected format
3. Click "Evaluate" to run automated tests

Good luck!
```

#### labDirectory/index.html

**Purpose:** Provides the HTML structure for web-based labs.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Array Operations Lab</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Array Operations Lab</h1>
        <p>Complete the tasks in script.js to manipulate arrays.</p>
        
        <!-- Output display area - DO NOT REMOVE -->
        <div id="output" class="output">
            Results will appear here...
        </div>
        
        <!-- Button to trigger operations - DO NOT REMOVE -->
        <button id="runButton" onclick="runOperations()">Run Operations</button>
    </div>
    
    <!-- JavaScript file where students write code -->
    <script src="script.js"></script>
</body>
</html>
```

#### labDirectory/script.js

**Purpose:** Starter JavaScript file with some code provided. Students complete the missing parts.

```javascript
// Purpose: Students complete this file to perform array operations
// Some code is provided, students fill in the missing parts

// DO NOT MODIFY THIS FUNCTION SIGNATURE
function runOperations() {
    const outputDiv = document.getElementById('output');
    let result = '';
    
    // TASK 1: Create an array with elements 1, 2, 3, 4, 5
    // TODO: Write your code below
    let myArray = [1, 2, 3, 4, 5];
    
    result += `Original Array: [${myArray}]<br>`;
    
    // TASK 2: Change the element at index 2 to 6
    // TODO: Write your code below
    myArray[2] = 6;
    
    result += `Modified Array: [${myArray}]<br>`;
    
    // TASK 3: Get the length of the array
    // TODO: Write your code below
    let arrayLength = myArray.length;
    
    result += `Array Length: ${arrayLength}<br>`;
    
    // Display results (DO NOT MODIFY)
    outputDiv.innerHTML = result;
}

// DO NOT REMOVE - This runs when page loads
window.onload = function() {
    console.log('Array Operations Lab loaded');
};
```

#### labDirectory/styles.css

**Purpose:** Provides styling for the lab interface.

```css
/* Purpose: Style the lab interface for better user experience */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    background: white;
    padding: 40px;
    border-radius: 10px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    max-width: 600px;
    width: 100%;
}

h1 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

.output {
    background: #f5f5f5;
    border: 2px solid #ddd;
    border-radius: 5px;
    padding: 20px;
    margin: 20px 0;
    min-height: 100px;
    font-family: 'Courier New', monospace;
    line-height: 1.6;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    width: 100%;
    transition: background 0.3s;
}

button:hover {
    background: #5568d3;
}
```

---

### E.3 .evaluationScripts/.bodhiFiles/ Files (Instructor-Facing)

#### autograder.py (Comprehensive Example)

**Purpose:** Automated grading script that tests student submissions and generates results in JSON format.

```python
#!/usr/bin/env python3
"""
Purpose: Automatically grade student submissions
Compares student output against expected output
Generates evaluate.json with test results
"""

import os
import subprocess
import json
import copy
import shutil

# Base Paths
base = "/home/.evaluationScripts/.bodhiFiles"
student_dir = os.path.join("/home", "labDirectory")
expected_dir = os.path.join(base, "expected")
output_json = os.path.join("/tmp", "evaluate.json")

# Template for test results
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Test failed"
}

# Results container
results = {"data": []}

print("Starting autograder...")

# Test 1: Check if array is created correctly
print("Test 1: Checking array creation")
test1 = copy.deepcopy(template)
test1["testid"] = 1

try:
    script_path = os.path.join(student_dir, "script.js")
    
    if not os.path.exists(script_path):
        test1["message"] = "script.js file not found"
        results["data"].append(test1)
    else:
        with open(script_path, 'r') as f:
            content = f.read()
        
        if "myArray" in content and "[1, 2, 3, 4, 5]" in content:
            test1["status"] = "success"
            test1["score"] = 1
            test1["message"] = "Array created correctly"
        else:
            test1["message"] = "Array not created correctly. Expected: [1, 2, 3, 4, 5]"
        
        results["data"].append(test1)
except Exception as e:
    test1["message"] = f"Error reading script.js: {str(e)}"
    results["data"].append(test1)

# Test 2: Check if element at index 2 is modified
print("Test 2: Checking array modification")
test2 = copy.deepcopy(template)
test2["testid"] = 2

try:
    with open(script_path, 'r') as f:
        content = f.read()
    
    if "myArray[2]" in content and "= 6" in content:
        test2["status"] = "success"
        test2["score"] = 1
        test2["message"] = "Array element modified correctly"
    else:
        test2["message"] = "Array element at index 2 not modified to 6"
    
    results["data"].append(test2)
except Exception as e:
    test2["message"] = f"Error checking modification: {str(e)}"
    results["data"].append(test2)

# Test 3: Check if length is retrieved
print("Test 3: Checking array length retrieval")
test3 = copy.deepcopy(template)
test3["testid"] = 3

try:
    with open(script_path, 'r') as f:
        content = f.read()
    
    if "arrayLength" in content and ".length" in content:
        test3["status"] = "success"
        test3["score"] = 1
        test3["message"] = "Array length retrieved correctly"
    else:
        test3["message"] = "Array length not retrieved correctly"
    
    results["data"].append(test3)
except Exception as e:
    test3["message"] = f"Error checking length: {str(e)}"
    results["data"].append(test3)

# Test 4: Check HTML output
print("Test 4: Checking HTML output")
test4 = copy.deepcopy(template)
test4["testid"] = 4

try:
    with open(script_path, 'r') as f:
        content = f.read()
    
    if "getElementById('output')" in content or 'getElementById("output")' in content:
        test4["status"] = "success"
        test4["score"] = 1
        test4["message"] = "Output div is used correctly"
    else:
        test4["message"] = "Output div not used. Use getElementById('output')"
    
    results["data"].append(test4)
except Exception as e:
    test4["message"] = f"Error checking HTML output: {str(e)}"
    results["data"].append(test4)

# Test 5: Overall code quality check
print("Test 5: Code quality check")
test5 = copy.deepcopy(template)
test5["testid"] = 5

try:
    index_path = os.path.join(student_dir, "index.html")
    with open(index_path, 'r') as f:
        html_content = f.read()
    
    if 'id="output"' in html_content and 'runOperations' in html_content:
        test5["status"] = "success"
        test5["score"] = 1
        test5["message"] = "Code quality check passed"
    else:
        test5["message"] = "Important HTML elements were removed or modified"
    
    results["data"].append(test5)
except Exception as e:
    test5["message"] = f"Error in code quality check: {str(e)}"
    results["data"].append(test5)

# Write results to JSON file
print("Writing results to evaluate.json")
with open(output_json, 'w') as f:
    json.dump(results, f, indent=2)

print("Autograder complete!")

# Print summary
total_score = sum(test["score"] for test in results["data"])
max_score = len(results["data"])
print(f"Score: {total_score}/{max_score}")
```

#### autograder.js (JavaScript Version)

**Purpose:** JavaScript-based autograder for Node.js environments (React/JS labs).

```javascript
/**
 * Purpose: Automatically grade JavaScript/React lab submissions
 * Uses Node.js to test student code
 * Generates evaluate.json with results
 */

const fs = require('fs');
const path = require('path');

// Paths
const studentDir = '/home/labDirectory';
const evaluationDir = '/home/.evaluationScripts';
const outputFile = '/tmp/evaluate.json';

// Test result template
const createTest = (testid, status = 'failure', score = 0, message = 'Test failed') => ({
    testid,
    status,
    score,
    'maximum marks': 1,
    message
});

// Results container
const results = { data: [] };

console.log('Starting JavaScript autograder...');

// Test 1: Check if script.js exists
console.log('Test 1: Checking if script.js exists');
const scriptPath = path.join(studentDir, 'script.js');

if (fs.existsSync(scriptPath)) {
    results.data.push(createTest(1, 'success', 1, 'script.js file found'));
} else {
    results.data.push(createTest(1, 'failure', 0, 'script.js file not found'));
}

// Test 2: Check if code contains required function
console.log('Test 2: Checking for required function');
try {
    const scriptContent = fs.readFileSync(scriptPath, 'utf8');
    
    if (scriptContent.includes('function runOperations()')) {
        results.data.push(createTest(2, 'success', 1, 'runOperations function found'));
    } else {
        results.data.push(createTest(2, 'failure', 0, 'runOperations function not found'));
    }
} catch (error) {
    results.data.push(createTest(2, 'failure', 0, `Error reading script.js: ${error.message}`));
}

// Test 3: Check if array operations are present
console.log('Test 3: Checking array operations');
try {
    const scriptContent = fs.readFileSync(scriptPath, 'utf8');
    
    const hasArrayCreation = scriptContent.includes('myArray') || 
                             scriptContent.includes('let') || 
                             scriptContent.includes('const');
    const hasArrayModification = scriptContent.includes('[2]') || 
                                  scriptContent.includes('myArray[');
    const hasLengthCheck = scriptContent.includes('.length');
    
    if (hasArrayCreation && hasArrayModification && hasLengthCheck) {
        results.data.push(createTest(3, 'success', 1, 'Array operations implemented correctly'));
    } else {
        let missing = [];
        if (!hasArrayCreation) missing.push('array creation');
        if (!hasArrayModification) missing.push('array modification');
        if (!hasLengthCheck) missing.push('length check');
        results.data.push(createTest(3, 'failure', 0, `Missing: ${missing.join(', ')}`));
    }
} catch (error) {
    results.data.push(createTest(3, 'failure', 0, `Error checking operations: ${error.message}`));
}

// Test 4: Check HTML file integrity
console.log('Test 4: Checking HTML integrity');
try {
    const htmlPath = path.join(studentDir, 'index.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    if (htmlContent.includes('id="output"') && htmlContent.includes('script.js')) {
        results.data.push(createTest(4, 'success', 1, 'HTML structure maintained correctly'));
    } else {
        results.data.push(createTest(4, 'failure', 0, 'HTML structure was modified incorrectly'));
    }
} catch (error) {
    results.data.push(createTest(4, 'failure', 0, `Error checking HTML: ${error.message}`));
}

// Test 5: Syntax check
console.log('Test 5: Syntax validation');
try {
    const scriptContent = fs.readFileSync(scriptPath, 'utf8');
    
    const hasSyntaxError = scriptContent.includes('}{') && !scriptContent.includes('} {');
    const hasMissingBracket = (scriptContent.match(/{/g) || []).length !== 
                               (scriptContent.match(/}/g) || []).length;
    
    if (!hasSyntaxError && !hasMissingBracket) {
        results.data.push(createTest(5, 'success', 1, 'No obvious syntax errors detected'));
    } else {
        results.data.push(createTest(5, 'failure', 0, 'Syntax errors detected'));
    }
} catch (error) {
    results.data.push(createTest(5, 'failure', 0, `Syntax validation error: ${error.message}`));
}

// Write results to file
console.log('Writing results to evaluate.json');
fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));

// Print summary
const totalScore = results.data.reduce((sum, test) => sum + test.score, 0);
const maxScore = results.data.length;
console.log(`\nAutograder complete!`);
console.log(`Score: ${totalScore}/${maxScore}`);

process.exit(totalScore === maxScore ? 0 : 1);
```

#### .solutions/answer1.txt

**Purpose:** Contains the correct solution for reference. Excluded from student archive.

```javascript
// SOLUTION: Task 1 - Create Array
let myArray = [1, 2, 3, 4, 5];
console.log('Original Array:', myArray);

// SOLUTION: Task 2 - Modify element at index 2
myArray[2] = 6;
console.log('Modified Array:', myArray);

// SOLUTION: Task 3 - Get array length
let arrayLength = myArray.length;
console.log('Array Length:', arrayLength);

// SOLUTION: Complete function
function runOperations() {
    const outputDiv = document.getElementById('output');
    let result = '';
    
    let myArray = [1, 2, 3, 4, 5];
    result += `Original Array: [${myArray}]<br>`;
    
    myArray[2] = 6;
    result += `Modified Array: [${myArray}]<br>`;
    
    let arrayLength = myArray.length;
    result += `Array Length: ${arrayLength}<br>`;
    
    outputDiv.innerHTML = result;
}
```

#### studentDirectory/README.md

**Purpose:** Initial README copied to student workspace.

```markdown
# Welcome to Array Operations Lab

## Getting Started

This lab will test your understanding of JavaScript arrays.

### Files in this lab:
- `index.html` - The main HTML file (DO NOT MODIFY)
- `script.js` - Write your code here
- `styles.css` - Styling (DO NOT MODIFY)
- `README.md` - This file

### Instructions:
1. Read the problem statement carefully
2. Complete the tasks in `script.js`
3. Test your solution by opening `index.html` in a browser
4. Click "Evaluate" to check your solution

### Important Notes:
- Do NOT remove existing HTML elements
- Do NOT change element IDs
- Focus on completing the tasks in `script.js`

Good luck!
```

#### expected/step1.txt, step2.txt, step3.txt

**Purpose:** Contains expected output for specific test cases.

```
# step1.txt
Original Array: [1,2,3,4,5]

# step2.txt
Modified Array: [1,2,6,4,5]

# step3.txt
Array Length: 5
```

#### init_helper.sh

**Purpose:** Additional initialization tasks.

```bash
#!/bin/bash
# Purpose: Helper script for additional initialization tasks

# Set up environment variables
export LAB_NAME="ArrayOperations"
export LAB_VERSION="1.0"

# Create any additional directories needed
mkdir -p /home/labDirectory/temp

# Set up any aliases
echo "alias check='bash /home/.evaluationScripts/evaluate.sh'" >> /root/.bashrc

# Display welcome message
echo "======================================"
echo "Welcome to $LAB_NAME Lab (v$LAB_VERSION)"
echo "======================================"
echo ""
echo "Type 'check' to evaluate your solution"
echo ""
```

#### package.json (For React/JS Labs)

**Purpose:** Defines Node.js dependencies and scripts.

```json
{
  "name": "array-operations-lab",
  "version": "1.0.0",
  "description": "Automated grading for Array Operations Lab",
  "main": "autograder.js",
  "scripts": {
    "start": "node server.js",
    "test": "node autograder.js",
    "evaluate": "node autograder.js"
  },
  "keywords": ["lab", "education", "javascript", "arrays"],
  "author": "BodhiLabs",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "puppeteer": "^19.0.0",
    "fs-extra": "^11.1.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.20"
  }
}
```

#### init.sh (For React Labs with Server)

**Purpose:** Initializes lab and starts development server.

```bash
#!/bin/bash
# Purpose: Initialize React/JS lab and start development server

if [ -f "/opt/check.txt" ]; then
    echo "Lab already initialized."
else
    # Copy student files
    cp -r /home/.evaluationScripts/.bodhiFiles/studentFiles/* /home/labDirectory/
    chmod -R 777 /home/labDirectory/*
    echo "Done" > /opt/check.txt
fi

# Navigate to evaluation scripts directory
cd /home/.evaluationScripts

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start the development server on port 30000
PORT=30000 npm start
```

---

### E.4 Unix-Specific Example

#### Unix/Lab1/.bodhiFiles/studentDirectory/explore_this/joke1

**Purpose:** Sample file for students to explore using Unix commands.

```
    Why don't eggs tell jokes? Because they might crack up!

    Why did the math book look sad? Because it had too many problems.

    What do you get when you cross a snowman and a vampire? Frostbite.






    Why did the scarecrow win an award? Because he was outstanding in his field!

    Why don't oysters donate to charity? Because they are shellfish!

    What's orange and sounds like a parrot? A carrot!
```

#### Unix/Lab1/labDirectory/README.md

**Purpose:** Instructions for Unix command practice.

```markdown
# Unix Commands Lab - File Exploration

## Problem Statement

Learn to navigate the Unix filesystem and use basic commands to explore files.

## Tasks

### Task 1: List Files
- Use the `ls` command to list all files in the current directory
- Save the command you used in `command.txt`

### Task 2: Find a Specific File
- Navigate to the `explore_this` directory
- Find a file named `joke1`
- Use `cat` to display its contents
- Count how many lines contain the word "why" (case-insensitive)
- Save the filename in `filename.txt`

### Task 3: Count Empty Lines
- In the `joke1` file, count how many empty lines there are
- Use `grep` or `wc` commands
- Save your answer (just the number) in `answer.txt`

## Expected Output

### command.txt should contain:
```
ls -la
```

### filename.txt should contain:
```
joke1
```

### answer.txt should contain:
```
5
```

## Helpful Commands

- `ls` - List directory contents
- `cd` - Change directory
- `cat` - Display file contents
- `grep` - Search for patterns
- `wc -l` - Count lines
- `find` - Find files

## Hints

- Use `grep -c` to count matches
- Empty lines can be found with `grep "^$"`
- Combine commands with pipes `|`

## Evaluation

When you're ready, type:
```bash
bash /home/.evaluationScripts/evaluate.sh
```
Or simply:
```bash
check
```
```

#### Unix Lab autograder.py

**Purpose:** Grades Unix command labs by checking student's answer files.

```python
#!/usr/bin/env python3
"""
Purpose: Grade Unix command lab submissions
Checks if students used correct commands and got correct results
"""

import os
import json
import copy

# Paths
base = "/home/.evaluationScripts/.bodhiFiles"
student_dir = "/home/labDirectory"
output_json = os.path.join("/tmp", "evaluate.json")

# Template
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Test failed"
}

results = {"data": []}

print("Starting Unix lab autograder...")

# Test 1: Check if command.txt exists and contains ls command
print("Test 1: Checking command.txt")
test1 = copy.deepcopy(template)
test1["testid"] = 1

command_file = os.path.join(student_dir, "command.txt")
if os.path.exists(command_file):
    with open(command_file, 'r') as f:
        command = f.read().strip()
    
    if "ls" in command:
        test1["status"] = "success"
        test1["score"] = 1
        test1["message"] = "Correct command used: ls"
    else:
        test1["message"] = "ls command not found in command.txt"
else:
    test1["message"] = "command.txt file not found"

results["data"].append(test1)

# Test 2: Check if filename.txt is correct
print("Test 2: Checking filename.txt")
test2 = copy.deepcopy(template)
test2["testid"] = 2

filename_file = os.path.join(student_dir, "filename.txt")
if os.path.exists(filename_file):
    with open(filename_file, 'r') as f:
        filename = f.read().strip()
    
    if filename == "joke1":
        test2["status"] = "success"
        test2["score"] = 1
        test2["message"] = "Correct filename identified"
    else:
        test2["message"] = f"Incorrect filename. Expected: joke1, Got: {filename}"
else:
    test2["message"] = "filename.txt not found"

results["data"].append(test2)

# Test 3: Check if answer.txt contains correct number
print("Test 3: Checking answer.txt")
test3 = copy.deepcopy(template)
test3["testid"] = 3

answer_file = os.path.join(student_dir, "answer.txt")
if os.path.exists(answer_file):
    with open(answer_file, 'r') as f:
        answer = f.read().strip()
    
    if answer == "5":
        test3["status"] = "success"
        test3["score"] = 1
        test3["message"] = "Correct count of empty lines"
    else:
        test3["message"] = f"Incorrect answer. Expected: 5, Got: {answer}"
else:
    test3["message"] = "answer.txt not found"

results["data"].append(test3)

# Write results
print("Writing results...")
with open(output_json, 'w') as f:
    json.dump(results, f, indent=2)

# Summary
total = sum(t["score"] for t in results["data"])
print(f"\nScore: {total}/{len(results['data'])}")
print("Autograder complete!")
```

---

### E.5 Upload Preparation Script (prepup.sh)

**Purpose:** Generates compressed archives for uploading to the platform.

```bash
#!/bin/bash
# Purpose: Prepare lab files for upload to BodhiLabs platform
# Creates two archives:
#   - instructor.tgz: Contains evaluation scripts (excluding solutions)
#   - student.tgz: Contains student workspace files
# Usage: ./prepup.sh <lab_name>

# Check if lab name is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <Lab Name>"
    echo "Example: ./prepup.sh Lab1"
    exit 1
fi

lab=$1

# Detect operating system
OS=$(uname -s)

# Define paths
evaluationScripts="$lab/.evaluationScripts"
labDir="$lab/labDirectory"

# Verify directories exist
if [ ! -d "$lab" ]; then
    echo "Error: Lab directory '$lab' not found"
    exit 1
fi

echo "Preparing lab: $lab"
echo "================================"

# Step 1: Remove extended attributes (macOS-specific metadata)
if [ "$OS" = "Darwin" ]; then
    echo "Removing macOS extended attributes..."
    xattr -cr "$evaluationScripts" 2>/dev/null
    xattr -cr "$labDir" 2>/dev/null
fi

# Step 2: Create instructor archive (excludes .solutions folder)
echo "Creating instructor archive..."
cd "$lab" || exit 1

if [ "$OS" = "Darwin" ]; then
    tar --no-mac-metadata --exclude=".solutions" --exclude=".DS_Store" -czvf ../instructor.tgz .evaluationScripts
else
    tar --exclude=".solutions" -czvf ../instructor.tgz .evaluationScripts
fi

# Step 3: Create student archive
echo "Creating student archive..."
if [ "$OS" = "Darwin" ]; then
    tar --no-mac-metadata --exclude=".DS_Store" -czvf ../student.tgz labDirectory
else
    tar -czvf ../student.tgz labDirectory
fi

cd - > /dev/null

# Step 4: Clean up macOS-specific files
if [ "$OS" = "Darwin" ]; then
    find "$lab" -name "._*" -delete
    find "$lab" -name ".DS_Store" -delete
    echo "✅ Archives created successfully (without macOS resource fork files)"
else
    echo "✅ Archives created successfully"
fi

echo ""
echo "Created files:"
echo "  - instructor.tgz ($(du -h instructor.tgz | cut -f1))"
echo "  - student.tgz ($(du -h student.tgz | cut -f1))"
echo ""
echo "Next steps:"
echo "  1. Upload instructor.tgz in the 'Add Script' section"
echo "  2. Upload student.tgz as student files"
echo "  3. In 'Add Script' section, add:"
echo "     Name: Evaluate"
echo "     Script: /home/.evaluationScripts/evaluate.sh"
```

---

## Appendix F: Complete Workflow Summary

### F.1 For Instructors Creating a Lab

1. **Create directory structure:**
```
YourLabName/
├── .evaluationScripts/
├── labDirectory/
├── init.sh
├── evaluate.sh
└── Dockerfile
```

2. **Write problem statement** in `labDirectory/README.md`

3. **Create starter files** in `labDirectory/`

4. **Write autograder** in `.evaluationScripts/`

5. **Add solutions** in `.evaluationScripts/.solutions/` (optional)

6. **Test locally with Docker:**
```bash
docker buildx build -t yourlab:latest .
docker run -it --rm -v .:/home/.evaluationScripts yourlab
```

7. **Generate upload files:**
```bash
./prepup.sh YourLabName
```

8. **Upload to platform:**
   - Upload instructor.tgz as evaluation scripts
   - Upload student.tgz as student files
   - Configure evaluation script path: `/home/.evaluationScripts/evaluate.sh`

### F.2 For Students Using the Lab

1. Lab opens in Docker container
2. `init.sh` runs automatically, copying files to workspace
3. Student reads `README.md` in `/home/labDirectory/`
4. Student completes tasks by editing files
5. Student runs evaluation:
```bash
bash /home/.evaluationScripts/evaluate.sh
```
6. Autograder runs and generates `evaluate.json`
7. Platform displays results to student

---

## Appendix G: Key Principles Summary

### File Separation

| Directory | Purpose | Access |
|-----------|---------|--------|
| `.evaluationScripts/` | Instructor-only, contains grading logic | Hidden from students |
| `labDirectory/` | Student workspace | Full read/write |
| `.solutions/` | Reference solutions | Never in student archive |

### Initialization Pattern

```bash
# init.sh runs once when container starts
if [ -f "/opt/check.txt" ]; then
    echo "Already initialized"
else
    # Copy files, set permissions
    cp -r /path/to/studentDirectory/* /home/labDirectory/
    chmod ugo+r+w /home/labDirectory/*
    echo "Done" > /opt/check.txt
fi
```

### Evaluation Pattern

```bash
# evaluate.sh entry point
cd /home/.evaluationScripts/.bodhiFiles
cp /home/labDirectory/answer.txt ./
python3 autograder.py
# Generates evaluate.json
```

### JSON Output Format

```json
{
  "data": [
    {
      "testid": 1,
      "status": "success",
      "score": 1,
      "maximum marks": 1,
      "message": "Test passed successfully"
    }
  ]
}
```

---

*End of Document*

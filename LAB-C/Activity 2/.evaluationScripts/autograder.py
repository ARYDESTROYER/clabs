#!/usr/bin/env python3
"""Activity 2 Autograder: Intermediate AXFR Challenge (30 marks)"""

import os
import json

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{4xfr_3num3r4t10n_m4st3r}"
# Sensitive internal hosts (ones in 10.x.x.x range, excluding intranet which is semi-public)
EXPECTED_HOSTS = {"hr-portal", "payroll-db", "admin-panel", "backup-nas"}
EXPECTED_A_COUNT = 11  # ns1, www, mail, vpn, ftp, intranet, hr-portal, payroll-db, admin-panel, backup-nas, legacy-app

results = {"data": []}

# ── Test 1: Flag from zone transfer (15 marks) ──
test1 = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 15,
    "message": "Flag not found or incorrect."
}

try:
    if os.path.exists("/tmp/submit_flag.txt"):
        with open("/tmp/submit_flag.txt", 'r') as f:
            answer = f.read().strip()
        if answer == EXPECTED_FLAG:
            test1["status"] = "success"
            test1["score"] = 15
            test1["message"] = "Correct! You found the hidden flag in the zone."
        else:
            test1["message"] = "Incorrect flag. Look carefully through all TXT records in the zone transfer output."
    else:
        test1["message"] = "SUBMIT_FLAG.txt not found."
except Exception as e:
    test1["message"] = f"Error: {str(e)}"

results["data"].append(test1)

# ── Test 2: Identify sensitive internal hosts (10 marks) ──
test2 = {
    "testid": 2,
    "status": "failure",
    "score": 0,
    "maximum marks": 10,
    "message": "Sensitive hosts not identified correctly."
}

try:
    if os.path.exists("/tmp/submit_hosts.txt"):
        with open("/tmp/submit_hosts.txt", 'r') as f:
            content = f.read().strip().lower()

        # Parse: accept comma-separated, newline-separated, space-separated
        # Strip .corp.internal suffix if present
        submitted = set()
        for token in content.replace(',', ' ').replace('\n', ' ').split():
            token = token.strip().strip('.')
            token = token.replace('.corp.internal', '')
            if token:
                submitted.add(token)

        matched = submitted & EXPECTED_HOSTS
        if matched == EXPECTED_HOSTS:
            test2["status"] = "success"
            test2["score"] = 10
            test2["message"] = "Correct! You identified all sensitive internal hosts."
        elif len(matched) >= 3:
            test2["score"] = 7
            test2["message"] = f"Partial credit: Found {len(matched)}/4 sensitive hosts. Missing: {', '.join(EXPECTED_HOSTS - matched)}"
        elif len(matched) >= 1:
            test2["score"] = 3
            test2["message"] = f"Partial credit: Found {len(matched)}/4. Look for hosts in the 10.10.x.x range."
        else:
            test2["message"] = "No correct hosts identified. Look for A records pointing to internal (10.x.x.x) IP ranges."
    else:
        test2["message"] = "SUBMIT_HOSTS.txt not found."
except Exception as e:
    test2["message"] = f"Error: {str(e)}"

results["data"].append(test2)

# ── Test 3: Count of A records (5 marks) ──
test3 = {
    "testid": 3,
    "status": "failure",
    "score": 0,
    "maximum marks": 5,
    "message": "Count not found or incorrect."
}

try:
    if os.path.exists("/tmp/submit_count.txt"):
        with open("/tmp/submit_count.txt", 'r') as f:
            answer = f.read().strip()
        try:
            count = int(answer)
            if count == EXPECTED_A_COUNT:
                test3["status"] = "success"
                test3["score"] = 5
                test3["message"] = f"Correct! There are {EXPECTED_A_COUNT} unique hostnames with A records."
            elif abs(count - EXPECTED_A_COUNT) <= 1:
                test3["score"] = 3
                test3["message"] = f"Close! You said {count}, expected {EXPECTED_A_COUNT}. Count only unique hostnames with A records."
            else:
                test3["message"] = f"Incorrect count ({count}). Count unique hostnames that have A records in the zone."
        except ValueError:
            test3["message"] = "Please enter a number only."
    else:
        test3["message"] = "SUBMIT_COUNT.txt not found."
except Exception as e:
    test3["message"] = f"Error: {str(e)}"

results["data"].append(test3)

# ── Write results ──
with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

total = sum(t["score"] for t in results["data"])
max_total = sum(t["maximum marks"] for t in results["data"])
print(f"Score: {total}/{max_total}")
for t in results["data"]:
    print(f"  Test {t['testid']}: {t['message']}")

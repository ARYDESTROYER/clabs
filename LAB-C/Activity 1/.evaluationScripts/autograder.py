#!/usr/bin/env python3
"""Activity 1 Autograder: Guided DNS Tutorial (20 marks)"""

import os
import json

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{w3lc0m3_t0_dn5_z0n3s}"
EXPECTED_ANSWER = "AXFR"

results = {"data": []}

# ── Test 1: Flag from TXT record (10 marks) ──
test1 = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 10,
    "message": "Flag not found or incorrect."
}

try:
    flag_file = "/tmp/submit_flag.txt"
    if os.path.exists(flag_file):
        with open(flag_file, 'r') as f:
            answer = f.read().strip()
        if answer == EXPECTED_FLAG:
            test1["status"] = "success"
            test1["score"] = 10
            test1["message"] = "Correct! You found the hidden flag from the zone transfer."
        else:
            test1["message"] = f"Incorrect flag. Make sure you copy the exact TXT record value."
    else:
        test1["message"] = "SUBMIT_FLAG.txt not found. Please submit your answer."
except Exception as e:
    test1["message"] = f"Error: {str(e)}"

results["data"].append(test1)

# ── Test 2: What query type dumps all records? (10 marks) ──
test2 = {
    "testid": 2,
    "status": "failure",
    "score": 0,
    "maximum marks": 10,
    "message": "Answer not found or incorrect."
}

try:
    answer_file = "/tmp/submit_answer.txt"
    if os.path.exists(answer_file):
        with open(answer_file, 'r') as f:
            answer = f.read().strip().upper()
        if answer == EXPECTED_ANSWER:
            test2["status"] = "success"
            test2["score"] = 10
            test2["message"] = "Correct! AXFR (Authoritative Zone Transfer) dumps all records."
        else:
            test2["message"] = f"Incorrect. Hint: What query type did you use with dig to dump the entire zone?"
    else:
        test2["message"] = "SUBMIT_ANSWER.txt not found. Please submit your answer."
except Exception as e:
    test2["message"] = f"Error: {str(e)}"

results["data"].append(test2)

# ── Write results ──
with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

total = sum(t["score"] for t in results["data"])
max_total = sum(t["maximum marks"] for t in results["data"])
print(f"Score: {total}/{max_total}")
for t in results["data"]:
    print(f"  Test {t['testid']}: {t['message']}")

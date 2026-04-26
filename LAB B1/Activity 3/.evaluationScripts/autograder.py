#!/usr/bin/env python3
"""LAB B1 Activity 3 autograder - validates two flags, 50 points each."""

import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"

CHECKS = [
    {
        "testid": 1,
        "submission": "/tmp/flag1.txt",
        "expected": "flag=bookhaven_orders_url_encoded",
        "ok_msg": "Correct! You bypassed the naive /orders rule with URL encoding.",
        "wrong_msg": "Flag 1 does not match. The /orders bypass should give you a flag starting with 'flag=bookhaven_orders_'.",
        "missing_msg": "flag1.txt not found in /home/labDirectory.",
        "empty_msg": "flag1.txt is empty.",
    },
    {
        "testid": 2,
        "submission": "/tmp/flag2.txt",
        "expected": "flag=bookhaven_console_xou_bypass",
        "ok_msg": "Correct! You bypassed the hardened /manage rule with the X-Original-URL header.",
        "wrong_msg": "Flag 2 does not match. The /manage bypass should give you a flag starting with 'flag=bookhaven_console_'.",
        "missing_msg": "flag2.txt not found in /home/labDirectory.",
        "empty_msg": "flag2.txt is empty.",
    },
]

results = {"data": []}

for check in CHECKS:
    result = {
        "testid": check["testid"],
        "status": "failure",
        "score": 0,
        "maximum marks": 50,
        "message": check["missing_msg"],
    }
    if os.path.exists(check["submission"]):
        with open(check["submission"], "r", encoding="utf-8", errors="replace") as handle:
            answer = handle.read().strip()
        if not answer:
            result["message"] = check["empty_msg"]
        elif answer == check["expected"]:
            result["status"] = "success"
            result["score"] = 50
            result["message"] = check["ok_msg"]
        else:
            result["message"] = check["wrong_msg"]
    results["data"].append(result)

with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

total = sum(r["score"] for r in results["data"])
print(f"Score: {total}/100")
for r in results["data"]:
    print(f"  Test {r['testid']}: {r['status']} ({r['score']}/50) - {r['message']}")

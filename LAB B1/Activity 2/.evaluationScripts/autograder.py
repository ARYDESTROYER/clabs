#!/usr/bin/env python3
"""LAB B1 Activity 2 autograder - validates the WAF-bypass admin flag."""

import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
SUBMISSION = "/tmp/flag.txt"
EXPECTED = "flag=admin_breached_via_url_rewrite"

result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 100,
    "message": "Incorrect or missing flag in flag.txt.",
}

if os.path.exists(SUBMISSION):
    with open(SUBMISSION, "r", encoding="utf-8", errors="replace") as handle:
        answer = handle.read().strip()
    if answer == EXPECTED:
        result["status"] = "success"
        result["score"] = 100
        result["message"] = "Correct! You bypassed the WAF and reached the admin dashboard."
    elif answer:
        result["message"] = "Flag does not match. Make sure you copied the admin dashboard flag exactly."
    else:
        result["message"] = "flag.txt is empty. Paste the admin flag value into it."
else:
    result["message"] = "flag.txt not found in /home/labDirectory."

results = {"data": [result]}
with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

print(f"Score: {result['score']}/{result['maximum marks']}")
print(f"Message: {result['message']}")

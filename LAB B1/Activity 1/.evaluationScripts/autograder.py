#!/usr/bin/env python3
"""LAB B1 Activity 1 autograder - validates the recon flag."""

import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
SUBMISSION = "/tmp/flag.txt"
EXPECTED = "flag=juicymart_recon_complete"

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
        result["message"] = "Correct! You completed the recon and found the hidden info endpoint."
    elif answer:
        result["message"] = "Flag does not match. Make sure you copied it exactly, including the 'flag=' prefix."
    else:
        result["message"] = "flag.txt is empty. Paste the flag value into it."
else:
    result["message"] = "flag.txt not found in /home/labDirectory."

results = {"data": [result]}
with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

print(f"Score: {result['score']}/{result['maximum marks']}")
print(f"Message: {result['message']}")

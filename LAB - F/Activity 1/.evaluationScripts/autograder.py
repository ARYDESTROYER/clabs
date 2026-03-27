#!/usr/bin/env python3
import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{labf_v2_a1_manual_rebind_origin}"

result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 20,
    "message": "Incorrect or missing flag.",
}

try:
    if os.path.exists("/tmp/submit_flag.txt"):
        answer = open("/tmp/submit_flag.txt", "r", encoding="utf-8").read().strip()
        if answer == EXPECTED_FLAG:
            result["status"] = "success"
            result["score"] = 20
            result["message"] = "Correct Activity 1 token submitted."
        else:
            result["message"] = "Wrong token. Verify the manual pivot to admin-a and retry."
    else:
        result["message"] = "SUBMIT_FLAG.txt not found."
except Exception as exc:
    result["message"] = f"Evaluation error: {exc}"

with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump({"data": [result]}, handle, indent=2)

print(f"Score: {result['score']}/{result['maximum marks']}")
print(result["message"])

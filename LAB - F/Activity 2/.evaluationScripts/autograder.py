#!/usr/bin/env python3
import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{labf_v2_a2_delayed_flip_exfil}"

result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 30,
    "message": "Incorrect or missing flag.",
}

try:
    if os.path.exists("/tmp/submit_flag.txt"):
        answer = open("/tmp/submit_flag.txt", "r", encoding="utf-8").read().strip()
        if answer == EXPECTED_FLAG:
            result["status"] = "success"
            result["score"] = 30
            result["message"] = "Correct Activity 2 token submitted."
        else:
            result["message"] = "Wrong token. Confirm delayed flip and exfil flow."
    else:
        result["message"] = "SUBMIT_FLAG.txt not found."
except Exception as exc:
    result["message"] = f"Evaluation error: {exc}"

with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump({"data": [result]}, handle, indent=2)

print(f"Score: {result['score']}/{result['maximum marks']}")
print(result["message"])

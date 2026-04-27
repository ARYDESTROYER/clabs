#!/usr/bin/env python3
# LAB F Activity 1 autograder.
# Writes to /tmp/evaluate.json (Section 7.7 of BODHILABS guide).

import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
SUBMISSION = "/tmp/flag.txt"
EXPECTED_FLAG = "IITB{labf_a1_threat_model_mapped}"

result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 100,
    "message": "flag.txt is missing or contains the wrong value.",
}

try:
    if os.path.exists(SUBMISSION):
        submitted = open(SUBMISSION, "r", encoding="utf-8").read().strip()
        if submitted == EXPECTED_FLAG:
            result["status"] = "success"
            result["score"] = 100
            result["message"] = "Correct. You enumerated the threat model and read FLAG1."
        elif submitted:
            result["message"] = "That flag is not correct. Re-read /admin/welcome from inside the container."
        else:
            result["message"] = "flag.txt is empty. Paste FLAG1 into it and click Evaluate."
    else:
        result["message"] = "flag.txt not found in /home/labDirectory."
except Exception as exc:
    result["message"] = "Evaluator error: {}".format(exc)

with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
    json.dump({"data": [result]}, fh, indent=2)

print("Score: {}/{}".format(result["score"], result["maximum marks"]))
print("Message: {}".format(result["message"]))

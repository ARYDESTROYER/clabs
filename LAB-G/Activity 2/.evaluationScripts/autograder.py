#!/usr/bin/env python3
import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{labg_a2_stored_xss_triggered}"

results = {"data": []}

checks = [
    {
        "testid": 1,
        "maximum marks": 50,
        "file": "/tmp/xss-payload.txt",
        "validator": lambda s: any(x in s.lower() for x in ["onerror=", "onload=", "<svg", "<img"]),
        "ok": "Payload has event-handler style execution vector.",
        "fail": "Payload should include a practical event-handler vector (e.g., onerror/onload).",
    },
    {
        "testid": 2,
        "maximum marks": 50,
        "file": "/tmp/flag.txt",
        "validator": lambda s: s.strip() == EXPECTED_FLAG,
        "ok": "Correct FLAG2 submitted.",
        "fail": "Incorrect FLAG2.",
    },
]

for item in checks:
    result = {
        "testid": item["testid"],
        "status": "failure",
        "score": 0,
        "maximum marks": item["maximum marks"],
        "message": item["fail"],
    }
    path = item["file"]
    if os.path.exists(path):
        data = open(path, "r", encoding="utf-8").read().strip()
        if item["validator"](data):
            result["status"] = "success"
            result["score"] = item["maximum marks"]
            result["message"] = item["ok"]
    else:
        result["message"] = f"Missing required file: {os.path.basename(path)}"
    results["data"].append(result)

with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

score = sum(x["score"] for x in results["data"])
max_score = sum(x["maximum marks"] for x in results["data"])
print(f"Score: {score}/{max_score}")

#!/usr/bin/env python3
import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
EXPECTED_FLAG = "IITB{labg_a1_scan_surface_mapped}"

results = {"data": []}

checks = [
    {
        "testid": 1,
        "maximum marks": 30,
        "file": "/tmp/recon.txt",
        "validator": lambda s: "/reviews" in s and "/products" in s and "/hidden/scan-checkpoint" in s,
        "ok": "Recon file includes key endpoints.",
        "fail": "Recon should mention /reviews, /products, and /hidden/scan-checkpoint.",
    },
    {
        "testid": 2,
        "maximum marks": 30,
        "file": "/tmp/zap-findings.txt",
        "validator": lambda s: "xss" in s.lower() and ("stored" in s.lower() or "cross" in s.lower()),
        "ok": "ZAP findings indicate relevant XSS observations.",
        "fail": "zap-findings.txt should mention stored XSS style finding details.",
    },
    {
        "testid": 3,
        "maximum marks": 40,
        "file": "/tmp/flag.txt",
        "validator": lambda s: s.strip() == EXPECTED_FLAG,
        "ok": "Correct FLAG1 submitted.",
        "fail": "Incorrect FLAG1.",
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

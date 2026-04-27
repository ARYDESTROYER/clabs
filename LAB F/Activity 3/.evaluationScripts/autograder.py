#!/usr/bin/env python3
# LAB F Activity 3 autograder. Same two-part shape as Activity 2.

import json
import os

OUTPUT_JSON = "/tmp/evaluate.json"
SUBMISSION = "/tmp/flag.txt"
EVENTS_FILE = "/tmp/labf_events.json"
EXPECTED_FLAG = "IITB{labf_a3_independent_pwn_complete}"

results = {"data": []}

t1 = {"testid": 1, "status": "failure", "score": 0, "maximum marks": 50,
      "message": "flag.txt is missing or wrong."}
try:
    if os.path.exists(SUBMISSION):
        submitted = open(SUBMISSION, "r", encoding="utf-8").read().strip()
        if submitted == EXPECTED_FLAG:
            t1["status"] = "success"
            t1["score"] = 50
            t1["message"] = "flag.txt matches FLAG3."
        elif submitted:
            t1["message"] = "flag.txt does not match the expected secret."
        else:
            t1["message"] = "flag.txt is empty."
    else:
        t1["message"] = "flag.txt not found in /home/labDirectory."
except Exception as exc:
    t1["message"] = "Evaluator error in test 1: {}".format(exc)
results["data"].append(t1)

t2 = {"testid": 2, "status": "failure", "score": 0, "maximum marks": 50,
      "message": "No bot exfiltration of FLAG3 found in event log."}
try:
    if os.path.exists(EVENTS_FILE):
        events = json.load(open(EVENTS_FILE, "r", encoding="utf-8"))
        exfils = [e for e in events if e.get("kind") == "bot_exfil"]
        leaked = any(EXPECTED_FLAG in (e.get("data", {}).get("payload") or "") for e in exfils)
        if leaked:
            t2["status"] = "success"
            t2["score"] = 50
            t2["message"] = "Bot exfiltrated FLAG3 successfully."
        elif exfils:
            t2["message"] = "Bot exfiltrated something, but it did not contain FLAG3."
        else:
            t2["message"] = "No exfil events recorded."
except Exception as exc:
    t2["message"] = "Evaluator error in test 2: {}".format(exc)
results["data"].append(t2)

with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)

total = sum(t["score"] for t in results["data"])
maxs = sum(t["maximum marks"] for t in results["data"])
print("Score: {}/{}".format(total, maxs))
for t in results["data"]:
    print("Test {} [{}]: {}".format(t["testid"], t["status"], t["message"]))

#!/usr/bin/env python3
"""Activity 3 Autograder: Advanced DNS Tunneling Detection (50 marks)"""

import os
import json

OUTPUT_JSON = "/tmp/evaluate.json"

EXPECTED_DOMAIN = "bad.exfil-dns.local"
EXPECTED_SECRET = "IITB{dn5_tunn3l_d4t4_3xf1ltr4t3d_succ3ssfully}"

# Compute expected tunnel count from the secret
_hex = EXPECTED_SECRET.encode().hex()
_chunk_size = 12
EXPECTED_TUNNEL_COUNT = len([_hex[i:i+_chunk_size] for i in range(0, len(_hex), _chunk_size)])

results = {"data": []}

# ── Test 1: Identify the malicious domain (15 marks) ──
test1 = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 15,
    "message": "Malicious domain not identified."
}

try:
    if os.path.exists("/tmp/submit_domain.txt"):
        with open("/tmp/submit_domain.txt", 'r') as f:
            answer = f.read().strip().lower().rstrip('.')

        if answer == EXPECTED_DOMAIN or answer == EXPECTED_DOMAIN.rstrip('.'):
            test1["status"] = "success"
            test1["score"] = 15
            test1["message"] = f"Correct! The tunneling domain is {EXPECTED_DOMAIN}"
        elif "exfil" in answer or "bad" in answer:
            test1["score"] = 5
            test1["message"] = "Partially correct. Include the full domain name (e.g., subdomain.example.com)"
        else:
            test1["message"] = "Incorrect. Filter for TXT queries and look for a domain that appears many times with unusual subdomains."
    else:
        test1["message"] = "SUBMIT_DOMAIN.txt not found."
except Exception as e:
    test1["message"] = f"Error: {str(e)}"

results["data"].append(test1)

# ── Test 2: Decoded exfiltrated secret (25 marks) ──
test2 = {
    "testid": 2,
    "status": "failure",
    "score": 0,
    "maximum marks": 25,
    "message": "Secret not decoded correctly."
}

try:
    if os.path.exists("/tmp/submit_secret.txt"):
        with open("/tmp/submit_secret.txt", 'r') as f:
            answer = f.read().strip()

        if answer == EXPECTED_SECRET:
            test2["status"] = "success"
            test2["score"] = 25
            test2["message"] = "Excellent! You decoded the exfiltrated data."
        elif "IITB{" in answer and "}" in answer:
            test2["score"] = 10
            test2["message"] = "You're close — the flag format is right but the content doesn't match exactly."
        elif answer.startswith("IITB"):
            test2["score"] = 5
            test2["message"] = "Partial credit. You identified it's a flag but the decoding is incomplete."
        else:
            test2["message"] = "Incorrect. Extract the hex subdomains from the tunneling queries, concatenate them in order, and decode with: echo '<hex>' | xxd -r -p"
    else:
        test2["message"] = "SUBMIT_SECRET.txt not found."
except Exception as e:
    test2["message"] = f"Error: {str(e)}"

results["data"].append(test2)

# ── Test 3: Count tunneling queries (10 marks) ──
test3 = {
    "testid": 3,
    "status": "failure",
    "score": 0,
    "maximum marks": 10,
    "message": "Tunnel query count not found or incorrect."
}

try:
    if os.path.exists("/tmp/submit_tunnel_count.txt"):
        with open("/tmp/submit_tunnel_count.txt", 'r') as f:
            answer = f.read().strip()
        try:
            count = int(answer)
            if count == EXPECTED_TUNNEL_COUNT:
                test3["status"] = "success"
                test3["score"] = 10
                test3["message"] = f"Correct! There are {EXPECTED_TUNNEL_COUNT} tunneling queries."
            elif abs(count - EXPECTED_TUNNEL_COUNT) <= 1:
                test3["score"] = 5
                test3["message"] = f"Close! You said {count}, expected {EXPECTED_TUNNEL_COUNT}."
            else:
                test3["message"] = f"Incorrect ({count}). Count only the DNS queries that are part of the tunneling to the malicious domain."
        except ValueError:
            test3["message"] = "Please enter a number only."
    else:
        test3["message"] = "SUBMIT_TUNNEL_COUNT.txt not found."
except Exception as e:
    test3["message"] = f"Error: {str(e)}"

results["data"].append(test3)

# ── Write results ──
with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

total = sum(t["score"] for t in results["data"])
max_total = sum(t["maximum marks"] for t in results["data"])
print(f"Score: {total}/{max_total}")
for t in results["data"]:
    print(f"  Test {t['testid']}: {t['message']}")

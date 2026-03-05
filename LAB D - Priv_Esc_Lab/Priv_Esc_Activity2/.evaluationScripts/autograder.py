#!/usr/bin/env python3
import os
import json

# Configuration
FLAG_FILE = "/tmp/student_flag.txt" 
# We read from /tmp because direct write to .evaluationScripts might be blocked
EXPECTED_FLAG = "IITB{p4th_v4r_m4n1pul4t10n_succ3ss}"
OUTPUT_JSON = "/home/.evaluationScripts/evaluate.json"

results = {"data": []}
test_result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Flag incorrect or missing"
}

try:
    if os.path.exists(FLAG_FILE):
        with open(FLAG_FILE, 'r') as f:
            student_flag = f.read().strip()
        
        # Check against expected flag
        if student_flag == EXPECTED_FLAG:
            test_result["status"] = "success"
            test_result["score"] = 1
            test_result["message"] = "Privilege escalation successful! Correct flag."
        else:
            test_result["message"] = f"Incorrect flag. Ensure you have root access and read /root/flag.txt."
    else:
        test_result["message"] = f"File {FLAG_FILE} not found. Please paste the flag into this file."

except Exception as e:
    test_result["message"] = f"Error reading submission: {str(e)}"

results["data"].append(test_result)

with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

# Print summary for the console output
print(f"Score: {test_result['score']}/1")

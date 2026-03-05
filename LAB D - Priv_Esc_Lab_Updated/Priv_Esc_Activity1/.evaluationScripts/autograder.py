#!/usr/bin/env python3
import os
import json

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Where we read student submission from (copied by evaluate.sh)
SUBMISSION_FILE = "/tmp/student_suid_names.txt"

# The 3 expected suspicious SUID binary basenames
EXPECTED_NAMES = {"sysmonitor", "logrotate_s", "envcheck"}

# Output file (LMS reads this)
OUTPUT_JSON = "/home/.evaluationScripts/evaluate.json"

# ═══════════════════════════════════════════════════════════════════════════
# EVALUATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

results = {"data": []}

test_result = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Incorrect or missing submission"
}

try:
    if os.path.exists(SUBMISSION_FILE):
        with open(SUBMISSION_FILE, 'r') as f:
            raw_lines = f.readlines()

        # Parse student answers:
        # - Strip whitespace from each line
        # - Skip blank lines and placeholder text
        # - Extract basename (handles both "sysmonitor" and "/usr/local/bin/sysmonitor")
        student_names = set()
        for line in raw_lines:
            name = line.strip()
            if not name or name.startswith("("):
                continue
            # Extract basename in case student wrote full path
            basename = os.path.basename(name)
            if basename:
                student_names.add(basename.lower())

        # Normalize expected names to lowercase for comparison
        expected_lower = {n.lower() for n in EXPECTED_NAMES}

        # All-or-nothing: student must have ALL 3 correct names
        found = student_names & expected_lower
        missing = expected_lower - student_names

        if missing:
            # Not all found — do NOT reveal which ones are correct/missing
            test_result["message"] = (
                f"Incomplete. You identified {len(found)}/3 suspected binaries. "
                f"Review your enumeration and try again."
            )
        else:
            # All 3 found — success!
            test_result["status"] = "success"
            test_result["score"] = 1
            test_result["message"] = "Excellent! You correctly identified all 3 suspected SUID binaries."
    else:
        test_result["message"] = (
            "Submission file not found. "
            "Please write the names into SUBMIT_SUID_NAMES.txt and click Evaluate."
        )

except Exception as e:
    test_result["message"] = f"Error during evaluation: {str(e)}"

results["data"].append(test_result)

# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT RESULTS
# ═══════════════════════════════════════════════════════════════════════════

with open(OUTPUT_JSON, 'w') as f:
    json.dump(results, f, indent=2)

# Print summary (shown in terminal)
print(f"Score: {test_result['score']}/{test_result['maximum marks']}")
print(f"Message: {test_result['message']}")

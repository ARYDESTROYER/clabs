#!/usr/bin/python3
import json, os, copy, subprocess, time
from datetime import datetime

# Constants
lab_dir = "/home/labDirectory"
jsonPath = "/home/.evaluationScripts/evaluate.json"
expected_txt_path = "/tmp/expected_combined.txt"
answer_path = os.path.join(lab_dir, "answer.txt")
combined_txt = "combined.txt"
expected_files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "combined.txt"]
X_time = "2024-06-15 14:00:00"  # expected mtime
Y_time = "2024-06-15 10:00:00"  # expected atime

# Parse expected times to epoch (localtime interpretation, same as `touch -d`)
def to_epoch(ts_str):
    return int(time.mktime(time.strptime(ts_str, "%Y-%m-%d %H:%M:%S")))

X_epoch = to_epoch(X_time)
Y_epoch = to_epoch(Y_time)

# Result structure
overall = {"data": []}
template = {
    "testid": 0,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

def add_result(testid, passed, message):
    entry = copy.deepcopy(template)
    entry["testid"] = testid
    entry["message"] = message
    entry["status"] = "success" if passed else "failure"
    entry["score"] = 1 if passed else 0
    overall["data"].append(entry)

def safe_read_lines(path):
    # Try to avoid atime updates; if not supported, fall back to normal open
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    except (PermissionError, AttributeError, OSError):
        fd = os.open(path, os.O_RDONLY)
    with os.fdopen(fd, 'r') as f:
        return f.readlines()

# Step 1: Move to lab directory
os.chdir(lab_dir)
testid = 1

# Step 2: Run the student's commands from answer.txt
if os.path.exists(answer_path):
    try:
        subprocess.run(f"bash {answer_path}", shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError:
        with open(jsonPath, 'w') as f:
            json.dump(overall, f, indent=4)
        exit(1)
else:
    with open(jsonPath, 'w') as f:
        json.dump(overall, f, indent=4)
    exit(1)

# Test 1: Check all required files exist
missing_files = [f for f in expected_files if not os.path.isfile(f)]
add_result(testid, not missing_files,
           f"Missing files: {', '.join(missing_files)}" if missing_files else "All required files are present")
testid += 1

# Test 2: Check for newline in one of the first 3 files
newline_found = False
for f in ["file1.txt", "file2.txt", "file3.txt"]:
    try:
        lines = safe_read_lines(f)
        if len(lines) > 1:
            newline_found = True
            break
    except:
        pass
add_result(testid, newline_found, "One file has a newline" if newline_found else "No newline found in any file")
testid += 1

# ---------- IMPORTANT: Timestamp check BEFORE any read of combined.txt ----------
# Test 3: Timestamp check (compare epoch seconds; do this before reading combined.txt)
try:
    stat_info = os.stat(combined_txt)
    atime_epoch = int(stat_info.st_atime)
    mtime_epoch = int(stat_info.st_mtime)
    passed = (atime_epoch == Y_epoch and mtime_epoch == X_epoch)
    msg = (f"Timestamps correct (Modify={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime_epoch))}, "
           f"Access={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(atime_epoch))})"
           if passed else
           f"Timestamps incorrect (Modify={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime_epoch))}, "
           f"Access={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(atime_epoch))})")
    add_result(testid, passed, msg)
except Exception as e:
    add_result(testid, False, f"Error checking timestamps: {e}")
testid += 1
# ------------------------------------------------------------------------------

# Test 4: No consecutive blank lines in combined.txt (cat -s behavior)
try:
    lines = safe_read_lines("combined.txt")
    consecutive_blank = False
    prev_blank = False
    for line in lines:
        if line.strip() == '':
            if prev_blank:
                consecutive_blank = True
                break
            prev_blank = True
        else:
            prev_blank = False
    add_result(testid, not consecutive_blank,
               "No consecutive blank lines in combined.txt" if not consecutive_blank else "Consecutive blank lines found")
except Exception as e:
    add_result(testid, False, f"Error checking blank lines: {e}")
testid += 1

# Test 5: Content match using cat -s semantics (allow single blank, disallow consecutive)
try:
    with open(expected_txt_path, 'w') as out:
        prev_blank = False
        for f in ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]:
            with open(f, 'r') as infile:
                for line in infile:
                    if line.strip() == '':
                        if not prev_blank:  # keep a single blank
                            out.write(line)
                        prev_blank = True
                    else:
                        out.write(line)
                        prev_blank = False
    expected = safe_read_lines(expected_txt_path)
    actual = safe_read_lines("combined.txt")
    passed = expected == actual
    msg = "combined.txt content matches expected (cat -s behavior)" if passed else "combined.txt content mismatch"
    add_result(testid, passed, msg)
except Exception as e:
    add_result(testid, False, f"Error comparing content: {e}")
testid += 1

# Final: Write and print results
with open(jsonPath, 'w') as f:
    json.dump(overall, f, indent=4)

with open(jsonPath, 'r') as f:
    print(f.read())


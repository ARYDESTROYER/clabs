#!/usr/bin/python3
import json, os, subprocess, copy

os.system('clear')

# Evaluation result template
overall = {
    "data": []
}

template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

# Paths
path = '/home/.evaluationScripts/'
inputFile = '/home/labDirectory/answer.txt'
jsonPath = path + 'evaluate.json'
backup_file = '/tmp/mystery_file_backup'

# Get correct MIME type using 'file --mime-type'
try:
    correct_mime = subprocess.check_output(
        ['file', '--mime-type', '-b', backup_file],
        text=True
    ).strip()
except Exception as e:
    correct_mime = None

# Evaluation logic
entry = copy.deepcopy(template)
entry["testid"] = 1

if not correct_mime:
    entry["message"] = "Failed to determine correct MIME type of file."
else:
    if os.path.isfile(inputFile):
        with open(inputFile, 'r') as f:
            student_command = f.read().strip()

        if student_command:
            try:
                # Run student's command in the lab directory
                student_output = subprocess.check_output(
                    student_command,
                    shell=True,
                    cwd='/home/labDirectory',
                    text=True
                ).strip()

                # Check if correct MIME type appears in student's output
                if correct_mime in student_output:
                    entry["message"] = f"PASS: MIME type '{correct_mime}' found."
                    entry["status"] = "success"
                    entry["score"] = 1
                else:
                    entry["message"] = f"FAIL: MIME type not found."
            except subprocess.CalledProcessError as e:
                entry["message"] = f"FAIL: Error running student's command: {e}"
        else:
            entry["message"] = "FAIL: answer.txt is empty."
    else:
        entry["message"] = "FAIL: answer.txt not found."

overall["data"].append(entry)

# Save results
with open(jsonPath, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

# Display results
with open(jsonPath, 'r', encoding='utf-8') as f:
    print(f.read())

#!/usr/bin/python3
import json, os, copy, subprocess, filecmp

# Clear terminal (optional)
os.system('clear')

# Common result structure
overall = {"data": []}
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

# Paths
base_path = '/home/.evaluationScripts/'
input_file = base_path + '.bodhiFiles/answer.txt'
json_path = base_path + 'evaluate.json'
lab_path = '/home/labDirectory'
expected_output_file = os.path.join(lab_path, 'expected.txt')
student_output_file = os.path.join(lab_path, 'output.txt')  # students must redirect here
backup_file = '/tmp/mystery_file_backup'

# Prepare template function
def add_result(testid, passed, message):
    entry = copy.deepcopy(template)
    entry["testid"] = testid
    entry["status"] = "success" if passed else "failure"
    entry["score"] = 1 if passed else 0
    entry["message"] = message
    overall["data"].append(entry)

# --------------------------
# TEST 1: head/tail check
# --------------------------
testid = 1
try:
    # Generate expected output safely
    subprocess.run(
        f"cd {lab_path} && head -n 50 example.txt | tail -n 10 > expected.txt",
        shell=True,
        executable="/bin/sh",  # Use sh for compatibility
        check=True
    )
except subprocess.CalledProcessError as e:
    add_result(testid, False, f"Error generating expected output: {e}")
else:
    if os.path.isfile(input_file):
        with open(input_file, 'r') as f:
            student_commands = [line.strip() for line in f if line.strip()]

        if student_commands:
            combined_script = " && ".join(student_commands)
            try:
                subprocess.run(
                    f"cd {lab_path} && {combined_script}",
                    shell=True,
                    executable="/bin/sh",
                    check=True
                )

                if not os.path.isfile(student_output_file):
                    add_result(testid, False, "output.txt not created")
                else:
                    if filecmp.cmp(expected_output_file, student_output_file, shallow=False):
                        add_result(testid, True, "PASS: Output matches expected")
                    else:
                        add_result(testid, False, "FAIL: Output mismatch")
            except subprocess.CalledProcessError as e:
                add_result(testid, False, f"FAIL: Error executing student's command: {e}")
        else:
            add_result(testid, False, "answer.txt is empty")
    else:
        add_result(testid, False, "answer.txt not found")
testid += 1

# --------------------------
# TEST 2: MIME type check
# --------------------------
try:
    correct_mime = subprocess.check_output(
        ['file', '--mime-type', '-b', backup_file],
        text=True
    ).strip()
except Exception as e:
    correct_mime = None

if correct_mime:
    if os.path.isfile(input_file):
        with open(input_file, 'r') as f:
            student_command = f.read().strip()

        if student_command:
            try:
                student_output = subprocess.check_output(
                    student_command,
                    shell=True,
                    cwd=lab_path,
                    executable="/bin/sh",
                    text=True
                ).strip()

                if correct_mime in student_output:
                    add_result(testid, True, f"PASS: MIME type '{correct_mime}' found")
                else:
                    add_result(testid, False, "FAIL: MIME type not found in output")
            except subprocess.CalledProcessError as e:
                add_result(testid, False, f"FAIL: Error running student's command: {e}")
        else:
            add_result(testid, False, "answer.txt is empty for MIME check")
    else:
        add_result(testid, False, "answer.txt not found for MIME check")
else:
    add_result(testid, False, "Failed to determine correct MIME type")
testid += 1

# Save results
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

# Print results
with open(json_path, 'r', encoding='utf-8') as f:
    print(f.read())


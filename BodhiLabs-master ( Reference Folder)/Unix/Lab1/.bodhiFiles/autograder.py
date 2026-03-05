#!/usr/bin/python3
import json, os, copy, subprocess

os.system('clear')

# The data structure for final results to be stored in evaluate.json
overall = {
    "data": []
}

# Template for evaluation entries
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

path = '/home/.evaluationScripts/.bodhiFiles/'
command_file = path + 'command.txt'
filename_file = path + 'filename.txt'
json_path = path + 'evaluate.json'
go_to_work_dir = "cd /home/labDirectory/explore_this && "

# Define the correct commands
correct_commands = [
    "ls -lRaS",  # Task 1: List all files (including hidden) recursively, sorted by size
    "ls -lR | grep ^- | sort -k 5 -nr | head -n 1 | awk '{print $NF}'" # Task 2: Get the largest file
]

# Run correct commands to get expected outputs
correct_outputs = []
try:
    for command in correct_commands:
        command = go_to_work_dir + command
        output = subprocess.check_output(command, shell=True, text=True).strip()
        correct_outputs.append(output)
except Exception as e:
    correct_outputs.append("")
    print("Error running correct command:", e)

# Task 1: Check command.txt
if os.path.isfile(command_file):
    with open(command_file, 'r') as file:
        lines = file.readlines()
        student_command = lines[0].strip() if lines else ""

    entry = copy.deepcopy(template)
    entry["testid"] = 0
    try:
        student_cmd = go_to_work_dir + student_command
        student_output = subprocess.check_output(student_cmd, shell=True, text=True).strip()
        if student_output == correct_outputs[0]:
            entry["message"] = f"{student_command}: PASS - Correctly lists all files recursively, sorted by size"
            entry["score"] = 1
            entry["status"] = "success"
        else:
            entry["message"] = f"{student_command}: FAIL - Output mismatch for recursive listing"
    except subprocess.CalledProcessError as e:
        entry["message"] = f"{student_command}: FAIL - Command not found or failed to execute"
    overall["data"].append(entry)
else:
    entry = copy.deepcopy(template)
    entry["testid"] = 0
    entry["message"] = "command.txt not found. Task 1 evaluation not generated."
    overall["data"].append(entry)

# Task 2: Check filename.txt and verify largest file
if os.path.isfile(filename_file):
    with open(filename_file, 'r') as file:
        student_filename = file.read().strip()

    entry = copy.deepcopy(template)
    entry["testid"] = 1
    try:
        # Parse the largest file name from the correct command output
        largest_file_line = correct_outputs[1].split('\n')[0]  # Get first line of largest file output
        largest_file_name = largest_file_line.split()[-1]  # Extract file name (last column)
        # If the file is in a subdirectory, include the path relative to explore_this
        if '/' in largest_file_name:
            largest_file_name = largest_file_name.split('/', 1)[1]  # Remove './' prefix
        if student_filename == largest_file_name:
            entry["message"] = f"{student_filename}: PASS - Correctly identified largest file"
            entry["score"] = 1
            entry["status"] = "success"
        else:
            entry["message"] = f"{student_filename}: FAIL - Incorrect file name"
    except Exception as e:
        entry["message"] = f"FAIL - Error processing largest file: {str(e)}"
    overall["data"].append(entry)
else:
    entry = copy.deepcopy(template)
    entry["testid"] = 1
    entry["message"] = "filename.txt not found. Task 2 evaluation not generated."
    overall["data"].append(entry)

# Store evaluation results
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

# Show evaluation results
with open(json_path, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        print(line)

os.remove(json_path)
if os.path.isfile(command_file):
    os.remove(command_file)
if os.path.isfile(filename_file):
    os.remove(filename_file)

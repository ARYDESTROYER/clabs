#!/usr/bin/python3
import json, os, copy, subprocess, shutil

# --- JSON Output Setup ---
overall = {"data": []}
template = {
    "testid": 1, "status": "failure", "score": 0,
    "maximum marks": 0.5, "message": "Autograder Failed!"
}

# --- Path Setup ---
BASE_PATH = '/home/.evaluationScripts/'
STUDENT_PATH = '/home/labDirectory/'
ANSWER_FILE = os.path.join(STUDENT_PATH, 'part-1', 'answer-1.txt')
JSON_PATH = os.path.join(BASE_PATH, 'evaluate.json')
SANDBOX_DIR = os.path.join(BASE_PATH, 'test_sandbox')

# --- Paths relative to sandbox ---
PROJECT_DIR = os.path.join(SANDBOX_DIR, 'project_files')
SRC_DIR = os.path.join(PROJECT_DIR, 'src')
DOCS_DIR = os.path.join(PROJECT_DIR, 'docs')
README_IN_ROOT = os.path.join(PROJECT_DIR, 'readme.txt')
README_IN_DOCS = os.path.join(DOCS_DIR, 'readme.txt')

def setup_environment():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(SANDBOX_DIR)

def final_cleanup():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    # if os.path.isfile(ANSWER_FILE):
        # os.remove(ANSWER_FILE)
    # if os.path.isfile(JSON_PATH):
    #     os.remove(JSON_PATH)

def run_commands(command_list):
    """Helper to run a list of commands."""
    for command in command_list:
        cmd_stripped = command.strip()
        if not cmd_stripped or cmd_stripped.startswith('#'):
            continue
        subprocess.run(
            cmd_stripped, shell=True, cwd=SANDBOX_DIR, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

# --- Task Check Functions ---
def check_task_1():
    return os.path.isdir(PROJECT_DIR)

def check_task_2():
    return os.path.isdir(SRC_DIR) and os.path.isdir(DOCS_DIR)

def check_task_3():
    return os.path.isfile(README_IN_ROOT)

def check_task_4():
    # Task 4: readme.txt moved to docs (exists in docs, NOT in root)
    return os.path.isfile(README_IN_DOCS) and not os.path.exists(README_IN_ROOT)

def main():
    setup_environment()
    
    # Initialize results for all tasks as failure
    results = []
    
    # Task definitions
    tasks = [
        {
            "id": 1,
            "check": check_task_1,
            "score": 0.5,
            "message_pass": "PASS: Task 1- project_files directory created.",
            "message_fail": "FAIL: project_files directory not created.",
            "status": "failure"
        },
        {
            "id": 2,
            "check": check_task_2,
            "score": 0.5,
            "message_pass": "PASS: Task 2- src and docs directories created.",
            "message_fail": "FAIL: src and/or docs directories not created.",
            "status": "failure"
        },
        {
            "id": 3,
            "check": check_task_3,
            "score": 0.5,
            "message_pass": "PASS: Task 3- readme.txt created in project_files root.",
            "message_fail": "FAIL: readme.txt not created in project_files root.",
            "status": "failure"
        },
        {
            "id": 4,
            "check": check_task_4,
            "score": 0.5,
            "message_pass": "PASS: Task 4 (move) correct.",
            "message_fail": "FAIL: readme.txt not found in docs or still exists in root.",
            "status": "failure"
        }
    ]

    if not os.path.isfile(ANSWER_FILE):
        for i in range(len(tasks)):
            entry = copy.deepcopy(template)
            entry["testid"] = tasks[i]["id"]
            entry["message"] = "FAIL: part-1/answer.txt not found."
            overall["data"].append(entry)
    else:
        with open(ANSWER_FILE, 'r') as f:
            # Read all lines, strip whitespace, ignore comments and empty lines
            all_commands = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
        
        if not all_commands:
            for i in range(len(tasks)):
                entry = copy.deepcopy(template)
                entry["testid"] = tasks[i]["id"]
                entry["message"] = "FAIL: No commands found in part-1/answer.txt."
                overall["data"].append(entry)
        else:
            current_task_idx = 0
            
            # Execute commands one by one
            for cmd in all_commands:
                # Stop if all tasks are already done
                if current_task_idx >= len(tasks):
                    break
                
                try:
                    # Run the command
                    run_commands([cmd])
                    
                    # Check if the CURRENT task is satisfied
                    # We loop here to handle cases where one command might satisfy multiple tasks (unlikely but robust)
                    # or if we want to check the next task immediately.
                    # Actually, just checking the current one is safer.
                    
                    while current_task_idx < len(tasks):
                        task = tasks[current_task_idx]
                        if task["check"]():
                            # Task passed!
                            task["status"] = "success"
                            current_task_idx += 1
                        else:
                            # Current task not yet satisfied, move to next command
                            break
                            
                except subprocess.CalledProcessError as e:
                    # If a command fails, we record it but continue (maybe subsequent commands fix it? unlikely)
                    # For now, just print/log? The original script added a failure entry.
                    # We'll just let the task checks fail if the command didn't work.
                    pass

            # Generate final JSON output based on task states
            for task in tasks:
                entry = copy.deepcopy(template)
                entry["testid"] = task["id"]
                entry["maximum marks"] = task["score"]
                
                if task["status"] == "success":
                    entry["status"] = "success"
                    entry["score"] = task["score"]
                    entry["message"] = task["message_pass"]
                else:
                    entry["status"] = "failure"
                    entry["score"] = 0
                    entry["message"] = task["message_fail"]
                
                overall["data"].append(entry)

    # --- JSON Output ---
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=4)
    final_cleanup()

if __name__ == "__main__":
    main()

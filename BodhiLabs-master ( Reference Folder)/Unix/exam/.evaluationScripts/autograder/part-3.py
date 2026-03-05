#!/usr/bin/python3
import json, os, copy, subprocess, shutil

# --- JSON Output Setup ---
template = {
    "testid": 1, "status": "failure", "score": 0,
    "maximum marks": 1, "message": "Autograder Failed!"
}

# --- Path Setup ---
BASE_PATH = '/home/.evaluationScripts/'
STUDENT_PATH = '/home/labDirectory/'
ANSWER_FILE = os.path.join(STUDENT_PATH, 'part-3', 'answer-3.txt')
JSON_PATH = os.path.join(BASE_PATH, 'evaluate.json')
SANDBOX_DIR = os.path.join(BASE_PATH, 'test_sandbox_3')

# --- Paths relative to sandbox ---
PART3_DIR = os.path.join(SANDBOX_DIR, 'part-3')
ACCESS_LOG_PATH = os.path.join(PART3_DIR, 'access.log')
IP_HITS_PATH = os.path.join(PART3_DIR, 'ip_hits.txt')
USERS_LIST_PATH = os.path.join(PART3_DIR, 'users_list.txt')

def setup_environment():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(PART3_DIR)
    
    # Copy access.log from student directory to sandbox
    student_part3 = os.path.join(STUDENT_PATH, 'part-3')
    if os.path.isdir(student_part3):
        src_log = os.path.join(student_part3, 'access.log')
        if os.path.isfile(src_log):
            shutil.copy(src_log, PART3_DIR)

def final_cleanup():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)

def run_commands(command_list):
    """Helper to run a list of commands."""
    for command in command_list:
        cmd_stripped = command.strip()
        if not cmd_stripped or cmd_stripped.startswith('#'):
            continue
        subprocess.run(
            cmd_stripped, shell=True, cwd=PART3_DIR, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def get_file_lines(path):
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def check_ip_hits(log_path, hits_path, target_ip="192.168.1.5"):
    if not os.path.isfile(hits_path):
        return False, "ip_hits.txt not found."
    
    log_lines = get_file_lines(log_path)
    hits_lines = get_file_lines(hits_path)
    
    expected_lines = [line for line in log_lines if target_ip in line]
    
    if hits_lines == expected_lines:
        return True, "Content matches."
    else:
        return False, f"Content mismatch. Expected {len(expected_lines)} lines, got {len(hits_lines)}."

def check_users_list(log_path, users_path):
    if not os.path.isfile(users_path):
        return False, "users_list.txt not found."
    
    log_lines = get_file_lines(log_path)
    users_lines = get_file_lines(users_path)
    
    # Extract users (field 2, delimiter :)
    expected_users = []
    for line in log_lines:
        parts = line.split(':')
        if len(parts) >= 2:
            expected_users.append(parts[1])
            
    if users_lines == expected_users:
        return True, "Content matches."
    else:
        return False, f"Content mismatch. Expected {len(expected_users)} lines, got {len(users_lines)}."

def main():
    setup_environment()
    
    # Load existing results or start fresh
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r') as f:
            try:
                overall = json.load(f)
            except json.JSONDecodeError:
                overall = {"data": []}
    else:
        overall = {"data": []}

    # Determine next testid start
    next_id = 1
    if overall["data"]:
        next_id = max(item.get("testid", 0) for item in overall["data"]) + 1

    if not os.path.isfile(ANSWER_FILE):
        for _ in range(2):
            entry = copy.deepcopy(template)
            entry["testid"] = next_id
            entry["message"] = "FAIL: part-3/answer.txt not found."
            overall["data"].append(entry)
            next_id += 1
    else:
        with open(ANSWER_FILE, 'r') as f:
            all_commands = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
        
        if not all_commands:
            for _ in range(2):
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["message"] = "FAIL: No commands found in part-3/answer.txt."
                overall["data"].append(entry)
                next_id += 1
        else:
            # Execute all commands
            try:
                run_commands(all_commands)
            except subprocess.CalledProcessError as e:
                pass

            if not os.path.isfile(ACCESS_LOG_PATH):
                 entry = copy.deepcopy(template)
                 entry["testid"] = next_id
                 entry["message"] = "FAIL: access.log not found in sandbox."
                 overall["data"].append(entry)
            else:
                # Check Task 1: ip_hits.txt
                success, msg = check_ip_hits(ACCESS_LOG_PATH, IP_HITS_PATH)
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["maximum marks"] = 1
                if success:
                    entry["status"] = "success"
                    entry["score"] = 1
                    entry["message"] = "PASS: ip_hits.txt created correctly."
                else:
                    entry["message"] = f"FAIL: ip_hits.txt incorrect. {msg}"
                overall["data"].append(entry)
                next_id += 1

                # Check Task 2: users_list.txt
                success, msg = check_users_list(ACCESS_LOG_PATH, USERS_LIST_PATH)
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["maximum marks"] = 1
                if success:
                    entry["status"] = "success"
                    entry["score"] = 1
                    entry["message"] = "PASS: users_list.txt created correctly."
                else:
                    entry["message"] = f"FAIL: users_list.txt incorrect. {msg}"
                overall["data"].append(entry)
                next_id += 1

    # --- JSON Output ---
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=4)
    final_cleanup()

if __name__ == "__main__":
    main()

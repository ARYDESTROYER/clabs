#!/usr/bin/python3
import json, os, copy, subprocess, shutil, glob

# --- JSON Output Setup ---
template = {
    "testid": 1, "status": "failure", "score": 0,
    "maximum marks": 1, "message": "Autograder Failed!"
}

# --- Path Setup ---
BASE_PATH = '/home/.evaluationScripts/'
STUDENT_PATH = '/home/labDirectory/'
ANSWER_FILE = os.path.join(STUDENT_PATH, 'part-2', 'answer-2.txt')
JSON_PATH = os.path.join(BASE_PATH, 'evaluate.json')
SANDBOX_DIR = os.path.join(BASE_PATH, 'test_sandbox_2')

# --- Paths relative to sandbox ---
PART2_DIR = os.path.join(SANDBOX_DIR, 'part-2')

def setup_environment():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(PART2_DIR)
    
    # Copy all server_log*.txt files from student directory to sandbox
    student_part2 = os.path.join(STUDENT_PATH, 'part-2')
    if os.path.isdir(student_part2):
        log_files = glob.glob(os.path.join(student_part2, 'server_*.log'))
        for log_file in log_files:
            shutil.copy(log_file, PART2_DIR)

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
            cmd_stripped, shell=True, cwd=PART2_DIR, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def get_file_lines(path):
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def check_summary(log_path, summary_path):
    if not os.path.isfile(summary_path):
        return False, "Summary file not found."
    
    log_lines = get_file_lines(log_path)
    summary_lines = get_file_lines(summary_path)
    
    # If log has fewer than 20 lines, logic might overlap, but standard head/tail behavior applies
    expected_lines = log_lines[:10] + log_lines[-10:]
    
    if summary_lines == expected_lines:
        return True, "Content matches."
    else:
        return False, f"Content mismatch. Expected {len(expected_lines)} lines, got {len(summary_lines)}."

def check_count(log_path, count_path):
    if not os.path.isfile(count_path):
        return False, "Count file not found."
    
    log_lines = get_file_lines(log_path)
    try:
        with open(count_path, 'r') as f:
            content = f.read().strip()
            # Handle cases where wc -l output might include filename e.g. "  45 server_log1.txt"
            # We just want the number
            student_count = int(content.split()[0])
            
        if student_count == len(log_lines):
            return True, "Count matches."
        else:
            return False, f"Count mismatch. Expected {len(log_lines)}, got {student_count}."
    except Exception as e:
        return False, f"Error reading count file: {str(e)}"

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
        for i in range(4):
            entry = copy.deepcopy(template)
            entry["testid"] = next_id
            entry["message"] = "FAIL: part-2/answer.txt not found."
            entry["maximum marks"] = 1 if i % 2 == 0 else 0.5
            overall["data"].append(entry)
            next_id += 1
    else:
        with open(ANSWER_FILE, 'r') as f:
            all_commands = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
        
        if not all_commands:
            for i in range(4):
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["message"] = "FAIL: No commands found in part-2/answer.txt."
                entry["maximum marks"] = 1 if i % 2 == 0 else 0.5
                overall["data"].append(entry)
                next_id += 1
        else:
            # Execute all commands
            try:
                run_commands(all_commands)
            except subprocess.CalledProcessError as e:
                pass

            # Find all log files in the sandbox
            log_files = sorted(glob.glob(os.path.join(PART2_DIR, 'server_*.log')))
            
            if not log_files:
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["message"] = "FAIL: No server_log files found in part-2 directory."
                overall["data"].append(entry)
            else:
                for log_path in log_files:
                    filename = os.path.basename(log_path)
                    # Extract number from filename assuming format server_logN.txt
                    # Or just use the filename to construct expected output names
                    # The requirement says: "log_summary1.txt, log_summary2.txt, so on" matching "server_log1.txt, server_log2.txt"
                    # So we can replace "server_log" with "log_summary" and "log_count"
                    
                    base_name = os.path.splitext(filename)[0] # server_1
                    number_part = base_name.replace('server_', '')
                    
                    summary_filename = f"log_summary{number_part}.txt"
                    count_filename = f"log_count{number_part}.txt"
                    
                    summary_path = os.path.join(PART2_DIR, summary_filename)
                    count_path = os.path.join(PART2_DIR, count_filename)
                    
                    # Check Summary Task
                    success, msg = check_summary(log_path, summary_path)
                    entry = copy.deepcopy(template)
                    entry["testid"] = next_id
                    entry["maximum marks"] = 1
                    if success:
                        entry["status"] = "success"
                        entry["score"] = 1
                        entry["message"] = f"PASS: {summary_filename} created correctly."
                    else:
                        entry["message"] = f"FAIL: {summary_filename} incorrect. {msg}"
                    overall["data"].append(entry)
                    next_id += 1

                    # Check Count Task
                    success, msg = check_count(log_path, count_path)
                    entry = copy.deepcopy(template)
                    entry["testid"] = next_id
                    entry["maximum marks"] = 0.5
                    if success:
                        entry["status"] = "success"
                        entry["score"] = 0.5
                        entry["message"] = f"PASS: {count_filename} created correctly."
                    else:
                        entry["message"] = f"FAIL: {count_filename} incorrect. {msg}"
                    overall["data"].append(entry)
                    next_id += 1

    # --- JSON Output ---
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=4)
    final_cleanup()

if __name__ == "__main__":
    main()

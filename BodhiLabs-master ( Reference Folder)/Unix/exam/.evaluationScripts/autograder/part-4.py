#!/usr/bin/python3
import json, os, copy, subprocess, shutil, time

# --- JSON Output Setup ---
template = {
    "testid": 1, "status": "failure", "score": 0,
    "maximum marks": 1, "message": "Autograder Failed!"
}

# --- Path Setup ---
BASE_PATH = '/home/.evaluationScripts/'
STUDENT_PATH = '/home/labDirectory/'
ANSWER_FILE = os.path.join(STUDENT_PATH, 'part-4', 'answer-4.txt')
JSON_PATH = os.path.join(BASE_PATH, 'evaluate.json')
SANDBOX_DIR = os.path.join(BASE_PATH, 'test_sandbox_4')

# --- Paths relative to sandbox ---
PART4_DIR = os.path.join(SANDBOX_DIR, 'part-4')
SCRIPT_PATH = os.path.join(PART4_DIR, 'data_processor.sh')

def setup_environment():
    try:
        subprocess.run(
            "pkill -9 -f data_processor.sh",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.5)
    except:
        pass
    
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(PART4_DIR)
    
    student_part4 = os.path.join(STUDENT_PATH, 'part-4')
    if os.path.isdir(student_part4):
        src_script = os.path.join(student_part4, 'data_processor.sh')
        if os.path.isfile(src_script):
            shutil.copy(src_script, PART4_DIR)

def final_cleanup():
    if os.path.isdir(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)

def run_commands(command_list):
    for command in command_list:
        cmd_stripped = command.strip()
        if not cmd_stripped or cmd_stripped.startswith('#'):
            continue
        subprocess.run(
            cmd_stripped, shell=True, cwd=PART4_DIR, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def check_executable(path):
    return os.access(path, os.X_OK)

def main():
    setup_environment()
    
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r') as f:
            try:
                overall = json.load(f)
            except json.JSONDecodeError:
                overall = {"data": []}
    else:
        overall = {"data": []}

    next_id = 1
    if overall["data"]:
        next_id = max(item.get("testid", 0) for item in overall["data"]) + 1

    if not os.path.isfile(ANSWER_FILE):
        for i in range(3):
            entry = copy.deepcopy(template)
            entry["testid"] = next_id
            entry["message"] = "FAIL: part-4/answer-4.txt not found."
            entry["maximum marks"] = 1 if i == 2 else 0.5
            overall["data"].append(entry)
            next_id += 1

    else:
        with open(ANSWER_FILE, 'r') as f:
            all_commands = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
        
        if not all_commands:
            for i in range(3):
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["message"] = "FAIL: No commands found in part-4/answer-4.txt."
                entry["maximum marks"] = 1 if i == 2 else 0.5
                overall["data"].append(entry)
                next_id += 1

        else:
            if not os.path.isfile(SCRIPT_PATH):
                 entry = copy.deepcopy(template)
                 entry["testid"] = next_id
                 entry["message"] = "FAIL: data_processor.sh not found in sandbox."
                 overall["data"].append(entry)

            else:
                try:
                    os.chmod(SCRIPT_PATH, 0o644)
                except:
                    pass
                
                try:
                    if len(all_commands) >= 1:
                        run_commands([all_commands[0]])
                except subprocess.CalledProcessError:
                    pass

                is_exec = check_executable(SCRIPT_PATH)
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["maximum marks"] = 0.5
                if is_exec:
                    entry["status"] = "success"
                    entry["score"] = 0.5
                    entry["message"] = "PASS: data_processor.sh is executable."
                else:
                    entry["message"] = "FAIL: data_processor.sh is not executable."
                overall["data"].append(entry)
                next_id += 1

                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["maximum marks"] = 0.5
                
                background_command = None
                if len(all_commands) >= 2:
                    background_command = all_commands[1].strip()
                
                if not background_command:
                    entry["message"] = "FAIL: No background command provided."
                elif './data_processor.sh' not in background_command or '&' not in background_command:
                    entry["message"] = "FAIL: Command does not appear to run data_processor.sh in background (missing './data_processor.sh' or '&')."
                else:
                    entry["status"] = "success"
                    entry["score"] = 0.5
                    entry["message"] = "PASS: Background command is correctly formatted."
                
                overall["data"].append(entry)
                next_id += 1

                # Check Task 3: Validate the student's PID-finding command syntax
                entry = copy.deepcopy(template)
                entry["testid"] = next_id
                entry["maximum marks"] = 1
                
                # We expect the PID finding commands to be after the background command (which is at index 1)
                pid_commands = all_commands[2:]
                
                if not pid_commands:
                    entry["message"] = "FAIL: No PID-finding commands found (expected after background command)."
                    overall["data"].append(entry)
                    next_id += 1
                else:
                    # To verify, we must ensure the process is running.
                    # Start TWO processes to support all these commands:
                    # - ps -C data_processor -o pid=
                    # - ps -C data_processor.sh -o pid=
                    # - pgrep -n -f data_processor
                    # - pgrep -n -f data_processor.sh
                    proc1 = None
                    proc2 = None
                    try:
                        # Ensure it is executable
                        os.chmod(SCRIPT_PATH, 0o755)
                        
                        # Create symlink without .sh extension (for ps -C data_processor)
                        symlink1 = os.path.join(PART4_DIR, 'data_processor')
                        if os.path.exists(symlink1):
                            os.remove(symlink1)
                        os.symlink('data_processor.sh', symlink1)
                        os.chmod(symlink1, 0o755)
                        
                        # Start process 1 via symlink (appears as "data_processor")
                        proc1 = subprocess.Popen(
                            [symlink1],
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL,
                            cwd=PART4_DIR
                        )
                        pid1 = str(proc1.pid)
                        
                        # Start process 2 with original name (appears as "data_processor.sh")
                        proc2 = subprocess.Popen(
                            [SCRIPT_PATH],
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL,
                            cwd=PART4_DIR
                        )
                        pid2 = str(proc2.pid)
                        
                        time.sleep(1) # Wait for processes to be visible in ps
                        
                        # Run the student's commands via a temp script
                        temp_script_path = os.path.join(PART4_DIR, 'student_cmd.sh')
                        script_content = "#!/bin/bash\n" + "\n".join(pid_commands) + "\n"
                        try:
                            with open(temp_script_path, 'w') as f:
                                f.write(script_content)
                            os.chmod(temp_script_path, 0o755)

                            # We use a timeout to prevent hanging
                            result = subprocess.run(
                                [temp_script_path], 
                                cwd=PART4_DIR, 
                                timeout=2,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True
                            )
                            student_output = result.stdout.decode().strip()
                            
                            # Accept if output is a SINGLE PID matching either process
                            output_lines = [line.strip() for line in student_output.split('\n') if line.strip()]
                            
                            # Check if it's exactly one line with one of our PIDs
                            if len(output_lines) == 1 and output_lines[0] in [pid1, pid2]:
                                entry["status"] = "success"
                                entry["score"] = 1
                                entry["message"] = "PASS: PID-finding command correctly outputs the PID."
                            elif len(output_lines) > 1:
                                entry["message"] = f"FAIL: Commands output multiple PIDs. Expected a single PID. Use 'pgrep -n' or 'ps -C' to get only one PID. Got: '{student_output}'"
                            else:
                                entry["message"] = f"FAIL: Commands output '{student_output}' but expected PID '{pid1}' or '{pid2}'."
                                
                        except subprocess.TimeoutExpired:
                            entry["message"] = f"FAIL: Commands timed out. Script: {repr(script_content)}"
                        except subprocess.CalledProcessError as e:
                            stderr_msg = e.stderr.decode().strip() if e.stderr else ""
                            stdout_msg = e.stdout.decode().strip() if e.stdout else ""
                            entry["message"] = f"FAIL: Commands failed (Exit: {e.returncode}). Script: {repr(script_content[:100])}... Stderr: '{stderr_msg[:200]}' Stdout: '{stdout_msg[:200]}'"
                        except Exception as e:
                            entry["message"] = f"FAIL: Error executing commands: {str(e)}"
                        finally:
                            if os.path.exists(temp_script_path):
                                os.remove(temp_script_path)

                    except Exception as e:
                        entry["message"] = f"FAIL: Could not start data_processor.sh for verification: {str(e)}"
                    finally:
                        if proc1:
                            proc1.kill()
                            proc1.wait()
                        if proc2:
                            proc2.kill()
                            proc2.wait()
                    
                    overall["data"].append(entry)
                next_id += 1

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=4)
    final_cleanup()

if __name__ == "__main__":
    main()

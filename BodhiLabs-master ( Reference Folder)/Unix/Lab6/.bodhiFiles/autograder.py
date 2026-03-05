#!/usr/bin/env python3

import os, subprocess, json, copy, shutil

# Base Paths
base = "/home/.evaluationScripts/.bodhiFiles"
student_dir = os.path.join("/home", "labDirectory")
expected_dir = os.path.join(base, "expected")
original_story = os.path.join(base, "original_story.txt")
output_json = os.path.join("/home/.evaluationScripts", "evaluate.json")

# Template
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed"
}
results = {"data": []}

total_steps = 7
story_path = os.path.join(student_dir, "story.txt")

print("Starting autograder...")

for step in range(1, total_steps + 1):
    print("Step", step)
    test = copy.deepcopy(template)
    test["testid"] = step

    # Reset story.txt fresh each step
    shutil.copyfile(original_story, story_path)

    student_answer_file = os.path.join(student_dir, f"answer{step}.txt")
    expected_step_file = os.path.join(expected_dir, f"step{step}.txt")

    if not os.path.exists(student_answer_file):
        test["message"] = f"answer{step}.txt not found"
        results["data"].append(test)
        continue

    with open(student_answer_file) as f:
        raw_commands = [line.strip() for line in f if line.strip()]

    # Build vim command
    vim_cmd_parts = ["vim", "-es", "story.txt"]
    for cmd in raw_commands:
        if cmd.startswith(":"):
            # Strip the leading ":" because -c does not need it
            vim_cmd_parts.append(f'-c "{cmd[1:]}"')
        else:
            # Treat as normal keystrokes
            vim_cmd_parts.append(f'-c "normal! {cmd}"')
    vim_cmd_parts.append('-c "wq"')

    final_cmd = " ".join(vim_cmd_parts)
    print("Running:", final_cmd)

    try:
        subprocess.run(
            final_cmd,
            shell=True,
            cwd=student_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except subprocess.CalledProcessError:
        test["message"] = f"Task {step}: Error running vim commands"
        results["data"].append(test)
        continue

    if not os.path.exists(expected_step_file):
        test["message"] = f"Expected step{step}.txt not found"
        results["data"].append(test)
        continue

    with open(story_path) as f:
        student_lines = [line.strip() for line in f.readlines()]
    with open(expected_step_file) as f:
        expected_lines = [line.strip() for line in f.readlines()]

    diff_lines = []
    for i, (e_line, s_line) in enumerate(zip(expected_lines, student_lines), 1):
        if e_line != s_line:
            diff_lines.append(f"Line {i}:\n  Expected: {e_line}\n  Found:    {s_line}")

    if len(expected_lines) > len(student_lines):
        for i in range(len(student_lines)+1, len(expected_lines)+1):
            diff_lines.append(f"Line {i}:\n  Expected: {expected_lines[i-1]}\n  Found:    <missing>")
    elif len(student_lines) > len(expected_lines):
        for i in range(len(expected_lines)+1, len(student_lines)+1):
            diff_lines.append(f"Line {i}:\n  Expected: <missing>\n  Found:    {student_lines[i-1]}")

    if not diff_lines:
        test["status"] = "success"
        test["score"] = 1
        test["message"] = f"Task {step}: PASS"
    else:
        test["message"] = f"Task {step}: FAIL\n" + "\n".join(diff_lines[:5])

    results["data"].append(test)

# Write results
with open(output_json, "w") as f:
    json.dump(results, f, indent=4)

with open(output_json) as f:
    print(f.read())

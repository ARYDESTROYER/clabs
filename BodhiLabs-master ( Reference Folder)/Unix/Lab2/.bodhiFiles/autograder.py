import json, os, copy, subprocess

os.system('clear')

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

path = '/home/.evaluationScripts/'
inputFile = path + '.bodhiFiles/answer.txt'
jsonPath = path + 'evaluate.json'

# Define the correct cd traversal and minimal expected commands
cd_appends = [
    '',
    'cd demo && ',
    'cd demo && cd .. && ',
    'cd demo && cd .. && cd - && ',
]

correct_sequence = [
    'cd demo',
    'cd ..',
    'cd -',
    'cd ../fun_dir'
]

try:
    with open(inputFile, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    for i, expected_cmd in enumerate(correct_sequence):
        entry = copy.deepcopy(template)
        entry["testid"] = i
        student_command = lines[i] if i < len(lines) else ''
        student_original = student_command
        student_command = cd_appends[i] + student_command
        expected_cmd = correct_sequence[i]
        expected_cmd = cd_appends[i] + expected_cmd

        try:
            cmd = f"bash -c 'cd /home/labDirectory && {student_command} && pwd' | tail -n 1"
            student_output = subprocess.check_output(cmd, shell=True, text=True).strip()

            expected_output = subprocess.check_output(
                f"bash -c 'cd /home/labDirectory && {expected_cmd} && pwd' | tail -n 1",
                shell=True, text=True
            ).strip()

            print(cmd)
            print(expected_cmd)
            print(student_output)
            print(expected_output)

            if student_output == expected_output:
                if student_command.strip() == expected_cmd:
                    entry["message"] = f"{student_command}: PASS"
                    entry["score"] = 1
                    entry["status"] = "success"
                else:
                    entry["message"] = f"{student_original}: PASS, but not minimal"
                    entry["score"] = 0.5
                    entry["status"] = "partial"
            else:
                entry["message"] = f"{student_original}: FAIL - Incorrect target directory"
        except subprocess.CalledProcessError as e:
            entry["message"] = f"{student_original}: FAIL - Command error"

        overall["data"].append(entry)

except FileNotFoundError:
    entry = copy.deepcopy(template)
    entry['message'] = f"answer.txt not found. Evaluation result not generated."
    overall["data"].append(entry)

with open(jsonPath, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

with open(jsonPath, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        print(line)


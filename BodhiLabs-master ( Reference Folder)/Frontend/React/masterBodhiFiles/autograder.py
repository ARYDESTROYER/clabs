#!/usr/bin/python3
import re, json, os, copy

os.system('clear')

# The data Structure for final results to be stored in evaluate.json
overall = {
    "data": []
}

# YOUR Evaluation Code here
template = {
    "testid": 1,
    "status": "fail",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
    }

path = '/home/.evaluationScripts/'

inputFile = path+'.bodhiFiles/out.txt'
jsonPath = path+'evaluate.json'

if os.path.isfile(inputFile):
    with open(inputFile, 'r') as file:
        lines = file.readlines()

    reqLines = []
    for line in lines:
        if re.search(r'✕|✓', line):
            reqLines.append(line.strip())

    for i,result in enumerate(reqLines):
        entry = copy.deepcopy(template)
        entry["testid"] = i
        if '✓' in result:
            entry["message"] = f"{result.split('(')[0][1:].strip()}: PASS"
            entry["score"] = 1
            entry["status"] = "pass"
        else:
            entry['message'] = f"{result.split('(')[0][1:].strip()}: FAIL"
        overall["data"].append(entry)
else:
    entry = copy.deepcopy(template)
    entry['message'] = f"Failed to get the npm test result. Since you have not run the evaluate the result is not generated yet."
    overall["data"].append([entry])

# Store evaluation results
with open(jsonPath,'w',encoding='utf-8') as f:
    json.dump(overall,f,indent=4)

# Show evaluation results
with open(jsonPath,'r',encoding='utf-8') as f:
    for line in f.readlines():
        print(line)
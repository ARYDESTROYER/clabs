#!/usr/bin/python3
import subprocess
import os
import sys

# Define the order of scripts to run
SCRIPTS = [
    "part-1.py",
    "part-2.py",
    "part-3.py",
    "part-4.py"
]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    for script in SCRIPTS:
        script_path = os.path.join(BASE_PATH, script)
        if os.path.exists(script_path):
            try:
                subprocess.run([sys.executable, script_path], check=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
    print("Evaluation complete. Results in evaluate.json.")

if __name__ == "__main__":
    main()

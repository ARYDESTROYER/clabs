#!/usr/bin/env python3
import hashlib
import json
import os
import re

FLAG_FILE = "/tmp/student_flags.txt"
OUTPUT_JSON = "/tmp/evaluate.json"

EXPECTED_FRAGMENT_HASHES = {
    1: "1096ea36f81ed7a4950e73f4acb9bc5479e1595d978a85faa1249b4a98122650",
    2: "a09ac8146652c3c5294366895be6d8ef4e6f3db20f25ec1f12cf966a23b260f3",
    3: "3dc13aa6e1229c6ae89b7f65498cda539bc6deb943444d10ec71c4c7a01c99c1",
    4: "83f5350499d977540d51dc47eb79ee5dc55c3811d723b138209befd78b2a23b1",
    5: "a2bb6cba9c940101566181a2b5058038dc4a30533d4c9b6cdbf5fca4eee4912d",
    6: "be752056bddd66fb9db3e28c839d744569487db9d9018cff2925eeea25820c1b",
}

EXPECTED_FINAL_FLAG_HASH = "e2aa5e1a25e930ac21798d0c699b717554dc8c0ba4c2f1f08aa9de3ac5125e34"
MAX_MARKS = 7


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def extract_fragments_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    fragments = {}
    current_fragment = None

    for line in lines:
        line_stripped = line.strip()

        fragment_match = re.match(r"^Fragment\s+([1-6])(?:\s*\([^)]*\))?\s*:\s*(.*)$", line_stripped)

        if fragment_match:
            current_fragment = int(fragment_match.group(1))
            value = fragment_match.group(2).strip()
            if value:
                fragments[current_fragment] = value
        elif line_stripped.startswith("Final Decoded Flag:"):
            current_fragment = "final"
            value = line_stripped.replace("Final Decoded Flag:", "", 1).strip()
            if value:
                fragments["final"] = value
        elif current_fragment is not None and line_stripped and current_fragment not in fragments:
            fragments[current_fragment] = line_stripped

    return fragments


def check_fragments(fragments: dict) -> tuple[int, list[str]]:
    score = 0
    feedback = []

    for index in range(1, 7):
        if index not in fragments:
            feedback.append(f"Fragment {index}: not submitted")
            continue

        user_hash = sha256_hex(fragments[index])
        if user_hash == EXPECTED_FRAGMENT_HASHES[index]:
            feedback.append(f"Fragment {index}: correct")
            score += 1
        else:
            feedback.append(f"Fragment {index}: incorrect")

    if "final" not in fragments:
        feedback.append("Final Decoded Flag: not submitted")
        return score, feedback

    final_hash = sha256_hex(fragments["final"])
    if final_hash == EXPECTED_FINAL_FLAG_HASH:
        feedback.append("Final Decoded Flag: correct")
        score += 1
    else:
        feedback.append("Final Decoded Flag: incorrect")

    return score, feedback


def write_results(result: dict) -> None:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as handle:
        json.dump({"data": [result]}, handle, indent=2)


def main():
    test_result = {
        "testid": 1,
        "status": "failure",
        "score": 0,
        "maximum marks": MAX_MARKS,
        "message": "Submission incomplete or incorrect",
    }

    feedback_lines = []

    try:
        if not os.path.exists(FLAG_FILE):
            feedback_lines.append(f"File {FLAG_FILE} not found.")
        else:
            fragments = extract_fragments_from_file(FLAG_FILE)
            if not fragments:
                feedback_lines.append("No fragments found in submission file.")
            else:
                score, feedback_lines = check_fragments(fragments)
                test_result["score"] = score
                if score == MAX_MARKS:
                    test_result["status"] = "success"

    except Exception as error:
        feedback_lines = [f"Error reading submission: {error}"]

    if feedback_lines:
        test_result["message"] = "\n".join(feedback_lines)

    write_results(test_result)

    print(f"Score: {test_result['score']}/{MAX_MARKS}")
    for line in feedback_lines:
        print(line)


if __name__ == "__main__":
    main()


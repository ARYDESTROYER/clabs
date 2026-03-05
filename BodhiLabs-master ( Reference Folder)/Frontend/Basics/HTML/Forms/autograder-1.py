#!/usr/bin/python3
import json, os
from bs4 import BeautifulSoup

# Paths
input_file = "/home/labDirectory/forms1/forms-1.html"

# Template for result entries
template = {
    "testid": "",
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": ""
}

# Final results container
overall = {"data": []}

try:
    with open(input_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 1. Email Input
    email_input = soup.find("input", {"type": "email"})
    entry = template.copy()
    entry["testid"] = "Form/Email Input"
    if email_input and email_input.get("name") == "email":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Email input is present and correctly named."
    else:
        entry["message"] = "Email input is missing or incorrectly named."
    overall["data"].append(entry)

    # 2. Radio Buttons
    radio_buttons = soup.find_all("input", {"type": "radio"})
    entry = template.copy()
    entry["testid"] = "Form/Radio Buttons"
    if len(radio_buttons) >= 4 and all(rb.get("name") == "age_group" for rb in radio_buttons):
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Radio buttons for age group are present and correctly named."
    else:
        entry["message"] = "Radio buttons for age group are missing or incorrectly named."
    overall["data"].append(entry)

    # 3. Checkbox for Agreement
    checkbox = soup.find("input", {"type": "checkbox"})
    entry = template.copy()
    entry["testid"] = "Form/Checkbox for Agreement"
    if checkbox and checkbox.get("name") == "agreement":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Checkbox for agreement is present and correctly named."
    else:
        entry["message"] = "Checkbox for agreement is missing or incorrectly named."
    overall["data"].append(entry)

    # 4. Hidden Input
    hidden_input = soup.find("input", {"type": "hidden"})
    entry = template.copy()
    entry["testid"] = "Form/Hidden Input"
    if hidden_input and hidden_input.get("name") == "survey_id" and hidden_input.get("value") == "survey123":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Hidden input is present with correct name and value."
    else:
        entry["message"] = "Hidden input is missing or incorrectly configured."
    overall["data"].append(entry)

    # 5. File Input
    file_input = soup.find("input", {"type": "file"})
    entry = template.copy()
    entry["testid"] = "Form/File Input"
    if file_input and file_input.get("name") == "document_attachment":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "File input for attaching a document is present and correctly named."
    else:
        entry["message"] = "File input is missing or incorrectly named."
    overall["data"].append(entry)

    # 6. Image Button
    image_button = soup.find("input", {"type": "image"})
    entry = template.copy()
    entry["testid"] = "Form/Image Button"
    if image_button and image_button.get("src") == "submit-animate.gif":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Image button for form submission is present and correctly configured."
    else:
        entry["message"] = "Image button is missing or incorrectly configured."
    overall["data"].append(entry)

except Exception as e:
    # Catch-all error block
    entry = template.copy()
    entry["testid"] = "Form/Error"
    entry["message"] = f"Autograder crashed: {e}"
    overall["data"].append(entry)

# Print results
eval_path = os.path.join(os.path.dirname(__file__), "../.evaluationScripts/evaluate.json")
with open(eval_path, "w") as f:
    json.dump(overall, f, indent=4)

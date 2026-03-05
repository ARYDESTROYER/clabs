#!/usr/bin/python3
import json, os
from bs4 import BeautifulSoup

# Paths
input_file = "/home/labDirectory/forms2/forms-2.html"

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

    # 1. Textarea for Comments
    textarea = soup.find("textarea", {"name": "comments"})
    entry = template.copy()
    entry["testid"] = "Form/Textarea for Comments"
    if textarea and textarea.get("id") == "comments":
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Textarea for comments is present and correctly named."
    else:
        entry["message"] = "Textarea for comments is missing or incorrectly named."
    overall["data"].append(entry)

    # 2. Dropdown Select for Feedback Type
    feedback_type_select = soup.find("select", {"name": "feedback_type"})
    entry = template.copy()
    entry["testid"] = "Form/Dropdown Select for Feedback Type"
    if feedback_type_select:
        options = [opt.get("value") for opt in feedback_type_select.find_all("option")]
        required_options = {"general", "product", "service", "other"}
        if required_options.issubset(options):
            entry["status"] = "success"
            entry["score"] = 1
            entry["message"] = "Dropdown select for feedback type is present with correct options."
        else:
            entry["message"] = "Dropdown select for feedback type is missing required options."
    else:
        entry["message"] = "Dropdown select for feedback type is missing."
    overall["data"].append(entry)

    # 3. Multiple Select for Product Type
    product_type_select = soup.find("select", {"name": "product_type", "multiple": True})
    entry = template.copy()
    entry["testid"] = "Form/Multiple Select for Product Type"
    if product_type_select:
        options = [opt.get("value") for opt in product_type_select.find_all("option")]
        required_options = {"laptop", "desktop", "tablet", "smartphone", "other"}
        if required_options.issubset(options):
            entry["status"] = "success"
            entry["score"] = 1
            entry["message"] = "Multiple select for product type is present with correct options."
        else:
            entry["message"] = "Multiple select for product type is missing required options."
    else:
        entry["message"] = "Multiple select for product type is missing."
    overall["data"].append(entry)

    # 4. Button to Reset the Form
    reset_button = soup.find("button", {"type": "reset"})
    entry = template.copy()
    entry["testid"] = "Form/Button to Reset the Form"
    if reset_button:
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Reset button is present."
    else:
        entry["message"] = "Reset button is missing."
    overall["data"].append(entry)

    # 5. Button to Submit the Form
    submit_button = soup.find("button", {"type": "submit"})
    entry = template.copy()
    entry["testid"] = "Form/Button to Submit the Form"
    if submit_button:
        entry["status"] = "success"
        entry["score"] = 1
        entry["message"] = "Submit button is present."
    else:
        entry["message"] = "Submit button is missing."
    overall["data"].append(entry)

except Exception as e:
    entry = template.copy()
    entry["testid"] = "Form/Error"
    entry["message"] = f"Autograder crashed: {e}"
    overall["data"].append(entry)

# Print results
eval_path = os.path.join(os.path.dirname(__file__), "../.evaluationScripts/evaluate.json")
with open(eval_path, "w") as f:
    json.dump(overall, f, indent=4)


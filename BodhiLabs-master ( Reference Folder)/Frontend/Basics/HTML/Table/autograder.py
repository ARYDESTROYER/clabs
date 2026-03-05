#!/usr/bin/python3
import json
from bs4 import BeautifulSoup

# Define paths
lab_file_path = "/home/labDirectory/tables.html"
json_output_path = "/home/.evaluationScripts/evaluate.json"

# Base template for each test case
template = {
    "testid": "",
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": ""
}

# Evaluation output structure
overall = {
    "data": []
}

# Category-wise criteria
criteria = {
    "Table Present": "",
    "Table Caption": "",
    "Header Row": "",
    "Data Rows": "",
    "Rowspan and Colspan": "",
    "Footer Row": ""
}

# Load HTML
try:
    with open(lab_file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table")

    # 1. Check table presence with border 2
    if table and table.get("border") == "2":
        criteria["Table Present"] = "success"
        msg = "Table is present with border 2."
    else:
        criteria["Table Present"] = "failure"
        msg = "Table is missing or does not have border 2."

    entry = template.copy()
    entry["testid"] = "Table/Table Present"
    entry["status"] = criteria["Table Present"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

    # 2. Table caption
    if table and table.find("caption"):
        criteria["Table Caption"] = "success"
        msg = "Table caption is present."
    else:
        criteria["Table Caption"] = "failure"
        msg = "Table caption is missing."

    entry = template.copy()
    entry["testid"] = "Table/Table Caption"
    entry["status"] = criteria["Table Caption"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

    # 3. Header row
    if table and table.find("thead"):
        header_row = table.find("thead").find("tr")
        if header_row and len(header_row.find_all("th")) == 4:
            criteria["Header Row"] = "success"
            msg = "Header row is present with correct columns."
        else:
            criteria["Header Row"] = "failure"
            msg = "Header row is missing or incorrect."
    else:
        criteria["Header Row"] = "failure"
        msg = "Header section is missing."

    entry = template.copy()
    entry["testid"] = "Table/Header Row"
    entry["status"] = criteria["Header Row"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

    # 4. Data rows
    if table and table.find("tbody"):
        data_rows = table.find("tbody").find_all("tr")
        if len(data_rows) >= 4:
            criteria["Data Rows"] = "success"
            msg = "Data rows are present."
        else:
            criteria["Data Rows"] = "failure"
            msg = "Insufficient data rows."
    else:
        criteria["Data Rows"] = "failure"
        msg = "Data section is missing."

    entry = template.copy()
    entry["testid"] = "Table/Data Rows"
    entry["status"] = criteria["Data Rows"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

    # 5. Rowspan and Colspan
    rowspan_correct = table.find("td", {"rowspan": "2"}) is not None
    colspan_correct = table.find("td", {"colspan": "2"}) is not None
    if rowspan_correct and colspan_correct:
        criteria["Rowspan and Colspan"] = "success"
        msg = "Rowspan and colspan are used correctly."
    else:
        criteria["Rowspan and Colspan"] = "failure"
        msg = "Rowspan and/or colspan are missing or incorrect."

    entry = template.copy()
    entry["testid"] = "Table/Rowspan and Colspan"
    entry["status"] = criteria["Rowspan and Colspan"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

    # 6. Footer row
    if table and table.find("tfoot"):
        footer_row = table.find("tfoot").find("tr")
        if footer_row and len(footer_row.find_all("td")) == 1:
            criteria["Footer Row"] = "success"
            msg = "Footer row is present with correct content."
        else:
            criteria["Footer Row"] = "failure"
            msg = "Footer row is missing or incorrect."
    else:
        criteria["Footer Row"] = "failure"
        msg = "Footer section is missing."

    entry = template.copy()
    entry["testid"] = "Table/Footer Row"
    entry["status"] = criteria["Footer Row"]
    entry["score"] = 1 if entry["status"] == "success" else 0
    entry["message"] = msg
    overall["data"].append(entry)

except Exception as e:
    # If any failure occurs, capture one generic entry
    entry = template.copy()
    entry["testid"] = "Table/Error"
    entry["message"] = f"Autograder crashed: {e}"
    overall["data"].append(entry)

# Save the results
with open(json_output_path, "w") as f:
    json.dump(overall, f, indent=4)

# Display results
with open(json_output_path, "r") as f:
    print(f.read())

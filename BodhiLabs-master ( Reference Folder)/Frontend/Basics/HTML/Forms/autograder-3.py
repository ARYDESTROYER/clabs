#!/usr/bin/python3
import json, os
from bs4 import BeautifulSoup

# Paths
input_file = "/home/labDirectory/forms3/forms-3.html"

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

    def check(condition, label, success_msg, fail_msg):
        entry = template.copy()
        entry["testid"] = f"Form/{label}"
        entry["status"] = "success" if condition else "failure"
        entry["score"] = 1 if condition else 0
        entry["message"] = success_msg if condition else fail_msg
        overall["data"].append(entry)

    # Get all fieldsets
    fieldsets = soup.find_all("fieldset")

    # Personal Information Fieldset
    pi_fieldset = fieldsets[0] if len(fieldsets) > 0 else None
    check(
        pi_fieldset and pi_fieldset.find("legend") and pi_fieldset.find("legend").text == "Personal Information",
        "Personal Information Fieldset",
        "Personal Information fieldset is present with legend.",
        "Personal Information fieldset is missing or incorrectly labeled."
    )

    # Full Name Input
    fn_input = soup.find("input", {"name": "full_name"})
    check(
        fn_input and fn_input.get("type") == "text" and fn_input.has_attr("required"),
        "Full Name Input",
        "Full Name input is present and correctly configured.",
        "Full Name input is missing or incorrectly configured."
    )

    # Email Input
    email_input = soup.find("input", {"name": "email"})
    check(
        email_input and email_input.get("type") == "email" and email_input.has_attr("required"),
        "Email Input",
        "Email input is present and correctly configured.",
        "Email input is missing or incorrectly configured."
    )

    # Date of Birth Input
    dob_input = soup.find("input", {"name": "dob"})
    check(
        dob_input and dob_input.get("type") == "date" and dob_input.has_attr("required"),
        "Date of Birth Input",
        "Date of Birth input is present and correctly configured.",
        "Date of Birth input is missing or incorrectly configured."
    )

    # Car Preferences Fieldset
    car_fieldset = fieldsets[1] if len(fieldsets) > 1 else None
    check(
        car_fieldset and car_fieldset.find("legend") and car_fieldset.find("legend").text == "Car Preferences",
        "Car Preferences Fieldset",
        "Car Preferences fieldset is present with legend.",
        "Car Preferences fieldset is missing or incorrectly labeled."
    )

    # Car Color Input
    car_color = car_fieldset.find("input", {"name": "car_color"}) if car_fieldset else None
    check(
        car_color and car_color.get("type") == "color" and car_color.has_attr("required"),
        "Car Color Input",
        "Car Color input is present and correctly configured.",
        "Car Color input is missing or incorrectly configured."
    )

    # Car Model Select
    car_model = car_fieldset.find("select", {"name": "car_model"}) if car_fieldset else None
    required_options = {"sedan", "suv", "hatchback", "convertible"}
    actual_options = {opt.get("value") for opt in car_model.find_all("option")} if car_model else set()
    check(
        required_options.issubset(actual_options),
        "Car Model Select",
        "Car Model select is present with correct options.",
        "Car Model select is missing required options or is absent."
    )

    # Car Age Range
    car_age = car_fieldset.find("input", {"name": "car_age"}) if car_fieldset else None
    check(
        car_age and car_age.get("type") == "range",
        "Car Age Range",
        "Car Age range input is present.",
        "Car Age range input is missing or incorrectly configured."
    )

    # Electric Car Preference Radios
    electric = car_fieldset.find("input", {"name": "electric"}) if car_fieldset else None
    radios = car_fieldset.find_all("input", {"type": "radio"}) if car_fieldset else []
    check(
        electric and len(radios) == 2,
        "Electric Car Preference",
        "Electric car preference radio buttons are present.",
        "Electric car preference radio buttons are missing or incorrect."
    )

    # Phone Preferences Fieldset
    phone_fieldset = fieldsets[2] if len(fieldsets) > 2 else None
    check(
        phone_fieldset and phone_fieldset.find("legend") and phone_fieldset.find("legend").text == "Phone Preferences",
        "Phone Preferences Fieldset",
        "Phone Preferences fieldset is present with legend.",
        "Phone Preferences fieldset is missing or incorrectly labeled."
    )

    # Phone Color Input
    phone_color = phone_fieldset.find("input", {"name": "phone_color"}) if phone_fieldset else None
    check(
        phone_color and phone_color.get("type") == "color" and phone_color.has_attr("required"),
        "Phone Color Input",
        "Phone Color input is present and correctly configured.",
        "Phone Color input is missing or incorrectly configured."
    )

    # Phone Brand Select
    phone_brand = phone_fieldset.find("select", {"name": "phone_brand"}) if phone_fieldset else None
    required_brands = {"apple", "samsung", "google", "oneplus"}
    actual_brands = {opt.get("value") for opt in phone_brand.find_all("option")} if phone_brand else set()
    check(
        required_brands.issubset(actual_brands),
        "Phone Brand Select",
        "Phone Brand select is present with correct options.",
        "Phone Brand select is missing required options or is absent."
    )

    # Phone Release Date Input
    release_date = phone_fieldset.find("input", {"name": "release_date"}) if phone_fieldset else None
    check(
        release_date and release_date.get("type") == "date" and release_date.has_attr("min"),
        "Phone Release Date Input",
        "Phone Release Date input is present and correctly configured.",
        "Phone Release Date input is missing or incorrectly configured."
    )

    # Submit Button
    submit_btn = soup.find("button", {"type": "submit"})
    check(
        submit_btn,
        "Submit Button",
        "Submit button is present.",
        "Submit button is missing."
    )

except Exception as e:
    entry = template.copy()
    entry["testid"] = "Form/Error"
    entry["message"] = f"Autograder crashed: {e}"
    overall["data"].append(entry)

# Print results
eval_path = os.path.join(os.path.dirname(__file__), "../.evaluationScripts/evaluate.json")
with open(eval_path, "w") as f:
    json.dump(overall, f, indent=4)


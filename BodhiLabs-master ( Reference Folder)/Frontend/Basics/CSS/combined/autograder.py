#!/usr/bin/python3
import os, json
import tinycss2
import webcolors

STYLE_FILE = "/home/labDirectory/style.css"
EXPECTED_FILE = os.path.join(os.path.dirname(__file__), "jsons", "combined.json")

def make_entry(selector, property_name, status, expected_val=None, student_val=None):
    if status:
        message = f"'{property_name}' correctly set to '{student_val}'"
    else:
        if student_val is None:
            message = f"'{property_name}' is missing"
        else:
            message = f"Expected '{expected_val}' but got '{student_val}'"
    return {
        "testid": f"CSS/{selector} - {property_name}",
        "status": "success" if status else "failure",
        "score": 1 if status else 0,
        "maximum marks": 1,
        "message": message
    }

def normalize_color(value):
    try:
        rgb = webcolors.name_to_rgb(value)
    except ValueError:
        try:
            rgb = webcolors.hex_to_rgb(value)
        except ValueError:
            try:
                if value.startswith("rgb("):
                    value = value.replace(" ", "").lower()
                    parts = value[4:-1].split(",")
                    rgb = tuple(int(p) for p in parts)
                else:
                    return value  # Not a recognizable color
            except Exception:
                return value
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

def normalize_value(property_name, value):
    if not value:
        return None
    value = value.strip().lower()
    if property_name == "color" or "color" in property_name or "background" in property_name:
        return normalize_color(value)
    return value

def parse_student_styles(css_path):
    with open(css_path, "r") as f:
        css = f.read()

    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    selector_to_props = {}

    for rule in rules:
        if rule.type != "qualified-rule":
            continue
        selector = tinycss2.serialize(rule.prelude).strip()
        declarations = tinycss2.parse_declaration_list(rule.content)
        props = {}
        for decl in declarations:
            if decl.type == "declaration":
                prop_name = decl.name.strip()
                prop_value = tinycss2.serialize(decl.value).strip()
                props[prop_name] = prop_value
        selector_to_props[selector] = props

    return selector_to_props

results = []

try:
    with open(EXPECTED_FILE) as f:
        expected_styles = json.load(f)

    student_styles = parse_student_styles(STYLE_FILE)

    for selector, expected_props in expected_styles.items():
        student_props = student_styles.get(selector, {})
        for prop, expected_val in expected_props.items():
            expected_norm = normalize_value(prop, expected_val)
            student_val = student_props.get(prop)
            student_norm = normalize_value(prop, student_val) if student_val else None
            status = student_norm == expected_norm
            results.append(make_entry(selector, prop, status, expected_norm, student_norm))

except Exception as e:
    results.append({
        "testid": "CSS/Error",
        "status": "failure",
        "score": 0,
        "maximum marks": 1,
        "message": f"Autograder crashed: {e}"
    })

eval_path = os.path.join(os.path.dirname(__file__), "evaluate.json")
with open(eval_path, "w") as f:
    json.dump(results, f, indent=4)

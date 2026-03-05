#!/usr/bin/env python3
import json
import os
import base64

# You might need to install cssutils: pip install cssutils
import cssutils

# --- Configuration -------------------------------------------------------------
# Output path for the results file.
RESULTS_PATH = '/home/.evaluationScripts/evaluate.json'

# Paths to student CSS files, configured according to the directory structure.
PARTS = {
    'Display-Visibility': {
        'css_path': '/home/labDirectory/part-1/style.css',
        'blob': """
eyIjYm94MiI6IHsiZGlzcGxheSI6ICJub25lIn0sICIjYm94MSI6IHsidmlzaWJpbGl0eSI6ICJo
aWRkZW4ifSwgIi5ib3giOiB7ImRpc3BsYXkiOiAiaW5saW5lLWJsb2NrIn19
"""
    },
    'Position-ZIndex': {
        'css_path': '/home/labDirectory/part-2/style.css',
        'blob': """
eyIjcGFwZXJjbGlwIjogeyJwb3NpdGlvbiI6ICJyZWxhdGl2ZSIsICJ0b3AiOiAiMjBweCIsICJs
ZWZ0IjogIi0zMHB4In0sICIuY2x1ZS1hcmVhIjogeyJwb3NpdGlvbiI6ICJyZWxhdGl2ZSJ9LCAi
I3JlZC1ibG90Y2giOiB7InBvc2l0aW9uIjogImFic29sdXRlIiwgInRvcCI6ICI1MHB4IiwgImxl
ZnQiOiAiMTAwcHgiLCAiei1pbmRleCI6ICIxIn0sICIjZGVjb2Rlci1sZW5zIjogeyJwb3NpdGlv
biI6ICJhYnNvbHV0ZSIsICJ0b3AiOiAiMzBweCIsICJsZWZ0IjogIjIwcHgiLCAiei1pbmRleCI6
ICIyIn0sICIjbWFpbi1oZWFkZXIiOiB7InBvc2l0aW9uIjogInN0aWNreSIsICJ0b3AiOiAiMCJ9
LCAiI2hlbHAtYnV0dG9uIjogeyJwb3NpdGlvbiI6ICJmaXhlZCIsICJib3R0b20iOiAiMjBweCIs
ICJyaWdodCI6ICIyMHB4In19
"""
    },
    'Float-Clear': {
        'css_path': '/home/labDirectory/part-3/style.css',
        'blob': """
eyIubWFpbi1pbWFnZSI6IHsiZmxvYXQiOiAibGVmdCJ9LCAiLnB1bGwtcXVvdGUiOiB7ImZsb2F0
IjogInJpZ2h0IiwgIndpZHRoIjogIjI1MHB4In0sICIuYXJ0aWNsZS1mb290ZXIiOiB7ImNsZWFy
IjogImJvdGgifX0=
"""
    }
}

# --- Script Logic --------------------------------------------------------------
overall = {"data": []}
test_id_counter = 0

def append_result(score, maximum, message):
    """Appends a single test result with an incrementing integer testid."""
    global test_id_counter
    overall['data'].append({
        'testid': test_id_counter,
        'status': 'success' if score == maximum else 'failure',
        'score': score,
        'maximum marks': maximum,
        'message': message
    })
    test_id_counter += 1

def load_css(path):
    """Loads a CSS file, returning an empty string if it doesn't exist."""
    if not os.path.exists(path):
        return ""
    with open(path, encoding='utf-8') as f:
        return f.read()

def get_final_style_for_selector(sheet, target_selector):
    """
    Merges all rules for a given selector into a single dictionary,
    mimicking the CSS cascade (last rule wins).
    """
    final_style = {}
    # Iterate forwards through the stylesheet
    for rule in sheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            selectors = [s.strip() for s in rule.selectorText.split(',')]
            if target_selector in selectors:
                # Add all properties from this rule to our dictionary.
                # If a property already exists, it gets overwritten,
                # which is exactly how the cascade works.
                for prop in rule.style:
                    final_style[prop.name] = prop.value
    return final_style

def evaluate_part(part_name, css_path, expected_rules):
    """Evaluates a single CSS file against a dictionary of expected rules."""
    css = load_css(css_path)
    if not css:
        append_result(0, 1, f"({part_name}) CSS file not found at: {css_path}")
        return

    cssutils.log.setLevel('CRITICAL')
    sheet = cssutils.parseString(css)

    for selector, props in expected_rules.items():
        # Get the final, merged style for the selector from all its definitions
        final_style = get_final_style_for_selector(sheet, selector)

        if not final_style:
            append_result(0, 1, f"({part_name}) Missing rule for selector `{selector}`.")
            for prop in props:
                append_result(0, 1, f"({part_name}) Cannot check `{prop}` because rule for `{selector}` is missing.")
            continue

        for prop, exp in props.items():
            # Check if the property exists in our merged style dictionary
            if prop not in final_style:
                append_result(0, 1, f"({part_name}) Rule `{selector}` is missing the required property `{prop}`.")
            else:
                actual_raw = final_style[prop]
                actual = actual_raw.replace('"', '').replace("'", "").lower().strip()
                expect = exp.lower().replace('"', '').replace("'", "").strip()

                if expect in actual:
                    append_result(1, 1, f"({part_name}) Correct: `{selector}` has `{prop}: {actual_raw}`.")
                else:
                    append_result(0, 1, f"({part_name}) Incorrect: `{selector}` has `{prop}: {actual_raw}`; expected `{exp}`.")

def main():
    """Main function to run the evaluation for all parts."""
    print("Starting evaluation...")
    for part_name, cfg in PARTS.items():
        blob = cfg['blob'].replace("\n", "")
        expected = json.loads(base64.b64decode(blob).decode('utf-8'))
        evaluate_part(part_name, cfg['css_path'], expected)

    # Ensure the output directory exists before writing the file
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=2)
    print(f"Evaluation complete. Results written to {RESULTS_PATH}")

if __name__ == "__main__":
    main()

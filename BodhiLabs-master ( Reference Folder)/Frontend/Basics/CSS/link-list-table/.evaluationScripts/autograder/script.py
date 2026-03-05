#!/usr/bin/env python3
import json
import os
import base64

# You might need to install cssutils: pip install cssutils
import cssutils

# --- Configuration -------------------------------------------------------------
# Output path for the results file.
RESULTS_PATH = '/home/.evaluationScripts/evaluate.json'

# CORRECTED: The blobs below have been regenerated to fix the base64 encoding error.
PARTS = {
    'Links-Activity': {
        'css_path': '/home/labDirectory/part-1/style.css',
        'blob': """
eyIuY29tcGFzcy1saW5rIjogeyJjb2xvciI6ICJkYXJrZ3JlZW4iLCAidGV4dC1kZWNvcmF0aW9uIjo
gIm5vbmUifSwgIi5jb21wYXNzLWxpbms6dmlzaXRlZCI6IHsiY29sb3IiOiAiIzU1NTU1NSJ9LCAiLm
NvbXBhc3MtbGluazpob3ZlciI6IHsiY29sb3IiOiAiI2RhYTUyMCIsICJ0ZXh0LWRlY29yYXRpb24iO
iAidW5kZXJsaW5lIn0sICIuY29tcGFzcy1saW5rOmFjdGl2ZSI6IHsiY29sb3IiOiAiI2ZmNDUwMCJ9
LCAiLmNvbXBhc3MtbGluazpmb2N1cyI6IHsiY29sb3IiOiAiIzAwNWY5OSIsICJ0ZXh0LWRlY29yYXR
pb24iOiAidW5kZXJsaW5lIn19
"""
    },
    'Lists-Activity': {
        'css_path': '/home/labDirectory/part-2/style.css',
        'blob': """
eyIuaW5ncmVkaWVudHMtbGlzdCI6IHsibGlzdC1zdHlsZS10eXBlIjogImNpcmNsZSIsICJsaXN0LX
N0eWxlLXBvc2l0aW9uIjogImluc2lkZSJ9LCAiLmluc3RydWN0aW9ucy1saXN0IjogeyJsaXN0LXN0
eWxlLXR5cGUiOiAidXBwZXItcm9tYW4ifSwgIi5zZWNyZXQtaW5ncmVkaWVudCI6IHsibGlzdC1zdH
lsZS1pbWFnZSI6ICJ1cmwoJ3N0YXIucG5nJykifX0=
"""
    },
    'Tables-Activity': {
        'css_path': '/home/labDirectory/part-3/style.css',
        'blob': """
eyIudHJlYXN1cnktdGFibGUiOiB7ImJvcmRlci1jb2xsYXBzZSI6ICJjb2xsYXBzZSIsICJlbXB0eS1
jZWxscyI6ICJoaWRlIiwgIndpZHRoIjogIjEwMCUifSwgInRkIjogeyJib3JkZXIiOiAiMXB4IHNvbG
lkICM5YzdhN2EiLCAicGFkZGluZyI6ICIxMnB4In0sICJ0aCI6IHsiYm9yZGVyIjogIjFweCBzb2xpZ
CAjOWM3YTdhIiwgImJhY2tncm91bmQtY29sb3IiOiAiI2Q0Yjk5NiIsICJwYWRkaW5nIjogIjEycHgi
LCAidGV4dC10cmFuc2Zvcm0iOiAidXBwZXJjYXNlIn0sICIuY29sLW51bSI6IHsidGV4dC1hbGlnbiI
6ICJyaWdodCJ9LCAidGJvZHkgdHI6bnRoLWNoaWxkKGV2ZW4pIjogeyJiYWNrZ3JvdW5kLWNvbG9yIj
ogIiNlOWUwYzkifSwgInRib2R5IHRyOmhvdmVyIjogeyJiYWNrZ3JvdW5kLWNvbG9yIjogIiNjOGJkY
TQifX0=
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

# NEW: Helper function to handle 3-digit vs 6-digit hex codes
def normalize_hex_color(color_str):
    """Expands 3-digit hex colors to 6 digits for accurate comparison."""
    color_str = color_str.strip()
    if color_str.startswith('#') and len(color_str) == 4:
        # Expands #RGB to #RRGGBB
        return f"#{color_str[1]*2}{color_str[2]*2}{color_str[3]*2}"
    return color_str

def get_final_style_for_selector(sheet, target_selector):
    """
    Merges all rules for a given selector into a single dictionary,
    mimicking the CSS cascade (last rule wins).
    """
    final_style = {}
    for rule in sheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            selectors = [s.strip() for s in rule.selectorText.split(',')]
            if target_selector in selectors:
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
        final_style = get_final_style_for_selector(sheet, selector)

        if not final_style:
            append_result(0, 1, f"({part_name}) Missing rule for selector `{selector}`.")
            for prop in props:
                append_result(0, 1, f"({part_name}) Cannot check `{prop}` because rule for `{selector}` is missing.")
            continue

        for prop, exp in props.items():
            if prop not in final_style:
                append_result(0, 1, f"({part_name}) Rule `{selector}` is missing the required property `{prop}`.")
            else:
                actual_raw = final_style[prop]
                
                # MODIFIED: Normalize both actual and expected values before comparing
                actual_clean = actual_raw.replace('"', '').replace("'", "").lower().strip()
                expect_clean = exp.lower().replace('"', '').replace("'", "").strip()

                actual_normalized = normalize_hex_color(actual_clean)
                expect_normalized = normalize_hex_color(expect_clean)
                
                # MODIFIED: Use a strict equality check now that values are normalized
                if expect_normalized == actual_normalized:
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

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=2)
    print(f"Evaluation complete. Results written to {RESULTS_PATH}")

if __name__ == "__main__":
    main()

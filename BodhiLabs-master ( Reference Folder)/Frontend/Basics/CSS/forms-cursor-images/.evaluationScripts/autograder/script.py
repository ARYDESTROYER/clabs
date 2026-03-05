#!/usr/bin/env python3
import json
import os
import base64
import cssutils

RESULTS_PATH = '/home/.evaluationScripts/evaluate.json'

PARTS = {
    'Forms': {
        'css_path': '/home/labDirectory/part-1/style.css',
        'blob': """
eyJmaWVsZHNldCI6IHsiYm9yZGVyIjogIjFweCBzb2xpZCAjN2Y4YzhkIiwgInBhZGRpbmciOiAi
MTVweCJ9LCAibGVnZW5kIjogeyJmb250LXdlaWdodCI6ICJib2xkIiwgImNvbG9yIjogIiMzNDk4
ZGIiLCAicGFkZGluZyI6ICIwIDVweCJ9LCAiaW5wdXRbdHlwZT0ndGV4dCddIjogeyJ3aWR0aCI6
ICIxMDAlIiwgInBhZGRpbmciOiAiMTBweCIsICJiYWNrZ3JvdW5kLWNvbG9yIjogIiMyYzNlNTAi
LCAiYm9yZGVyIjogIjFweCBzb2xpZCAjN2Y4YzhkIiwgImNvbG9yIjogIiNlY2YwZjEiLCAiYm94
LXNpemluZyI6ICJib3JkZXItYm94IiwgIm1hcmdpbi1ib3R0b20iOiAiMTVweCJ9LCAiaW5wdXRb
dHlwZT0ncGFzc3dvcmQnXSI6IHsid2lkdGgiOiAiMTAwJSIsICJwYWRkaW5nIjogIjEwcHgiLCAi
YmFja2dyb3VuZC1jb2xvciI6ICIjMmMzZTUwIiwgImJvcmRlciI6ICIxcHggc29saWQgIzdmOGM4
ZCIsICJjb2xvciI6ICIjZWNmMGYxIiwgImJveC1zaXppbmciOiAiYm9yZGVyLWJveCIsICJtYXJn
aW4tYm90dG9tIjogIjE1cHgifSwgInRleHRhcmVhIjogeyJ3aWR0aCI6ICIxMDAlIiwgInBhZGRp
bmciOiAiMTBweCIsICJiYWNrZ3JvdW5kLWNvbG9yIjogIiMyYzNlNTAiLCAiYm9yZGVyIjogIjFw
eCBzb2xpZCAjN2Y4YzhkIiwgImNvbG9yIjogIiNlY2YwZjEiLCAiYm94LXNpemluZyI6ICJib3Jk
ZXItYm94IiwgIm1hcmdpbi1ib3R0b20iOiAiMTVweCJ9LCAiaW5wdXQ6Zm9jdXMiOiB7ImJvcmRl
ci1jb2xvciI6ICIjMzQ5OGRiIiwgIm91dGxpbmUiOiAibm9uZSJ9LCAidGV4dGFyZWE6Zm9jdXMi
OiB7ImJvcmRlci1jb2xvciI6ICIjMzQ5OGRiIiwgIm91dGxpbmUiOiAibm9uZSJ9LCAiYnV0dG9u
IjogeyJ3aWR0aCI6ICIxMDAlIiwgInBhZGRpbmciOiAiMTJweCIsICJiYWNrZ3JvdW5kLWNvbG9y
IjogIiMyN2FlNjAiLCAiY29sb3IiOiAid2hpdGUiLCAiYm9yZGVyIjogIm5vbmUiLCAiY3Vyc29y
IjogInBvaW50ZXIiLCAiZm9udC1zaXplIjogIjFlbSJ9LCAiYnV0dG9uOmhvdmVyIjogeyJiYWNr
Z3JvdW5kLWNvbG9yIjogIiMyZWNjNzEifX0=
"""
    },
    'Cursors': {
        'css_path': '/home/labDirectory/part-2/style.css',
        'blob': """
eyIjZHJhZ2dhYmxlLWdlbSI6IHsiY3Vyc29yIjogIm1vdmUifSwgIiNsb2NrZWQtY2Fza2V0Ijog
eyJjdXJzb3IiOiAibm90LWFsbG93ZWQifSwgIiNoZWxwLXNjcm9sbCI6IHsiY3Vyc29yIjogImhl
bHAifSwgIiN0ZXh0LXBsYXF1ZSI6IHsiY3Vyc29yIjogInRleHQifSwgIiNhY3RpdmF0ZS1tZWNo
YW5pc20iOiB7ImN1cnNvciI6ICJ3YWl0In0sICIjbWFwLWdyaWQiOiB7ImN1cnNvciI6ICJjcm9z
c2hhaXIifSwgImJ1dHRvbi5hcnRpZmFjdCI6IHsiY3Vyc29yIjogInBvaW50ZXIifX0=
"""
    },
    'Gallery': {
        'css_path': '/home/labDirectory/part-3/style.css',
        'blob': """
eyIuZ2FsbGVyeS1pbWFnZSI6IHsibWF4LXdpZHRoIjogIjEwMCUiLCAiaGVpZ2h0IjogImF1dG8i
LCAiYm9yZGVyIjogIjVweCBzb2xpZCAjNDQ0IiwgImJveC1zaGFkb3ciOiAiMCA0cHggOHB4IHJn
YmEoMCwwLDAsMC4yKSIsICJkaXNwbGF5IjogImJsb2NrIiwgInRyYW5zaXRpb24iOiAib3BhY2l0
eSAwLjNzIGVhc2UifSwgIi5hcnQtcGllY2UiOiB7InBhZGRpbmciOiAiMjBweCIsICJiYWNrZ3Jv
dW5kLWNvbG9yIjogIiNlMGUwZTAiLCAiZGlzcGxheSI6ICJpbmxpbmUtYmxvY2sifSwgIi5hcnQt
cGllY2U6aG92ZXIgLmdhbGxlcnktaW1hZ2UiOiB7Im9wYWNpdHkiOiAiMC44In19
"""
    }
}

overall = {"data": []}
test_id_counter = 0

def append_result(score, maximum, message):
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
    if not os.path.exists(path):
        return ""
    with open(path, encoding='utf-8') as f:
        return f.read()

def normalize_selector(sel):
    return sel.strip().lower().replace('"', "").replace("'", "").replace(" ", "")

def normalize_value(val):
    return val.strip().lower().replace(" ", "")

def get_final_style_for_selector(sheet, target_selector):
    final_style = {}
    target_norm = normalize_selector(target_selector)
    for rule in sheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            for s in rule.selectorText.split(','):
                if normalize_selector(s) == target_norm:
                    for prop in rule.style:
                        final_style[prop.name.lower()] = prop.value
    return final_style

def evaluate_part(part_name, css_path, expected_rules):
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
            if prop.lower() not in final_style:
                append_result(0, 1, f"({part_name}) Rule `{selector}` missing property `{prop}`.")
            else:
                actual_raw = final_style[prop.lower()]
                if normalize_value(exp) == normalize_value(actual_raw):
                    append_result(1, 1, f"({part_name}) Correct: `{selector}` has `{prop}: {actual_raw}`.")
                else:
                    append_result(0, 1, f"({part_name}) Incorrect: `{selector}` has `{prop}: {actual_raw}`; expected `{exp}`.")

def main():
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


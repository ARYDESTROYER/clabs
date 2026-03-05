#!/usr/bin/env python3
"""
Autograder for Lab-G: Stored XSS Tutorial
Grading model:
- Activity 1: Recon + FLAG1
- Activity 2: ZAP analysis artifact
- Activity 3: Basic XSS payload artifact
- Activity 4: Admin escalation + FLAG4
"""
import os
import json
import urllib.parse
import urllib.request

# ... (imports remain)

LAB_DIR = '/home/labDirectory'
FLAGS_DIR = '/opt'
OUTPUT_FILE = '/home/.evaluationScripts/evaluate.json'

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except:
        return None

def test_activity1_recon(max_marks=34):
    """Activity 1: Reconnaissance + FLAG1"""
    test_result = {
        "testid": 1,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    master_flag1 = read_file(os.path.join(FLAGS_DIR, 'masterflag1.txt'))
    if not master_flag1:
        test_result["message"] = "FLAG1 not generated. Visit main app sections (home, products, cart, reviews)."
        return test_result

    submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))
    if submitted_flags and master_flag1 in submitted_flags:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ Activity 1 complete. FLAG1 verified."
    else:
        test_result["message"] = "FLAG1 exists but is missing from /home/labDirectory/flag.txt"

    return test_result

def test_activity3_basic_xss(max_marks=33):
    """Activity 3: Basic stored XSS payload quality"""
    test_result = {
        "testid": 2,  # Renumbered
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    payload = read_file(os.path.join(LAB_DIR, 'xss-payload.txt'))
    if not payload:
        test_result["message"] = "Missing payload file: /home/labDirectory/xss-payload.txt"
        return test_result

    payload_lower = payload.lower()
    feedback = []

    event_handlers = ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onsubmit']
    has_event_handler = any(h in payload_lower for h in event_handlers)
    has_html_vector = ('<img' in payload_lower) or ('<svg' in payload_lower) or ('<iframe' in payload_lower)
    has_js_intent = any(k in payload_lower for k in ['alert(', 'fetch(', 'document.', 'window.'])

    if has_event_handler: feedback.append("✓ Event-handler based execution vector detected")
    else: feedback.append("✗ No event-handler vector detected")

    if has_html_vector: feedback.append("✓ HTML injection vector detected")
    else: feedback.append("✗ No HTML injection vector detected")

    if has_js_intent: feedback.append("✓ JavaScript execution intent detected")
    else: feedback.append("✗ No JavaScript execution intent detected")

    if has_event_handler and has_html_vector and has_js_intent:
        test_result["status"] = "pass"
        test_result["score"] = max_marks

    test_result["message"] = "\n".join(feedback)
    return test_result

def test_activity4_admin_escalation(max_marks=33):
    """Activity 4: Admin escalation + FLAG4"""
    test_result = {
        "testid": 3, # Renumbered
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))
    if not submitted_flags:
        test_result["message"] = "Missing /home/labDirectory/flag.txt"
        return test_result

    master_flag4 = read_file(os.path.join(FLAGS_DIR, 'masterflag4.txt'))
    if not master_flag4:
        test_result["message"] = "FLAG4 not generated yet. Admin profile API likely not hit in admin context."
        return test_result

    if master_flag4 in submitted_flags:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ Activity 4 complete. FLAG4 verified."
    else:
        # FIXED: Do NOT reveal expected flag
        test_result["message"] = "FLAG4 not found in /home/labDirectory/flag.txt."

    return test_result

def main():
    print("=" * 60)
    print("Lab-G Autograder: Stored XSS Tutorial")
    print("=" * 60)

    results = []

    print("\n[Activity 1] Basic Recon + FLAG1...")
    results.append(test_activity1_recon(34))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Activity 3] First XSS Payload...")
    results.append(test_activity3_basic_xss(33))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Activity 4] Admin Escalation + FLAG4...")
    results.append(test_activity4_admin_escalation(33))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    total_score = sum(r['score'] for r in results)
    max_score = sum(r['maximum marks'] for r in results)

    print("\n" + "=" * 60)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print("=" * 60)

    output = {"data": results}
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    return 0 if total_score >= 70 else 1

if __name__ == '__main__':
    raise SystemExit(main())

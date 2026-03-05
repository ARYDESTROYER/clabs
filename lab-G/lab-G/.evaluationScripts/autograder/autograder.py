#!/usr/bin/env python3
"""
Autograder for Lab-G: Stored XSS & OWASP ZAP Challenge
Validates student submissions and compares with master flags
"""
import os
import json
import re
from pathlib import Path

# Paths
LAB_DIR = '/home/labDirectory'
FLAGS_DIR = '/opt'  # Changed to match clab standard
OUTPUT_FILE = '/home/.evaluationScripts/evaluate.json'

def read_file(filepath):
    """Read file content, return None if not exists"""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)

def test_reconnaissance(max_marks=15):
    """Test 1: Reconnaissance Complete (FLAG1)"""
    test_result = {
        "testid": 1,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    # Check if FLAG1 was generated
    flag1_file = os.path.join(FLAGS_DIR, 'masterflag1.txt')
    master_flag1 = read_file(flag1_file)

    if not master_flag1:
        test_result["message"] = "FLAG1 not generated. You need to access all main pages: home, products, cart, and reviews."
        return test_result

    # Check if student submitted the flag
    submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))

    if submitted_flags and master_flag1 in submitted_flags:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ Reconnaissance complete! FLAG1 correct: {master_flag1}"
    else:
        test_result["message"] = f"FLAG1 exists but not submitted. Explore the application and copy FLAG1 to flag.txt"

    return test_result

def test_zap_scan(max_marks=20):
    """Test 2: OWASP ZAP Scanning (FLAG2)"""
    test_result = {
        "testid": 2,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    # Check if ZAP report exists
    zap_report = os.path.join(LAB_DIR, 'zap-report.html')

    if not file_exists(zap_report):
        test_result["message"] = "ZAP report not found. Generate and save report to /home/labDirectory/zap-report.html"
        return test_result

    # Read report content
    report_content = read_file(zap_report)

    if not report_content:
        test_result["message"] = "ZAP report is empty"
        return test_result

    # Check for XSS findings in report
    xss_keywords = ['cross site scripting', 'xss', 'Cross-Site Scripting']
    has_xss_finding = any(keyword.lower() in report_content.lower() for keyword in xss_keywords)

    if not has_xss_finding:
        test_result["message"] = "ZAP report doesn't contain XSS findings. Run active scan with XSS policies enabled."
        test_result["score"] = int(max_marks * 0.3)  # Partial credit for report
        return test_result

    # Check FLAG2
    flag2_file = os.path.join(FLAGS_DIR, 'masterflag2.txt')
    master_flag2 = read_file(flag2_file)

    submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))

    if master_flag2 and submitted_flags and master_flag2 in submitted_flags:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ ZAP scan complete with XSS findings! FLAG2 correct: {master_flag2}"
    else:
        test_result["score"] = int(max_marks * 0.7)  # Most credit for finding XSS
        test_result["message"] = "ZAP scan found XSS but FLAG2 not submitted correctly"

    return test_result

def test_payload_crafting(max_marks=30):
    """Test 3: XSS Payload Crafting (FLAG3)"""
    test_result = {
        "testid": 3,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    # Check if payload file exists
    payload_file = os.path.join(LAB_DIR, 'xss-payload.txt')
    payload = read_file(payload_file)

    if not payload:
        test_result["message"] = "XSS payload not found. Save your working payload to /home/labDirectory/xss-payload.txt"
        return test_result

    # Check payload characteristics
    score = 0
    feedback = []

    # 1. Check for event handlers (bypass <script> filter)
    event_handlers = ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onsubmit']
    has_event_handler = any(handler in payload.lower() for handler in event_handlers)

    if has_event_handler:
        score += 10
        feedback.append("✓ Uses event handler to bypass script tag filter")
    else:
        feedback.append("✗ No event handler found (needed to bypass <script> filter)")

    # 2. Check for exfiltration logic
    exfil_keywords = ['fetch', 'xmlhttprequest', 'xhr', 'image', 'img']
    has_exfiltration = any(keyword in payload.lower() for keyword in exfil_keywords)

    if has_exfiltration:
        score += 10
        feedback.append("✓ Contains exfiltration mechanism")
    else:
        feedback.append("✗ No exfiltration logic found")

    # 3. Check for exploit server reference
    if 'exploit' in payload.lower() or '8000' in payload or 'exfil' in payload.lower():
        score += 5
        feedback.append("✓ References exploit server")

    # 4. Check if FLAG3 was generated (exploit server received callback)
    flag3_file = os.path.join(FLAGS_DIR, 'masterflag3.txt')
    master_flag3 = read_file(flag3_file)

    if master_flag3:
        score += 5
        feedback.append("✓ Payload successfully executed (exploit server received callback)")

        # Check if FLAG3 submitted
        submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))
        if submitted_flags and master_flag3 in submitted_flags:
            test_result["status"] = "pass"
            test_result["score"] = max_marks
            test_result["message"] = f"{chr(10).join(feedback)}\n✓ FLAG3 correct: {master_flag3}"
            return test_result

    test_result["score"] = score
    test_result["message"] = "\n".join(feedback)

    if score >= 20:
        test_result["message"] += "\n⚠ Payload looks good but FLAG3 not generated. Wait for victim bot to trigger it."

    return test_result

def test_exfiltration(max_marks=30):
    """Test 4: Data Exfiltration (FLAG4)"""
    test_result = {
        "testid": 4,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    # Check if exfiltrated flag file exists
    exfil_file = os.path.join(LAB_DIR, 'exfiltrated-flag.txt')
    exfiltrated_flag = read_file(exfil_file)

    if not exfiltrated_flag:
        test_result["message"] = "No exfiltrated data found. Check exploit server dashboard at http://localhost:30000/dashboard"
        return test_result

    # Check FLAG4
    flag4_file = os.path.join(FLAGS_DIR, 'masterflag4.txt')
    master_flag4 = read_file(flag4_file)

    if not master_flag4:
        test_result["message"] = "FLAG4 not generated yet. Admin profile API hasn't been called. Wait for victim bot."
        test_result["score"] = int(max_marks * 0.3)  # Partial for having exfiltration
        return test_result

    # Compare flags
    if exfiltrated_flag == master_flag4:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ Admin session hijacked! FLAG4 correct: {master_flag4}\nSuccessfully exfiltrated admin's secret data!"
    else:
        test_result["score"] = int(max_marks * 0.5)
        test_result["message"] = f"Exfiltrated flag doesn't match. Expected: {master_flag4}, Got: {exfiltrated_flag}"

    return test_result

def test_bonus_documentation(max_marks=5):
    """Bonus Test: Vulnerability Report"""
    test_result = {
        "testid": 5,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    report_file = os.path.join(LAB_DIR, 'vulnerability-report.md')
    report = read_file(report_file)

    if not report:
        test_result["message"] = "Bonus: No vulnerability report found"
        return test_result

    # Check for key sections
    score = 0
    required_sections = ['description', 'impact', 'remediation']
    found_sections = [section for section in required_sections if section in report.lower()]

    if len(found_sections) >= 3:
        score = max_marks
        test_result["status"] = "pass"
        test_result["message"] = "✓ Bonus: Professional vulnerability report submitted"
    elif len(found_sections) >= 2:
        score = int(max_marks * 0.6)
        test_result["message"] = f"Bonus: Report found but missing sections: {set(required_sections) - set(found_sections)}"
    else:
        test_result["message"] = "Bonus: Report incomplete"

    test_result["score"] = score
    return test_result

def main():
    """Run all tests and generate evaluation JSON"""
    print("=" * 60)
    print("Lab-G Autograder: Stored XSS & OWASP ZAP")
    print("=" * 60)

    results = []

    # Run all tests
    print("\n[Test 1] Reconnaissance...")
    results.append(test_reconnaissance(15))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Test 2] ZAP Scanning...")
    results.append(test_zap_scan(20))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Test 3] Payload Crafting...")
    results.append(test_payload_crafting(30))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Test 4] Data Exfiltration...")
    results.append(test_exfiltration(30))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Bonus] Vulnerability Report...")
    results.append(test_bonus_documentation(5))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    # Calculate total
    total_score = sum(r['score'] for r in results)
    max_score = sum(r['maximum marks'] for r in results)

    print("\n" + "=" * 60)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print("=" * 60)

    # Generate output JSON
    output = {"data": results}

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results written to {OUTPUT_FILE}")

    return 0 if total_score >= (max_score * 0.7) else 1

if __name__ == '__main__':
    exit(main())

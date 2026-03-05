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

LAB_DIR = '/home/labDirectory'
FLAGS_DIR = '/opt'
OUTPUT_FILE = '/home/.evaluationScripts/evaluate.json'
ZAP_API_BASE = os.environ.get('ZAP_API_BASE', 'http://localhost:30003')


def read_file(filepath):
    """Read file content and return stripped text, or None if unavailable."""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def file_exists(filepath):
    """Check whether a file exists."""
    return os.path.exists(filepath)

def zap_api_json(path, params=None, timeout=8):
    """Call ZAP API endpoint and return parsed JSON."""
    query = urllib.parse.urlencode(params or {})
    url = f"{ZAP_API_BASE}{path}"
    if query:
        url = f"{url}?{query}"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def test_activity1_recon(max_marks=25):
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
        test_result["message"] = f"✓ Activity 1 complete. FLAG1 verified: {master_flag1}"
    else:
        test_result["message"] = "FLAG1 exists but is missing from /home/labDirectory/flag.txt"

    return test_result


def test_activity2_zap(max_marks=25):
    """Activity 2: Auto-detect that ZAP was run against the target."""
    test_result = {
        "testid": 2,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    try:
        urls_resp = zap_api_json('/JSON/core/view/urls/', {'baseurl': 'http://localhost:30000'})
        alerts_resp = zap_api_json('/JSON/core/view/alerts/', {
            'baseurl': 'http://localhost:30000',
            'start': '0',
            'count': '5000'
        })

        urls = urls_resp.get('urls', []) if isinstance(urls_resp, dict) else []
        alerts = alerts_resp.get('alerts', []) if isinstance(alerts_resp, dict) else []

        has_target_urls = any('localhost:30000' in u for u in urls)
        has_auth_path = any('/login' in u for u in urls)
        has_review_path = any(('/reviews' in u) or ('/product/' in u) or ('/review' in u) for u in urls)

        # Pass criteria: any evidence that ZAP ran against the lab target.
        has_target_alerts = len(alerts) > 0
        if has_target_urls or has_target_alerts:
            test_result["status"] = "pass"
            test_result["score"] = max_marks
            test_result["message"] = "✓ Activity 2 complete. ZAP run detected on target."
            return test_result

        if has_auth_path or has_review_path:
            # Defensive fallback in case baseurl filtering changes behavior.
            test_result["status"] = "pass"
            test_result["score"] = max_marks
            test_result["message"] = "✓ Activity 2 complete. ZAP run detected on target paths."
            return test_result
    except Exception as e:
        # Fallback for environments where API access is unavailable.
        print(f"ZAP API detection failed: {e}")

    # Fallback: if a report file exists, treat that as evidence of ZAP usage.
    zap_report = os.path.join(LAB_DIR, 'zap-report.html')
    report_content = read_file(zap_report) if file_exists(zap_report) else None
    if report_content:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = "✓ Activity 2 complete. ZAP usage detected from fallback report artifact."
        return test_result

    test_result["message"] = (
        "No ZAP scan evidence detected yet. Run Spider/Active Scan against http://localhost:30000."
    )
    return test_result


def test_activity3_basic_xss(max_marks=25):
    """Activity 3: Basic stored XSS payload quality (tutorial milestone, no flag)"""
    test_result = {
        "testid": 3,
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

    # Binary pass checks for a realistic first XSS payload
    event_handlers = ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onsubmit']
    has_event_handler = any(h in payload_lower for h in event_handlers)
    has_html_vector = ('<img' in payload_lower) or ('<svg' in payload_lower) or ('<iframe' in payload_lower)
    has_js_intent = any(k in payload_lower for k in ['alert(', 'fetch(', 'document.', 'window.'])

    if has_event_handler:
        feedback.append("✓ Event-handler based execution vector detected")
    else:
        feedback.append("✗ No event-handler vector detected")

    if has_html_vector:
        feedback.append("✓ HTML injection vector detected")
    else:
        feedback.append("✗ No HTML injection vector detected")

    if has_js_intent:
        feedback.append("✓ JavaScript execution intent detected")
    else:
        feedback.append("✗ No JavaScript execution intent detected")

    if has_event_handler and has_html_vector and has_js_intent:
        test_result["status"] = "pass"
        test_result["score"] = max_marks

    test_result["message"] = "\n".join(feedback)
    return test_result


def test_activity4_admin_escalation(max_marks=25):
    """Activity 4: Admin escalation + FLAG4"""
    test_result = {
        "testid": 4,
        "status": "fail",
        "score": 0,
        "maximum marks": max_marks,
        "message": ""
    }

    submitted_flags = read_file(os.path.join(LAB_DIR, 'flag.txt'))
    if not submitted_flags:
        test_result["message"] = "Missing /home/labDirectory/flag.txt (submit FLAG1 and FLAG4)."
        return test_result

    master_flag4 = read_file(os.path.join(FLAGS_DIR, 'masterflag4.txt'))
    if not master_flag4:
        test_result["message"] = "FLAG4 not generated yet. Admin profile API likely not hit in admin context."
        return test_result

    if master_flag4 in submitted_flags:
        test_result["status"] = "pass"
        test_result["score"] = max_marks
        test_result["message"] = f"✓ Activity 4 complete. FLAG4 verified: {master_flag4}"
    else:
        test_result["message"] = (
            f"FLAG4 not found in /home/labDirectory/flag.txt. "
            f"Expected value: {master_flag4}"
        )

    return test_result


def main():
    """Run all activity checks and write evaluate.json."""
    print("=" * 60)
    print("Lab-G Autograder: Stored XSS Tutorial")
    print("=" * 60)

    results = []

    print("\n[Activity 1] Basic Recon + FLAG1...")
    results.append(test_activity1_recon(25))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Activity 2] ZAP Analysis...")
    results.append(test_activity2_zap(25))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Activity 3] First XSS Payload...")
    results.append(test_activity3_basic_xss(25))
    print(f"  Score: {results[-1]['score']}/{results[-1]['maximum marks']}")

    print("\n[Activity 4] Admin Escalation + FLAG4...")
    results.append(test_activity4_admin_escalation(25))
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

    print(f"\n✓ Results written to {OUTPUT_FILE}")
    return 0 if total_score >= 70 else 1


if __name__ == '__main__':
    main()

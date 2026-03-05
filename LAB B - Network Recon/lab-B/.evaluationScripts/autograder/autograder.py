#!/usr/bin/env python3
import json
import os
import re

LAB_DIR = '/home/labDirectory'
FLAGS_DIR = '/opt'
OUTPUT_FILE = '/home/.evaluationScripts/evaluate.json'


def read_file(path):
    try:
        with open(path, 'r') as handle:
            return handle.read().strip()
    except FileNotFoundError:
        return None


def flag_value(flag_name):
    digits = ''.join(ch for ch in flag_name if ch.isdigit())
    if not digits:
        return None
    return read_file(os.path.join(FLAGS_DIR, f'masterflag{digits}.txt'))


def contains_keywords(content, keywords):
    if not content:
        return False
    lowered = content.lower()
    return all(keyword.lower() in lowered for keyword in keywords)


def load_submission_flags():
    content = read_file(os.path.join(LAB_DIR, 'flag.txt'))
    if not content:
        return set()
    return {line.strip() for line in content.splitlines() if line.strip()}


def test_service_discovery(max_marks=25):
    result = {
        'testid': 1,
        'status': 'fail',
        'score': 0,
        'maximum marks': max_marks,
        'message': ''
    }

    discovery = read_file(os.path.join(LAB_DIR, 'discovery.txt'))
    if not discovery:
        result['message'] = 'discovery.txt not found in /home/labDirectory'
        return result

    if not contains_keywords(discovery, ['apache', 'modsecurity']):
        result['message'] = 'discovery.txt missing required keywords (Apache, ModSecurity)'
        return result

    if not re.search(r'\b(80|30000)\b', discovery):
        result['message'] = 'discovery.txt must mention the exposed port (80 or 30000)'
        return result

    master_flag = flag_value('flag1')
    if not master_flag:
        result['message'] = 'FLAG1 not generated yet (bypass the search filter on /rest/products/search)'
        return result

    submitted = load_submission_flags()
    if master_flag in submitted:
        result['status'] = 'pass'
        result['score'] = max_marks
        result['message'] = 'WAF fingerprinting validated and FLAG1 correct'
    else:
        result['message'] = 'FLAG1 generated but not submitted in flag.txt'

    return result


def test_enumeration(max_marks=25):
    result = {
        'testid': 2,
        'status': 'fail',
        'score': 0,
        'maximum marks': max_marks,
        'message': ''
    }

    enumeration = read_file(os.path.join(LAB_DIR, 'enumeration.txt'))
    if not enumeration:
        result['message'] = 'enumeration.txt not found in /home/labDirectory'
        return result

    endpoints = [line.strip() for line in enumeration.splitlines() if line.strip()]
    if len(endpoints) < 10:
        result['message'] = 'enumeration.txt must contain at least 10 endpoints'
        return result

    invalid = [line for line in endpoints if not (line.startswith('/') or line.startswith('http'))]
    if invalid:
        result['message'] = 'enumeration.txt contains invalid endpoint entries'
        return result

    if not any('/internal/' in line for line in endpoints):
        result['message'] = 'enumeration.txt must include at least one /internal/ endpoint'
        return result

    master_flag = flag_value('flag2')
    if not master_flag:
        result['message'] = 'FLAG2 not generated yet (bypass internal ACL to access /internal/device-status)'
        return result

    submitted = load_submission_flags()
    if master_flag in submitted:
        result['status'] = 'pass'
        result['score'] = max_marks
        result['message'] = 'Enumeration validated and FLAG2 correct'
    else:
        result['message'] = 'FLAG2 generated but not submitted in flag.txt'

    return result


def test_waf_bypass(max_marks=30):
    result = {
        'testid': 3,
        'status': 'fail',
        'score': 0,
        'maximum marks': max_marks,
        'message': ''
    }

    bypass = read_file(os.path.join(LAB_DIR, 'bypass-technique.txt'))
    if not bypass:
        result['message'] = 'bypass-technique.txt not found in /home/labDirectory'
        return result

    if 'x-original-url' not in bypass.lower():
        result['message'] = 'bypass-technique.txt must mention X-Original-URL header'
        return result

    master_flag = flag_value('flag3')
    if not master_flag:
        result['message'] = 'FLAG3 not generated yet'
        return result

    submitted = load_submission_flags()
    if master_flag in submitted:
        result['status'] = 'pass'
        result['score'] = max_marks
        result['message'] = 'WAF bypass validated and FLAG3 correct'
    else:
        result['message'] = 'FLAG3 generated but not submitted in flag.txt'

    return result


def test_data_exfiltration(max_marks=20):
    result = {
        'testid': 4,
        'status': 'fail',
        'score': 0,
        'maximum marks': max_marks,
        'message': ''
    }

    master_flag = flag_value('flag4')
    if not master_flag:
        result['message'] = 'FLAG4 not generated yet'
        return result

    submitted = load_submission_flags()
    if master_flag in submitted:
        result['status'] = 'pass'
        result['score'] = max_marks
        result['message'] = 'Admin data access validated and FLAG4 correct'
    else:
        result['message'] = 'FLAG4 generated but not submitted in flag.txt'

    return result


def main():
    results = [
        test_service_discovery(25),
        test_enumeration(25),
        test_waf_bypass(30),
        test_data_exfiltration(20)
    ]

    output = {'data': results}
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as handle:
        json.dump(output, handle, indent=2)

    total_score = sum(r['score'] for r in results)
    max_score = sum(r['maximum marks'] for r in results)
    return 0 if total_score >= (max_score * 0.7) else 1


if __name__ == '__main__':
    raise SystemExit(main())

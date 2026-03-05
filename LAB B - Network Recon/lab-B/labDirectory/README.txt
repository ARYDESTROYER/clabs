Lab-B: Network Recon & Device Efficacy Audit
=============================================

Objective:
- Assess WAF/firewall effectiveness
- Discover hidden admin console
- Use header tampering to bypass controls

Target:
- http://localhost:30000

Services:
- OWASP ZAP GUI: http://localhost:30004 (browser-based)
- ZAP API: http://localhost:30003
- ZAP Proxy: http://localhost:8080

How to capture flags:
- FLAG1: send a successful /rest/products/search request that contains a UNION SELECT-style payload and copy the X-Lab-Flag1 response header.
- FLAG2: access /internal/device-status and copy the JSON field flag (requires X-Forwarded-For: 10.0.0.1).
- FLAG3: reach /admin-console via the misapplied X-Original-URL routing header and copy the FLAG3: value in the HTML.
- FLAG4: reach /rest/admin/application-version via the same routing issue and copy the JSON field flag.

Submission Files:
- discovery.txt
- enumeration.txt
- bypass-technique.txt
- flag.txt

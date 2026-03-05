# Lab-B: Network Recon & Device Efficacy Audit

**Duration**: 20-30 minutes | **Difficulty**: Intermediate | **Type**: Infrastructure Security

## Overview
Assess the edge defenses, enumerate the exposed paths, and exploit the controlled misconfigurations to reach the internal admin interface.

## Lab setup
- Entry point: `http://localhost:30000`
- WAF: Apache with ModSecurity (OWASP CRS)
- Backend: Juice Shop (proxied through Apache)
- ZAP GUI: `http://localhost:30004`
- ZAP API: `http://localhost:30003`
- ZAP Proxy: `http://localhost:8080`

## Key observations
- Apache reroutes requests using the `X-Original-URL` header (`.evaluationScripts/activityInitiator/config/apache/juiceshop.single.conf`).
- ModSecurity blocks `/admin*` and `/rest/admin*` based on `REQUEST_URI`, but the rewrite lets a safe path plus `X-Original-URL` reach those endpoints.
- `/internal/*` endpoints trust `X-Forwarded-For: 10.x.x.x`, so a spoofed header mimicking the internal network is accepted (`.evaluationScripts/activityInitiator/config/apache/custom-rules.conf`).

## Tasks (flags)
1. **FLAG1** – Bypass the filter on `/rest/products/search` with an encoded payload (e.g., `UNION SELECT` with `%20` instead of spaces). Capture the `X-Lab-Flag1` header.
2. **FLAG2** – Access `/internal/device-status` with `X-Forwarded-For: 10.0.0.1` and read the `flag` field from the JSON response.
3. **FLAG3** – Send requests to `/public/` while setting `X-Original-URL: /admin-console`; the returned HTML contains `FLAG3`.
4. **FLAG4** – Use the same routing trick to reach `/rest/admin/application-version` and read the `flag` entry in the JSON output.

## Deliverables
Inside the running lab container, create these files under `/home/labDirectory/`:
- `discovery.txt`: mention `Apache`, `ModSecurity`, and port `30000`.
- `enumeration.txt`: list 10+ endpoints, including at least one `/internal/` path.
- `bypass-technique.txt`: describe the working request that uses `X-Original-URL`.
- `flag.txt`: list FLAG1–FLAG4, one per line.

## Evaluation
```bash
sh /home/.evaluationScripts/evaluate.sh
```

## Quick start
```bash
docker build -t trustlab-lab-b ./lab-B
docker run -d --rm --name trustlab-lab-b -p 30000:30000 -p 30003:30003 -p 30004:30004 -p 8080:8080 trustlab-lab-b
```

## Recommended tools
nmap, curl, Burp Suite, OWASP ZAP, gobuster, tcpdump

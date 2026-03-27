# Activity 1 Walkthrough: Recon and Safe Scanning Baseline

## Objective
Map the target surface safely with OWASP ZAP and capture FLAG1 from the hidden scan checkpoint endpoint.

## Services
- Target app: `http://localhost:30000`
- ZAP Web UI (WebSwing): `http://localhost:30004/zap`

## Safe Scanning Rules
- Scope only `localhost:30000`.
- Do not scan external hosts.
- Start with manual browse + spider + passive scan.

## Step-by-Step

### 1. Open the application
1. Visit `http://localhost:30000`.
2. Explore pages:
- `/`
- `/products`
- `/reviews`
- `/robots.txt`

### 2. Launch ZAP browser UI
1. Open `http://localhost:30004/zap`.
2. In ZAP, define context/scope for `http://localhost:30000`.

### 3. Run baseline crawl
1. Use the Sites tree and run Spider on `http://localhost:30000`.
2. Let passive scan finish.
3. Inspect discovered paths; focus on hidden or non-linked endpoints.

### 4. Discover checkpoint endpoint
1. Use `robots.txt` hint and discovered paths.
2. Visit `http://localhost:30000/hidden/scan-checkpoint`.
3. Capture response header `X-Lab-Flag1`.

You can also verify with curl:
```bash
curl -i http://localhost:30000/hidden/scan-checkpoint
```

### 5. Fill submission files
Under `/home/labDirectory`:
- `recon.txt`: include at least `/reviews`, `/products`, `/hidden/scan-checkpoint`.
- `zap-findings.txt`: include one relevant XSS/security observation from ZAP.
- `flag.txt`: paste only FLAG1 (format: `IITB{...}`).

### 6. Evaluate
```bash
bash /home/.evaluationScripts/evaluate.sh
```

## Troubleshooting
- If ZAP UI seems blank, reload `http://localhost:30004/zap` after 15-20 seconds.
- If checkpoint not seen in Spider, manually browse `/robots.txt` and follow the hint.
- If grading fails, verify exact filename and no extra spaces/newlines in `flag.txt`.

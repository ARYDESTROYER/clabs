# Activity 2 Walkthrough: Stored XSS Payload Crafting

## Objective
Exploit stored XSS in `/reviews`, trigger execution in victim flow, and submit FLAG2.

## Services
- Target app: `http://localhost:30000`
- Vulnerable feature: `http://localhost:30000/reviews`
- ZAP Web UI: `http://localhost:30004/zap`

## Key Behavior
- Input sanitization is intentionally weak.
- `<script>` tags are stripped, but event-handler payloads can still execute.
- A victim worker periodically revisits comments and processes payload-like content.

## Step-by-Step

### 1. Open reviews page
1. Visit `http://localhost:30000/reviews`.
2. Confirm comment form is functional.

### 2. Craft payload
Use an event-handler style payload, for example:
```html
<img src=x onerror="fetch('/collect?d=probe')">
```

### 3. Submit payload
1. Post payload as a review comment.
2. Refresh and confirm payload is rendered back in review list.

### 4. Wait for victim cycle
- Victim worker runs periodically.
- Wait around 10-15 seconds, then request proof endpoint:
```bash
curl -s http://localhost:30000/api/activity2/proof
```
If successful, response contains:
```json
{"flag":"IITB{labg_a2_stored_xss_triggered}"}
```

### 5. Fill submission files
Under `/home/labDirectory`:
- `xss-payload.txt`: paste payload used.
- `flag.txt`: paste only FLAG2.

### 6. Evaluate
```bash
bash /home/.evaluationScripts/evaluate.sh
```

## Troubleshooting
- If proof still says XSS not triggered, submit payload again and wait one victim interval.
- Avoid `<script>...</script>` payloads; use `onerror`/`onload` style instead.
- Keep `flag.txt` as only one line with exact flag value.

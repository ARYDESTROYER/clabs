# Activity 3: Victim-Context Flag Exfiltration

## Objective
Use stored XSS to execute in victim context and exfiltrate the victim-only flag.

## Target
- Web app: `http://localhost:30000`
- ZAP WebSwing UI: `http://localhost:30004/zap`

## Tasks
1. Inject a stored payload into `/reviews`.
2. Payload should attempt victim-only data access (`/api/victim/profile`).
3. Exfiltrate the value to `/collect`.
4. Retrieve the leaked value via `/api/exfil/latest` and submit FLAG3.

## Submission Files
- `xss-payload.txt`
- `flag.txt`

## Evaluation
```bash
bash /home/.evaluationScripts/evaluate.sh
```

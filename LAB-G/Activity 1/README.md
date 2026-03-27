# Activity 1: Recon and Safe Scanning Baseline

## Objective
Use OWASP ZAP (browser UI) to map the application attack surface and identify endpoints relevant to stored XSS testing.

## Target
- Web app: `http://localhost:30000`
- ZAP WebSwing UI: `http://localhost:30004/zap`

## Tasks
1. Browse the app manually and identify key functionality paths.
2. Use ZAP Spider + passive scan in-scope (`localhost:30000` only).
3. Discover the hidden scanning checkpoint endpoint.
4. Capture FLAG1 and submit artifacts.

## Submission Files
- `recon.txt`
- `zap-findings.txt`
- `flag.txt`

## Evaluation
```bash
bash /home/.evaluationScripts/evaluate.sh
```

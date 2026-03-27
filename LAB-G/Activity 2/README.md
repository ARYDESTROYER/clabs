# Activity 2: Stored XSS Payload Crafting

## Objective
Exploit the stored XSS issue in the review flow and prove payload execution.

## Target
- Web app: `http://localhost:30000/reviews`
- ZAP WebSwing UI: `http://localhost:30004/zap`

## Tasks
1. Submit a payload that bypasses weak filtering.
2. Wait for victim bot visit cycle.
3. Confirm XSS trigger proof and capture FLAG2.

## Submission Files
- `xss-payload.txt`
- `flag.txt`

## Evaluation
```bash
bash /home/.evaluationScripts/evaluate.sh
```

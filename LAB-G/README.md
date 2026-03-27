# LAB-G: Web App Security - Stored XSS + OWASP ZAP

LAB-G is a browser-first, three-activity web security lab focused on:
- Safe web scanning with OWASP ZAP (WebSwing UI)
- Discovering stored XSS in a vulnerable comment workflow
- Exfiltrating a victim-only flag via script execution context

## Activities

1. Activity 1: Recon and safe scanning baseline
2. Activity 2: Stored XSS payload crafting and trigger proof
3. Activity 3: Victim-context flag exfiltration

Each activity includes a full step-by-step `WALKTHROUGH.md`:
- `LAB-G/Activity 1/WALKTHROUGH.md`
- `LAB-G/Activity 2/WALKTHROUGH.md`
- `LAB-G/Activity 3/WALKTHROUGH.md`

## Runtime Endpoints

- Target app: `http://localhost:30000`
- ZAP browser UI: `http://localhost:30004/zap`
- ZAP API: `http://localhost:30003`
- ZAP proxy: `http://localhost:8080`

## Design Notes

- The app intentionally uses weak sanitization by removing `<script>` tags only.
- The victim profile flag is not directly accessible to normal requests.
- Activity scripts use the `/tmp/evaluate.json` pattern for robust BodhiLabs grading.
- Submission files are created at runtime to avoid LMS read-only tarball issues.

## Activity Packaging

Each activity folder is deployable as an independent Bodhi activity and should contain:
- `student_directory.tgz` (archive of `labDirectory/`)
- `client_evaluation.tgz` (archive of `.evaluationScripts/`)

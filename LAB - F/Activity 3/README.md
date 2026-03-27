# Activity 3: Hardened Target Header Hunt (Exam)

## Objective

Apply the rebinding model against a hardened internal target where direct `/admin` access is blocked and sensitive data leaks via alternate telemetry.

This mirrors the mitigation-thinking outcome from the original plan. Burp is not required.

## Constraints

- Use the same victim hostname: `evil.attacker.local`
- `/admin` path is intentionally blocked when routed to `admin-b`
- Valid token is still present in this environment

## Starting Point

1. `cd /home/labDirectory`
2. `labfctl set evil.attacker.local admin-b`
3. `fetch-sim evil.attacker.local /admin`
4. `fetch-sim evil.attacker.local /healthz`
5. Extract the `IITB{...}` token and write it to `SUBMIT_FLAG.txt`

## Evidence Tools

- `labfctl logs proxy`
- `labfctl logs exfil`
- Browser UI: `http://127.0.0.1:8080`

## Submission

- Submit only `SUBMIT_FLAG.txt`.

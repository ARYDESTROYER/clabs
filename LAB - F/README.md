# LAB - F: Browser-First DNS Rebinding Lab

LAB - F is a three-stage, high-fidelity lab that models DNS rebinding behavior through an isolated multi-service runtime.

## Original Plan Alignment

- Objective: use DNS rebinding or host-file simulation to make a browser reach an internal admin endpoint and exfiltrate a token.
- Setup model: attacker page + internal admin target (conceptually `192.168.50.21:8080`) with rebinding emulation.
- Tools in this lab: browser, `fetch-sim`, `labfctl`, `curl`, and optional `python -m http.server` style testing.
- Explicitly out of scope: Burp Suite is not required for this lab.
- Estimated time: 30-40 minutes.
- Learning outcomes: Same-Origin Policy, rebinding mechanics, CORS boundaries, and common mitigations.

Note: the runtime emulates these concepts on localhost services to keep setup deterministic for grading.

## Runtime Architecture

Each activity starts a local service mesh with dedicated ports:

- `frontend` on `127.0.0.1:8080` (victim browser UI)
- `gateway` on `127.0.0.1:8081` (hostname-based router / rebinding pivot)
- `admin-a` on `127.0.0.1:8082` (vulnerable internal admin)
- `proxy-log` on `127.0.0.1:8083` (routing evidence)
- `exfil` on `127.0.0.1:8084` (token collection sink)
- `control` on `127.0.0.1:8085` (state control plane)
- `admin-b` on `127.0.0.1:8086` (hardened internal admin)

In the narrative, `admin-a`/`admin-b` represent the internal target (`192.168.50.21:8080`) reachable only after host pivot/rebinding.

## Activity Flow

1. Activity 1 (Guided): Manual host pivot to internal admin.
2. Activity 2 (Guided): Delayed DNS flip and token exfiltration evidence.
3. Activity 3 (Exam): Hardened target with header-only token discovery.

## Student Submission Contract

- Exactly one file per activity: `SUBMIT_FLAG.txt`
- Exactly one unique flag per activity
- No additional files are required

## Control Commands

- `labfctl status`
- `labfctl set evil.attacker.local admin-a`
- `labfctl arm 3`
- `labfctl logs proxy`
- `labfctl logs exfil`
- `fetch-sim evil.attacker.local /admin`

## Build

Use `LAB - F/Dockerfile` as the base image for all three activities.

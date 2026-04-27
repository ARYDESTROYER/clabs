> Audience: instructor / teaching staff

# LAB F &middot; Activity 1 &mdash; Map the threat model

Browser-first threat-model orientation for LAB F (DNS rebinding). No exploit yet &mdash; the student confirms what is and isn't reachable, then submits a flag they read off the internal admin from inside the container.

## Services
| Service | Bind | LMS-exposed |
| --- | --- | --- |
| Attacker dashboard | `0.0.0.0:30000` | yes |
| Internal admin | `127.0.0.1:8080` | no |

## What the autograder checks
- `flag.txt` matches `IITB{labf_a1_threat_model_mapped}` (the value baked into `/admin/welcome`).
- One test, 100 points, all-or-nothing.

## Setup notes for staff
- Both Flask servers carry the LAB-G compatibility shim for the IITB base image (Section 4.6.8 of `BODHILABS_COMPLETE_GUIDE.md`).
- Init script follows the multi-service template (Section 4.6.9): `nohup ... & disown`, port-poll verify, `pkill` for idempotency.
- `flag.txt`, `dns_config.json`, `attack_plan.json` are created at runtime &mdash; never in the tarball.

## Documentation
- `activity_guide.md` &mdash; **paste this into the LMS activity-description field**. It's the student-facing pedagogical doc.
- `WALKTHROUGH.md` &mdash; full instructor solution path.

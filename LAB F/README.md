# LAB F &mdash; DNS Rebinding & Same-Origin Policy Bypass

Three-activity browser-first web security lab focused on:
- The Same-Origin Policy and what it does (and doesn't) protect.
- DNS rebinding: how an attacker page can make a victim browser fetch from internal hosts.
- Realistic mitigations: `Host` allow-lists, DNS pinning, strong auth, segmentation.

## Activities

1. **Activity 1 &mdash; Map the threat model.** Confirm what is and isn't reachable. Submit FLAG1.
2. **Activity 2 &mdash; Perform the DNS rebind.** Edit `dns_config.json` + `attack_plan.json`, click "Run Bot", capture FLAG2.
3. **Activity 3 &mdash; Independent variation.** Same technique, new admin surface. No walkthrough.

## Runtime architecture (per activity, single container)

```
+---------------------+        +------------------------------+
|  Student's browser  |  -->   |  Attacker dashboard :30000   |  (LMS-exposed)
+---------------------+        |  + in-process victim bot     |
                               |  + fake DNS resolver         |
                               +---------------+--------------+
                                               |
                                               | (bot's HTTP fetches)
                                               v
                               +------------------------------+
                               |  Internal admin :8080        |  (loopback only)
                               +------------------------------+
```

The bot is in-process inside the attacker server, so "Run Bot" is synchronous and interactive -- no waiting for a background timer. Each activity runs both Flask services from `initactivity.sh` (LAB-G pattern, not supervisor).

## Why DNS rebinding is *emulated*

Real DNS rebinding requires a victim browser whose DNS resolution we can manipulate. In BodhiLabs the student's browser is on their own machine, beyond our control. We replace the victim browser with a Python "victim bot" inside the container that:

- Resolves hostnames via `/home/labDirectory/dns_config.json`.
- Enforces Same-Origin Policy on follow-up fetches by hostname.

The lesson is identical: same-hostname URLs at TOCTOU between resolution and origin-checking, the bot can be tricked into hitting an "internal" host.

## Bodhi-specific design choices

- `/tmp/evaluate.json` write pattern (Section 7.7 of `BODHILABS_COMPLETE_GUIDE.md`).
- Submission and config files created at runtime by `initactivity.sh` -- never baked into the tarball (Section 7.1 / 7.8).
- LAB-G-style background service launches inside `initactivity.sh`.
- `student` ownership re-applied each container start.
- Temporary sudo dropped at end of init (Section 7.3).

## Per-activity layout (BodhiLabs deployable)

Per Section 3.1 / 4.5 of the BodhiLabs guide:

```
Activity N/
+- Dockerfile
+- README.md              <- instructor-facing; not in any tarball
+- WALKTHROUGH.md         <- instructor-facing; full solution; not in any tarball
+- activity_guide.md      <- STUDENT-FACING; paste into LMS activity-description field
+- labDirectory/          <- empty in tarball; init.sh creates submission files at runtime
+- .evaluationScripts/
   +- evaluate.sh
   +- autograder.py
   +- evaluate.json       <- placeholder; /tmp pattern overwrites it
   +- activityInitiator/
      +- initactivity.sh
      +- attacker_server.py
      +- admin_server.py
```

The three top-level docs (`README.md`, `WALKTHROUGH.md`, `activity_guide.md`) live at the activity root and are NOT packaged into either tarball. The first two are reference for staff; the third is the pedagogical guide whose contents you paste into the LMS lab-page description field.

To package, run `bash prepup.sh` from the LAB F root. It produces `client_evaluation.tgz` and `student_directory.tgz` in each activity folder.

## Scoring

| Activity | Tests | Total |
| --- | --- | --- |
| 1 | 1 (flag.txt) | 100 |
| 2 | 2 (flag.txt + bot exfil event) | 100 |
| 3 | 2 (flag.txt + bot exfil event) | 100 |

## Files

- `Activity 1/`, `Activity 2/`, `Activity 3/` &mdash; deployable activities.
- `_shared_runtime/` &mdash; canonical source for the runtime services. Each activity's `activityInitiator/` keeps a copy.
- `prepup.sh` &mdash; build the tarballs.

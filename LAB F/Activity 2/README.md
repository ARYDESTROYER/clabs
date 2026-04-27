> Audience: instructor / teaching staff

# LAB F &middot; Activity 2 &mdash; Perform the DNS rebind

The student edits two JSON configs (`dns_config.json`, `attack_plan.json`) in the LMS file editor, clicks "Run Bot" on the dashboard, and observes the in-process victim bot exfiltrate the internal admin's session token (FLAG2).

## Services
| Service | Bind | LMS-exposed |
| --- | --- | --- |
| Attacker dashboard + bot | `0.0.0.0:30000` | yes |
| Internal admin | `127.0.0.1:8080` | no |

## What the autograder checks (50 + 50 = 100)
1. `flag.txt` matches `IITB{labf_a2_dns_rebinding_works}`.
2. The dashboard event log (`/tmp/labf_events.json`) contains a `bot_exfil` event whose payload includes that flag.

Both required for full credit. Prevents "I just typed the flag in" bypasses &mdash; the student must actually run the rebind through the bot.

## Vulnerability summary
- The "internal admin" trusts loopback callers; this is the realistic misconfig.
- Real browsers (and our bot) enforce SOP by hostname, not by IP. Resolving `attacker.lab` first to the attacker's IP and then to the admin's IP after page-load lets a follow-up `fetch('//attacker.lab/admin/token')` reach the admin while the SOP check still passes.

## Documentation
- `activity_guide.md` &mdash; paste into LMS activity description.
- `WALKTHROUGH.md` &mdash; reference solution + mitigations.

> Audience: instructor / teaching staff

# LAB F &middot; Activity 3 &mdash; Independent variation

Same architecture as Activity 2, different admin surface, no walkthrough handed to the student.

## What's different from Activity 2
- Endpoints under `/api/v2/*` instead of `/admin/*`.
- The secret endpoint requires a `?token=` query parameter.
- `/api/v2/healthz` leaks the required token via response header `X-Internal-Token-Debug` &mdash; a realistic developer-debug-leak pattern.
- Hostname to use for the rebind is up to the student (`activity_guide.md` suggests they pick one).

## What the autograder checks (100)
1. `flag.txt` matches `IITB{labf_a3_independent_pwn_complete}`. That's the only test.

## Documentation
- `activity_guide.md` &mdash; student-facing, hint-style (no full reveal). Paste into LMS.
- `WALKTHROUGH.md` &mdash; reference solution. Instructor-only; do NOT paste this anywhere students see.

# LAB F Shared Runtime (reference copies)

These files are the canonical sources for the runtime services used by every
LAB F activity. Each activity's `activityInitiator/` keeps a **copy** of the
relevant file because Bodhi tarballs are mounted per-activity and there is no
shared volume across activities.

| File | Used by | Purpose |
| --- | --- | --- |
| `attacker_server.py` | All activities (verbatim) | Dashboard at `:30000`, victim bot, fake DNS resolver |
| `admin_server_a1a2.py` | Activities 1 & 2 | Admin server at `127.0.0.1:8080` with `/admin/welcome` and `/admin/token` |
| `admin_server_a3.py` | Activity 3 | Variation: `/api/v2/secret` gated by `?token=`, `/api/v2/healthz` leaks the token |

If you change anything here, run `prepup.sh` from the LAB F root to refresh
the per-activity copies and re-tarball.

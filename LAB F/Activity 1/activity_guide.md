# LAB F &middot; Activity 1: Map the threat model

**Time:** ~15 minutes &middot; **Goal:** understand what is and isn't reachable, and where the secret lives, before we attack anything in Activity 2.

## What's running

| Service | Address | Reachable from your real browser? |
| --- | --- | --- |
| Attacker page (dashboard) | `http://localhost:30000` | **Yes** -- open it now. |
| Internal admin server | `http://127.0.0.1:8080` | **No** -- only from inside this container. |

Open the dashboard at <http://localhost:30000>. Read it. Come back when you have.

## What to do

You're going to confirm two facts experimentally, then claim FLAG1.

### Step 1 -- Confirm the admin is not exposed to your browser

Try opening `http://localhost:8080/admin/welcome` in your real browser. It will fail to load (`ERR_CONNECTION_REFUSED` or similar). The LMS only mapped port 30000 to your machine; port 8080 is internal.

### Step 2 -- Confirm the admin IS reachable from inside the container

In the LMS terminal (the one rooted at `/home/labDirectory`), run:

```bash
curl http://127.0.0.1:8080/admin/welcome
```

You'll see a JSON response like:

```json
{
  "msg": "Hello internal staff. This is the corporate admin panel.",
  "activity1_flag": "IITB{labf_a1_...}",
  "note": "If you can read this, you are on the corporate loopback interface."
}
```

That's the trust assumption your future rebinding attack will exploit: **the admin trusts whoever connects on `127.0.0.1`**. In Activity 2 you'll trick the in-browser victim bot into being that "whoever".

### Step 3 -- Submit FLAG1

Copy the value of `activity1_flag` (the full `IITB{...}` string) and paste it into `flag.txt` in this directory. Then click **Evaluate** in the LMS.

## Tips

- Use the LMS file editor to open `flag.txt`. If you can't save the file, run the evaluator anyway -- the init script recreates the file fresh on every container boot.
- The dashboard at `localhost:30000` will keep working through Activities 2 and 3; you'll come back to it.

## Files in this folder

- `flag.txt` &mdash; paste FLAG1 here.
- `dns_config.json`, `attack_plan.json` &mdash; ignore these for Activity 1. They are placeholders so the dashboard renders cleanly. You'll edit them in Activity 2.

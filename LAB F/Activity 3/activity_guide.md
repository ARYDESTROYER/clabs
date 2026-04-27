# LAB F &middot; Activity 3: Independent variation

**Time:** ~30 minutes &middot; **Goal:** apply the technique from Activity 2 to a new internal admin layout, with no walkthrough.

## What's different from Activity 2

The internal admin server has been redeployed. Different paths, different rules. You don't get a walkthrough this time -- you get a target.

## What's the same

- Attacker dashboard at `http://localhost:30000`.
- Internal admin at `http://127.0.0.1:8080`, not LMS-exposed.
- The bot still enforces Same-Origin Policy on follow-up fetches.
- You still drive everything via `dns_config.json` and `attack_plan.json`.

## Starter scaffold

`/home/labDirectory/dns_config.json` and `/home/labDirectory/attack_plan.json` are pre-populated with **shape-only skeletons**: the JSON keys and structure are filled in, every value is a `TODO-` placeholder you must replace. The schema is given so you don't have to guess field names; the actual answers (which hostname, which target IP/port, which endpoint, which query parameter, which token value) are still up to you to discover.

## Your task

1. Enumerate the new admin server. From the in-container terminal, hit a few endpoints under `http://127.0.0.1:8080/...` until you have a complete picture. (Hint: try `/api/v2/whoami`, `/api/v2/healthz`, `/api/v2/secret`. Inspect the **response headers**, not just the body.)
2. Figure out what's required to make `/api/v2/secret` return the secret. The bot's `attack_plan.json` already has a `query` object stub on the fetch action -- just fill in the right key and value.
3. Fill in `dns_config.json`. Pick any hostname you want; use it consistently in both files.
4. Run the bot from the dashboard. Capture the secret. Submit.

## Submission

Paste the leaked corporate secret into `flag.txt`, then click **Evaluate**.

The autograder checks one thing: `flag.txt` matches the expected value. Full marks (100) if it does, zero if it doesn't.

## Tips

- The bot supports a `query` object on `fetch` actions -- the placeholder in `attack_plan.json` shows exactly where to put it.
- If `bot_sop_block` shows up in the dashboard event log, your fetch URL hostname differs from your `page_url` hostname. Both must use the same hostname (the one you defined in `dns_config.json`).
- Use `curl` from the container terminal to enumerate; use the bot only to perform the rebind itself.
- The dashboard's "Reload configs" button is your friend after every save.

You've already seen the moves. Apply them.

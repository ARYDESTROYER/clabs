# Activity 1 walkthrough &mdash; Map the threat model

## Why this activity exists

DNS rebinding is one of the few web attacks that bypasses the Same-Origin Policy at the network layer. Before you attack it, you need a clear mental model of:

1. What's the **target** (the internal admin server)?
2. Why is it normally **safe** (your browser can't reach it)?
3. What's the **vulnerability** (admin trusts whoever lands on its loopback)?

Activity 1 walks you through confirming those three facts. Activity 2 turns them into an attack.

## Step-by-step

### 1. Open the attacker dashboard

In your real browser, open `http://localhost:30000`.

You'll see:

- A "System map" panel listing the two services.
- Two JSON config previews (`dns_config.json`, `attack_plan.json`) -- these are placeholders for Activity 1, ignore them.
- A "Run Bot" button -- you don't need it yet.

The dashboard updates every couple seconds. Leave the tab open.

### 2. Try to reach the admin from your browser

Open a new tab and visit `http://localhost:8080/admin/welcome`. It will fail (`ERR_CONNECTION_REFUSED` or "this site can't be reached"). 

This is **not** because the admin server is broken. It's because the BodhiLabs LMS only forwarded container port `30000` to your machine. Port `8080` is bound to `127.0.0.1` *inside* the container; no remote tunnel exists for it.

This is the realistic "internal" model: imagine the admin lives on a corporate LAN that you, as the attacker, cannot route to.

### 3. Reach the admin from the LMS terminal

In the LMS terminal (which gives you a shell **inside** the container), run:

```bash
curl http://127.0.0.1:8080/admin/welcome
```

You'll see a JSON response containing `"activity1_flag": "IITB{labf_a1_threat_model_mapped}"`.

Why does this work? Because from inside the container, `127.0.0.1:8080` is reachable -- exactly like a corporate insider on the LAN can reach the admin while outsiders cannot.

While you're here, also try:
```bash
curl http://127.0.0.1:8080/admin/whoami
curl http://127.0.0.1:8080/admin/token
```

That `/admin/token` endpoint will be the target in Activity 2.

### 4. Submit FLAG1

Open `/home/labDirectory/flag.txt` in the LMS file editor, paste the flag, save. Then click **Evaluate**.

If the editor shows the file as read-only, exit and re-open the activity (this triggers `initactivity.sh` to recreate the file with student ownership -- see Section 7.1 of `BODHILABS_COMPLETE_GUIDE.md`).

## Pedagogy recap (read before moving on)

- **Same-Origin Policy** stops a page on `attacker.com` from reading data off `corporate-admin.local` -- different origins.
- **Network reachability** stops your browser, sitting on the public internet, from even initiating a connection to `192.168.1.100` (or `127.0.0.1:8080`, in our analogue).
- **DNS rebinding** breaks both. The attacker page tells your browser to fetch `attacker.com/something`, your browser dutifully resolves `attacker.com` -- but the DNS answer has flipped to point at the internal IP. Same hostname (so SOP is happy), different IP (so the request hits the internal service).

In Activity 2 you'll set this up explicitly: edit a JSON file that controls the bot's resolver, point the bot's attack page at the right URL, and watch the secret leak out.

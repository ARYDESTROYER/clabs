# Activity 1 Walkthrough - JuicyMart Recon

You've been given access to a freshly-deployed web app at `http://localhost:30000`. You don't know what's running, what's exposed, or whether there's anything sensitive hidden behind it. Your job is to find out.

This walkthrough takes you through five recon steps. The flag is hidden behind step 5.

---

## Step 1 - Port and service discovery (nmap)

`nmap` doesn't just list open ports; with `-sV` it grabs the service banner and tells you *what software* is running.

```bash
nmap -sV -p 30000 localhost
```

Expected output (abbreviated):
```
PORT      STATE SERVICE VERSION
30000/tcp open  http    Apache httpd 2.4.x
```

**What you learned:** the target is Apache 2.4.

---

## Step 2 - HTTP fingerprinting (curl)

The `Server` response header confirms what nmap inferred from the banner.

```bash
curl -I http://localhost:30000/
```

Look for:
```
HTTP/1.1 200 OK
Server: Apache/2.4.x (Ubuntu)
```

You can also just open `http://localhost:30000/` in the browser, then **F12 -> Network tab -> click the request -> Headers**. Same information.

---

## Step 3 - WAF detection

Try poking at `/admin` directly:
```bash
curl -i http://localhost:30000/admin
```

Expected:
```
HTTP/1.1 403 Forbidden
...
<title>403 Forbidden</title>
```

Check the WAF log to confirm what just happened:
- Browser: open `http://localhost:30000/lab/waf-log`
- Terminal: `tail /tmp/modsec_audit.log`

You will see an entry with rule ID `100001` and the message `Admin path blocked by WAF`. **You have just confirmed there is a mod_security WAF in front of this app.** Bookmark this — you'll attack it in Activity 2.

For an even louder confirmation, run a broad scanner:
```bash
nikto -h http://localhost:30000
```

Nikto will identify the Apache version and report mod_security audit logging.

---

## Step 4 - Directory enumeration (gobuster)

The visible site has Home, Products, About, Contact. There should be more. Brute-force common paths. (Note: this container ships gobuster v2, which uses a flat command syntax — no `dir` subcommand.)

```bash
gobuster -u http://localhost:30000 -w /usr/share/dirb/wordlists/common.txt -q
```

Notable findings (the WAF blocks every variant of /admin* with 403):
```
/about    (Status: 200)
/admin    (Status: 403)   <- the WAF blocked it (Activity 2 target)
/contact  (Status: 200)
/products (Status: 200)
/robots.txt (Status: 200)
```

`/robots.txt` is the lead worth following.

---

## Step 5 - Follow the breadcrumbs to the flag

```bash
curl http://localhost:30000/robots.txt
```

Output:
```
User-agent: *
Disallow: /admin/

# internal: /api/v1/info
```

That commented line is the hint — there's an internal API endpoint not linked anywhere on the site. Hit it:

```bash
curl http://localhost:30000/api/v1/info
```

Response:
```json
{
  "app": "JuicyMart",
  "version": "1.4.2",
  "environment": "production",
  "recon_token": "flag=juicymart_recon_complete",
  "note": "Internal endpoint used by our service-discovery agent."
}
```

The `recon_token` value is your flag.

---

## Submission

```bash
echo "flag=juicymart_recon_complete" > /home/labDirectory/flag.txt
bash /home/.evaluationScripts/evaluate.sh
```

Or paste it into `flag.txt` via the editor and click **Evaluate**.

---

## What you practiced

| Step | Skill |
|------|-------|
| 1 | Service & version discovery via banner grabbing |
| 2 | HTTP response header inspection |
| 3 | Identifying the presence of a WAF and reading its audit log |
| 4 | Directory brute-forcing |
| 5 | Following hints in `robots.txt` to find unlinked endpoints |

These five techniques are the foundation of every web pentest. In Activity 2, you'll use the same toolkit to actually *bypass* the WAF you just identified.

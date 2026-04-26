## Activity 1: Recon & WAF Discovery

### Objective
- Understand reconnaissance as the first phase of any web pentest — before you attack anything, you map what's actually there.
- Use `nmap` to identify the server software running behind an unknown port.
- Use `curl` and a browser's developer tools to inspect HTTP response headers.
- Identify the presence of a Web Application Firewall (WAF) and read its audit log.
- Use `gobuster` to brute-force directory paths and discover unlinked endpoints.
- Use `robots.txt` as a hint source — a real recon habit, not just a lab trick.

There are five steps to this activity. The flag is hidden behind step 5.

### The target

A web application has been deployed at `http://localhost:30000`. You don't know what's running, what's exposed, or whether there's anything sensitive hidden behind it. Your job is to find out.

You have these tools pre-installed in the container:

| Tool | What it does |
|---|---|
| `nmap` | Port scanner. With `-sV` it also identifies service versions. |
| `curl` | HTTP client. Used here to inspect headers and request specific paths. |
| `nikto` | Web server scanner. Reports tech stack and known issues. |
| `gobuster` (v2) | Brute-forces directory and file paths against a target. |
| `dirb` | Alternative directory scanner. Ships with wordlists at `/usr/share/dirb/wordlists/`. |

### Step 1 — Port and Service Discovery (nmap)

`nmap` doesn't just list which ports are open; with the `-sV` flag, it grabs the service banner and tells you *what software* is running on each port. This is called **banner grabbing** and it's the first thing a pentester does on a new target.

```
nmap -sV -p 30000 localhost
```

Each part of this command:
- `-sV` → enable service/version detection
- `-p 30000` → only scan port 30000 (skips the full 65k-port scan)
- `localhost` → the target

Expected output (abbreviated):
```
PORT      STATE SERVICE VERSION
30000/tcp open  http    Apache httpd 2.4.x
```

**What you learned:** the target is an Apache 2.4 web server. Note the version — pentesters cross-reference versions against CVE databases for known vulnerabilities.

### Step 2 — HTTP Fingerprinting (curl)

The `Server` HTTP response header confirms what nmap inferred from the banner. Use `curl -I` to fetch only the response headers (a HEAD request):

```
curl -I http://localhost:30000/
```

Look for the `Server:` line:
```
HTTP/1.1 200 OK
Server: Apache/2.4.66 (Debian)
Content-Type: text/html; charset=utf-8
```

#### Browser alternative

Open `http://localhost:30000/` in your browser, press **F12** to open developer tools, go to the **Network** tab, click on the request, and view the **Headers** panel. Same information, friendlier interface. Use whichever you prefer — pentesters use both depending on what's faster for the question they're answering.

### Step 3 — Detect the WAF

A WAF (Web Application Firewall) sits between the internet and the web app, inspecting requests and blocking ones that match attack patterns. Detecting that a WAF exists is critical recon: it tells you which kinds of attacks won't work directly.

Try poking at a sensitive-looking path:

```
curl -i http://localhost:30000/admin
```

Expected:
```
HTTP/1.1 403 Forbidden
Server: Apache/2.4.66 (Debian)
...
<title>403 Forbidden</title>
```

A 403 on a path you haven't even seen linked anywhere is a strong WAF signal. To **confirm** which WAF and which rule blocked you, this lab gives you two ways to read the WAF audit log:

#### Option A — Browser
Open `http://localhost:30000/lab/waf-log` — a live table of recent WAF blocks.

| Time | Method | Blocked URI | Rule ID | Message |
|---|---|---|---|---|
| ... | GET | `/admin` | 100001 | Admin path blocked by WAF |

#### Option B — Terminal
```
tail -n 30 /tmp/modsec_audit.log
```

Look for the `Message:` line. You'll see something like:
```
Message: Access denied with code 403 (phase 1).
String match "/admin" at REQUEST_URI.
[id "100001"] [msg "Admin path blocked by WAF"]
```

**What you learned:** there is a **mod_security** WAF in front of this app. Rule `100001` blocks anything matching `/admin` in the request URI. Bookmark this — you'll attack the same WAF in Activity 2.

#### Optional: a second confirmation with nikto

```
nikto -h http://localhost:30000
```

Nikto runs hundreds of checks and will report the Apache version, mod_security audit-log presence, and any obvious misconfigurations. It's noisy but useful for cross-checking what nmap and your manual probing already found.

### Step 4 — Directory Enumeration (gobuster)

The visible site has Home, Products, About, Contact. There should be more — most apps have admin panels, API endpoints, debug pages, and forgotten files. **Directory brute-forcing** discovers them by trying thousands of common path names and reporting which ones return a non-404 response.

> **Note:** This container ships gobuster v2, which uses a flat command syntax. The newer v3 syntax (`gobuster dir -u ...`) won't work here.

```
gobuster -u http://localhost:30000 -w /usr/share/dirb/wordlists/common.txt -q
```

Each part:
- `-u http://localhost:30000` → the target URL
- `-w /usr/share/dirb/wordlists/common.txt` → the wordlist (a list of common path names to try)
- `-q` → quiet mode (suppresses the gobuster banner)

Notable findings (the WAF blocks every variant of `/admin*` with 403):
```
/about     (Status: 200)
/admin     (Status: 403)   <- the WAF blocked it (Activity 2 target)
/contact   (Status: 200)
/products  (Status: 200)
/robots.txt (Status: 200)
```

`/robots.txt` is the lead worth following.

### Step 5 — Follow the Breadcrumbs to the Flag

`/robots.txt` is a file websites use to tell search engines which paths *not* to crawl. Pentesters read it for the opposite reason: it often **lists exactly the paths the site owner wants hidden**, including admin areas and internal tools.

```
curl http://localhost:30000/robots.txt
```

Output:
```
User-agent: *
Disallow: /admin/

# internal: /api/v1/info
```

That commented line is the hint — there's an internal API endpoint not linked anywhere on the site. Hit it:

```
curl http://localhost:30000/api/v1/info
```

Response:
```
{
  "app": "JuicyMart",
  "version": "1.4.2",
  "environment": "production",
  "recon_token": "flag=juicymart_recon_complete",
  "note": "Internal endpoint used by our service-discovery agent."
}
```

The value of the `recon_token` field is your flag. It looks like `flag=...`.

### Submission

Paste the flag into `/home/labDirectory/flag.txt`. Save the file and click **Evaluate** to check it.

Or via terminal:
```
echo "flag=juicymart_recon_complete" > /home/labDirectory/flag.txt
bash /home/.evaluationScripts/evaluate.sh
```

### What you practiced

| Step | Skill |
|---|---|
| 1 | Service & version discovery via banner grabbing |
| 2 | HTTP response header inspection |
| 3 | Identifying the presence of a WAF and reading its audit log |
| 4 | Directory brute-forcing |
| 5 | Following hints in `robots.txt` to find unlinked endpoints |

These five techniques are the foundation of every web pentest. In Activity 2, you'll use the same toolkit to actually *bypass* the WAF you just identified.

### Further reading

- [OWASP Web Security Testing Guide — Information Gathering](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/)
- [nmap reference: service and version detection](https://nmap.org/book/man-version-detection.html)
- [gobuster on GitHub](https://github.com/OJ/gobuster)
- [The robots.txt convention](https://www.robotstxt.org/)

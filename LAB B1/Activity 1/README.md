# LAB B1 - Activity 1: Reconnaissance & WAF Fingerprinting

> **Audience:** instructor / teaching staff. This is a reference doc, not shown to students.

## Learning objective
Map an unknown web target, identify its server stack, detect the presence of a Web Application Firewall (WAF), and discover hidden endpoints through directory enumeration. The flag is hidden behind correctly-executed recon.

## Target
- **Web app:** http://localhost:30000 (JuicyMart Flask app behind Apache + mod_security)

## Tools pre-installed
- `nmap` - port scanning and service version detection
- `curl` - HTTP requests and header inspection
- `nikto` - web server scanner (reports tech stack and known issues)
- `gobuster` v2 - directory and file brute-forcing
- `dirb` - alternative directory scanner; wordlists in `/usr/share/dirb/wordlists/`

## Flag
- `flag=juicymart_recon_complete` - returned in the JSON body of `/api/v1/info` (an unlinked endpoint discoverable via `gobuster` + the hint in `/robots.txt`).

## Submission
Student writes the flag into `/home/labDirectory/flag.txt` (created at runtime by `initactivity.sh`) and clicks **Evaluate**. Autograder validates exact string match. 100/100 on success.

## Helper endpoints available to the student
- WAF audit log viewer (browser): http://localhost:30000/lab/waf-log
- WAF audit log file (terminal): `/tmp/modsec_audit.log`

See `WALKTHROUGH.md` for the full step-by-step solution path.

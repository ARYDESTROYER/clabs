Activity: DNS Zone Transfer Exploitation and Enumeration
Objective
Understand how to enumerate internal corporate infrastructure by exploiting a misconfigured DNS server.
Task
Exploit the local DNS server which is serving the `corp.internal` domain, enumerate the internal hosts, and retrieve a hidden flag.

Guidance
Step 1 — Read the Background Material
Review what you learned about AXFR (DNS Zone Transfers) and DNS enumeration in Activity 1.

Step 2 — Enumerate the DNS Server
The target DNS server is running locally on this machine (`127.0.0.1`). The organization uses `corp.internal` as their internal domain.
Use tools like `dig`, `host`, or `nslookup` to perform a zone transfer. For example, using `dig`:
dig @localhost corp.internal AXFR

Step 3 — Analyse the Zone Records
Look through the dumped records carefully. A zone transfer reveals the entire internal map of the network.
Make a note of any sensitive internal infrastructure (e.g., systems an attacker would value like databases, admin panels, or HR systems). Often these are hidden in internal IP ranges like `10.x.x.x`.
Calculate the number of unique hostnames that have `A` (IPv4 address) records.

Step 4 — Retrieve the Flag
Keep looking through the records, particularly the `TXT` records, to find a hidden flag representing compromised credentials.

Submission
Paste the flag you found into `SUBMIT_FLAG.txt`.
List the sensitive internal hostnames you identified in `SUBMIT_HOSTS.txt` (comma-separated, e.g., `host1, host2`). Please only include truly sensitive internal hosts in the 10.x.x.x range (exclude public or generic ones like `www`, `ns1`, `vpn`).
Write the total count of unique hostnames that have `A` records in `SUBMIT_COUNT.txt`.
Save the files and click Evaluate to check your answers. Submit these files.

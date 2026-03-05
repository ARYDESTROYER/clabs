Activity: Advanced DNS Tunneling Detection and Decoding
Objective
Understand how to detect covert communication channels and decode data exfiltrated via DNS tunneling.
Task
Analyze the provided network traffic capture (`dns_traffic.pcap`) to identify the command-and-control domain and reconstruct the exfiltrated sensitive data.

Guidance
Step 1 — Read the Background Material
Review what you learned about DNS tunneling in Activity 1. Attackers bypass port restrictions by encapsulating data within standard DNS queries (usually TXT or NULL records) directed at a domain they control.

Step 2 — Analyze the Traffic
The Security Operations Center (SOC) flagged unusual DNS activity from workstation `10.0.0.50`. A packet capture (`dns_traffic.pcap`) is available in your home directory.
Use `tshark` or `tcpdump` to read the file:
tshark -r dns_traffic.pcap

Step 3 — Identify the Malicious Domain
Filter the traffic to look for DNS tunneling indicators. Tunneling often involves a high volume of `TXT` queries with long, random-looking subdomains.
Filter for TXT queries:
tshark -r dns_traffic.pcap -Y "dns.qry.type == 16"

Identify the parent domain that is receiving these unusual queries. This is the attacker's command-and-control domain.

Step 4 — Extract and Decode the Exfiltrated Data
The subdomains prepended to the malicious domain contain hex-encoded data chunks.
Extract all these hex subdomains from the tunneling queries.
Concatenate them in chronological order.
Decode the resulting hex string to reveal the exfiltrated secret flag. You can use tools like `xxd` or `python3` to decode it:
echo '<hex_string>' | xxd -r -p

Step 5 — Count the Tunneling Queries
Determine exactly how many DNS queries were part of this specific data exfiltration to the malicious domain.

Submission
Write the malicious parent domain (e.g., `evil.example.com`) in `SUBMIT_DOMAIN.txt`.
Write the decoded exfiltrated secret flag in `SUBMIT_SECRET.txt`.
Write the total number of tunneling queries in `SUBMIT_TUNNEL_COUNT.txt`.
Click Evaluate to check the correctness of your findings. Submit these files.

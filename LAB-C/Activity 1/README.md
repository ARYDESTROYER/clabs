Activity: Introduction to DNS Zone Transfers and DNS Tunneling
Objective
Understand how DNS zone transfers (AXFR) work and why misconfigured DNS servers pose a security risk.
Learn how attackers use DNS queries as a covert channel for data exfiltration (DNS tunneling).
There are two parts to this activity.

Part 1: Exploiting DNS Zone Transfers (AXFR)
Security analysis of internal networks often starts with enumerating exposed infrastructure. Centralized services like DNS, when misconfigured to allow unauthorized zone transfers, can leak the entire network map.

Task: Identify the internal hostnames by performing a DNS Zone Transfer and locate the hidden flag.

Guidance
A DNS server is currently running on your local machine (`localhost`).
We need to check if the DNS server is configured to allow unauthorized zone transfers for the domain `demo.lab.local`.

Run the following command to query the SOA (Start of Authority) record and confirm the server is responsive:
dig @localhost demo.lab.local SOA

Now, attempt a full zone transfer using the `AXFR` query type:
dig @localhost demo.lab.local AXFR

Analysing the Output
Observe the output carefully. You will see a dump of every record in the zone.
Look for multiple `A` records revealing internal IP addresses (e.g., `internal-db`).
Find the `TXT` record. Attackers and defenders often look at TXT records for descriptive data, and in this case, it contains a sensitive flag.

Submission
Copy the flag from the TXT record and specify it in `SUBMIT_FLAG.txt`. 
Specify the type of DNS query that dumps all records (the one you used above) in `SUBMIT_ANSWER.txt`. 
Click Evaluate to check the correctness of your answers. Submit the files.

Part 2: Introduction to DNS Tunneling
DNS tunneling is a technique where attackers hide data inside DNS queries to bypass firewalls and exfiltrate data. They encode stolen data into the subdomain labels.

Task: Analyze a sample packet capture (`demo_dns.pcap`) to find exfiltrated data.

Guidance
We have provided a sample packet capture file named `demo_dns.pcap`.
Open and analyze it using `tshark`:
tshark -r demo_dns.pcap

DNS tunneling usually relies on `TXT` (Type 16) queries. Filter the capture to only show TXT queries:
tshark -r demo_dns.pcap -Y "dns.qry.type == 16"

Notice the unusual subdomain labels in the queries directed to `tunnel.demo.local`. These long strings are hex-encoded data.
Concatenate all the subdomain chunks together, and decode them using the `xxd` command line tool:
echo '<concatenated_hex_string>' | xxd -r -p

This will reveal the hidden message the attacker was exfiltrating! This part is for your understanding and does not require submission.

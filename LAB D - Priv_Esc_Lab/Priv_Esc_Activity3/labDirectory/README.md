# Activity 3: SUID & GTFOBins Exploitation

## Objective
Gain root privileges and read the secret flag located at `/root/flag.txt`.

## Scenario
You have access to a system as a low-privileged user (`student`). The system administrator has installed some standard utilities but may have misconfigured their permissions.

## Instructions
1.  **Enumeration**: Search for binaries that have the SUID (Set Owner User ID) bit set.
    *   Hint: Use the `find` command to look for files with specific permissions.
    *   Command hint: `find / -perm -4000 2>/dev/null`

2.  **Exploitation**: Identify if any of the SUID binaries are known to be exploitable for privilege escalation.
    *   Resource: Search online for "GTFOBins".
    *   Look for binaries like `vim`, `less`, or `awk`.

3.  **Capture the Flag**:
    *   Once you have escalated your privileges (or found a way to read files as root), read the content of `/root/flag.txt`.

4.  **Submission**:
    *   Paste the flag content into the file `SUBMIT_FLAG_HERE.txt` in this directory.
    *   Click "Evaluate" or run `evaluate.sh` (if available) to verify your submission.

## Note
- This lab focuses on standard Unix binaries configured insecurely. No custom C code is involved here.
- The tool `ltrace` is not available. Rely on standard system commands.

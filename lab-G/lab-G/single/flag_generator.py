"""
Flag generation system for Lab-G
Generates unique, persistent flags for each challenge part
"""
import os
import secrets
import fcntl
from datetime import datetime

FLAGS_DIR = '/opt'  # Changed from /opt/flags to match clab standard

def ensure_flags_dir():
    """Ensure flags directory exists"""
    os.makedirs(FLAGS_DIR, exist_ok=True)

def generate_random_suffix(length=8):
    """Generate random hex suffix for flags (8 chars to match standard)"""
    return secrets.token_hex(length // 2)

def generate_flag(flag_name, flag_template):
    """
    Generate a flag if it doesn't exist, otherwise return existing flag
    Uses file locking to prevent race conditions
    Flag naming: masterflag1.txt, masterflag2.txt, etc. (clab standard)
    """
    ensure_flags_dir()
    flag_file = os.path.join(FLAGS_DIR, f'masterflag{flag_name[-1]}.txt')  # Extract number from flagN

    # Check if flag already exists
    if os.path.exists(flag_file):
        with open(flag_file, 'r') as f:
            return f.read().strip()

    # Generate new flag with file locking
    flag_value = flag_template.format(random=generate_random_suffix())

    # Write with exclusive lock
    with open(flag_file, 'w') as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(flag_value)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            print(f"Error writing flag: {e}")

    # Also write to labDirectory for student access
    try:
        lab_dir = '/home/labDirectory'
        os.makedirs(lab_dir, exist_ok=True)
    except:
        pass

    return flag_value

def generate_flag1():
    """FLAG1: Reconnaissance Complete"""
    return generate_flag('flag1', 'FLAG{{R3c0n_C0mpl3t3_Ec0mm3rc3_{random}}}')

def generate_flag2():
    """FLAG2: ZAP Scan Complete"""
    return generate_flag('flag2', 'FLAG{{ZAP_Sc4n_XSS_D3t3ct3d_{random}}}')

def generate_flag3():
    """FLAG3: XSS Payload Crafted"""
    return generate_flag('flag3', 'FLAG{{XSS_P4yl04d_Cr4ft3d_{random}}}')

def generate_flag4():
    """FLAG4: Admin Session Hijacked"""
    return generate_flag('flag4', 'FLAG{{Adm1n_S3ss10n_H1j4ck3d_{random}}}')

def get_all_flags():
    """Get all generated flags"""
    return {
        'flag1': generate_flag1(),
        'flag2': generate_flag2(),
        'flag3': generate_flag3(),
        'flag4': generate_flag4()
    }

def reset_flags():
    """Delete all flags (for lab reset)"""
    ensure_flags_dir()
    for flag_file in ['masterflag1.txt', 'masterflag2.txt', 'masterflag3.txt', 'masterflag4.txt']:
        flag_path = os.path.join(FLAGS_DIR, flag_file)
        if os.path.exists(flag_path):
            os.remove(flag_path)
            print(f"Deleted: {flag_path}")

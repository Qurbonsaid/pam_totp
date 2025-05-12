#!/usr/bin/env python3
import os
import sys
import time
import struct
import hashlib
import hmac
import getpass
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

SECRET_FILE = ".totp_secret.enc"
KEY_FILE = ".totp_key"


def generate_totp(secret: str, for_time: int, digits: int = 6) -> str:
    counter = for_time // 30
    counter_bytes = struct.pack(">Q", counter)
    key_bytes = secret.encode("utf-8")
    hmac_hash = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0xF
    binary = ((hmac_hash[offset] & 0x7F) << 24 |
              (hmac_hash[offset + 1] & 0xFF) << 16 |
              (hmac_hash[offset + 2] & 0xFF) << 8 |
              (hmac_hash[offset + 3] & 0xFF))
    otp = binary % (10 ** digits)
    return str(otp).zfill(digits)


def verify_totp(secret: str, input_code: str, window: int = 1) -> bool:
    now = int(time.time())
    for offset in range(-window, window + 1):
        expected = generate_totp(secret, now + offset * 30)
        if expected == input_code:
            return True
    return False


def load_encrypted_secret(home: Path) -> str:
    key_path = home / KEY_FILE
    secret_path = home / SECRET_FILE

    if not key_path.exists() or not secret_path.exists():
        print("Error: Missing TOTP secret or key file.", file=sys.stderr)
        sys.exit(1)

    key = key_path.read_bytes()
    fernet = Fernet(key)
    try:
        encrypted = secret_path.read_bytes()
        return fernet.decrypt(encrypted).decode()
    except InvalidToken:
        print("Error: Failed to decrypt TOTP secret.", file=sys.stderr)
        sys.exit(1)


def pam_mode():
    username = os.getenv("PAM_USER")
    if not username:
        sys.exit(1)

    try:
        from pwd import getpwnam
        home = Path(getpwnam(username).pw_dir)
    except Exception:
        sys.exit(1)

    secret = load_encrypted_secret(home)
    try:
        code = getpass.getpass(prompt="TOTP: ")
    except Exception:
        sys.exit(1)

    if verify_totp(secret, code):
        sys.exit(0)
    else:
        sys.exit(1)


def init_mode():
    home = Path.home()
    secret = input("Enter a 6-digit PIN to use as TOTP secret: ").strip()

    if len(secret) != 6 or not secret.isdigit():
        print("Error: Invalid PIN. Must be 6 digits.")
        return

    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(secret.encode())

    (home / SECRET_FILE).write_bytes(encrypted)
    (home / KEY_FILE).write_bytes(key)

    print("Success: TOTP secret encrypted and stored.")


def check_mode():
    home = Path.home()
    secret = load_encrypted_secret(home)
    code = input("Enter TOTP: ").strip()
    if verify_totp(secret, code):
        print("Success: TOTP is valid")
        sys.exit(0)
    else:
        print("Error: Invalid TOTP")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        pam_mode()
    elif sys.argv[1] == "init":
        init_mode()
    elif sys.argv[1] == "check":
        check_mode()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)

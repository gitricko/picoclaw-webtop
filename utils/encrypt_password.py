#!/usr/bin/env python3
import getpass
from pathlib import Path
import hashlib
import base64

def xor_crypt(data, key):
    key_hash = hashlib.sha256(key.lower().encode()).digest()
    crypted = bytearray()
    for i, char in enumerate(data):
        crypted.append(char ^ key_hash[i % len(key_hash)])
    return crypted

def main():
    print("🔐 Password Encryption Utility for PicoClaw Automation")
    email = input("Enter your Google Email (used as encryption key): ").strip()
    
    if not email or "@" not in email:
        print("❌ Invalid email format.")
        return
        
    pwd = getpass.getpass("Enter your Google Password: ")
    
    if not pwd:
        print("❌ Password cannot be empty.")
        return
    
    # Encrypt
    crypted_bytes = xor_crypt(pwd.encode(), email)
    enc_str = base64.b64encode(crypted_bytes).decode('utf-8')
    
    # Save
    out_file = Path.home() / ".google-oauth-automation" / "password.enc"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(enc_str)
    
    print(f"✅ Encrypted password saved to {out_file}")
    print("   The automation script will now dynamically extract your email from")
    print("   the Google login screen to secretly decrypt this on the fly.")

if __name__ == "__main__":
    main()

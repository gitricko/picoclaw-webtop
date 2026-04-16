# PicoClaw Web Authentication Utilities

> [!NOTE]
> **Educational Purpose**: This project is created strictly for learning purposes to demonstrate advanced techniques in headless browser automation, navigating complex OAuth flows, and implementing localized, hardware-salted obfuscation.

This directory contains advanced Playwright automation scripts designed to automatically handle Google OAuth login and re-authentication loops specifically for the PicoClaw Webtop interface. 

## 🚀 The Automations

### 1. `browser_reauth.py`
The primary automation runner. 
- **First Run**: Connects to the PicoClaw `.credentials` Web UI in a visible browser. You manually click "Browser OAuth" and log in to seed the persistent Chromium profile.
- **Subsequent Runs**: Connects to the Web UI perfectly headlessly, presses the "Browser OAuth" button, catches the native Google popup, clicks through the consent screens, and automatically feeds your password if Google demands a re-verification.

### 2. `encrypt_password.py` & `machine_id.py`
Because Google's backend randomly but frequently demands a password to verify Web OAuth sessions running headlessly, `browser_reauth` needs your password to succeed without hanging. 
These scripts provide a mechanism to securely obfuscate your password and mathematically bind it to your specific physical machine.

---

## 🛡️ Risk & Threat Model

Automating authentication inherently requires storing secrets. Because we implemented a custom OS-agnostic obfuscation layer rather than relying on native OS Keychains (like macOS Keychain or Linux Secret Service) to ensure portability and zero-prompt automation, it's vital to understand the exact security model.

### 🔐 How the Encryption Works
When you run `python utils/encrypt_password.py`:
1. It queries your operating system natively for a **Hardware UUID** (e.g., macOS `IOPlatformExpertDevice`, Linux `/etc/machine-id`, or Windows `MachineGuid`).
2. It blends this unique machine identifier with your Google Email to form a highly specific Salt/Key.
3. It uses a cryptographic XOR cipher to obfuscate your password with the SHA-256 hash of this key.
4. It saves the ciphertext to `~/.google-oauth-automation/password.enc`.

During headless automation, `browser_reauth.py` dynamically scrapes your email from the Google login screen, computes the hardware ID on the fly, unlocks the `.enc` file in memory, and submits the password.

### ✅ Threats Mitigated
- **Shoulder Surfing / Accidental Exposure**: Your plaintext password is never written to disk. Casual viewers cannot read your password.
- **Physical Exfiltration (The Stolen File)**: If a hacker remotely accesses your file system and steals `password.enc`, they **cannot** decrypt it on their computer. The decryption algorithm strictly requires the Hardware UUID of the specific machine that encrypted it.

### ⚠️ Residual Risks (Limitations)
- **Local System Compromise**: This is **Obfuscation**, not military-grade Encryption. If a sophisticated attacker gains root/admin access to your specific machine, they can easily execute the exact same Python script to pull the hardware ID, read the `.enc` file, and decrypt your password locally. 
- **Privilege Checking**: The `.google-oauth-automation` folder relies entirely on Standard User OS permissions to restrict access. If other users on the same machine have read access, they can compromise the obfuscation.

### 💡 Security Best Practices
1. **Dedicated Automation Accounts**: Never use your primary personal Google account for headless automation. Create a dedicated workspace or sandbox Google account that only has access to the minimal required scopes.
2. **File Permissions**: Ensure `~/.google-oauth-automation/` is strictly set to `chmod 600` or `chmod 700` so no other local Unix users can access the encrypted payload.
3. **Machine Security**: The safety of this obfuscation is fundamentally anchored to the physical security of the machine/VM it runs on. Secure the host securely.

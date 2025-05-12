# pam_totp

A lightweight, secure PAM module for passwordless TOTP authentication on Linux login screens.  
Supports encrypted secret storage and integrates cleanly with LightDM and other PAM-based login systems.

> 🔐 One-time codes. No passwords. No nonsense.

---

## 🚀 Features

- Passwordless login via 6-digit TOTP
- Encrypted secret storage using `cryptography.Fernet`
- Works seamlessly with PAM and LightDM
- Optional CLI modes for setup and testing
- Written in pure Python (3.x)

---

## 📦 Installation

Build and install the `.deb` package on Ubuntu/Debian-based systems:

```bash
sudo dpkg -i pam_totp.deb
````

This installs the module to `/usr/local/bin/pam_totp.py`.

---

## 🔧 Configuration

After installation, modify your PAM config:

```bash
sudo nano /etc/pam.d/common-auth
```

Add this line **at the top**:

```pam
auth    [success=1 default=ignore]    pam_exec.so expose_authtok /usr/local/bin/pam_totp.py
```

⚠️ Make sure this is above `pam_unix.so`, and that `pam_totp.py` is executable.

---

## 🔑 Secret Setup (per user)

Each user should run:

```bash
pam_totp.py init
```

This will:

- Ask for a 6-digit PIN (TOTP seed)
- Encrypt and store it securely in the user's home directory (`~/.totp_secret.enc` and `~/.totp_key`)

---

## ✅ Verifying

You can test it manually with:

```bash
pam_totp.py check
```

---

## 🛠 Modes

- `pam_totp.py` (no args): PAM login mode
- `pam_totp.py init`: Setup encrypted TOTP secret
- `pam_totp.py check`: Manual verification

---

## 🔗 Related Projects

📱 Looking for the Android app to generate codes?

→ [PC Authenticator (Android)](https://github.com/Qurbonsaid/pc-authenticator)

---

## 🧠 Author

**Qurbonsaid**
[GitHub](https://github.com/Qurbonsaid) · [LinkedIn](https://www.linkedin.com/in/kuzatuvchi)

---

## 📜 License

MIT — Do whatever you want, just don't blame us if you get locked out.

# SecurePass

SecurePass is a secure, local, offline password manager built with Python and CustomTkinter. It features an Obsidian-inspired Dark Mode UI, zero-knowledge encryption, and a suite of security auditing tools to keep your credentials safe.

## ✨ Features

- **Zero-Knowledge Encryption**: Uses AES-256-GCM and Argon2id for key derivation. Your master password is never stored.
- **Local SQLite Vault**: Your passwords never leave your machine unless you explicitly export them.
- **Breach Intelligence**: Integrates with the HaveIBeenPwned API using k-Anonymity. Checks if your passwords have been leaked without ever exposing them.
- **Security Audit**: Automatically detects weak, reused, and old (90+ days) passwords.
- **Secure Password Generator**: Generates strong, highly-random passwords on demand.
- **Categorization**: Organize your vault into customizable categories (Banking, Social, Work, etc).
- **Auto-Lock & Clipboard Clear**: Automatically locks the vault after inactivity and clears copied passwords from the clipboard.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SecurePass.git
   cd SecurePass
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   cd src
   python main.py
   ```
   *(Note: if `main.py` is called `app.py`, use `python app.py`)*

## 🛡️ Security Note

This is a local password manager. **DO NOT** commit your `s_pass.db` file to GitHub or any public repository. A `.gitignore` file is already included in this repository to prevent the database from being uploaded accidentally.

## 🛠️ Built With

- **Python 3.10+**
- **CustomTkinter** (for modern UI components)
- **Cryptography** (AES-256-GCM, Argon2)
- **SQLite3** (for local data persistence)

# SecurePass — Post-Release Feature Roadmap

This document lists features and improvements that can be implemented in future versions of SecurePass following the v1.0.0 submission release.

---

## 🔐 Security & Authentication

### 1. TOTP / Two-Factor Authentication (2FA)
**Priority:** High | **Effort:** Medium

- Integrate `pyotp` to generate TOTP secrets per vault
- Show QR code or secret key for scanning with Google Authenticator / Authy
- Require 6-digit OTP on login in addition to master password
- Store the TOTP secret encrypted alongside the entry in the DB

### 2. OS Keychain Integration
**Priority:** Medium | **Effort:** High

- Store the Argon2id-derived session key in the OS keychain (`keyring` library) instead of in-memory only
- Prevents the lockout bypass attack noted in Known Limitations
- Supports: Linux Secret Service, macOS Keychain, Windows Credential Manager

### 3. Master Password Change  
**Priority:** High | **Effort:** Medium

- Allow users to change their master password without losing vault data
- Re-derive a new key → re-encrypt all entries with the new key → save new salt + verifier

### 4. Vault Export Encryption (Secure Backup)
**Priority:** Medium | **Effort:** Low-Medium

- Export entire vault as an encrypted `.securepass` backup file (AES-256-GCM)
- Password-protect the export file independently from the master password
- Import backup to restore a vault on a new machine

### 5. Failed Login Notification Log
**Priority:** Low | **Effort:** Low

- Log all failed login attempts with timestamp to a local log file
- Show a "Last failed attempt" notification on successful login (like SSH)

---

## 📋 Vault Management

### 6. Category / Folder Tagging
**Priority:** High | **Effort:** Low

- Add a `category` column (e.g., "Banking", "Social", "Work")
- Sidebar filter panel to browse entries by category
- Color-coded category badges on vault cards

### 7. Duplicate / Reused Password Detection
**Priority:** Medium | **Effort:** Medium

- Hash all decrypted passwords on vault load (salted, in-memory only)
- Flag entries that share the same password with a warning badge
- Show a "Reused Passwords" count in the Vault Health stat card

### 8. Password Expiry Reminders
**Priority:** Medium | **Effort:** Low

- Add an optional `last_changed` timestamp per entry
- Show a warning badge on entries older than N days (configurable)
- Dashboard widget showing "X passwords haven't been changed in 90+ days"

### 9. Bulk Import (CSV)
**Priority:** High | **Effort:** Medium

- Import from exported CSV files from Chrome, Firefox, and Bitwarden
- Preview import before confirming
- Skip duplicates automatically

### 10. Drag-and-Drop Reordering
**Priority:** Low | **Effort:** Medium

- Allow users to manually reorder vault entries by dragging
- Store custom order preference per user in `config` table

---

## 🌐 Breach & Security Intelligence

### 11. Bulk Vault Breach Scan
**Priority:** High | **Effort:** Medium

- Add a "Scan All" button in Breach Check page
- Run k-Anonymity check for all stored passwords in background
- Update the "Exposed" counter in Vault Overview in real time
- Highlight breached entries in the vault list with a red badge

### 12. Username / Email Breach Check
**Priority:** Medium | **Effort:** Low

- Extend breach checking to email addresses using HIBP's email API
- Show which data breaches a specific email address appeared in

### 13. Weak Password Audit Report
**Priority:** Medium | **Effort:** Low

- Generate a report listing all "Weak" or "Moderate" strength passwords
- Score the overall vault health with a letter grade (A-F)
- Export report as a PDF or plain text

---

## 🖥 UI / UX Improvements

### 14. System Tray Integration
**Priority:** Medium | **Effort:** Medium

- Minimize app to system tray instead of closing
- Tray icon: quick "Lock Vault" and "Open" options
- Use `pystray` or `PyQt` system tray API

### 15. Keyboard Shortcuts
**Priority:** Low | **Effort:** Low

- `Ctrl+N` --> New Entry
- `Ctrl+F` --> Focus Search
- `Ctrl+G` --> Generator page
- `Ctrl+L` --> Lock vault immediately

### 16. Entry Details Panel / Modal
**Priority:** Medium | **Effort:** Low

- Click an entry to open a details side-panel (not just Edit/Delete)
- Show created date, last modified date, related context in a read-only view

### 17. Responsive / Resizable Layout
**Priority:** Low | **Effort:** Medium

- Make vault cards scale gracefully at smaller window sizes
- Support a compact list view for users with many entries

---

## 🔧 Technical / Infrastructure

### 18. PyInstaller Executable Packaging
**Priority:** High | **Effort:** Low

- Bundle the app into a single executable with PyInstaller
- `pyinstaller --onefile --windowed src/gui.py`
- Test on Windows and Linux
- Include the `.spec` file in the repository

### 19. Automated Unit Tests
**Priority:** Medium | **Effort:** Medium

- Test suite for `crypto_manager.py` (encrypt/decrypt round trip)
- Test suite for `db_manager.py` (CRUD operations)
- Test suite for `security_engine.py` (password strength thresholds, HIBP mock)
- Use `pytest` + `pytest-mock`

### 20. Git `.gitignore` Setup
**Priority:** High | **Effort:** Low

Add a proper `.gitignore` to prevent committing sensitive or generated files:

```
venv/
__pycache__/
*.pyc
*.db
.securepass/
*.spec
dist/
build/
```

---

## Summary Table

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| 1 | TOTP / 2FA | High | Medium |
| 2 | OS Keychain Integration | Medium | High |
| 3 | Master Password Change | High | Medium |
| 4 | Encrypted Vault Backup/Export | Medium | Low |
| 5 | Failed Login Log | Low | Low |
| 6 | Category / Folder Tagging | High | Low |
| 7 | Duplicate Password Detection | Medium | Medium |
| 8 | Password Expiry Reminders | Medium | Low |
| 9 | Bulk CSV Import | High | Medium |
| 10 | Drag-and-drop Reorder | Low | Medium |
| 11 | Bulk Vault Breach Scan | High | Medium |
| 12 | Email Breach Check | Medium | Low |
| 13 | Weak Password Audit Report | Medium | Low |
| 14 | System Tray Integration | Medium | Medium |
| 15 | Keyboard Shortcuts | Low | Low |
| 16 | Entry Details Panel | Medium | Low |
| 17 | Responsive Layout | Low | Medium |
| 18 | PyInstaller Packaging | High | Low |
| 19 | Automated Unit Tests | Medium | Medium |
| 20 | `.gitignore` Setup | High | Low |

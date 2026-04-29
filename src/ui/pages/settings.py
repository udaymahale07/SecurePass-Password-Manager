import customtkinter as ctk
import os
import csv
import json
import threading
import time
from datetime import datetime
from tkinter import filedialog
from ui.design import (
    FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_BODY_SM, FONT_LABEL,
    FONT_CAPTION, BG_BASE, TEXT_1, TEXT_2, TEXT_3, GOLD, GOLD_GLOW,
    TEXT_INV, TEAL, CARD, BORDER, CARD_HOVER, RED_DANGER, GREEN_OK,
    AMBER, BORDER_BRIGHT, Toast
)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self._build_ui()

    # ─────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Page header ──────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent", height=68)
        hdr.grid(row=0, column=0, sticky="ew", padx=35, pady=(28, 0))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="Settings",
                     font=("Georgia", 32, "bold"), text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Customise your SecurePass experience",
                     font=("Helvetica", 15), text_color=TEXT_3).pack(anchor="w", pady=(4, 0))

        # ── Scrollable body ──────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=BORDER_BRIGHT
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=35, pady=(18, 20))
        self.scroll.grid_columnconfigure(0, weight=1)

        self._section_appearance()
        self._section_security()
        self._section_vault()
        self._section_about()

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────
    def _section_card(self, icon, title, subtitle):
        """Returns the inner content frame of a section card."""
        outer = ctk.CTkFrame(self.scroll, fg_color=CARD, corner_radius=14,
                             border_width=1, border_color=BORDER)
        outer.pack(fill="x", pady=(0, 16))
        outer.grid_columnconfigure(0, weight=1)

        # Section header bar
        hdr = ctk.CTkFrame(outer, fg_color=CARD_HOVER, corner_radius=0,
                           height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text=icon, font=("Helvetica", 20),
                     text_color=GOLD).pack(side="left", padx=(18, 8), pady=14)
        blk = ctk.CTkFrame(hdr, fg_color="transparent")
        blk.pack(side="left", fill="y", pady=8)
        ctk.CTkLabel(blk, text=title, font=("Helvetica", 15, "bold"),
                     text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(blk, text=subtitle, font=FONT_CAPTION,
                     text_color=TEXT_3).pack(anchor="w")

        # Divider
        ctk.CTkFrame(outer, fg_color=BORDER, height=1).pack(fill="x")

        # Content area
        body = ctk.CTkFrame(outer, fg_color="transparent")
        body.pack(fill="x", padx=24, pady=16)
        body.grid_columnconfigure(0, weight=1)
        return body

    def _row(self, parent, label, hint, widget_factory, row_idx):
        """Places a label+hint on the left and a widget on the right."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=row_idx, column=0, sticky="ew", pady=6)
        row.grid_columnconfigure(0, weight=1)

        lbl_blk = ctk.CTkFrame(row, fg_color="transparent")
        lbl_blk.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lbl_blk, text=label, font=("Helvetica", 14, "bold"),
                     text_color=TEXT_1).pack(anchor="w")
        if hint:
            ctk.CTkLabel(lbl_blk, text=hint, font=FONT_CAPTION,
                         text_color=TEXT_3).pack(anchor="w")

        widget = widget_factory(row)
        widget.pack(side="right", padx=(16, 0))

        # Thin divider below each row
        ctk.CTkFrame(parent, fg_color=BORDER, height=1).grid(
            row=row_idx * 10 + 5, column=0, sticky="ew", pady=(0, 2))

        return row

    # ─────────────────────────────────────────────────────────
    # SECTION: APPEARANCE
    # ─────────────────────────────────────────────────────────
    def _section_appearance(self):
        body = self._section_card("🎨", "Appearance", "Theme and display preferences")

        # Theme
        self.theme_var = ctk.StringVar(value="Dark")
        saved_theme = self.app.db.get_config("theme_preference")
        if saved_theme:
            self.theme_var.set(saved_theme.decode("utf-8"))

        def _mk_theme(parent):
            return ctk.CTkOptionMenu(
                parent, variable=self.theme_var,
                values=["Dark", "Light", "System Default"],
                width=180, height=36, fg_color=CARD,
                button_color=BORDER, button_hover_color=CARD_HOVER,
                text_color=TEXT_1, font=FONT_BODY,
                command=self._change_theme
            )
        self._row(body, "Colour Theme", "Choose Dark, Light, or follow your system", _mk_theme, 0)

        # Font scale
        self.scale_var = ctk.StringVar(value="Normal")
        saved_scale = self.app.db.get_config("font_scale")
        if saved_scale:
            self.scale_var.set(saved_scale.decode("utf-8"))

        def _mk_scale(parent):
            return ctk.CTkOptionMenu(
                parent, variable=self.scale_var,
                values=["Small", "Normal", "Large"],
                width=180, height=36, fg_color=CARD,
                button_color=BORDER, button_hover_color=CARD_HOVER,
                text_color=TEXT_1, font=FONT_BODY,
                command=self._change_font_scale
            )
        self._row(body, "Font Size", "Affects labels across the whole app", _mk_scale, 1)

        # Compact mode toggle
        self.compact_var = ctk.BooleanVar(value=False)
        saved_compact = self.app.db.get_config("compact_mode")
        if saved_compact:
            self.compact_var.set(saved_compact.decode() == "1")

        def _mk_compact(parent):
            sw = ctk.CTkSwitch(parent, variable=self.compact_var, text="",
                               onvalue=True, offvalue=False,
                               progress_color=TEAL, button_color=TEXT_1,
                               command=self._save_compact)
            return sw
        self._row(body, "Compact Mode",
                  "Reduces card padding for a denser layout", _mk_compact, 2)

    # ─────────────────────────────────────────────────────────
    # SECTION: SECURITY
    # ─────────────────────────────────────────────────────────
    def _section_security(self):
        body = self._section_card("🔒", "Security", "Auto-lock, clipboard and password policy")

        # Auto-lock timer
        lock_options = ["1 minute", "3 minutes", "5 minutes", "10 minutes", "30 minutes", "Never"]
        lock_ms = {
            "1 minute": 60_000, "3 minutes": 180_000,
            "5 minutes": 300_000, "10 minutes": 600_000,
            "30 minutes": 1_800_000, "Never": 0
        }
        self.lock_var = ctk.StringVar(value="3 minutes")
        saved_lock = self.app.db.get_config("auto_lock_pref")
        if saved_lock:
            self.lock_var.set(saved_lock.decode("utf-8"))

        def _mk_lock(parent):
            return ctk.CTkOptionMenu(
                parent, variable=self.lock_var, values=lock_options,
                width=180, height=36, fg_color=CARD,
                button_color=BORDER, button_hover_color=CARD_HOVER,
                text_color=TEXT_1, font=FONT_BODY,
                command=lambda v: self._save_lock_pref(v, lock_ms)
            )
        self._row(body, "Auto-Lock Timer",
                  "Vault locks automatically after inactivity", _mk_lock, 0)

        # Clipboard clear timer
        clip_options = ["10 seconds", "15 seconds", "30 seconds", "60 seconds", "Never"]
        self.clip_var = ctk.StringVar(value="15 seconds")
        saved_clip = self.app.db.get_config("clipboard_clear_pref")
        if saved_clip:
            self.clip_var.set(saved_clip.decode("utf-8"))

        def _mk_clip(parent):
            return ctk.CTkOptionMenu(
                parent, variable=self.clip_var, values=clip_options,
                width=180, height=36, fg_color=CARD,
                button_color=BORDER, button_hover_color=CARD_HOVER,
                text_color=TEXT_1, font=FONT_BODY,
                command=self._save_clip_pref
            )
        self._row(body, "Clipboard Auto-Clear",
                  "Copied passwords are wiped from clipboard after this delay", _mk_clip, 1)

        # Show passwords in vault by default
        self.show_pwd_var = ctk.BooleanVar(value=False)
        saved_spwd = self.app.db.get_config("show_pwd_default")
        if saved_spwd:
            self.show_pwd_var.set(saved_spwd.decode() == "1")

        def _mk_show_pwd(parent):
            return ctk.CTkSwitch(parent, variable=self.show_pwd_var, text="",
                                 onvalue=True, offvalue=False,
                                 progress_color=TEAL, button_color=TEXT_1,
                                 command=lambda: self.app.db.set_config(
                                     "show_pwd_default",
                                     b"1" if self.show_pwd_var.get() else b"0"))
        self._row(body, "Reveal Passwords by Default",
                  "If off, passwords are always masked on load (recommended: off)", _mk_show_pwd, 2)

        # Breach check on save toggle
        self.breach_on_save_var = ctk.BooleanVar(value=True)
        saved_bos = self.app.db.get_config("breach_check_on_save")
        if saved_bos:
            self.breach_on_save_var.set(saved_bos.decode() == "1")
        else:
            self.app.db.set_config("breach_check_on_save", b"1")

        def _mk_bos(parent):
            return ctk.CTkSwitch(parent, variable=self.breach_on_save_var, text="",
                                 onvalue=True, offvalue=False,
                                 progress_color=TEAL, button_color=TEXT_1,
                                 command=lambda: self.app.db.set_config(
                                     "breach_check_on_save",
                                     b"1" if self.breach_on_save_var.get() else b"0"))
        self._row(body, "Warn on Weak Password When Saving",
                  "Shows a warning toast if you save a weak password", _mk_bos, 3)

        # Change Master Password button
        def _mk_change_mp(parent):
            return ctk.CTkButton(
                parent, text="Change Master Password",
                font=("Helvetica", 13, "bold"),
                fg_color="transparent", border_width=1,
                border_color=RED_DANGER, text_color=RED_DANGER,
                hover_color="#2A1515", width=210, height=36,
                command=self._change_master_password
            )
        self._row(body, "Master Password",
                  "Re-encrypt your vault with a new master password", _mk_change_mp, 4)

    # ─────────────────────────────────────────────────────────
    # SECTION: VAULT
    # ─────────────────────────────────────────────────────────
    def _section_vault(self):
        body = self._section_card("🗄️", "Vault Management", "Export, import and maintenance")

        # Export CSV
        def _mk_export(parent):
            return ctk.CTkButton(
                parent, text="Export to CSV",
                font=("Helvetica", 13, "bold"),
                fg_color=TEAL, hover_color="#00B39F",
                text_color=TEXT_INV, width=180, height=36,
                command=self._export_csv
            )
        self._row(body, "Export Vault",
                  "Save all entries to a plain CSV file (store securely!)", _mk_export, 0)

        # Export JSON
        def _mk_export_json(parent):
            return ctk.CTkButton(
                parent, text="Export to JSON",
                font=("Helvetica", 13, "bold"),
                fg_color=GOLD, hover_color=GOLD_GLOW,
                text_color=TEXT_INV, width=180, height=36,
                command=self._export_json
            )
        self._row(body, "Export as JSON",
                  "Machine-readable export of all decrypted entries", _mk_export_json, 1)

        # Breach cache
        def _mk_clear_cache(parent):
            return ctk.CTkButton(
                parent, text="Clear Breach Cache",
                font=("Helvetica", 13, "bold"),
                fg_color="transparent", border_width=1,
                border_color=AMBER, text_color=AMBER,
                hover_color=CARD_HOVER, width=180, height=36,
                command=self._clear_breach_cache
            )
        self._row(body, "Breach Check Cache",
                  "Cached API responses expire in 7 days — clear to force fresh checks", _mk_clear_cache, 2)

        # Danger zone
        ctk.CTkFrame(body, fg_color=BORDER, height=1).grid(row=35, column=0, sticky="ew", pady=(12, 8))
        ctk.CTkLabel(body, text="⚠  Danger Zone", font=("Helvetica", 13, "bold"),
                     text_color=RED_DANGER).grid(row=36, column=0, sticky="w", pady=(0, 8))

        def _mk_wipe(parent):
            return ctk.CTkButton(
                parent, text="Wipe All Entries",
                font=("Helvetica", 13, "bold"),
                fg_color=RED_DANGER, hover_color="#C53A3A",
                text_color=TEXT_INV, width=180, height=36,
                command=self._confirm_wipe
            )
        self._row(body, "Delete All Vault Entries",
                  "Permanently removes every saved password — cannot be undone!", _mk_wipe, 4)

    # ─────────────────────────────────────────────────────────
    # SECTION: ABOUT
    # ─────────────────────────────────────────────────────────
    def _section_about(self):
        body = self._section_card("ℹ️", "About SecurePass", "Version info and project details")

        info = [
            ("Version",       "1.0.0  (Obsidian Vault)"),
            ("Encryption",    "AES-256-GCM  ·  Argon2-based KDF"),
            ("Breach API",    "HaveIBeenPwned  ·  k-Anonymity"),
            ("Built With",    "Python  ·  CustomTkinter  ·  SQLite3"),
            ("Developed By",  "SecurePass Project Team"),
        ]
        for i, (k, v) in enumerate(info):
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=5)
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=k, font=("Helvetica", 13, "bold"),
                         text_color=TEXT_2, width=130, anchor="w").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(row, text=v, font=FONT_BODY, text_color=TEXT_1,
                         anchor="w").grid(row=0, column=1, sticky="w", padx=(12, 0))

    # ─────────────────────────────────────────────────────────
    # CALLBACKS — APPEARANCE
    # ─────────────────────────────────────────────────────────
    def _change_theme(self, choice: str):
        if choice == "System Default":
            ctk.set_appearance_mode("System")
        else:
            ctk.set_appearance_mode(choice)
        self.app.db.set_config("theme_preference", choice.encode("utf-8"))
        Toast(self.app, f"Theme changed to {choice}.", "success")

    def _change_font_scale(self, choice: str):
        self.app.db.set_config("font_scale", choice.encode("utf-8"))
        Toast(self.app, f"Font scale set to {choice}. Restart to fully apply.", "info")

    def _save_compact(self):
        val = b"1" if self.compact_var.get() else b"0"
        self.app.db.set_config("compact_mode", val)
        Toast(self.app, "Compact mode preference saved. Restart to apply.", "info")

    # ─────────────────────────────────────────────────────────
    # CALLBACKS — SECURITY
    # ─────────────────────────────────────────────────────────
    def _save_lock_pref(self, choice: str, mapping: dict):
        self.app.db.set_config("auto_lock_pref", choice.encode("utf-8"))
        ms = mapping.get(choice, 180_000)
        if ms == 0:
            # Cancel any existing timer
            if self.app.inactivity_timer:
                self.app.after_cancel(self.app.inactivity_timer)
                self.app.inactivity_timer = None
            self.app.auto_lock_time_ms = 0
        else:
            self.app.auto_lock_time_ms = ms
            self.app.reset_inactivity_timer()
        Toast(self.app, f"Auto-lock set to {choice}.", "success")

    def _save_clip_pref(self, choice: str):
        self.app.db.set_config("clipboard_clear_pref", choice.encode("utf-8"))
        Toast(self.app, f"Clipboard will clear after {choice}.", "success")

    def _change_master_password(self):
        win = ctk.CTkToplevel(self.app)
        win.title("Change Master Password")
        win.geometry("460x500")
        win.resizable(False, False)
        win.configure(fg_color=BG_BASE)
        win.transient(self.app)
        win.after(100, win.grab_set)
        win.after(100, win.focus)

        ctk.CTkLabel(win, text="Change Master Password",
                     font=FONT_H2, text_color=TEXT_1).pack(pady=(28, 4), padx=36, anchor="w")
        ctk.CTkLabel(win, text="Enter your current password, then set a new one.",
                     font=FONT_CAPTION, text_color=TEXT_3).pack(padx=36, anchor="w")
        ctk.CTkFrame(win, fg_color=BORDER, height=1).pack(fill="x", padx=30, pady=(12, 18))

        def _field(label, placeholder):
            ctk.CTkLabel(win, text=label, font=FONT_LABEL,
                         text_color=TEXT_2).pack(anchor="w", padx=36)
            e = ctk.CTkEntry(win, placeholder_text=placeholder, show="*",
                             height=44, fg_color=CARD, border_width=1,
                             border_color=BORDER, corner_radius=8,
                             font=FONT_BODY, text_color=TEXT_1)
            e.pack(fill="x", padx=36, pady=(4, 14))
            return e

        cur_e = _field("Current Password", "Your current master password")
        new_e = _field("New Password", "Minimum 8 characters")
        con_e = _field("Confirm New Password", "Re-enter new password")

        def _apply():
            cur = cur_e.get()
            new = new_e.get()
            con = con_e.get()

            # ── Validation ───────────────────────────────────────
            if not cur:
                status_lbl.configure(text="Please enter your current password.", text_color=AMBER)
                return
            if len(new) < 8:
                status_lbl.configure(text="New password must be at least 8 characters.", text_color=AMBER)
                return
            if new != con:
                status_lbl.configure(text="New passwords do not match.", text_color=AMBER)
                return
            if new == cur:
                status_lbl.configure(text="New password must differ from the current one.", text_color=AMBER)
                return

            # ── Step 1: Verify current password ─────────────────
            salt = self.app.db.get_salt()
            val_c = self.app.db.get_config("val_cipher")
            val_n = self.app.db.get_config("val_nonce")

            from crypto_manager import EncryptionManager
            old_crypto = EncryptionManager()
            try:
                old_crypto.derive_key(cur, salt)
                verified = old_crypto.decrypt_data(val_c, val_n)
                if verified != "AUTH_SUCCESS":
                    raise ValueError("wrong password")
            except Exception:
                status_lbl.configure(text="Current password is incorrect.", text_color=RED_DANGER)
                return

            # ── Step 2: Disable UI + show progress ───────────────
            apply_btn.configure(state="disabled", text="Re-encrypting...")
            cancel_btn.configure(state="disabled")
            status_lbl.configure(text="Deriving new key (this may take a moment)...", text_color=TEXT_3)
            win.update()

            def _do_rekey():
                try:
                    # Derive new key
                    new_crypto = EncryptionManager()
                    _, new_salt = new_crypto.derive_key(new)

                    # ── Step 3: Re-encrypt every vault entry ─────
                    entries = self.app.db.get_all_entries()
                    win.after(0, lambda: status_lbl.configure(
                        text=f"Re-encrypting {len(entries)} entries...", text_color=TEXT_3))

                    for entry in entries:
                        plaintext = old_crypto.decrypt_data(entry["ciphertext"], entry["nonce"])
                        if plaintext.startswith("ERROR:"):
                            continue
                        result = new_crypto.encrypt_data(plaintext)
                        try:
                            cat = entry["category"] or "General"
                        except Exception:
                            cat = "General"
                        try:
                            ctx = entry["context"] or ""
                        except Exception:
                            ctx = ""
                        self.app.db.update_entry(
                            entry["id"], entry["website"], entry["username"],
                            result["ciphertext"], result["nonce"],
                            context=ctx, category=cat
                        )

                    # ── Step 4: Save new salt + verifier ─────────
                    self.app.db.set_config("master_salt", new_salt)
                    val = new_crypto.encrypt_data("AUTH_SUCCESS")
                    self.app.db.set_config("val_cipher", val["ciphertext"])
                    self.app.db.set_config("val_nonce", val["nonce"])

                    # Swap in-memory key so current session keeps working
                    self.app.crypto.key = new_crypto.key

                    win.after(0, _on_success)

                except Exception as ex:
                    win.after(0, lambda e=str(ex): _on_error(e))

            def _on_success():
                win.destroy()
                Toast(self.app, "Master password changed! All entries re-encrypted.", "success")

            def _on_error(msg):
                apply_btn.configure(state="normal", text="Apply Change")
                cancel_btn.configure(state="normal")
                status_lbl.configure(text=f"Error: {msg}", text_color=RED_DANGER)

            import threading
            threading.Thread(target=_do_rekey, daemon=True).start()

        # Status label (shown between fields and buttons)
        status_lbl = ctk.CTkLabel(win, text="", font=FONT_CAPTION, text_color=AMBER,
                                   wraplength=380, justify="left")
        status_lbl.pack(padx=36, anchor="w", pady=(0, 6))

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=36, pady=(4, 24))
        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent",
                                   border_width=1, border_color=BORDER, text_color=TEXT_2,
                                   width=110, height=44, hover_color=BORDER,
                                   command=win.destroy)
        cancel_btn.pack(side="left", padx=(0, 10))
        apply_btn = ctk.CTkButton(btn_row, text="Apply Change", fg_color=TEAL,
                                  hover_color="#00B39F", text_color=TEXT_INV,
                                  width=160, height=44, font=("Helvetica", 14, "bold"),
                                  command=_apply)
        apply_btn.pack(side="right")

    # ─────────────────────────────────────────────────────────
    # CALLBACKS — VAULT
    # ─────────────────────────────────────────────────────────
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"securepass_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not path:
            return
        try:
            entries = self.app.db.get_all_entries()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["website", "username", "password", "category", "context", "created_at"])
                for e in entries:
                    try:
                        pwd = self.app.crypto.decrypt_data(e["ciphertext"], e["nonce"])
                    except Exception:
                        pwd = "[decryption error]"
                    writer.writerow([
                        e["website"] or "",
                        e["username"] or "",
                        pwd,
                        e["category"] or "General",
                        e["context"] or "",
                        e["created_at"] or ""
                    ])
            Toast(self.app, f"Exported {len(entries)} entries to CSV.", "success")
        except Exception as ex:
            Toast(self.app, f"Export failed: {ex}", "error")

    def _export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"securepass_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        if not path:
            return
        try:
            entries = self.app.db.get_all_entries()
            data = []
            for e in entries:
                try:
                    pwd = self.app.crypto.decrypt_data(e["ciphertext"], e["nonce"])
                except Exception:
                    pwd = "[decryption error]"
                data.append({
                    "website": e["website"] or "",
                    "username": e["username"] or "",
                    "password": pwd,
                    "category": e["category"] or "General",
                    "context": e["context"] or "",
                    "created_at": e["created_at"] or ""
                })
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            Toast(self.app, f"Exported {len(entries)} entries to JSON.", "success")
        except Exception as ex:
            Toast(self.app, f"Export failed: {ex}", "error")

    def _clear_breach_cache(self):
        try:
            self.app.db.cursor.execute("DELETE FROM breach_cache")
            self.app.db.conn.commit()
            Toast(self.app, "Breach cache cleared. Next scan will fetch fresh data.", "info")
        except Exception as ex:
            Toast(self.app, f"Failed to clear cache: {ex}", "error")

    def _confirm_wipe(self):
        win = ctk.CTkToplevel(self.app)
        win.title("Confirm Wipe")
        win.geometry("400x220")
        win.resizable(False, False)
        win.configure(fg_color=CARD)
        win.transient(self.app)
        win.after(100, win.grab_set)
        win.after(100, win.focus)

        ctk.CTkLabel(win, text="⚠  Delete All Entries?",
                     font=FONT_H2, text_color=RED_DANGER).pack(pady=(28, 8))
        ctk.CTkLabel(win, text="This will permanently delete every saved password.\nThis action CANNOT be undone.",
                     font=FONT_BODY, text_color=TEXT_3, justify="center").pack(pady=(0, 24))

        row = ctk.CTkFrame(win, fg_color="transparent")
        row.pack()

        def _wipe():
            self.app.db.cursor.execute("DELETE FROM entries")
            self.app.db.conn.commit()
            win.destroy()
            # Refresh vault page if it's showing
            vault = self.app.pages.get("Vault")
            if vault and hasattr(vault, "refresh_list"):
                vault.refresh_list()
            Toast(self.app, "All entries wiped from vault.", "error")

        ctk.CTkButton(row, text="Cancel", fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT_2, width=110,
                      hover_color=BORDER, command=win.destroy).pack(side="left", padx=8)
        ctk.CTkButton(row, text="Yes, Delete All", fg_color=RED_DANGER,
                      hover_color="#C53A3A", text_color=TEXT_INV, width=150,
                      command=_wipe).pack(side="left", padx=8)

import customtkinter as ctk
import time
import threading
import os
from PIL import Image
from db_manager import DatabaseManager
from crypto_manager import EncryptionManager
from security_engine import SecurityEngine
from ui.design import BG_BASE, BG_DEEP, PANEL, TEXT_1, TEXT_2, GOLD, BORDER, TEXT_3, CARD, BORDER_BRIGHT, FONT_BODY, FONT_H3, FONT_LABEL, GOLD_GLOW, TEXT_INV, Toast
from ui.components.common import StrengthBar
from ui.components.sidebar import Sidebar

from ui.pages.vault import VaultPage
from ui.pages.generator import GeneratorPage
from ui.pages.breach_check import BreachCheckPage
from ui.pages.settings import SettingsPage
from ui.pages.audit import AuditPage

class SecurePassApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db       = DatabaseManager()
        self.crypto   = EncryptionManager()
        self.security = SecurityEngine()

        # Appearance mode load
        saved_theme = self.db.get_config("theme_preference")
        if saved_theme:
            t = saved_theme.decode("utf-8")
            if t == "System Default":
                ctk.set_appearance_mode("System")
            else:
                ctk.set_appearance_mode(t)

        self.title("SecurePass — Obsidian Vault")
        self.geometry("1200x820")
        self.minsize(1060, 680)
        self.configure(fg_color=BG_BASE)

        self.is_unlocked       = False
        self.auto_lock_time_ms = 180_000
        self.inactivity_timer  = None
        self.cover_frame       = None
        self._copied_pwd       = None

        self.dialog_open = False

        self.bind("<Any-Motion>",   self.reset_inactivity_timer)
        self.bind("<Any-KeyPress>", self.reset_inactivity_timer)

        # Row 1 is main
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, app=self)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_remove()

        self._build_main_container()

        # Clipboard Shredder Daemon
        threading.Thread(target=self._clipboard_shredder_daemon, daemon=True).start()

        self.after(80, self.check_user_status)

    def _build_main_container(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=1, sticky="nsew")
        self.main_container.grid_remove()
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "Vault":        VaultPage(self.main_container, self),
            "Generator":    GeneratorPage(self.main_container, self),
            "Breach Check": BreachCheckPage(self.main_container, self),
            "Audit":        AuditPage(self.main_container, self),
            "Settings":     SettingsPage(self.main_container, self)
        }
        for f in self.pages.values():
            f.grid(row=0, column=0, sticky="nsew")

    def show_page(self, key: str):
        for k, f in self.pages.items():
            if k == key:
                f.grid(row=0, column=0, sticky="nsew")
                if hasattr(f, 'refresh_list'):
                    f.refresh_list()
            else:
                f.grid_remove()
        self.sidebar.highlight_active(key)

    # Auth Methods
    def check_user_status(self):
        if not self.db.get_salt():
            self._show_master_setup()
        elif not self.is_unlocked:
            self.show_login()

    def _show_master_setup(self):
        self._build_auth_screen("register")

    def show_login(self):
        self._build_auth_screen("login")

    def _build_auth_screen(self, mode):
        self.sidebar.grid_remove()
        self.main_container.grid_remove()
        if self.cover_frame:
            self.cover_frame.destroy()

        self.cover_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_BASE)
        self.cover_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        center_wrap = ctk.CTkFrame(self.cover_frame, fg_color="transparent")
        center_wrap.place(relx=0.5, rely=0.45, anchor="center")

        brand_frame = ctk.CTkFrame(center_wrap, fg_color="transparent")
        brand_frame.pack(pady=(0, 30))

        # --- Logo image — dark pill so it looks right in both themes ---
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png")
        logo_path = os.path.normpath(logo_path)
        if os.path.exists(logo_path):
            pil_img = Image.open(logo_path).resize((88, 88), Image.LANCZOS)
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(88, 88))
            logo_pill = ctk.CTkFrame(brand_frame, width=100, height=100,
                                     corner_radius=20, fg_color="#12151F")
            logo_pill.pack(pady=(0, 16))
            logo_pill.pack_propagate(False)
            ctk.CTkLabel(logo_pill, image=logo_img, text="").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(brand_frame, text="SecurePass",
                     font=("Georgia", 34, "bold"), text_color=TEXT_1).pack()

        form_container = ctk.CTkFrame(center_wrap, fg_color=CARD, border_width=1, border_color=BORDER_BRIGHT, corner_radius=16)
        form_container.pack()
        inner = ctk.CTkFrame(form_container, fg_color="transparent")
        inner.pack(padx=45, pady=40)
        element_width = 360

        if mode == "register":
            ctk.CTkLabel(inner, text="Create Your Vault", font=("Georgia", 28, "bold"), text_color=TEXT_1).pack(anchor="center", pady=(0, 8))
            ctk.CTkLabel(inner, text="Set a master password. We cannot recover it for you.",
                         font=("Helvetica", 14), text_color=TEXT_3).pack(anchor="center", pady=(0, 32))
            ctk.CTkLabel(inner, text="MASTER PASSWORD", font=("Helvetica", 12, "bold"), text_color=TEXT_3).pack(anchor="w")
            self.entry_reg_pass = ctk.CTkEntry(inner, placeholder_text="Minimum 8 characters", show="*",
                                               height=50, width=element_width, 
                                               fg_color=BG_BASE, border_width=1, border_color=BORDER,
                                               corner_radius=10, font=FONT_BODY, text_color=TEXT_1)
            self.entry_reg_pass.pack(fill="x", pady=(8, 8))
            self.entry_reg_pass.bind("<Return>", lambda _e: self.register_user())
            self.entry_reg_pass.focus()
            sb = StrengthBar(inner)
            sb.pack(fill="x", pady=(0, 28))
            self.entry_reg_pass.bind("<KeyRelease>", lambda _e: sb.update_strength(self.entry_reg_pass.get()))
            ctk.CTkButton(inner, text="Initialize Vault", font=("Helvetica", 15, "bold"),
                          fg_color=GOLD, hover_color=GOLD_GLOW, text_color=TEXT_INV,
                          height=50, width=element_width, corner_radius=12, command=self.register_user).pack(fill="x")
        else:
            salt = self.db.get_salt()
            ctk.CTkLabel(inner, text="Unlock Vault", font=("Georgia", 28, "bold"), text_color=TEXT_1).pack(anchor="center", pady=(0, 8))
            ctk.CTkLabel(inner, text="Enter your master password to access your credentials.",
                         font=("Helvetica", 14), text_color=TEXT_3).pack(anchor="center", pady=(0, 32))
            ctk.CTkLabel(inner, text="MASTER PASSWORD", font=("Helvetica", 12, "bold"), text_color=TEXT_3).pack(anchor="w")
            self.entry_login_pass = ctk.CTkEntry(inner, placeholder_text="Master Password", show="*",
                                                 height=50, width=element_width, 
                                                 fg_color=BG_BASE, border_width=1, border_color=BORDER,
                                                 corner_radius=10, font=FONT_BODY, text_color=TEXT_1)
            self.entry_login_pass.pack(fill="x", pady=(8, 32))
            self.entry_login_pass.bind("<Return>", lambda _e: self.login_user(salt))
            self.entry_login_pass.focus()
            ctk.CTkButton(inner, text="Unlock Vault", font=("Helvetica", 15, "bold"),
                          fg_color=GOLD, hover_color=GOLD_GLOW, text_color=TEXT_INV,
                          height=50, width=element_width, corner_radius=12, command=lambda: self.login_user(salt)).pack(fill="x")

    def register_user(self):
        pwd = self.entry_reg_pass.get().strip()
        if len(pwd) < 8:
            Toast(self, "Password must be at least 8 characters.", "error")
            return
        key, new_salt = self.crypto.derive_key(pwd)
        self.db.set_config("master_salt", new_salt)
        val = self.crypto.encrypt_data("AUTH_SUCCESS")
        self.db.set_config("val_cipher", val["ciphertext"])
        self.db.set_config("val_nonce", val["nonce"])
        self.db.set_config("failed_attempts", b"0")
        self.db.set_config("lockout_until", b"0.0")
        Toast(self, "Vault created successfully!", "success")
        self.is_unlocked = True
        self.reset_inactivity_timer()
        self.show_dashboard()

    def login_user(self, salt):
        lockout = self.db.get_config("lockout_until")
        if lockout and time.time() < float(lockout.decode()):
            Toast(self, "Vault locked due to failed attempts. Try again later.", "error")
            return
        try:
            self.crypto.derive_key(self.entry_login_pass.get().strip(), salt)
        except Exception as e:
            print(f"[WARN] Key derivation error during login: {e}")
        val_c = self.db.get_config("val_cipher")
        val_n = self.db.get_config("val_nonce")
        if val_c and val_n:
            try:
                if self.crypto.decrypt_data(val_c, val_n) == "AUTH_SUCCESS":
                    self.db.set_config("failed_attempts", b"0")
                    self.db.set_config("lockout_until", b"0.0")
                    self.is_unlocked = True
                    self.reset_inactivity_timer()
                    self.show_dashboard()
                    return
            except Exception:
                pass
        attempts = int((self.db.get_config("failed_attempts") or b"0").decode()) + 1
        if attempts >= 3:
            self.db.set_config("lockout_until", str(time.time() + 14400).encode())
            Toast(self, "3 failed attempts — vault locked for 4 hours.", "error")
        else:
            self.db.set_config("failed_attempts", str(attempts).encode())
            Toast(self, f"Incorrect password. {3 - attempts} attempt(s) remaining.", "error")

    def show_dashboard(self):
        self.sidebar.grid()
        self.main_container.grid()
        if self.cover_frame:
            self.cover_frame.grid_remove()
        self.show_page("Vault")

    def lock_vault(self):
        """Immediately lock the vault and show the login screen."""
        if not self.is_unlocked:
            return
        self.is_unlocked = False
        self.crypto.key = None          # Wipe in-memory key for security
        if self.inactivity_timer:
            self.after_cancel(self.inactivity_timer)
            self.inactivity_timer = None
        self.check_user_status()
        Toast(self, "Vault locked.", "warn")

    def reset_inactivity_timer(self, event=None):
        if not self.is_unlocked: return
        now = time.time()
        if hasattr(self, '_last_interact') and now - self._last_interact < 0.2:
            return
        self._last_interact = now

        if self.inactivity_timer:
            self.after_cancel(self.inactivity_timer)
        self.inactivity_timer = self.after(self.auto_lock_time_ms, self.trigger_auto_lock)

    def trigger_auto_lock(self):
        if self.is_unlocked:
            self.is_unlocked = False
            self.check_user_status()
            Toast(self, "Vault auto-locked due to inactivity.", "warn")

    def _clipboard_shredder_daemon(self):
        while True:
            time.sleep(15)  # Clear clipboard every 15s (as documented)
            if self._copied_pwd:
                try:
                    if self.clipboard_get() == self._copied_pwd:
                        self.clipboard_clear()
                        self._copied_pwd = None
                except Exception:
                    pass

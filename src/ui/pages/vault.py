import customtkinter as ctk
from security_engine import SecurityEngine
from ui.design import FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_BODY_SM, FONT_LABEL, FONT_MONO, FONT_CAPTION, BG_BASE, TEXT_1, TEXT_2, TEXT_3, GOLD, GOLD_GLOW, TEXT_INV, TEAL, CARD, BORDER, CARD_HOVER, RED_DANGER, GREEN_OK, AMBER, AVATAR_COLORS, BORDER_BRIGHT, Toast
from ui.components.common import StrengthBar

CATEGORIES = ["General", "Social", "Banking", "Work", "Shopping", "Email", "Gaming", "Other"]
SORT_OPTIONS = ["Name (A→Z)", "Name (Z→A)", "Newest First", "Oldest First"]

class VaultPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self.pwd_vars = {}
        
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent", height=68)
        header.grid(row=0, column=0, sticky="ew", padx=35, pady=(28, 0))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        title_blk = ctk.CTkFrame(header, fg_color="transparent")
        title_blk.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_blk, text="Vault Overview", font=("Georgia", 32, "bold"), text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(title_blk, text="All your credentials, encrypted at rest",
                     font=("Helvetica", 15), text_color=TEXT_3).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(header, text="+ Add Entry", font=("Helvetica", 13, "bold"),
                      fg_color=GOLD, hover_color=GOLD_GLOW, text_color=TEXT_INV,
                      corner_radius=10, width=130, height=42,
                      command=self.open_add_password_window).grid(row=0, column=1, sticky="e")

        # ── Stat cards ───────────────────────────────────────
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=35, pady=(18, 16))
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_total    = self._stat_card(stats, 0, "Total Passwords", "0",   GOLD,       "total password and lock.png")
        self.lbl_breached = self._stat_card(stats, 1, "Exposed",         "0",   RED_DANGER, "exposed.png")
        self.lbl_reused   = self._stat_card(stats, 2, "Reused",          "0",   AMBER,      "reused.png")
        self.lbl_health   = self._stat_card(stats, 3, "Vault Health",    "Good",GREEN_OK,   "vaulthealth.png")

        # ── Search + Sort + Filter row ───────────────────────
        ctrl_row = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_row.grid(row=2, column=0, sticky="ew", padx=35, pady=(0, 10))
        ctrl_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(ctrl_row,
                          placeholder_text="Search by website or username...",
                          height=46, fg_color=CARD, border_width=1, border_color=BORDER_BRIGHT,
                          corner_radius=10, text_color=TEXT_1, placeholder_text_color=TEXT_3,
                          font=("Helvetica", 14))
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda _e: self.refresh_list())

        # Sort + Category filter
        filter_bar = ctk.CTkFrame(ctrl_row, fg_color="transparent")
        filter_bar.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(filter_bar, text="Sort:", font=("Helvetica", 13, "bold"),
                     text_color=TEXT_2).pack(side="left", padx=(2, 6))
        self.sort_var = ctk.StringVar(value=SORT_OPTIONS[0])
        ctk.CTkOptionMenu(filter_bar, variable=self.sort_var, values=SORT_OPTIONS,
                          width=160, height=34, fg_color=CARD, button_color=BORDER,
                          button_hover_color=CARD_HOVER, text_color=TEXT_1,
                          font=("Helvetica", 13),
                          command=lambda _: self.refresh_list()
                          ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filter_bar, text="Category:", font=("Helvetica", 13, "bold"),
                     text_color=TEXT_2).pack(side="left", padx=(0, 6))
        self.cat_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filter_bar, variable=self.cat_var,
                          values=["All"] + CATEGORIES,
                          width=150, height=34, fg_color=CARD, button_color=BORDER,
                          button_hover_color=CARD_HOVER, text_color=TEXT_1,
                          font=("Helvetica", 13),
                          command=lambda _: self.refresh_list()
                          ).pack(side="left")

        # ── Vault list ───────────────────────────────────────
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                   scrollbar_button_color=BORDER,
                                                   scrollbar_button_hover_color=BORDER_BRIGHT)
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=35, pady=(0, 20))

        self.refresh_list()

    def _load_colored_icon(self, filename, hex_color):
        import os
        from PIL import Image
        base_dir = os.path.dirname(__file__)
        path = os.path.normpath(os.path.join(base_dir, "..", "..", "..", "assets", filename))
        
        if os.path.exists(path):
            pil_img = Image.open(path).convert("RGBA")
            data = pil_img.getdata()
            new_data = []
            h = hex_color.lstrip('#') if isinstance(hex_color, str) else "FFFFFF"
            if len(h) == 6:
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            else:
                r, g, b = 255, 255, 255
                
            for item in data:
                if item[3] > 0:
                    new_data.append((r, g, b, item[3]))
                else:
                    new_data.append(item)
            pil_img.putdata(new_data)
            pil_img = pil_img.resize((24, 24), Image.LANCZOS)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
        return None

    def _stat_card(self, parent, col, title, value, color, icon):
        pad_l = 0 if col == 0 else 8
        pad_r = 0 if col == 2 else 8
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, height=110)
        card.grid(row=0, column=col, sticky="ew", padx=(pad_l, pad_r))
        card.grid_propagate(False)

        stripe = ctk.CTkFrame(card, fg_color=color, width=3, height=94, corner_radius=0)
        stripe.place(x=0, y=8)

        icon_bg = ctk.CTkFrame(card, fg_color=CARD_HOVER, width=42, height=42, corner_radius=10)
        icon_bg.place(x=18, rely=0.5, anchor="w")
        
        img = None
        if icon.endswith(".png"):
            img = self._load_colored_icon(icon, color)
            
        if img:
            ctk.CTkLabel(icon_bg, text="", image=img).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(icon_bg, text=icon, font=("Helvetica", 16, "bold"), text_color=color).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=title, font=("Helvetica", 14, "bold"), text_color=TEXT_2).place(x=76, y=22)
        lbl = ctk.CTkLabel(card, text=value, font=("Georgia", 28, "bold"), text_color=TEXT_1)
        lbl.place(x=76, y=50)
        return lbl

    def refresh_list(self, search_query: str = None):
        if search_query is None:
            search_query = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=30)
        hdr.pack(fill="x", padx=6, pady=(2, 6))
        hdr_kw = {"font": ("Helvetica", 13, "bold"), "text_color": TEXT_2}
        ctk.CTkLabel(hdr, text="SERVICE",  **hdr_kw).place(x=68,  rely=0.5, anchor="w")
        ctk.CTkLabel(hdr, text="USERNAME", **hdr_kw).place(x=285, rely=0.5, anchor="w")
        ctk.CTkLabel(hdr, text="PASSWORD", **hdr_kw).place(x=530, rely=0.5, anchor="w")
        ctk.CTkLabel(hdr, text="ACTIONS",  **hdr_kw).place(relx=0.97, rely=0.5, anchor="e")
        ctk.CTkFrame(self.scroll_frame, fg_color=BORDER, height=1).pack(fill="x", padx=4, pady=(0, 6))

        all_entries = self.app.db.get_all_entries()
        total_cnt = len(all_entries)
        self.lbl_total.configure(text=str(total_cnt))

        # Compute duplicate set for badge display
        import hashlib
        _hash_count = {}
        for e in all_entries:
            try:
                pwd = self.app.crypto.decrypt_data(e["ciphertext"], e["nonce"])
                h = hashlib.sha256(pwd.encode()).hexdigest()
                _hash_count[h] = _hash_count.get(h, 0) + 1
            except Exception:
                pass
        reuse_ids = set()
        for e in all_entries:
            try:
                pwd = self.app.crypto.decrypt_data(e["ciphertext"], e["nonce"])
                h = hashlib.sha256(pwd.encode()).hexdigest()
                if _hash_count.get(h, 0) > 1:
                    reuse_ids.add(e["id"])
            except Exception:
                pass
        self.lbl_reused.configure(text=str(len(reuse_ids)))

        entries = list(all_entries)

        # Category filter
        cat = self.cat_var.get() if hasattr(self, 'cat_var') else "All"
        if cat != "All":
            entries = [e for e in entries if (e["category"] or "General") == cat]

        # Search filter
        q = search_query.strip().lower()
        if q:
            entries = [e for e in entries
                       if q in (e["website"] or "").lower() or q in (e["username"] or "").lower()]

        # Sort
        sort = self.sort_var.get() if hasattr(self, 'sort_var') else SORT_OPTIONS[0]
        if sort == "Name (A→Z)":
            entries.sort(key=lambda e: (e["website"] or "").lower())
        elif sort == "Name (Z→A)":
            entries.sort(key=lambda e: (e["website"] or "").lower(), reverse=True)
        elif sort == "Newest First":
            entries.sort(key=lambda e: (e["created_at"] or "1970-01-01"), reverse=True)
        elif sort == "Oldest First":
            entries.sort(key=lambda e: (e["created_at"] or "1970-01-01"))

        if not entries:
            empty = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            empty.pack(pady=80)
            ctk.CTkLabel(empty, text="No entries found", font=("Georgia", 24, "bold"), text_color=TEXT_2).pack(pady=(0, 8))
            ctk.CTkLabel(empty, text="Try a different search or add a new entry",
                         font=("Helvetica", 15), text_color=TEXT_3).pack()
            return

        for i, row in enumerate(entries):
            self._build_entry_card(row, i, is_reused=(row["id"] in reuse_ids))

    def _build_entry_card(self, row, idx: int, is_reused: bool = False):
        color = AVATAR_COLORS[idx % len(AVATAR_COLORS)]

        item = ctk.CTkFrame(self.scroll_frame, fg_color=CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        item.pack(fill="x", pady=6, padx=8, ipady=8)

        website = row["website"] or ""
        initial = website[0].upper() if website else "?"

        av = ctk.CTkFrame(item, fg_color=color, width=42, height=42, corner_radius=21)
        av.pack(side="left", padx=16, pady=8)
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=initial, font=("Georgia", 18, "bold"), text_color=TEXT_INV).pack(expand=True)

        info = ctk.CTkFrame(item, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(0, 12))
        ctk.CTkLabel(info, text=row["website"], font=FONT_H3, text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(info, text=row["username"], font=FONT_BODY, text_color=TEXT_2).pack(anchor="w")
        
        try:
            ctx = row["context"]
            if ctx:
                display_ctx = ctx if len(ctx) <= 35 else ctx[:32] + "..."
                ctk.CTkLabel(info, text=display_ctx, font=FONT_CAPTION, text_color=TEXT_3).pack(anchor="w")
        except IndexError:
            pass

        pwd_container = ctk.CTkFrame(item, fg_color=CARD_HOVER, corner_radius=8)
        pwd_container.pack(side="left", padx=12, pady=8)

        pwd_var = ctk.StringVar(value="••••••••••••")
        self.pwd_vars[row["id"]] = pwd_var
        pwd_lbl = ctk.CTkLabel(pwd_container, textvariable=pwd_var, font=FONT_MONO, text_color=GOLD)
        pwd_lbl.pack(side="left", padx=12, pady=8)

        eye_img = self._load_colored_icon("eye.png", GOLD)
        eye_off_img = self._load_colored_icon("eye-off.png", GOLD)

        def _toggle(r=row, var=pwd_var, lbl=pwd_lbl):
            if var.get().startswith("•"):
                try:
                    dec = self.app.crypto.decrypt_data(r["ciphertext"], r["nonce"])
                    var.set(dec)
                    lbl.configure(text_color=TEXT_1)
                    eye_btn.configure(image=eye_off_img)
                except Exception:
                    var.set("Decryption failed")
                    lbl.configure(text_color=RED_DANGER)
            else:
                var.set("••••••••••••")
                lbl.configure(text_color=GOLD)
                eye_btn.configure(image=eye_img)

        eye_btn = ctk.CTkButton(pwd_container, text="", width=30, height=30, image=eye_img,
                      fg_color="transparent", text_color=TEXT_2,
                      hover_color=BORDER, command=_toggle)
        eye_btn.pack(side="left", padx=(0, 8))

        # Reused badge
        if is_reused:
            badge = ctk.CTkFrame(item, fg_color=AMBER, corner_radius=6, height=24)
            badge.pack(side="right", padx=(0, 8))
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text="  Reused  ", font=("Helvetica", 11, "bold"),
                         text_color="#07080D").pack(padx=4, pady=3)

        act = ctk.CTkFrame(item, fg_color="transparent")
        act.pack(side="right", padx=12)
        ctk.CTkButton(act, text="Copy", width=80, height=36,
                      fg_color=TEAL, text_color=TEXT_INV,
                      command=lambda r=row: self._copy_pass(r)).pack(side="left", padx=3)
        ctk.CTkButton(act, text="Edit", width=80, height=36,
                      fg_color=GOLD, text_color=TEXT_INV,
                      command=lambda r=row: self.open_edit_password_window(r)).pack(side="left", padx=3)
        ctk.CTkButton(act, text="Delete", width=80, height=36,
                      fg_color=RED_DANGER, text_color=TEXT_INV,
                      command=lambda r=row: self._delete_entry(r["id"])).pack(side="left", padx=3)

    def _copy_pass(self, row):
        try:
            pwd = self.app.crypto.decrypt_data(row["ciphertext"], row["nonce"])
            self.app.clipboard_clear()
            self.app.clipboard_append(pwd)
            self.app.update()
            self.app._copied_pwd = pwd  # Register with clipboard shredder daemon
            Toast(self.app, "Password copied! Clipboard clears in 15s.", "success")
        except Exception as e:
            print(f"[ERROR] Decryption error on copy: {e}")
            Toast(self.app, "Decryption error on copy.", "error")

    def _delete_entry(self, eid: int):
        win = ctk.CTkToplevel(self.app)
        win.title("Confirm Delete")
        win.geometry("380x200")
        win.resizable(False, False)
        win.configure(fg_color=CARD)
        win.transient(self.app)
        win.after(100, win.grab_set)
        win.after(100, win.focus)

        ctk.CTkLabel(win, text="Are you sure?", font=FONT_H2, text_color=TEXT_1).pack(pady=(30, 8))
        ctk.CTkLabel(win, text="This password will be permanently deleted.", font=FONT_BODY, text_color=TEXT_3).pack()

        row_df = ctk.CTkFrame(win, fg_color="transparent")
        row_df.pack(pady=(24, 0))

        def confirm():
            self.app.db.delete_entry(eid)
            self.refresh_list()
            win.destroy()
            Toast(self.app, "Entry deleted.", "info")

        ctk.CTkButton(row_df, text="Cancel", fg_color="transparent", border_width=1, border_color=BORDER, text_color=TEXT_2, width=100, hover_color=BORDER, command=win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(row_df, text="Delete", fg_color=RED_DANGER, hover_color="#C53A3A", text_color=TEXT_INV, width=100, command=confirm).pack(side="left", padx=10)

    def open_add_password_window(self):
        self._open_entry_form(row=None)

    def open_edit_password_window(self, row):
        self._open_entry_form(row=row)

    def _open_entry_form(self, row=None):
        is_edit = row is not None
        win = ctk.CTkToplevel(self.app)
        win.title("Edit Entry" if is_edit else "New Entry")
        win.geometry("500x720")
        win.resizable(False, False)
        win.configure(fg_color=BG_BASE)
        win.transient(self.app)
        win.after(100, win.grab_set)
        win.after(100, win.focus)

        ctk.CTkLabel(win, text="Edit Entry" if is_edit else "New Entry",
                     font=FONT_H2, text_color=TEXT_1).pack(pady=(30, 4), padx=36, anchor="w")
        ctk.CTkLabel(win, text="Saved with AES-256-GCM encryption. Zero plaintext stored.",
                     font=FONT_CAPTION, text_color=TEXT_3).pack(padx=36, anchor="w")
        ctk.CTkFrame(win, fg_color=BORDER, height=1).pack(fill="x", padx=30, pady=(14, 18))

        def _field(label: str, placeholder: str, masked: bool = False):
            ctk.CTkLabel(win, text=label, font=FONT_LABEL, text_color=TEXT_2).pack(anchor="w", padx=36)
            e = ctk.CTkEntry(win, placeholder_text=placeholder,
                             show="*" if masked else "",
                             height=44, fg_color=CARD,
                             border_width=1, border_color=BORDER,
                             corner_radius=8, font=FONT_BODY, text_color=TEXT_1)
            e.pack(fill="x", padx=36, pady=(4, 14))
            return e

        site_e    = _field("Website / Service",          "e.g. github.com")
        user_e    = _field("Username / Email",            "e.g. user@example.com")

        # ── Password field: entry + 👁 eye button rendered INSIDE the box ──
        ctk.CTkLabel(win, text="Password", font=FONT_LABEL, text_color=TEXT_2).pack(anchor="w", padx=36)

        # Outer frame styled to look like an entry box
        pass_box = ctk.CTkFrame(win, fg_color=CARD,
                                border_width=1, border_color=BORDER,
                                corner_radius=8, height=44)
        pass_box.pack(fill="x", padx=36, pady=(4, 14))
        pass_box.pack_propagate(False)
        pass_box.grid_columnconfigure(0, weight=1)

        # Actual entry — no border, transparent bg (inherits box styling)
        pass_e = ctk.CTkEntry(pass_box,
                              placeholder_text="Enter or generate a password",
                              show="*", height=42,
                              fg_color="transparent", border_width=0,
                              font=FONT_BODY, text_color=TEXT_1)
        pass_e.grid(row=0, column=0, sticky="ew", padx=(10, 0))

        eye_img = self._load_colored_icon("eye.png", GOLD)
        eye_off_img = self._load_colored_icon("eye-off.png", GOLD)

        def _toggle_pass():
            if pass_e.cget("show") == "*":
                pass_e.configure(show="")
                eye_btn.configure(image=eye_off_img)
            else:
                pass_e.configure(show="*")
                eye_btn.configure(image=eye_img)

        eye_btn = ctk.CTkButton(pass_box, text="", width=36, height=36, image=eye_img,
                                fg_color="transparent", hover_color=BORDER,
                                text_color=TEXT_2, corner_radius=6,
                                command=_toggle_pass)
        eye_btn.grid(row=0, column=1, padx=(0, 4))
        # ───────────────────────────────────────────────────────────────

        context_e = _field("Related Context / Notes", "e.g. PIN, recovery codes, or hints")

        # ── Category dropdown ────────────────────────────────
        ctk.CTkLabel(win, text="Category", font=FONT_LABEL, text_color=TEXT_2).pack(anchor="w", padx=36)
        cat_var = ctk.StringVar(value="General")
        ctk.CTkOptionMenu(win, variable=cat_var, values=CATEGORIES,
                          height=44, fg_color=CARD, button_color=BORDER,
                          button_hover_color=CARD_HOVER, text_color=TEXT_1,
                          font=FONT_BODY
                          ).pack(fill="x", padx=36, pady=(4, 14))

        if is_edit:
            site_e.insert(0, row["website"])
            user_e.insert(0, row["username"])
            try:
                if row["context"]:
                    context_e.insert(0, row["context"])
            except IndexError:
                pass
            try:
                cat_var.set(row["category"] or "General")
            except Exception:
                pass
            try:
                dec = self.app.crypto.decrypt_data(row["ciphertext"], row["nonce"])
                pass_e.insert(0, dec)
            except Exception:
                pass

        sb = StrengthBar(win)
        sb.pack(fill="x", padx=36, pady=(0, 4))
        pass_e.bind("<KeyRelease>", lambda _e: sb.update_strength(pass_e.get()))

        def _gen():
            pwd = SecurityEngine.generate_secure_password(16)
            pass_e.delete(0, "end")
            pass_e.insert(0, pwd)
            pass_e.configure(show="*")
            eye_btn.configure(image=eye_img)
            sb.update_strength(pwd)

        ctk.CTkButton(win, text="Generate Strong Password",
                      font=FONT_BODY_SM, fg_color="transparent",
                      border_width=1, border_color=GOLD, text_color=GOLD,
                      hover_color=CARD_HOVER, height=36, corner_radius=8,
                      command=_gen).pack(padx=36, pady=(0, 18), anchor="w")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=36, pady=(0, 28))

        def _save():
            site = site_e.get().strip()
            user = user_e.get().strip()
            pwd  = pass_e.get()
            ctx  = context_e.get().strip()
            cat  = cat_var.get()

            if not site or not pwd:
                Toast(win, "Service and Password are required.", "warn")
                return

            if len(site) > 200:
                Toast(win, "Website/Service name is too long (max 200 chars).", "warn")
                return
            if len(user) > 200:
                Toast(win, "Username is too long (max 200 chars).", "warn")
                return
            if len(pwd) > 500:
                Toast(win, "Password is too long (max 500 chars).", "warn")
                return
            if len(ctx) > 500:
                Toast(win, "Notes/Context is too long (max 500 chars).", "warn")
                return

            cipher_result = self.app.crypto.encrypt_data(pwd)
            cipher = cipher_result["ciphertext"]
            nonce  = cipher_result["nonce"]

            if is_edit:
                self.app.db.update_entry(row["id"], site, user, cipher, nonce, context=ctx, category=cat)
            else:
                self.app.db.add_entry(site, user, cipher, nonce, context=ctx, category=cat)

            self.refresh_list()
            win.destroy()
            Toast(self.app, "Entry saved to vault.", "success")

        ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent", border_width=1, border_color=BORDER, text_color=TEXT_2, width=120, hover_color=BORDER, height=44, corner_radius=8, command=win.destroy).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Save Entry", fg_color=TEAL, hover_color="#00B39F", text_color=TEXT_INV, width=160, height=44, corner_radius=8, font=("Helvetica", 14, "bold"), command=_save).pack(side="right")

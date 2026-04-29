import customtkinter as ctk
import threading
from security_engine import SecurityEngine
from ui.design import (
    FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_BODY_SM, FONT_LABEL,
    FONT_CAPTION, FONT_MONO, BG_BASE, TEXT_1, TEXT_2, TEXT_3,
    GOLD, GOLD_GLOW, TEXT_INV, TEAL, CARD, BORDER, CARD_HOVER,
    RED_DANGER, GREEN_OK, AMBER, BORDER_BRIGHT, AVATAR_COLORS, Toast
)

CATEGORIES = ["All", "Weak Passwords", "Reused Passwords", "Old Passwords (90+ days)"]

class AuditPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self._running = False
        self._results = {}          # cache of last audit results
        self._active_tab = "Weak Passwords"
        self._build_ui()

    # ─────────────────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent", height=68)
        header.grid(row=0, column=0, sticky="ew", padx=35, pady=(28, 0))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        title_blk = ctk.CTkFrame(header, fg_color="transparent")
        title_blk.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_blk, text="Security Audit",
                     font=("Georgia", 32, "bold"), text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(title_blk, text="Analyse your vault for weak, reused, and stale passwords",
                     font=("Helvetica", 15), text_color=TEXT_3).pack(anchor="w", pady=(4, 0))

        self.scan_btn = ctk.CTkButton(
            header, text="⟳  Run Audit", font=("Helvetica", 13, "bold"),
            fg_color=GOLD, hover_color=GOLD_GLOW, text_color=TEXT_INV,
            corner_radius=10, width=140, height=42,
            command=self._start_audit
        )
        self.scan_btn.grid(row=0, column=1, sticky="e")

        # ── Score row ────────────────────────────────────────
        self.score_row = ctk.CTkFrame(self, fg_color="transparent")
        self.score_row.grid(row=1, column=0, sticky="ew", padx=35, pady=(18, 0))
        self.score_row.grid_columnconfigure((0, 1, 2), weight=1)

        self._lbl_weak  = self._stat_card(self.score_row, 0, "Weak",       "—", RED_DANGER, "✗")
        self._lbl_reuse = self._stat_card(self.score_row, 1, "Reused",     "—", AMBER,      "⊙")
        self._lbl_old   = self._stat_card(self.score_row, 2, "Stale (90d)","—", TEXT_3,     "⌛")

        # ── Tab bar ──────────────────────────────────────────
        tab_row = ctk.CTkFrame(self, fg_color="transparent")
        tab_row.grid(row=2, column=0, sticky="nsew", padx=35, pady=(18, 0))
        tab_row.grid_rowconfigure(1, weight=1)
        tab_row.grid_columnconfigure(0, weight=1)

        tab_bar = ctk.CTkFrame(tab_row, fg_color="transparent")
        tab_bar.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self._tab_btns = {}
        tabs = [
            ("Weak Passwords",            RED_DANGER),
            ("Reused Passwords",          AMBER),
            ("Old Passwords (90+ days)",  TEXT_3),
        ]
        for label, accent in tabs:
            btn = ctk.CTkButton(
                tab_bar, text=label,
                font=("Helvetica", 13, "bold"),
                fg_color=CARD, hover_color=CARD_HOVER,
                text_color=TEXT_2, border_width=1, border_color=BORDER,
                corner_radius=8, height=36, width=190,
                command=lambda l=label: self._switch_tab(l)
            )
            btn.pack(side="left", padx=(0, 8))
            self._tab_btns[label] = (btn, accent)

        self._highlight_tab(self._active_tab)

        # ── Content scroll area ──────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            tab_row, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=BORDER_BRIGHT
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", pady=(0, 20))

        self._show_idle_placeholder()

    # ─────────────────────────────────────────────────────────
    # STAT CARDS
    # ─────────────────────────────────────────────────────────
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
        ctk.CTkLabel(icon_bg, text=icon, font=("Helvetica", 16, "bold"),
                     text_color=color).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=title, font=("Helvetica", 14, "bold"),
                     text_color=TEXT_2).place(x=76, y=22)
        lbl = ctk.CTkLabel(card, text=value, font=("Georgia", 28, "bold"), text_color=TEXT_1)
        lbl.place(x=76, y=50)
        return lbl

    # ─────────────────────────────────────────────────────────
    # TAB SWITCHING
    # ─────────────────────────────────────────────────────────
    def _switch_tab(self, label: str):
        self._active_tab = label
        self._highlight_tab(label)
        self._render_current_tab()

    def _highlight_tab(self, active: str):
        for label, (btn, accent) in self._tab_btns.items():
            if label == active:
                btn.configure(fg_color=accent, text_color=TEXT_INV, border_color=accent)
            else:
                btn.configure(fg_color=CARD, text_color=TEXT_2, border_color=BORDER)

    # ─────────────────────────────────────────────────────────
    # AUDIT LOGIC
    # ─────────────────────────────────────────────────────────
    def refresh_list(self):
        """Called by app.show_page — re-run audit automatically."""
        self._start_audit()

    def _start_audit(self):
        if self._running:
            return
        self._running = True
        self.scan_btn.configure(text="Scanning…", state="disabled")
        self._clear_scroll()
        self._show_scanning_placeholder()
        threading.Thread(target=self._run_audit_thread, daemon=True).start()

    def _run_audit_thread(self):
        try:
            entries = self.app.db.get_all_entries()
            weak   = SecurityEngine.find_weak_passwords(entries, self.app.crypto)
            dupes  = SecurityEngine.find_duplicate_passwords(entries, self.app.crypto)
            old    = SecurityEngine.find_old_passwords(entries, days=90)

            reuse_flat = []
            for group in dupes.values():
                reuse_flat.extend(group)

            self._results = {
                "Weak Passwords":           weak,
                "Reused Passwords":         (dupes, reuse_flat),
                "Old Passwords (90+ days)": old,
            }

            # Count unique sites in reuse (len of reuse_flat)
            self.app.after(0, self._on_audit_done,
                           len(weak), len(reuse_flat), len(old))
        except Exception as e:
            print(f"[ERROR] Audit failed: {e}")
            self._running = False
            self.app.after(0, lambda: self.scan_btn.configure(text="⟳  Run Audit", state="normal"))

    def _on_audit_done(self, n_weak, n_reuse, n_old):
        self._running = False
        self.scan_btn.configure(text="⟳  Run Audit", state="normal")
        self._lbl_weak.configure(text=str(n_weak))
        self._lbl_reuse.configure(text=str(n_reuse))
        self._lbl_old.configure(text=str(n_old))
        self._render_current_tab()

    # ─────────────────────────────────────────────────────────
    # RENDERING
    # ─────────────────────────────────────────────────────────
    def _render_current_tab(self):
        self._clear_scroll()
        if not self._results:
            self._show_idle_placeholder()
            return

        tab = self._active_tab
        data = self._results.get(tab)

        if tab == "Weak Passwords":
            self._render_simple_list(data, RED_DANGER, "Weak", "These passwords scored low on strength. Update them now.")
        elif tab == "Reused Passwords":
            dupes_dict, _ = data
            self._render_reuse_groups(dupes_dict)
        elif tab == "Old Passwords (90+ days)":
            self._render_simple_list(data, AMBER, "Stale", "These passwords haven't been changed in over 90 days.")

    def _clear_scroll(self):
        for w in self.scroll.winfo_children():
            w.destroy()

    def _show_idle_placeholder(self):
        self._clear_scroll()
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.pack(pady=80, expand=True)
        ctk.CTkLabel(wrap, text="🔍", font=("Helvetica", 48)).pack(pady=(0, 12))
        ctk.CTkLabel(wrap, text="No audit run yet",
                     font=("Georgia", 22, "bold"), text_color=TEXT_2).pack()
        ctk.CTkLabel(wrap, text="Press  ⟳ Run Audit  to scan your vault",
                     font=("Helvetica", 14), text_color=TEXT_3).pack(pady=(8, 0))

    def _show_scanning_placeholder(self):
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.pack(pady=80, expand=True)
        ctk.CTkLabel(wrap, text="⚙",
                     font=("Helvetica", 48), text_color=GOLD).pack(pady=(0, 12))
        ctk.CTkLabel(wrap, text="Analysing your vault…",
                     font=("Georgia", 22, "bold"), text_color=TEXT_2).pack()
        ctk.CTkLabel(wrap, text="Decrypting and evaluating all entries",
                     font=("Helvetica", 14), text_color=TEXT_3).pack(pady=(8, 0))

    def _empty_tab_msg(self, icon, title, sub):
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.pack(pady=60, expand=True)
        ctk.CTkLabel(wrap, text=icon,
                     font=("Helvetica", 48), text_color=GREEN_OK).pack(pady=(0, 12))
        ctk.CTkLabel(wrap, text=title,
                     font=("Georgia", 22, "bold"), text_color=GREEN_OK).pack()
        ctk.CTkLabel(wrap, text=sub,
                     font=("Helvetica", 14), text_color=TEXT_3).pack(pady=(8, 0))

    # ── Simple list (weak / old) ──────────────────────────────
    def _render_simple_list(self, entries, accent, badge_text, subtitle):
        if not entries:
            self._empty_tab_msg("✓", "All Clear!", "No issues found in this category.")
            return

        ctk.CTkLabel(self.scroll, text=subtitle,
                     font=FONT_BODY_SM, text_color=TEXT_3).pack(anchor="w", padx=8, pady=(4, 10))

        for i, row in enumerate(entries):
            self._entry_card(row, i, accent, badge_text)

    # ── Reuse groups ──────────────────────────────────────────
    def _render_reuse_groups(self, dupes_dict: dict):
        if not dupes_dict:
            self._empty_tab_msg("✓", "No Reused Passwords!", "Every account uses a unique password.")
            return

        ctk.CTkLabel(
            self.scroll,
            text="Entries sharing the same password are grouped below. Reusing passwords is a critical risk.",
            font=FONT_BODY_SM, text_color=TEXT_3, wraplength=820, justify="left"
        ).pack(anchor="w", padx=8, pady=(4, 10))

        global_idx = 0
        for group_id, (key, group) in enumerate(dupes_dict.items()):
            # Group header
            group_hdr = ctk.CTkFrame(self.scroll, fg_color=CARD_HOVER, corner_radius=10,
                                     border_width=1, border_color=AMBER)
            group_hdr.pack(fill="x", padx=8, pady=(8, 2))

            ctk.CTkLabel(group_hdr,
                         text=f"  ⚠  Group {group_id + 1} — {len(group)} accounts share this password",
                         font=("Helvetica", 13, "bold"), text_color=AMBER).pack(
                             anchor="w", padx=12, pady=8)

            for row in group:
                self._entry_card(row, global_idx, AMBER, "Reused", indent=True)
                global_idx += 1

    # ── Single entry card ─────────────────────────────────────
    def _entry_card(self, row, idx: int, accent, badge: str, indent: bool = False):
        color = AVATAR_COLORS[idx % len(AVATAR_COLORS)]
        website = row.get("website") or ""
        username = row.get("username") or ""
        initial = website[0].upper() if website else "?"

        lpad = 28 if indent else 8

        card = ctk.CTkFrame(self.scroll, fg_color=CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=4, padx=(lpad, 8), ipady=8)

        # Avatar
        av = ctk.CTkFrame(card, fg_color=color, width=42, height=42, corner_radius=21)
        av.pack(side="left", padx=16, pady=8)
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=initial, font=("Georgia", 18, "bold"),
                     text_color=TEXT_INV).pack(expand=True)

        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(0, 12))
        ctk.CTkLabel(info, text=website, font=FONT_H3, text_color=TEXT_1).pack(anchor="w")
        ctk.CTkLabel(info, text=username, font=FONT_BODY, text_color=TEXT_2).pack(anchor="w")

        # Date info for old passwords
        try:
            created = row.get("updated_at") or row.get("created_at")
        except Exception:
            created = row.get("created_at")
        if created:
            try:
                from datetime import datetime, timezone
                ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                delta = datetime.now(timezone.utc) - ts
                age_str = f"{delta.days} days ago"
                ctk.CTkLabel(info, text=f"Last changed: {age_str}",
                             font=FONT_CAPTION, text_color=TEXT_3).pack(anchor="w")
            except Exception:
                pass

        # Badge
        badge_frame = ctk.CTkFrame(card, fg_color=accent, corner_radius=6, height=26)
        badge_frame.pack(side="right", padx=(0, 16), pady=8)
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(badge_frame, text=f"  {badge}  ",
                     font=("Helvetica", 11, "bold"), text_color=TEXT_INV).pack(
                         side="left", padx=4, pady=4)

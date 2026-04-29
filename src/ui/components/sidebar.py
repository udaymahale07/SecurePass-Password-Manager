import customtkinter as ctk
import os
from PIL import Image
from ui.design import PANEL, GOLD, TEXT_1, BORDER, TEXT_2, TEXT_3, GREEN_OK, RED_DANGER, CARD_HOVER, FONT_CAPTION

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, corner_radius=0, fg_color=PANEL, width=255, **kwargs)
        self.app = app
        self.sidebar_btns = {}  # key -> (row_frame, indicator, icon_lbl, text_lbl)
        self.grid_propagate(False)
        self._build_ui()

    def _build_ui(self):
        # ── Brand ────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", pady=(28, 10))
        brand_inner = ctk.CTkFrame(brand, fg_color="transparent")
        brand_inner.pack(anchor="center")

        # Logo thumbnail — wrapped in dark pill so it looks right in both themes
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "logo.png")
        logo_path = os.path.normpath(logo_path)
        if os.path.exists(logo_path):
            pil_img = Image.open(logo_path).resize((34, 34), Image.LANCZOS)
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(34, 34))
            logo_pill = ctk.CTkFrame(brand_inner, width=40, height=40,
                                     corner_radius=10, fg_color="#12151F")
            logo_pill.pack(side="left", padx=(0, 10))
            logo_pill.pack_propagate(False)
            ctk.CTkLabel(logo_pill, image=logo_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkFrame(brand_inner, width=18, height=18,
                         corner_radius=9, fg_color=GOLD).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(brand_inner, text="SecurePass",
                     font=("Georgia", 22, "bold"), text_color=TEXT_1).pack(side="left")

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(8, 16))
        ctk.CTkLabel(self, text="NAVIGATION",
                     font=("Helvetica", 11, "bold"), text_color=TEXT_3).pack(anchor="w", padx=22, pady=(0, 8))

        # ── Nav items ─────────────────────────────────────────
        # (page_key, icon_char, label)
        # Icons chosen from Miscellaneous Symbols block — reliable on all Linux distros
        items = [
            ("Vault",        "\u2756",  "Vault"),        # ❖  diamond bullet
            ("Generator",    "\u2732",  "Generator"),    # ✲  open centre asterisk
            ("Breach Check", "\u26a1",  "Breach Check"), # ⚡  high voltage / scan
            ("Audit",        "\u2724",  "Security Audit"),# ✤  shield-like
            ("Settings",     "\u2699",  "Settings"),     # ⚙  gear
        ]

        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(fill="x", padx=8)

        for key, icon, label in items:
            self._build_nav_item(key, icon, label)

        # ── Spacer + footer ───────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(0, 12))

        sess = ctk.CTkFrame(self, fg_color="transparent")
        sess.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkFrame(sess, width=8, height=8,
                     corner_radius=4, fg_color=GREEN_OK).pack(side="left", padx=(4, 8))
        ctk.CTkLabel(sess, text="Session Active",
                     font=FONT_CAPTION, text_color=TEXT_3).pack(side="left")

        ctk.CTkButton(self,
                      text="⚿   Lock Vault",        # ⚿  lock icon
                      font=("Helvetica", 14, "bold"),
                      fg_color="transparent",
                      hover_color="#2A1515",
                      text_color=RED_DANGER,
                      border_width=1, border_color=RED_DANGER,
                      height=46, corner_radius=8,
                      command=self.app.lock_vault      # ← properly locks vault
                      ).pack(padx=14, pady=(0, 24), fill="x")

    def _build_nav_item(self, key: str, icon: str, label: str):
        """Build one sidebar nav item: indicator strip | big icon | text label."""
        row = ctk.CTkFrame(self.menu_frame, fg_color="transparent", corner_radius=10, height=56)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)

        # Gold left-edge active indicator
        indicator = ctk.CTkFrame(row, width=4, corner_radius=2, fg_color="transparent")
        indicator.pack(side="left", fill="y", padx=(2, 0), pady=10)

        # ── Icon label — large, independent font ──────────────
        icon_lbl = ctk.CTkLabel(
            row,
            text=icon,
            font=("DejaVu Sans", 24),   # 24pt gives a bold, clear glyph
            width=46,
            text_color=TEXT_2,
        )
        icon_lbl.pack(side="left", pady=4)

        # ── Page name label ───────────────────────────────────
        text_lbl = ctk.CTkLabel(
            row,
            text=label,
            font=("Helvetica", 15, "bold"),
            text_color=TEXT_2,
            anchor="w",
        )
        text_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # ── Hover + click wiring ──────────────────────────────
        def _navigate(e=None, k=key):
            self.app.show_page(k)

        def _on_enter(e=None, r=row):
            # Only change bg if not already the active page
            r.configure(fg_color=CARD_HOVER)

        def _on_leave(e=None, r=row, k=key):
            entry = self.sidebar_btns.get(k)
            if entry and entry[1].cget("fg_color") == GOLD:
                pass  # keep active highlight
            else:
                r.configure(fg_color="transparent")

        for widget in (row, indicator, icon_lbl, text_lbl):
            widget.bind("<Button-1>", _navigate)
            widget.bind("<Enter>",    _on_enter)
            widget.bind("<Leave>",    _on_leave)

        row.configure(cursor="hand2")
        self.sidebar_btns[key] = (row, indicator, icon_lbl, text_lbl)

    def highlight_active(self, page_name: str):
        for name, (row, indicator, icon_lbl, text_lbl) in self.sidebar_btns.items():
            if name == page_name:
                row.configure(fg_color=CARD_HOVER)
                indicator.configure(fg_color=GOLD)
                icon_lbl.configure(text_color=GOLD)
                text_lbl.configure(text_color=TEXT_1)
            else:
                row.configure(fg_color="transparent")
                indicator.configure(fg_color="transparent")
                icon_lbl.configure(text_color=TEXT_2)
                text_lbl.configure(text_color=TEXT_2)

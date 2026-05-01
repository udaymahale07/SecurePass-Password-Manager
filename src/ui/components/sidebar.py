import customtkinter as ctk
import os
from PIL import Image
from ui.design import PANEL, GOLD, TEXT_1, BORDER, TEXT_2, TEXT_3, GREEN_OK, RED_DANGER, CARD_HOVER, FONT_CAPTION

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, corner_radius=0, fg_color=PANEL, width=255, **kwargs)
        self.app = app
        self.sidebar_btns = {}  # key -> (row_frame, indicator, icon_lbl, text_lbl, img_normal, img_hover)
        self.grid_propagate(False)
        self._build_ui()

    def _load_icon(self, filename, color_hex="#FFFFFF"):
        base_dir = os.path.dirname(__file__)
        path = os.path.normpath(os.path.join(base_dir, "..", "..", "..", "assets", filename))
        if os.path.exists(path):
            pil_img = Image.open(path).convert("RGBA")
            data = pil_img.getdata()
            new_data = []
            h = color_hex.lstrip('#') if isinstance(color_hex, str) else "FFFFFF"
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

    def _build_ui(self):
        # ── Brand ────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", pady=(28, 10))
        brand_inner = ctk.CTkFrame(brand, fg_color="transparent")
        brand_inner.pack(anchor="center")

        # Logo thumbnail
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "logo.png")
        logo_path = os.path.normpath(logo_path)
        if os.path.exists(logo_path):
            pil_img = Image.open(logo_path).resize((34, 34), Image.LANCZOS)
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(34, 34))
            ctk.CTkLabel(brand_inner, image=logo_img, text="").pack(side="left", padx=(0, 10))

        ctk.CTkLabel(brand_inner, text="SecurePass",
                     font=("Georgia", 22, "bold"), text_color=TEXT_1).pack(side="left")

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(8, 16))
        ctk.CTkLabel(self, text="NAVIGATION",
                     font=("Helvetica", 11, "bold"), text_color=TEXT_3).pack(anchor="w", padx=22, pady=(0, 8))

        # ── Nav items ─────────────────────────────────────────
        # (page_key, icon_filename, label)
        items = [
            ("Vault",        "vault.png",          "Vault"),
            ("Generator",    "key-round.png",      "Generator"),
            ("Breach Check", "shield-alert.png",   "Breach Check"),
            ("Audit",        "security_audit.png", "Security Audit"),
            ("Settings",     "settings(1).png",    "Settings"),
        ]

        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(fill="x", padx=8)

        for key, icon, label in items:
            self._build_nav_item(key, icon, label)

        # ── Spacer + footer ───────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(0, 18))

        lock_img = self._load_icon("total password and lock.png", RED_DANGER)
        ctk.CTkButton(self,
                      text=" Lock Vault",
                      image=lock_img,
                      font=("Helvetica", 14, "bold"),
                      fg_color="transparent",
                      hover_color="#2A1515",
                      text_color=RED_DANGER,
                      border_width=1, border_color=RED_DANGER,
                      height=46, corner_radius=8,
                      command=self.app.lock_vault
                      ).pack(padx=14, pady=(0, 24), fill="x")

    def _build_nav_item(self, key: str, icon_filename: str, label: str):
        row = ctk.CTkFrame(self.menu_frame, fg_color="transparent", corner_radius=10, height=50)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)

        indicator = ctk.CTkFrame(row, width=4, corner_radius=2, fg_color="transparent")
        indicator.pack(side="left", fill="y", padx=(2, 0), pady=10)

        img_normal = self._load_icon(icon_filename, TEXT_2[1] if isinstance(TEXT_2, tuple) else TEXT_2)
        img_hover  = self._load_icon(icon_filename, GOLD)

        icon_lbl = ctk.CTkLabel(row, text="", image=img_normal, width=46)
        icon_lbl.pack(side="left", pady=4)

        text_lbl = ctk.CTkLabel(
            row, text=label, font=("Helvetica", 15, "bold"),
            text_color=TEXT_2, anchor="w",
        )
        text_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def _navigate(e=None, k=key):
            self.app.show_page(k)

        def _on_enter(e=None, r=row, lbl=icon_lbl, img=img_hover, txt=text_lbl, k=key):
            r.configure(fg_color=CARD_HOVER)
            lbl.configure(image=img)
            txt.configure(text_color=GOLD)

        def _on_leave(e=None, r=row, lbl=icon_lbl, img_n=img_normal, txt=text_lbl, k=key):
            entry = self.sidebar_btns.get(k)
            if entry and entry[1].cget("fg_color") == GOLD:
                pass  # keep active highlight
            else:
                r.configure(fg_color="transparent")
                lbl.configure(image=img_n)
                txt.configure(text_color=TEXT_2)

        for widget in (row, indicator, icon_lbl, text_lbl):
            widget.bind("<Button-1>", _navigate)
            widget.bind("<Enter>",    _on_enter)
            widget.bind("<Leave>",    _on_leave)

        row.configure(cursor="hand2")
        self.sidebar_btns[key] = (row, indicator, icon_lbl, text_lbl, img_normal, img_hover)

    def highlight_active(self, page_name: str):
        for name, (row, indicator, icon_lbl, text_lbl, img_normal, img_hover) in self.sidebar_btns.items():
            if name == page_name:
                row.configure(fg_color=CARD_HOVER)
                indicator.configure(fg_color=GOLD)
                icon_lbl.configure(image=img_hover)
                text_lbl.configure(text_color=TEXT_1)
            else:
                row.configure(fg_color="transparent")
                indicator.configure(fg_color="transparent")
                icon_lbl.configure(image=img_normal)
                text_lbl.configure(text_color=TEXT_2)

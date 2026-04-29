import customtkinter as ctk

# ═══════════════════════════════════════════════════════════
#   DESIGN TOKENS  —  "Obsidian Vault"
# ═══════════════════════════════════════════════════════════
BG_DEEP        = ("#E5E7EB", "#07080D")
BG_BASE        = ("#F3F4F6", "#0D0F18")
PANEL          = ("#FFFFFF", "#12151F")
CARD           = ("#FFFFFF", "#181C28")
CARD_HOVER     = ("#E5E7EB", "#1E2235")
BORDER         = ("#D1D5DB", "#252A3D")
BORDER_BRIGHT  = ("#9CA3AF", "#353C58")

GOLD           = "#C9A84C"
GOLD_DIM       = "#8C6F30"
GOLD_GLOW      = ("#AA862E", "#E8C66A")
TEAL           = "#00C9B1"
RED_DANGER     = "#E05252"
GREEN_OK       = "#3DD68C"
AMBER          = "#F5A623"

TEXT_1         = ("#111827", "#F0F2FF")
TEXT_2         = ("#4B5563", "#8A92B2")
TEXT_3         = ("#6B7280", "#4A5270")
TEXT_INV       = ("#FFFFFF", "#07080D")

FONT_BRAND     = ("Georgia", 24, "bold")
FONT_H1        = ("Georgia", 32, "bold")
FONT_H2        = ("Georgia", 24, "bold")
FONT_H3        = ("Georgia", 18, "bold")
FONT_BODY      = ("Helvetica", 15)
FONT_BODY_SM   = ("Helvetica", 14)
FONT_MONO      = ("Courier New", 16, "bold")
FONT_LABEL     = ("Helvetica", 13, "bold")
FONT_CAPTION   = ("Helvetica", 12)

AVATAR_COLORS  = [GOLD, TEAL, "#7B68EE", "#FF6B8A", "#44D7B6", AMBER]

ctk.set_appearance_mode("Dark")

class Toast:
    _COLORS = {"info": TEAL, "success": GREEN_OK, "error": RED_DANGER, "warn": AMBER}
    _ICONS  = {"info": "\u2139", "success": "\u2713", "error": "\u2715", "warn": "\u26a0"}

    def __init__(self, root, message: str, kind: str = "info", duration: int = 2800):
        color = self._COLORS.get(kind, TEAL)
        icon  = self._ICONS.get(kind, "i")

        self.win = ctk.CTkToplevel(root)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(fg_color=CARD)

        rx = root.winfo_x() + root.winfo_width() - 360
        ry = root.winfo_y() + root.winfo_height() - 90
        self.win.geometry(f"330x62+{max(rx, 0)}+{max(ry, 0)}")

        ctk.CTkFrame(self.win, fg_color=color, width=4, corner_radius=0).pack(side="left", fill="y")

        inner = ctk.CTkFrame(self.win, fg_color=CARD, corner_radius=0)
        inner.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(inner, text=icon, font=("Helvetica", 17, "bold"),
                     text_color=color).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(inner, text=message, font=FONT_BODY_SM,
                     text_color=TEXT_1, wraplength=240,
                     justify="left").pack(side="left", fill="x", expand=True)

        self.win.deiconify()
        root.after(duration, self._dismiss)

    def _dismiss(self):
        try:
            self.win.destroy()
        except Exception:
            pass

import customtkinter as ctk
from security_engine import SecurityEngine
from ui.design import GOLD, BORDER, TEXT_3, FONT_CAPTION

class StrengthBar(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        bg = ctk.CTkFrame(self, fg_color=BORDER, height=5, corner_radius=3)
        bg.pack(fill="x")
        self._fill = ctk.CTkFrame(bg, fg_color=GOLD, height=5, corner_radius=3)
        self._fill.place(x=0, y=0, relheight=1, relwidth=0)
        self._lbl = ctk.CTkLabel(self, text="", font=FONT_CAPTION, text_color=TEXT_3)
        self._lbl.pack(anchor="e", pady=(2, 0))

    def update_strength(self, password: str):
        result = SecurityEngine.evaluate_password_strength(password)
        self._fill.place_configure(relwidth=result["percentage"])
        self._fill.configure(fg_color=result["color"])
        self._lbl.configure(text=result["level"], text_color=result["color"])

import customtkinter as ctk
from security_engine import SecurityEngine
from ui.design import FONT_H1, FONT_MONO, FONT_BODY, BG_BASE, TEXT_1, TEXT_2, GOLD, GOLD_GLOW, TEXT_INV, TEAL, CARD, BORDER, Toast
from ui.components.common import StrengthBar

class GeneratorPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER, width=560, height=480)
        card.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card, text="Password Generator", font=FONT_H1, text_color=TEXT_1).pack(pady=(32, 0))

        self.gen_display = ctk.CTkTextbox(card, font=FONT_MONO, height=80,
                                          fg_color=BG_BASE, text_color=TEXT_1, wrap="none")
        self.gen_display.pack(pady=20, padx=40, fill="x")

        len_frame = ctk.CTkFrame(card, fg_color="transparent")
        len_frame.pack(pady=10, padx=40, fill="x")
        ctk.CTkLabel(len_frame, text="Length", font=FONT_BODY, text_color=TEXT_2).pack(side="left")
        self.gen_length = ctk.IntVar(value=16)
        slider = ctk.CTkSlider(len_frame, from_=12, to=32, variable=self.gen_length,
                               command=lambda _: self._update_length_label())
        slider.pack(side="left", fill="x", expand=True, padx=12)
        self.length_lbl = ctk.CTkLabel(len_frame, text="16", font=FONT_BODY, text_color=TEXT_1)
        self.length_lbl.pack(side="right")

        self.gen_strength = StrengthBar(card)
        self.gen_strength.pack(pady=10, padx=40, fill="x")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=20, padx=40, fill="x")
        ctk.CTkButton(btn_frame, text="Generate", font=("Helvetica", 14, "bold"),
                      fg_color=GOLD, hover_color=GOLD_GLOW, text_color=TEXT_INV,
                      height=46, command=self._generate_password).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_frame, text="Copy to Clipboard", font=("Helvetica", 14, "bold"),
                      fg_color=TEAL, hover_color="#00B39F", text_color=TEXT_INV,
                      height=46, command=self._copy_gen_password).pack(side="left", fill="x", expand=True)

    def _update_length_label(self):
        self.length_lbl.configure(text=str(self.gen_length.get()))

    def _generate_password(self):
        pwd = SecurityEngine.generate_secure_password(self.gen_length.get())
        self.gen_display.delete("1.0", "end")
        self.gen_display.insert("1.0", pwd)
        self.gen_strength.update_strength(pwd)

    def _copy_gen_password(self):
        pwd = self.gen_display.get("1.0", "end").strip()
        if pwd:
            self.app.clipboard_clear()
            self.app.clipboard_append(pwd)
            self.app.update()
            self.app._copied_pwd = pwd  # Register with clipboard shredder daemon
            Toast(self.app, "Password copied! Clipboard clears in 15s.", "success")

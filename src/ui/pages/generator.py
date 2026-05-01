import customtkinter as ctk
from security_engine import SecurityEngine
from ui.design import FONT_H1, FONT_H2, FONT_H3, FONT_MONO, FONT_BODY, BG_BASE, TEXT_1, TEXT_2, GOLD, GOLD_GLOW, TEXT_INV, TEAL, CARD, BORDER, CARD_HOVER, BORDER_BRIGHT, Toast
from ui.components.common import StrengthBar

class GeneratorPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.nums_var = ctk.BooleanVar(value=True)
        self.syms_var = ctk.BooleanVar(value=True)
        self.gen_length = ctk.IntVar(value=16)
        
        self._build_ui()
        self._generate_password()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER, width=640, height=620)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_propagate(False)
        card.pack_propagate(False)

        # Header
        ctk.CTkLabel(card, text="Password Generator", font=FONT_H1, text_color=TEXT_1).pack(pady=(36, 8))
        ctk.CTkLabel(card, text="Create strong, unique passwords for your accounts", font=FONT_BODY, text_color=TEXT_2).pack(pady=(0, 24))

        # ── Display Area ──
        display_frame = ctk.CTkFrame(card, fg_color=BG_BASE, corner_radius=12, border_width=1, border_color=BORDER_BRIGHT)
        display_frame.pack(padx=40, fill="x")
        
        self.gen_display = ctk.CTkLabel(display_frame, text="", font=("Courier New", 28, "bold"), text_color=GOLD, anchor="center")
        self.gen_display.pack(side="left", fill="x", expand=True, pady=24, padx=20)
        
        # Inline Regenerate Button
        reg_btn = ctk.CTkButton(display_frame, text="↻", width=44, height=44, fg_color="transparent", 
                                hover_color=BORDER, text_color=TEXT_2, font=("Helvetica", 24),
                                command=self._generate_password)
        reg_btn.pack(side="right", padx=12, pady=12)

        # ── Strength Bar ──
        self.gen_strength = StrengthBar(card)
        self.gen_strength.pack(pady=(24, 24), padx=40, fill="x")

        # ── Length Slider ──
        len_frame = ctk.CTkFrame(card, fg_color="transparent")
        len_frame.pack(pady=10, padx=40, fill="x")
        
        lbl_frame = ctk.CTkFrame(len_frame, fg_color="transparent")
        lbl_frame.pack(fill="x")
        ctk.CTkLabel(lbl_frame, text="Password Length", font=FONT_H3, text_color=TEXT_1).pack(side="left")
        self.length_lbl = ctk.CTkLabel(lbl_frame, text="16", font=FONT_H3, text_color=GOLD)
        self.length_lbl.pack(side="right")
        
        slider = ctk.CTkSlider(len_frame, from_=8, to=64, variable=self.gen_length,
                               button_color=GOLD, progress_color=GOLD,
                               command=lambda _: self._update_length_label())
        slider.pack(fill="x", pady=10)

        # ── Options Checkboxes ──
        opts_frame = ctk.CTkFrame(card, fg_color="transparent")
        opts_frame.pack(pady=16, padx=40, fill="x")
        
        def _cb(text, var):
            cb = ctk.CTkCheckBox(opts_frame, text=text, variable=var, 
                                 font=FONT_BODY, text_color=TEXT_2, 
                                 fg_color=GOLD, hover_color=GOLD_GLOW,
                                 command=self._generate_password)
            return cb

        col1 = ctk.CTkFrame(opts_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True)
        col2 = ctk.CTkFrame(opts_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True)

        _cb("Uppercase (A-Z)", self.upper_var).pack(in_=col1, anchor="w", pady=8)
        _cb("Lowercase (a-z)", self.lower_var).pack(in_=col1, anchor="w", pady=8)
        
        _cb("Numbers (0-9)", self.nums_var).pack(in_=col2, anchor="w", pady=8)
        _cb("Symbols (!@#)", self.syms_var).pack(in_=col2, anchor="w", pady=8)

        # ── Copy Button ──
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(20, 0), padx=40, fill="x")
        
        ctk.CTkButton(btn_frame, text="Copy to Clipboard", font=("Helvetica", 14, "bold"),
                      fg_color=TEAL, hover_color="#00B39F", text_color=TEXT_INV,
                      height=48, corner_radius=8, command=self._copy_gen_password).pack(fill="x")

    def _update_length_label(self):
        self.length_lbl.configure(text=str(self.gen_length.get()))
        self._generate_password()

    def _generate_password(self):
        if not (self.upper_var.get() or self.lower_var.get() or self.nums_var.get() or self.syms_var.get()):
            self.lower_var.set(True)
            
        pwd = SecurityEngine.generate_secure_password(
            length=self.gen_length.get(),
            upper=self.upper_var.get(),
            lower=self.lower_var.get(),
            nums=self.nums_var.get(),
            syms=self.syms_var.get()
        )
        self.gen_display.configure(text=pwd)
        self.gen_strength.update_strength(pwd)

    def _copy_gen_password(self):
        pwd = self.gen_display.cget("text").strip()
        if pwd:
            self.app.clipboard_clear()
            self.app.clipboard_append(pwd)
            self.app.update()
            self.app._copied_pwd = pwd
            Toast(self.app, "Password copied! Clipboard clears in 15s.", "success")

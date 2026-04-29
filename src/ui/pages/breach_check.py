import customtkinter as ctk
import threading
from security_engine import SecurityEngine
from ui.design import FONT_H1, FONT_BODY, FONT_LABEL, BG_BASE, TEXT_1, TEXT_2, TEXT_3, AMBER, GREEN_OK, RED_DANGER, CARD, BORDER, GOLD, GOLD_GLOW, TEXT_INV, TEAL, Toast

class BreachCheckPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self._checking = False  # In-flight guard to prevent spam
        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER, width=560, height=300)
        card.place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(card, text="Breach Intelligence", font=FONT_H1, text_color=TEXT_1).pack(pady=(32, 12))
        ctk.CTkLabel(card, text="Check if a password has been exposed in known data breaches.\nUses k-Anonymity so the full password is never sent over the network.",
                     font=FONT_BODY, text_color=TEXT_3, justify="center").pack(pady=4)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=28, padx=40, fill="x")

        self.breach_entry = ctk.CTkEntry(row, width=320, height=46, font=("Helvetica", 16),
                                         fg_color=BG_BASE, border_width=1, border_color=BORDER,
                                         placeholder_text="Enter password to check...", show="•")
        self.breach_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(row, text="Scan", font=("Helvetica", 14, "bold"), width=120, height=46,
                      fg_color=TEAL, hover_color="#00B39F", text_color=TEXT_INV,
                      command=self._run_breach_check).pack(side="left")

        self.breach_result_lbl = ctk.CTkLabel(card, text="", font=FONT_LABEL)
        self.breach_result_lbl.pack(pady=(0, 20))

    def _run_breach_check(self):
        if self._checking:
            Toast(self.app, "Scan already in progress...", "warn")
            return
        pwd = self.breach_entry.get().strip()
        if not pwd:
            Toast(self.app, "Enter a password to check.", "warn")
            return
        self._checking = True
        self.breach_result_lbl.configure(text="Checking against breach database...", text_color=TEXT_2)
        self.app.update()

        # Threading for async operation
        def task():
            count = SecurityEngine.check_pwned_password(pwd, db=self.app.db)
            self.app.after(0, self._render_result, count)
            self._checking = False
        
        threading.Thread(target=task, daemon=True).start()

    def _render_result(self, count):
        if count == -1:
            self.breach_result_lbl.configure(text="Could not reach the breach database. Check your internet connection.", text_color=AMBER)
        elif count == 0:
            self.breach_result_lbl.configure(text="Not found in any known data breach. Keep it safe!", text_color=GREEN_OK)
        else:
            self.breach_result_lbl.configure(text=f"Found {count:,} times in known breaches! Change this password immediately.", text_color=RED_DANGER)

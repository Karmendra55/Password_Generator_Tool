"""
Password generator page UI.

Generates secure passwords with configurable options,
shows strength metrics, and saves to history.
"""

import tkinter as tk

from assets.theme import *
from assets.widgets import *
from assets.widgets import _entry
from tkinter import messagebox
from src import crypto, generator, utils

# --------------
# Generator Page
# --------------

class GeneratorPage(tk.Frame):
    """Password generator UI with strength meter and history actions."""
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack_propagate(False)

        self.app = app
        self._username = app._username
        self._master_pw = app._master_pw

        self._build()
    
    def refresh(self):
        self._pw_var.set("")
        self._strength_lbl.config(text="")
        self._entropy_lbl.config(text="")
        self._bar.delete("all")

    # --- UI build ---

    def _build(self):

        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=PAD_X, pady=(PAD_Y_LARGE, 0))
        tk.Label(hdr, text="Password Generator", font=FONT_HEAD, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hdr, text="Cryptographically secure — powered by Python secrets.",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        Divider(self).pack(fill="x", padx=PAD_X, pady=PAD_Y_SMALL)

        # --- Options card ---
        card = Card(self)
        card.pack(fill="x", padx=PAD_X, pady=PAD_Y_SMALL)

        self._len_var = tk.IntVar(value=16)
        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill="x")
        tk.Label(row, text="Length", font=FONT_LABEL, bg=SURFACE, fg=TEXT_DIM,
                 anchor="w").pack(side="left")
        self._len_label = tk.Label(row, text="16", font=FONT_LABEL, bg=SURFACE, fg=ACCENT)
        self._len_label.pack(side="right")
        tk.Scale(card, from_=4, to=64, orient="horizontal",
                 variable=self._len_var, bg=SURFACE, fg=TEXT,
                 troughcolor=SURFACE2, highlightthickness=0,
                 activebackground=ACCENT, showvalue=False,
                 command=lambda v: self._len_label.configure(text=v)
                 ).pack(fill="x", pady=(2, 10))

        # --- Options to select from ---
        self._use_upper   = self._checkbox(card, "Uppercase  A–Z", True)
        self._use_digits  = self._checkbox(card, "Digits  0–9",    True)
        self._use_special = self._checkbox(card, "Symbols  !@#$…", True)

        HoverButton(self, text="⚡  Generate Password",
                    command=self._do_generate).pack(fill="x", padx=28, pady=12)

        # --- Output card ---
        out = Card(self)
        out.pack(fill="x", padx=28)

        self._pw_var = tk.StringVar()
        _entry(out, var=self._pw_var, state="readonly",
               readonlybackground=SURFACE2).pack(fill="x", pady=(0, 8))

        self._strength_lbl = tk.Label(out, text="", font=FONT_SMALL, bg=SURFACE, fg=TEXT_DIM)
        self._strength_lbl.pack(anchor="w")

        self._bar = tk.Canvas(out, height=5, bg=SURFACE2, highlightthickness=0)
        self._bar.pack(fill="x", pady=(3, 8))

        self._entropy_lbl = tk.Label(out, text="", font=FONT_SMALL, bg=SURFACE, fg=TEXT_DIM)
        self._entropy_lbl.pack(anchor="w")

        act = tk.Frame(out, bg=SURFACE)
        act.pack(fill="x", pady=(10, 0))
        HoverButton(act, text="📋  Copy", command=self._copy_pw,
                    bg=SURFACE2, hover_bg=BORDER).pack(side="left", padx=(0, 8))
        HoverButton(act, text="💾  Save to History", command=self._save_to_history,
                    bg=SURFACE2, hover_bg=BORDER).pack(side="left")

        return self

    # --- Helper Function ---

    @staticmethod
    def _checkbox(parent, label, default) -> tk.BooleanVar:
        var = tk.BooleanVar(value=default)
        tk.Checkbutton(parent, text=label, variable=var, font=FONT_BODY,
                       bg=SURFACE, fg=TEXT, activebackground=SURFACE,
                       activeforeground=TEXT, selectcolor=ACCENT,
                       cursor="hand2", highlightthickness=0).pack(anchor="w", pady=2)
        return var

    # --- Actions ---

    def _do_generate(self):
        try:
            pw = generator.generate_password(
                self._len_var.get(),
                self._use_upper.get(),
                self._use_digits.get(),
                self._use_special.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Error", str(exc)); return
        self._pw_var.set(pw)
        self._update_strength(pw)

    def _update_strength(self, pw: str):
        ent = generator.calculate_entropy(pw)
        lbl, col = generator.strength_label(ent)
        self._strength_lbl.configure(text=f"Strength: {lbl}", fg=col)
        self._entropy_lbl.configure(text=f"Entropy: {ent} bits  ·  Length: {len(pw)}", fg=TEXT_DIM)
        self._bar.update_idletasks()
        total = self._bar.winfo_width() or 500
        fill  = min(int(ent / 120 * total), total)
        self._bar.delete("all")
        self._bar.create_rectangle(0, 0, total, 5, fill=SURFACE2, outline="")
        if fill > 0:
            self._bar.create_rectangle(0, 0, fill, 5, fill=col, outline="")

    def _copy_pw(self):
        pw = self._pw_var.get()
        if not pw:
            self.app.toast("Generate a password first", RED)
            return
        utils.copy_to_clipboard(pw)
        self.app.toast("Password copied to clipboard")

    def _save_to_history(self):
        pw = self._pw_var.get()
        if not pw:
            self.app.toast("Generate a password first", RED)
            return
        crypto.save_history(pw, self.app._username, self.app._master_pw)
        self.app.toast("Password added to encrypted.")

        if "history" in self.app.pages:
            self.app.pages["history"]._refresh_history()
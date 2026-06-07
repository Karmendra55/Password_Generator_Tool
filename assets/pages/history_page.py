"""
Password history page UI.

Displays previously generated passwords with strength info and management actions.
"""

import tkinter as tk

from assets.theme import *
from assets.widgets import *
from tkinter import messagebox, ttk
from src import crypto, generator, utils

class HistoryPage(tk.Frame):
    """Encrypted password history viewer and manager."""
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack_propagate(False)

        self.app = app

        self._username = app._username
        self._master_pw = app._master_pw

        self._build()

    def refresh(self):
        self._refresh_history()

    # --- UI Building ----

    def _build(self):

        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=PAD_X, pady=(PAD_Y_LARGE, 0))
        tk.Label(hdr, text="Password History", font=FONT_HEAD, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hdr, text="Previously generated passwords — encrypted at rest.",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        Divider(self).pack(fill="x", padx=PAD_X, pady=PAD_Y_SMALL)

        acts = tk.Frame(self, bg=BG)
        acts.pack(fill="x", padx=28, pady=(0, 8))
        HoverButton(acts, text="🗑  Clear All", command=self._clear_history,
                    bg=SURFACE2, hover_bg=BORDER, fg=RED).pack(side="right")

        # Scrollable list
        cont = tk.Frame(self, bg=BG)
        cont.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        cv = tk.Canvas(cont, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(cont, orient="vertical", command=cv.yview)
        self._hist_inner = tk.Frame(cv, bg=BG)
        self._hist_canvas = cv  # keep ref for width updates

        win_id = cv.create_window((0, 0), window=self._hist_inner, anchor="nw")

        # Keep inner frame exactly as wide as the canvas (minus scrollbar)
        def _on_canvas_resize(e, c=cv, w=win_id):
            c.itemconfigure(w, width=e.width)
        cv.bind("<Configure>", _on_canvas_resize)

        self._hist_inner.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        # Bind mousewheel
        cv.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>",
            lambda ev: cv.yview_scroll(int(-1*(ev.delta/120)), "units")))
        cv.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))

        return self

    # --- Data ---

    def _refresh_history(self):
        for w in self._hist_inner.winfo_children():
            w.destroy()

        entries = crypto.load_history(self.app._username, self.app._master_pw)
        if not entries:
            tk.Label(self._hist_inner, text="No history yet.",
                     font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=12)
            return

        # entries[0] is oldest; show newest first → enumerate reversed
        for display_idx, (real_idx, pw) in enumerate(
                zip(range(len(entries)-1, -1, -1), reversed(entries))):
            self._hist_row(self._hist_inner, real_idx, pw)

    # --- Row UI ---

    def _hist_row(self, parent, real_idx: int, pw: str):
        row = tk.Frame(parent, bg=SURFACE, padx=12, pady=10)
        row.pack(fill="x", pady=3)
        row.columnconfigure(0, weight=1)  # make row stretch

        ent = generator.calculate_entropy(pw)
        str_lbl, col = generator.strength_label(ent)

        def delete_h(i=real_idx):
            if messagebox.askyesno("Delete", "Remove this entry from history?"):
                crypto.delete_history_entry(i, self.app._username, self.app._master_pw)
                self._refresh_history()

        def copy_h(p=pw):
            utils.copy_to_clipboard(p)
            self.app.toast("Copied to clipboard")

        # --- Top row ---
        top = tk.Frame(row, bg=SURFACE)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        top.columnconfigure(0, weight=1)

        tk.Label(top, text=str_lbl, font=FONT_SMALL,
                 bg=SURFACE, fg=col).grid(row=0, column=0, sticky="w")

        btn_frame = tk.Frame(top, bg=SURFACE)
        btn_frame.grid(row=0, column=1, sticky="e")

        tk.Button(btn_frame, text=" 📋 Copy ", font=FONT_SMALL,
                  bg=SURFACE2, fg=TEXT, relief="flat", cursor="hand2",
                  command=copy_h, activebackground=BORDER, activeforeground=TEXT, bd=0,
                  pady=2).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text=" 🗑 Delete ", font=FONT_SMALL,
                  bg=SURFACE2, fg=RED, relief="flat", cursor="hand2",
                  command=delete_h, activebackground=BORDER, activeforeground=TEXT, bd=0,
                  pady=2).pack(side="left")

        # --- Row 1: password text, full width, wraps to next line ---
        pw_lbl = tk.Label(row, text=pw, font=FONT_MONO,
                          bg=SURFACE2, fg=TEXT,
                          anchor="w", justify="left",
                          padx=8, pady=6, wraplength=420)
        pw_lbl.grid(row=1, column=0, sticky="ew")

        def _sync_wrap(e, lbl=pw_lbl):
            new_w = e.width - 24
            if new_w > 60:
                lbl.configure(wraplength=new_w)
        row.bind("<Configure>", _sync_wrap)

    # --- Actions ---

    def _clear_history(self):
        if not messagebox.askyesno("Clear History", "Permanently delete all history?"):
            return
        crypto.clear_history(self.app._username, self.app._master_pw)
        self._refresh_history()

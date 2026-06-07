"""
Main application shell for PasswordGuard.

Handles authentication, window layout, navigation, and page switching.
"""

import tkinter as tk

from assets.auth.auth_dialog import AuthDialog
from assets.pages.generator_page import GeneratorPage
from assets.pages.vault_page import VaultPage
from assets.pages.history_page import HistoryPage

from assets.theme import *
from assets.widgets import Divider

# --------
# App core
# --------

class PasswordGuardApp:
    """Main Tkinter application controller."""
    def __init__(self):
        self._username = ""
        self._master_pw = ""

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("PasswordGuard")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.root.geometry("680x700") 
        self.root.minsize(680, 700)
        self.root.maxsize(680, 700)

        self._pages = {}
        self._current_page = None

        if not self._authenticate():
            self.root.destroy()
            return

        self._build_ui()
        self.root.deiconify()
        self.root.mainloop()

    # --- Authenticate ---
    def _authenticate(self):
        dlg = AuthDialog(self.root)
        self.root.wait_window(dlg)

        if not dlg.username:
            return False

        self._username = dlg.username
        self._master_pw = dlg.master_pw
        return True

    # --- UI SHELL ---
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        # --- LEFT SIDEBAR ---
        nav = tk.Frame(outer, bg=SURFACE, width=160)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        tk.Label(
            nav,
            text="🔐 PasswordGuard",
            bg=SURFACE,
            fg=TEXT,
            font=FONT_BODY
        ).pack(pady=(22, 10))

        Divider(nav).pack(fill="x", padx=12, pady=12)

        self._nav_buttons = {}

        items = [
            ("⚡ Generator", "gen"),
            ("🗄 Vault", "vault"),
            ("📜 History", "history"),
        ]

        def make_btn(parent, label, key):
            btn = tk.Label(
                parent,
                text=label,
                bg=SURFACE,
                fg=TEXT_DIM,
                anchor="w",
                padx=15,
                pady=10,
                cursor="hand2"
            )

            # --- hover effects ---
            btn.bind("<Enter>", lambda e, b=btn, k=key: (
                b.configure(bg=SURFACE2, fg=TEXT if self.current_page != k else TEXT)
            ))

            btn.bind("<Leave>", lambda e, b=btn, k=key: (
                b.configure(
                    bg=SURFACE2 if self.current_page == k else SURFACE,
                    fg=TEXT if self.current_page == k else TEXT_DIM
                )
            ))

            btn.bind("<Button-1>", lambda e, k=key: self.show_page(k))

            btn.pack(fill="x")
            return btn

        for label, key in items:
            self._nav_buttons[key] = make_btn(nav, label, key)

        Divider(nav).pack(fill="x", padx=10, pady=10, side="bottom")

        tk.Label(
            nav,
            text=f"👤 {self._username}",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=FONT_SMALL
        ).pack(side="bottom", pady=(0, 5))

        # --- Switch user button ---
        switch_lbl = tk.Label(
            nav,
            text="⇄ Switch User",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=FONT_SMALL,
            cursor="hand2"
        )

        switch_lbl.pack(side="bottom", pady=(0, 5))
        switch_lbl.bind("<Button-1>", lambda e: self._switch_user())
        switch_lbl.bind("<Enter>", lambda e: switch_lbl.configure(fg=TEXT))
        switch_lbl.bind("<Leave>", lambda e: switch_lbl.configure(fg=TEXT_DIM))

        # --- RIGHT SIDEBAR ---
        right = tk.Frame(outer, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(right, bg=BG)
        self.content.pack(fill="both", expand=True)
        self.content.pack_propagate(False)

        footer = tk.Frame(right, bg=SURFACE, height=25)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="Tkinter| Karmendra Bahadur Srivastava | Made with ❤️",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=FONT_SMALL
        ).pack()

        # --- PAGES ---
        self.pages = {
            "gen": GeneratorPage(self.content, self),
            "vault": VaultPage(self.content, self),
            "history": HistoryPage(self.content, self),
        }

        self.current_page = None
        self.show_page("gen")

    # --- NAVIGATIONS ---
    def show_page(self, page):
        for p in self.pages.values():
            p.pack_forget()

        self.pages[page].pack(fill="both", expand=True)
        self.current_page = page

        self.pages[page].refresh()

        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg=TEXT if k == page else TEXT_DIM,
                bg=SURFACE2 if k == page else SURFACE
            )

    # --- User Switch ---
    def _switch_user(self):
        self.root.withdraw()

        if not self._authenticate():
            self.root.deiconify()
            return

        for w in self.root.winfo_children():
            w.destroy()

        self._build_ui()
        self.root.deiconify()

    # --- Toast ---
    def toast(self, text, color=TEXT):
        if hasattr(self, "_toast"):
            self._toast.destroy()

        self._toast = tk.Label(
            self.root,
            text=text,
            bg=SURFACE2,
            fg=color,
            font=FONT_SMALL,
            padx=12,
            pady=6
        )

        self._toast.place(relx=0.5, rely=0.92, anchor="center")

        self.root.after(1500, self._toast.destroy)

    def refresh(self):
        self._refresh_history()
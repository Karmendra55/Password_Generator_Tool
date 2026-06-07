"""
Authentication dialog for login and user registration.

Handles user selection, login verification, and account creation flow.
"""

import tkinter as tk

from tkinter import messagebox
from assets.theme import *
from assets.widgets import _entry, HoverButton
from src import crypto

# -----------
# Auth Dialog
# -----------

class AuthDialog(tk.Toplevel):
    """
    Full auth flow in one dialog:
      • If no users → straight to register form
      • Otherwise   → user list + login, with a 'New user' button
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.username: str | None = None
        self.master_pw: str | None = None

        self.title("PasswordGuard — Sign in")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        self._centre(400, 420)
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _centre(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # --- Layout ---

    def _build(self):
        self._frame = tk.Frame(self, bg=BG)
        self._frame.pack(fill="both", expand=True)
        users = crypto.list_users()
        if users:
            self._show_login(users)
        else:
            self._show_register(first_time=True)

    def _clear(self):
        for w in self._frame.winfo_children():
            w.destroy()

    # --- login ---

    def _show_login(self, users):
        self._clear()
        f = self._frame

        tk.Label(f, text="🔐", font=("Segoe UI Emoji", 30), bg=BG, fg=TEXT).pack(pady=(26, 4))
        tk.Label(f, text="Welcome back", font=("Segoe UI", 15, "bold"), bg=BG, fg=TEXT).pack()
        tk.Label(f, text="Select your account to continue.",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=(2, 14))

        # User tiles
        tiles = tk.Frame(f, bg=BG)
        tiles.pack(padx=30, fill="x")
        self._sel_user = tk.StringVar(value=users[0])

        for u in users:
            row = tk.Frame(tiles, bg=SURFACE2, cursor="hand2")
            row.pack(fill="x", pady=3)
            rb = tk.Radiobutton(row, text=f"  👤  {u}", variable=self._sel_user,
                                value=u, font=FONT_BODY, bg=SURFACE2, fg=TEXT,
                                activebackground=SURFACE2, activeforeground=TEXT,
                                selectcolor=SURFACE2, indicatoron=True,
                                highlightthickness=0, cursor="hand2")
            rb.pack(anchor="w", padx=10, pady=8)

        tk.Label(f, text="Master password", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=(14, 2))
        self._pw_var = tk.StringVar()
        pw_e = _entry(f, var=self._pw_var, show="●")
        pw_e.pack(padx=30, fill="x")
        pw_e.bind("<Return>", lambda e: self._do_login())
        pw_e.focus_set()

        HoverButton(f, text="Unlock →", command=self._do_login,
                    width=340, height=38).pack(pady=14)

        sep = tk.Frame(f, bg=BG)
        sep.pack()
        tk.Label(sep, text="New here?  ", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(side="left")
        lnk = tk.Label(sep, text="Create account", font=(FONT_SMALL[0], FONT_SMALL[1], "underline"),
                       bg=BG, fg=ACCENT, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self._show_register())

    def _do_login(self):
        user = self._sel_user.get()
        pw   = self._pw_var.get().strip()
        if not pw:
            messagebox.showerror("Error", "Enter your master password.", parent=self)
            return
        if crypto.verify_master_password(user, pw):
            self.username  = user
            self.master_pw = pw
            self.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.", parent=self)

    # --- Register ---

    def _show_register(self, first_time=False):
        self._clear()
        f = self._frame

        tk.Label(f, text="✨", font=("Segoe UI Emoji", 28), bg=BG, fg=TEXT).pack(pady=(24, 4))
        tk.Label(f, text="Create your account", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack()
        tk.Label(f, text="Your master password encrypts all data.\nIt cannot be recovered if forgotten.",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM, justify="center").pack(pady=(4, 14))

        tk.Label(f, text="Username", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="center")
        self._reg_user = tk.StringVar()
        _entry(f, var=self._reg_user).pack(padx=30, fill="x")

        tk.Label(f, text="Master password", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="center", pady=(10,2))
        self._reg_pw1 = tk.StringVar()
        e1 = _entry(f, var=self._reg_pw1, show="●")
        e1.pack(padx=30, fill="x")

        tk.Label(f, text="Confirm password", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="center", pady=(8,2))
        self._reg_pw2 = tk.StringVar()
        e2 = _entry(f, var=self._reg_pw2, show="●")
        e2.pack(padx=30, fill="x")
        e2.bind("<Return>", lambda e: self._do_register())
        self._reg_user.set("")
        e1.focus_set()

        HoverButton(f, text="Create Account →", command=self._do_register,
                    width=340, height=38).pack(pady=14)

        if not first_time:
            sep = tk.Frame(f, bg=BG)
            sep.pack()
            tk.Label(sep, text="Already have an account?  ", font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(side="left")
            lnk = tk.Label(sep, text="Sign in", font=(FONT_SMALL[0], FONT_SMALL[1], "underline"),
                           bg=BG, fg=ACCENT, cursor="hand2")
            lnk.pack(side="left")
            lnk.bind("<Button-1>", lambda e: self._show_login(crypto.list_users()))

    def _do_register(self):
        user = self._reg_user.get().strip()
        pw1  = self._reg_pw1.get().strip()
        pw2  = self._reg_pw2.get().strip()

        if not user:
            messagebox.showerror("Error", "Username cannot be empty.", parent=self); return
        if len(user) < 2:
            messagebox.showerror("Error", "Username must be at least 2 characters.", parent=self); return
        if crypto.user_exists(user):
            messagebox.showerror("Error", f'User "{user}" already exists.', parent=self); return
        if not pw1:
            messagebox.showerror("Error", "Password cannot be empty.", parent=self); return
        if len(pw1) < 6:
            messagebox.showwarning("Weak password", "Use at least 6 characters.", parent=self); return
        if pw1 != pw2:
            messagebox.showerror("Error", "Passwords do not match.", parent=self); return

        crypto.setup_vault(user, pw1)
        self.username  = user
        self.master_pw = pw1
        self.destroy()

    # --- Cancel ---
    def _cancel(self):
        self.username  = None
        self.master_pw = None
        self.destroy()
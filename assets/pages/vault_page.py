"""
Credential vault page UI.

Stores, displays, and manages encrypted user credentials.
"""

import tkinter as tk

from assets.theme import *
from assets.widgets import *
from assets.widgets import _entry
from tkinter import messagebox, ttk

from src import crypto, utils

class VaultPage(tk.Frame):
    """Encrypted credential storage and management UI."""
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack_propagate(False)

        self.app = app
        self._username = app._username
        self._master_pw = app._master_pw

        self._build()

    def refresh(self):
        self._refresh_vault()

    # --- UI Building ---

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=PAD_X, pady=(PAD_Y_LARGE, 0))
        tk.Label(hdr, text="Credential Vault", font=FONT_HEAD, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hdr, text="All entries are encrypted with your master password.",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        Divider(self).pack(fill="x", padx=PAD_X, pady=PAD_Y_SMALL)

        form = Card(self)
        form.pack(fill="x", padx=PAD_X, pady=PAD_Y_SMALL)
        tk.Label(form, text="Add Credential", font=FONT_LABEL, bg=SURFACE, fg=TEXT).pack(anchor="w", pady=(0, 8))

        self._site_var    = tk.StringVar()
        self._user_var    = tk.StringVar()
        self._cred_pw_var = tk.StringVar()

        for label, var, show in [
            ("Website / App",    self._site_var,    ""),
            ("Username / Email", self._user_var,    ""),
            ("Password",         self._cred_pw_var, "●"),
        ]:
            tk.Label(form, text=label, font=FONT_SMALL, bg=SURFACE, fg=TEXT_DIM).pack(anchor="w")
            _entry(form, var=var, show=show).pack(fill="x", pady=(0, 6))

        HoverButton(form, text="🔒  Save Credential",
                    command=self._save_cred).pack(fill="x", pady=(6, 0))

        Divider(self).pack(fill="x", padx=28, pady=12)

        tk.Label(self, text="Stored Credentials", font=FONT_LABEL,
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=28, pady=(0, 0))

        # --- Scrollable credential list ---
        cont = tk.Frame(self, bg=BG)
        cont.pack(fill="both", expand=True, padx=28, pady=(0, 0))

        cv = tk.Canvas(cont, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(cont, orient="vertical", command=cv.yview)
        self._vault_inner = tk.Frame(cv, bg=BG)
        self._vault_inner.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=self._vault_inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        return self

    # --- Actions ---

    def _save_cred(self):
        site = self._site_var.get().strip()
        user = self._user_var.get().strip()
        pw   = self._cred_pw_var.get().strip()
        if not (site and user and pw):
            messagebox.showerror("Error", "All fields are required."); return
        crypto.save_credential(site, user, pw, self.app._username, self.app._master_pw)
        self._site_var.set(""); self._user_var.set(""); self._cred_pw_var.set("")
        self.app.toast("Credentials encrypted & saved.")
        self._refresh_vault()

    def _refresh_vault(self):
        for w in self._vault_inner.winfo_children():
            w.destroy()
        creds = crypto.load_credentials(self.app._username, self.app._master_pw)
        if not creds:
            tk.Label(self._vault_inner, text="No credentials stored yet.",
                     font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=10)
            return
        for idx, c in enumerate(creds):
            self._cred_row(self._vault_inner, idx, c)

    def _cred_row(self, parent, idx, cred):
        row = tk.Frame(parent, bg=SURFACE, pady=8, padx=12)
        row.pack(fill="x", pady=3)

        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=cred.get("website", "—"), font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=cred.get("username", ""), font=FONT_SMALL,
                 bg=SURFACE, fg=TEXT_DIM, anchor="w").pack(anchor="w")

        acts = tk.Frame(row, bg=SURFACE)
        acts.pack(side="right")

        pw_shown = tk.BooleanVar(value=False)
        pw_lbl = tk.Label(acts, text="••••••••", font=FONT_MONO,
                          bg=SURFACE, fg=TEXT_DIM)
        pw_lbl.pack()

        def toggle(lbl=pw_lbl, var=pw_shown, p=cred.get("password", "")):
            var.set(not var.get())
            lbl.configure(text=p if var.get() else "••••••••",
                          fg=TEXT if var.get() else TEXT_DIM)

        def copy_c(p=cred.get("password", "")):
            utils.copy_to_clipboard(p)
            self.app.toast("Password Copied to clipboard")

        def delete_c(i=idx):
            if messagebox.askyesno("Delete", "Delete this credential?"):
                crypto.delete_credential(i, self.app._username, self.app._master_pw)
                self._refresh_vault()

        for txt, fn, colour in [("👁", toggle, TEXT), ("📋", copy_c, TEXT), ("🗑", delete_c, RED)]:
            tk.Button(acts, text=txt, font=FONT_SMALL, bg=SURFACE2, fg=colour,
                      relief="flat", cursor="hand2", command=fn,
                      activebackground=BORDER, activeforeground=TEXT,
                      bd=0).pack(side="left", padx=2)

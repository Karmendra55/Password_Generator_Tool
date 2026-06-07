"""
Reusable UI widgets for the application.

These widgets are built on top of Tkinter and styled using the centralized theme.
"""

import tkinter as tk
from assets.theme import *

# --------
# Buttons
# --------

class HoverButton(tk.Label):
    """Flat styled button — Label-based so it works reliably on all platforms."""

    def __init__(self, parent, text, command,
                 bg=ACCENT, fg=TEXT, hover_bg=ACCENT_DIM,
                 width=200, height=38, **kw):
        kw.pop("radius", None)
        super().__init__(parent, text=text, font=FONT_LABEL,
                         fg=fg, bg=bg, cursor="hand2",
                         anchor="center", relief="flat",
                         padx=12, pady=8, **kw)
        self.bind("<Enter>",    lambda e: self.configure(bg=hover_bg))
        self.bind("<Leave>",    lambda e: self.configure(bg=bg))
        self.bind("<Button-1>", lambda e: command())

# -------------
# Card Container
# --------------

class Card(tk.Frame):
    """
    A simple container widget used for grouping UI elements with consistent background and padding.
    """
    def __init__(self, parent, **kw):
        kw.setdefault("bg", SURFACE)
        kw.setdefault("padx", CARD_PAD)
        kw.setdefault("pady", CARD_PAD)
        super().__init__(parent, **kw)

# ------------
# Divider Line
# ------------

class Divider(tk.Frame):
    """
    A thin horizontal line used to visually separate UI sections.
    """
    def __init__(self, parent, **kw):
        kw.setdefault("height", 1)
        kw.setdefault("bg", BORDER)
        super().__init__(parent, **kw)

# ---------------------
# Internal Entry Factory
# ---------------------
def _entry(parent, var=None, show="", **kw) -> tk.Entry:
    """
    Creates a styled Tkinter Entry Widget.
    """
    return tk.Entry(parent, textvariable=var, show=show,
                    font=FONT_MONO, bg=SURFACE2, fg=TEXT,
                    insertbackground=ACCENT, relief="flat",
                    highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=ACCENT, **kw)
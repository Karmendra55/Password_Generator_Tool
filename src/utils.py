"""
Small utility helpers for PasswordGuard.
"""

import pyperclip

def copy_to_clipboard(text: str) -> None:
    """Copy *text* to the system clipboard via pyperclip."""
    pyperclip.copy(text)
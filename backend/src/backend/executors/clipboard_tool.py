"""
Direct OS clipboard access for the browser agent.

Sites' own "Copy" buttons write via the browser's navigator.clipboard API,
which doesn't reliably reach the real OS clipboard in headless Chromium
(headless's clipboard is effectively a virtual/in-memory one). This writes
from the Python backend process itself instead - the same mechanism either
way, headless or headed.
"""

import pyperclip


def set_clipboard(text: str) -> dict:
    """Copies `text` to the real OS clipboard, bypassing the browser entirely."""
    pyperclip.copy(text)
    return {"copied": True, "length": len(text)}

"""Premium UI building blocks for the banking shell."""

from __future__ import annotations

import ctypes
import tkinter as tk


def expose_win_text(widget: tk.Misc, text: str) -> None:
    """Make Tk widget text visible to pywinauto (win32 window text is often empty)."""
    try:
        hwnd = int(widget.winfo_id())
        ctypes.windll.user32.SetWindowTextW(hwnd, str(text))
    except Exception:
        pass


def fade_in(widget: tk.Misc, steps: int = 8, delay: int = 18) -> None:
    try:
        widget.update_idletasks()
    except tk.TclError:
        return

    def step(i=0):
        if not widget.winfo_exists():
            return
        if i < steps:
            widget.after(delay, lambda: step(i + 1))

    step()


def glass_card(parent: tk.Misc, theme: dict, padx=16, pady=16) -> tk.Frame:
    outer = tk.Frame(parent, bg=theme["card_border"], bd=0, highlightthickness=0)
    inner = tk.Frame(outer, bg=theme["card"], bd=0, highlightthickness=0)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    pad = tk.Frame(inner, bg=theme["card"])
    pad.pack(fill="both", expand=True, padx=padx, pady=pady)
    return pad


def styled_label(parent, theme, text, *, font=None, fg=None, bg=None, **kw) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=bg or theme["card"],
        fg=fg or theme["text"],
        font=font,
        **kw,
    )


def styled_entry(parent, theme, *, show=None, width=32) -> tk.Entry:
    return tk.Entry(
        parent,
        bg=theme["input_bg"],
        fg=theme["text"],
        insertbackground=theme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme["input_border"],
        highlightcolor=theme["purple"],
        font=("Segoe UI", 11),
        width=width,
        show=show or "",
    )


def primary_button(parent, theme, text, command, *, width=18) -> tk.Button:
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=theme["accent"],
        fg="#ffffff",
        activebackground=theme["accent_soft"],
        activeforeground="#ffffff",
        relief="flat",
        bd=0,
        padx=16,
        pady=8,
        font=("Segoe UI Semibold", 10),
        cursor="hand2",
        width=width,
    )

    def on_enter(_e):
        btn.configure(bg=theme["purple"])

    def on_leave(_e):
        btn.configure(bg=theme["accent"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    try:
        parent.update_idletasks()
        expose_win_text(btn, text)
    except Exception:
        pass
    return btn


def ghost_button(parent, theme, text, command, *, width=18) -> tk.Button:
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=theme["card"],
        fg=theme["text"],
        activebackground=theme["hover"],
        activeforeground=theme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme["card_border"],
        bd=0,
        padx=12,
        pady=8,
        font=("Segoe UI Semibold", 10),
        cursor="hand2",
        width=width,
    )
    try:
        parent.update_idletasks()
        expose_win_text(btn, text)
    except Exception:
        pass
    return btn


def inline_alert(parent, theme) -> tk.Label:
    return tk.Label(
        parent,
        text="",
        bg=theme["card"],
        fg=theme["danger"],
        font=("Segoe UI", 9),
        wraplength=320,
        justify="left",
    )


def set_alert(label: tk.Label, theme: dict, message: str, *, ok: bool = False) -> None:
    if not message:
        label.configure(text="", bg=theme["card"])
        return
    if ok:
        label.configure(text=message, fg=theme["green"], bg=theme["success_bg"])
    else:
        label.configure(text=message, fg=theme["danger"], bg=theme["danger_bg"])


def vermeg_logo(parent, theme, *, size=22) -> tk.Frame:
    wrap = tk.Frame(parent, bg=theme.get("logo_bg", theme["card"]))
    tk.Label(
        wrap,
        text="/",
        bg=wrap["bg"],
        fg=theme["accent"],
        font=("Segoe UI Black", size + 4),
    ).pack(side="left")
    tk.Label(
        wrap,
        text="vermeg",
        bg=wrap["bg"],
        fg=theme["text"],
        font=("Segoe UI Semibold", size),
    ).pack(side="left")
    return wrap

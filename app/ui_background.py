from pathlib import Path
import tkinter as tk

from PIL import Image, ImageTk


BACKGROUND_IMAGE_PATH = Path(__file__).resolve().parent / "assets" / "background.png"

_original_image: Image.Image | None = None


def _load_original() -> Image.Image | None:
    global _original_image
    if _original_image is not None:
        return _original_image
    if not BACKGROUND_IMAGE_PATH.exists():
        return None
    try:
        _original_image = Image.open(BACKGROUND_IMAGE_PATH).convert("RGB")
        return _original_image
    except Exception:
        return None


def apply_window_background(window: tk.Misc) -> None:
    original = _load_original()
    if original is None:
        return

    background_label = tk.Label(window, borderwidth=0, highlightthickness=0)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background_label.lower()

    state = {"photo": None, "last_size": (0, 0)}

    def _paint(event=None) -> None:
        try:
            if not background_label.winfo_exists():
                return
        except tk.TclError:
            return

        width = max(window.winfo_width(), 1)
        height = max(window.winfo_height(), 1)
        if width < 2 or height < 2:
            return
        if state["last_size"] == (width, height):
            return

        try:
            resized = original.resize((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            background_label.configure(image=photo)
            state["photo"] = photo
            state["last_size"] = (width, height)
            window._background_image = photo
            background_label.lower()
        except tk.TclError:
            return

    window.bind("<Configure>", _paint, add="+")
    window.after(1, _paint)
    window._background_label = background_label


def style_on_background(widget: tk.Misc, *, fg: str = "#1a1a2e") -> None:
    """Readable controls over the photo background."""
    try:
        widget.configure(bg="#ffffff", fg=fg, highlightthickness=0)
    except tk.TclError:
        try:
            widget.configure(bg="#ffffff", highlightthickness=0)
        except tk.TclError:
            pass

import tkinter as tk

THEMES = {
    "light": {
        "bg": "#d8b4f8",          # light purple background
        "sidebar_bg": "#c084fc",  # medium purple for sidebar
        "fg": "black",            # text color
        "btn_bg": "#e9d5ff",      # lightest purple for buttons
        "btn_fg": "black"         # button text color
    },
    "dark": {
        "bg": "#5a189a",          # dark purple background
        "sidebar_bg": "#3c096c",  # darker purple for sidebar
        "fg": "white",            # text color
        "btn_bg": "#7b2cbf",      # medium purple for buttons
        "btn_fg": "white"         # button text color
    }
}

def create_theme_menu(root: tk.Tk, apply_theme_callback):
    """Add theme selection menu to the root window"""
    menubar = tk.Menu(root)
    theme_menu = tk.Menu(menubar, tearoff=0)
    for name in THEMES:
        theme_menu.add_command(
            label=name.title(),
            command=lambda n=name: apply_theme_callback(n)
        )
    menubar.add_cascade(label="Theme", menu=theme_menu)
    root.config(menu=menubar)
import tkinter as tk

# Define your two teal themes
THEMES = {
    "dark":  {"bg": "#005f5f", "fg": "white"},
    "light": {"bg": "#a8e6e6", "fg": "black"},
}

def create_theme_menu(root: tk.Tk, apply_theme_callback):
    """
    Add a “Theme” menu to the root window that lets you pick a theme.
    apply_theme_callback(name) will be called with "dark" or "light".
    """
    menubar = tk.Menu(root)
    theme_menu = tk.Menu(menubar, tearoff=0)
    for name in THEMES:
        theme_menu.add_command(
            label=name.title(),
            command=lambda n=name: apply_theme_callback(n)
        )
    menubar.add_cascade(label="Theme", menu=theme_menu)
    root.config(menu=menubar)

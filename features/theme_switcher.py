# features/theme_switcher.py

import tkinter as tk

THEMES = {
    "light": {"bg":"#ffffff","fg":"#000000"},
    "dark":  {"bg":"#2e2e2e","fg":"#ffffff"}
}

class ThemeSwitcher:
    """Attach to a root window to toggle light/dark themes."""
    def __init__(self, root: tk.Tk):
        self.root    = root
        self.current = "light"
        self.button  = tk.Button(root, text="Toggle Theme", command=self.toggle)
        self.button.pack(pady=5)

    def apply(self):
        t = THEMES[self.current]
        for w in self.root.winfo_children():
            try:
                w.config(bg=t["bg"], fg=t["fg"])
            except tk.TclError:
                pass

    def toggle(self):
        self.current = "dark" if self.current == "light" else "light"
        self.apply()

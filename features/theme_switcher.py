import tkinter as tk

THEMES = {
    "light": {"bg": "#f0f4f7", "fg": "#000000"},
    "dark":  {"bg": "#2e2e2e", "fg": "#ffffff"}
}

class ThemeSwitcher:
    def __init__(self, root: tk.Tk):
        self.root    = root
        self.current = "light"
        self.button  = tk.Button(root, text="Toggle Theme", command=self.toggle)

    def apply(self):
        scheme = THEMES[self.current]
        for w in self.root.winfo_children():
            try:
                w.config(bg=scheme["bg"], fg=scheme["fg"])
            except tk.TclError:
                pass

    def toggle(self):
        self.current = "dark" if self.current=="light" else "light"
        self.apply()

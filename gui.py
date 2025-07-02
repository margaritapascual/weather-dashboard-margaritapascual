import tkinter as tk

class MainWindow:
    """Basic Tkinter window for searching and displaying weather."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("400x300")

        # ——— Search bar ———
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="City:").pack(side=tk.LEFT)
        self.city_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.city_var, width=20).pack(side=tk.LEFT)
        self.search_btn = tk.Button(search_frame, text="Search")
        self.search_btn.pack(side=tk.LEFT, padx=5)

        # ——— Results area ———
        self.error_lbl = tk.Label(self.root, text="", fg="red")
        self.error_lbl.pack()

        self.city_lbl = tk.Label(self.root, text="", font=("Arial", 16))
        self.city_lbl.pack()

        self.temp_lbl = tk.Label(self.root, text="", font=("Arial", 14))
        self.temp_lbl.pack()

        self.desc_lbl = tk.Label(self.root, text="", font=("Arial", 12))
        self.desc_lbl.pack()

        # Placeholder for extra feature widgets
        self.feature_frame = tk.Frame(self.root)
        self.feature_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def register_callback(self, name, fn):
        """Allow external code to hook up search/refresh, etc."""
        if name == "search":
            self.search_btn.config(command=lambda: fn(self.city_var.get()))

    def display_weather(self, data: dict):
        """Show fetched/processed weather on the labels."""
        self.error_lbl.config(text="")
        self.city_lbl.config(text=f"{data['city']}, {data['country']}")
        self.temp_lbl.config(text=f"{data['temperature']} °C")
        self.desc_lbl.config(text=data['description'].capitalize())

    def show_error(self, msg: str):
        self.error_lbl.config(text=msg)

    def run(self):
        self.root.mainloop()

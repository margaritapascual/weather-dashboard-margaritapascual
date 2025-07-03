# features/historical_data.py

import tkinter as tk
from tkinter import ttk
from typing import List, Dict

def show_history(parent: tk.Frame, history: List[Dict]):
    """Render the last-7-days history in a Treeview table."""
    tree = ttk.Treeview(parent, columns=("city","country","temp","desc","time"), show="headings")
    tree.heading("city",    text="City")
    tree.heading("country", text="Country")
    tree.heading("temp",    text="Temp (°C)")
    tree.heading("desc",    text="Description")
    tree.heading("time",    text="Timestamp")

    tree.column("city",    width=80, anchor=tk.CENTER)
    tree.column("country", width=60, anchor=tk.CENTER)
    tree.column("temp",    width=80, anchor=tk.CENTER)
    tree.column("desc",    width=120)
    tree.column("time",    width=140)

    for row in history:
        tree.insert("", tk.END, values=(
            row["city"],
            row["country"],
            f"{row['temperature']:.1f}",
            row["description"].capitalize(),
            row["timestamp"]
        ))

    tree.pack(fill=tk.BOTH, expand=True, pady=5)
    return tree
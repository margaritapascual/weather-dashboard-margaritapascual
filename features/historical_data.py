import tkinter as tk
from tkinter import ttk
from typing import List, Dict

def show_history(parent: tk.Frame, history: List[Dict]):
    """Render last-7-days history in a Treeview."""
    tree = ttk.Treeview(parent, columns=("city","country","temp","desc","time"), show="headings")
    # … set up headings & insert rows …
    tree.pack(fill=tk.BOTH, expand=True)
    return tree

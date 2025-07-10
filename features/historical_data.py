import tkinter as tk
from tkinter import ttk

def show_history(frame: tk.Frame, rows: list[tuple]):
    """
    Clear `frame` and draw a scrollable table with columns:
      Date | Temp (°F) | Precip (mm) | Humidity (%) | Description
    `rows` should be an iterable of 5-tuples matching those columns.
    """
    # Clear any existing widgets
    for w in frame.winfo_children():
        w.destroy()

    cols = ("Date", "Temp (°F)", "Precip (mm)", "Humidity (%)", "Description")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)

    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # Insert the data
    for date, precip, hum, temp, desc in rows:
        tree.insert("", "end", values=(date, temp, precip, hum, desc))

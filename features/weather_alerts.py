import tkinter as tk
from tkinter import messagebox
from datetime import datetime

def show_alerts(banner_label: tk.Label, alerts: list[dict], theme: dict):
    """
    Display a banner if alerts exist; clicking it shows full details.
    - banner_label: the Label widget at top of gui to use as banner.
    - alerts: list of alert dicts from One Call.
    - theme: dict with 'bg' and 'fg' colors.
    """
    # clear any previous binding/text
    banner_label.unbind("<Button-1>")
    banner_label.configure(text="", bg=theme["bg"], fg=theme["fg"])

    if not alerts:
        return

    # brief banner text
    text = " | ".join(a["event"] for a in alerts)
    banner_label.configure(text=text, bg="#FFCC00", fg="black")

    # on‐click, show full alert descriptions
    def on_click(_):
        parts = []
        for a in alerts:
            start = datetime.utcfromtimestamp(a["start"]).strftime("%m/%d %H:%M")
            end   = datetime.utcfromtimestamp(a["end"]).strftime("%m/%d %H:%M")
            parts.append(f"{a['event']} ({start}–{end}):\n{a['description']}")
        messagebox.showinfo("Weather Alerts", "\n\n".join(parts))

    banner_label.bind("<Button-1>", on_click)

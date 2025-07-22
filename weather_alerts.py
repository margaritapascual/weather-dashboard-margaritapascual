# weather_alerts.py

import tkinter as tk
from datetime import datetime


def show_alerts(banner_label: tk.Label, alerts: list[dict], theme: dict):
    """
    Display weather alerts in the banner label as multiline text.
    - banner_label: the Label widget at top of GUI to use as banner.
    - alerts: list of alert dicts from One Call.
    - theme: dict with 'bg' and 'fg' colors.
    """
    # clear previous text and styling
    banner_label.unbind("<Button-1>")
    banner_label.configure(text="", bg=theme["bg"], fg=theme["fg"])

    if not alerts:
        return

    # build detailed alert text
    lines = []
    for a in alerts:
        # format start/end
        start = datetime.utcfromtimestamp(a.get("start", 0)).strftime("%m/%d %H:%M")
        end = datetime.utcfromtimestamp(a.get("end", 0)).strftime("%m/%d %H:%M")
        event = a.get("event", "Alert")
        desc = a.get("description", "")
        lines.append(f"{event} ({start}–{end}): {desc}")

    # set banner as multiline with alert details
    banner_label.configure(
        text="\n".join(lines),
        bg="#FFCC00",
        fg="black",
        justify='left'
    )

# features/weather_alerts.py
import tkinter as tk
from datetime import datetime
from typing import List, Dict

def show_alerts(alerts: List[Dict], parent: tk.Frame, theme: Dict):
    """Render weather alerts full‐page with improved formatting"""
    # Clear previous
    for widget in parent.winfo_children():
        widget.destroy()

    # If no alerts, show a placeholder
    if not alerts:
        lbl = tk.Label(
            parent,
            text="No active weather alerts",
            bg=theme['bg'],
            fg=theme['fg'],
            font=('Helvetica', 14),
            wraplength=parent.winfo_width(),
            justify='center'
        )
        lbl.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        return

    # Create a full‐page scrollable canvas
    canvas = tk.Canvas(parent, bg=theme['bg'], highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=theme['bg'])

    # Configure scroll region
    def on_frame_config(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_config)

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack full‐page
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Populate alerts
    for alert in alerts:
        frame = tk.Frame(
            scroll_frame,
            bg=theme['bg'],
            padx=10,
            pady=10,
            relief=tk.RIDGE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Header
        start = datetime.utcfromtimestamp(alert.get('start', 0)).strftime('%Y-%m-%d %I:%M %p')
        end   = datetime.utcfromtimestamp(alert.get('end',   0)).strftime('%Y-%m-%d %I:%M %p')
        header = tk.Label(
            frame,
            text=f"⚠️  {alert.get('event', 'Alert')}\n({start} to {end})",
            font=('Helvetica', 14, 'bold'),
            bg=theme['bg'],
            fg='red',
            justify='left'
        )
        header.pack(fill=tk.X, pady=(0,5))

        # Description
        desc = tk.Label(
            frame,
            text=alert.get('description', 'No details available'),
            font=('Helvetica', 12),
            bg=theme['bg'],
            fg=theme['fg'],
            wraplength=parent.winfo_width() - 40,
            justify='left'
        )
        desc.pack(fill=tk.X, pady=(0,5))

        # Sender
        sender = tk.Label(
            frame,
            text=f"Source: {alert.get('sender_name', 'Unknown')}",
            font=('Helvetica', 10, 'italic'),
            bg=theme['bg'],
            fg=theme['fg'],
            justify='left'
        )
        sender.pack(fill=tk.X)
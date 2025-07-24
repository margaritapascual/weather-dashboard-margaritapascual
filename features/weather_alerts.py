import tkinter as tk
from datetime import datetime
from typing import List, Dict

def show_alerts(alerts: List[Dict], parent: tk.Frame, theme: Dict):
    """Render weather alerts with improved formatting"""
    for widget in parent.winfo_children():
        widget.destroy()
    
    if not alerts:
        lbl = tk.Label(parent,
                     text="No active weather alerts",
                     bg=theme['bg'],
                     fg=theme['fg'],
                     wraplength=280,
                     justify='left')
        lbl.pack(fill=tk.X, padx=5, pady=5)
        return
    
    # Create scrollable frame
    canvas = tk.Canvas(parent, bg=theme['bg'], highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme['bg'])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Add each alert
    for alert in alerts:
        alert_frame = tk.Frame(scrollable_frame, 
                             bg=theme['bg'],
                             padx=5,
                             pady=5,
                             relief=tk.RAISED,
                             borderwidth=1)
        alert_frame.pack(fill=tk.X, pady=2)
        
        # Alert header
        start = datetime.utcfromtimestamp(alert.get('start', 0)).strftime('%m/%d %H:%M')
        end = datetime.utcfromtimestamp(alert.get('end', 0)).strftime('%m/%d %H:%M')
        
        header = tk.Label(alert_frame,
                        text=f"⚠️ {alert.get('event', 'Alert')} ({start} to {end})",
                        font=('Helvetica', 10, 'bold'),
                        bg=theme['bg'],
                        fg='red',
                        justify='left',
                        anchor='w')
        header.pack(fill=tk.X)
        
        # Alert description
        desc = tk.Label(alert_frame,
                       text=alert.get('description', 'No details available'),
                       wraplength=250,
                       justify='left',
                       bg=theme['bg'],
                       fg=theme['fg'],
                       anchor='w')
        desc.pack(fill=tk.X)
        
        # Alert sender
        sender = tk.Label(alert_frame,
                         text=f"Source: {alert.get('sender_name', 'Unknown')}",
                         font=('Helvetica', 8),
                         bg=theme['bg'],
                         fg=theme['fg'],
                         anchor='w')
        sender.pack(fill=tk.X)
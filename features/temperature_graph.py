# features/temperature_graph.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Dict

def embed_temperature_graph(parent, history: List[Dict]):
    """Embed a line chart of the last N temperatures."""
    # Ensure chronological order
    history = list(reversed(history))

    # Extract data
    times = [row["timestamp"] for row in history]
    temps = [row["temperature"] for row in history]

    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.plot(times, temps, marker="o")
    ax.set_title("Last 7 Days: Temperature")
    ax.set_ylabel("°C")
    ax.set_xticks(times)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas
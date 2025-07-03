import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Dict

def embed_temperature_graph(parent, history: List[Dict]):
    """Embed a line chart of temperatures over time."""
    # … prepare fig & axes, plot, then:
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas

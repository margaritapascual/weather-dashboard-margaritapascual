import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def show_temp_chart(frame, rows, days):
    """
    Clear `frame` and draw a line chart of the last `days` temperatures (°F).
    `rows` should be an iterable of (date, precip, humidity, temp, description).
    """
    # Clear existing content
    for w in frame.winfo_children():
        w.destroy()

    # Unpack and slice
    dates, _, _, temps, _ = zip(*rows)
    dates = dates[-days:]
    temps = temps[-days:]

    # Build the plot
    fig, ax = plt.subplots(figsize=(8,3))
    ax.plot(dates, temps, marker="o")
    ax.set_title(f"{days}-Day Temperature")
    ax.set_ylabel("°F")
    fig.autofmt_xdate(rotation=45)

    # Embed in Tk
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

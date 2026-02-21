import matplotlib
import matplotlib.pyplot as plt

def generate(temps_str: list, filename: str):
    """
    :param temps_str: list of temp values
    :param filename: e.g. temp_260219.png
    :return:
    """

    # LaTeX-Schriften verwenden
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",  # oder lualatex/xelatex
        "font.family": "serif",
        "text.usetex": True,
        "pgf.rcfonts": False,
    })

    temps = [float(t) for t in temps_str]
    hours = list(range(24))

    fig_width = 5  # in inch
    fig_height = fig_width / 2.5

    # Plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.plot(hours, temps)
    ax.set_ylabel("Temp. °C")
    ax.set_xlabel("Stunde")
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True)

    # Speichern als PGF
    plt.savefig(filename, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

if __name__ == "__main__":
    # Gegebene Daten
    temps_str = ['2.7', '2.5', '2.7', '2.7', '2.8', '3.0', '3.2', '3.4',
                 '3.7', '4.0', '4.2', '4.6', '4.9', '5.2', '5.5', '5.7',
                 '5.9', '5.9', '5.8', '5.6', '5.4', '5.2', '5.0', '4.9']
    generate(temps_str, "temperaturverlauf.png")



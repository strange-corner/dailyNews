import matplotlib
import matplotlib.pyplot as plt

def generate_image_and_get_insertiontext(temps_str: list, folder: str, filename: str):
    """
    :param temps_str: list of temp values
    :param filename: e.g. temp_260219.png
    :return: TeX, das direkt im Dokument eingefügt werden kann.
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
    plt.savefig(f"{folder}/{filename}", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    return "\\includegraphics[width =\\columnwidth]{" + filename + "}\n"


def generate_tikz(temps_str: list):

    part1 = r"""
\begin{tikzpicture}
\begin{axis}[
    width=\columnwidth,
    height=0.5\columnwidth,
    enlargelimits=true,
    tick label style={font=\tiny},
    label style={font=\tiny},
    title style={font=\tiny},
    xlabel={Stunde},
    ylabel={Temp. °C},
    xtick={0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22},
    grid=major,
    axis lines=left,
    clip=true,
    trim axis left,
    trim axis right
]

\addplot[
    thick,
    color=blue
] coordinates {
"""

    coords = ""
    for i, p in enumerate(temps_str):
        coords = coords + f"({i}, {p})\n"

    part3 = r"""
    };

\end{axis}
\end{tikzpicture}"""

    return part1 + coords + part3


if __name__ == "__main__":
    # Gegebene Daten
    temps_str = ['2.7', '2.5', '2.7', '2.7', '2.8', '3.0', '3.2', '3.4',
                 '3.7', '4.0', '4.2', '4.6', '4.9', '5.2', '5.5', '5.7',
                 '5.9', '5.9', '5.8', '5.6', '5.4', '5.2', '5.0', '4.9']
    generate_image_and_get_insertiontext(temps_str, ".", "temperaturverlauf.png")



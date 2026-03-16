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

def _generate_precip_part(precip_d: list, pmax, precip_quant10: list, precip_quant90: list) -> str:
    """ Gibt den String für das Balkendiagramm zurück. Wenn es keinen Niederschlag gibt, dann Leerstring"""
    doGenerate = False
    precip_coords = ""
    for i, p in enumerate(precip_d):
        precip_coords = precip_coords + f"({i}, {p}) -= (0, {p - precip_quant10[i]}) += (0, {precip_quant90[i] - p})\n"
        if precip_quant90[i] > 0:
            doGenerate = True
    if doGenerate:
        result = r"""
    
    % Rechte Achse (Balkendiagramm)
\begin{axis}[
    width=\columnwidth,
    height=0.5\columnwidth,
    axis y line*=right,
    axis x line=none,
    tick label style={font=\tiny},
    label style={font=\tiny, color=red},
    ylabel={Niederschlag mm},
    ymin=0,
    ymax=""" + f"{pmax}," + r"""
    ybar,
    xmin=0, xmax=23,
    bar width=3pt,
]

\addplot[red, fill=red!40,
error bars/.cd,
    y dir=both,
    y explicit
] coordinates {
""" + precip_coords + r"""
};

\end{axis}"""
    else:
        result = ""
    return result

def generate_tikz(tempf: list, ymin, ymax, precip_str: list, pmax, precip_quant10: list, precip_quant90: list):
    tmin = min(tempf)
    tmin_idx = tempf.index(tmin)
    tmin_pos = tmin_idx / 23
    tmax = max(tempf)
    tmax_idx = tempf.index(tmax)
    tmax_pos = tmax_idx / 23


    part1 = r"""
\begin{tikzpicture}
""" + _generate_precip_part(precip_str, pmax, precip_quant10, precip_quant90) + r"""

\begin{axis}[
    width=\columnwidth,
    height=0.5\columnwidth,
    enlargelimits=true,
    tick label style={font=\tiny},
    ylabel style={font=\tiny, color=blue},
    xlabel style={font=\tiny},
    title style={font=\tiny},
    xlabel={Stunde},
    ylabel={Temperatur °C},
    xtick={0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22},
    grid=major,
    axis lines=left,
    clip=true,
    trim axis left,
    trim axis right,
    """ + \
            f"ymin={ymin},ymax={ymax}," + \
            r"""
]

\addplot[
    thick,
    color=blue
] coordinates {
"""

    coords = ""
    for i, p in enumerate(tempf):
        coords = coords + f"({i}, {p})\n"
    coords = coords + "}\n"
    coords = coords + f"node[pos={tmin_pos}, above{' right' if tmin_pos < 0.05 else ' left' if tmin_pos > 0.95 else ''}, font=\\tiny, color=black]{{{tmin}°}}\n"
    coords = coords + f"node[pos={tmax_pos}, below{' right' if tmax_pos < 0.05 else ' left' if tmax_pos > 0.95 else ''}, font=\\tiny, color=black]{{{tmax}°}}\n;\n"

    part3 = r"""

\end{axis}
\end{tikzpicture}"""

    return part1 + coords + part3


if __name__ == "__main__":
    # Gegebene Daten
    temps_str = ['2.7', '2.5', '2.7', '2.7', '2.8', '3.0', '3.2', '3.4',
                 '3.7', '4.0', '4.2', '4.6', '4.9', '5.2', '5.5', '5.7',
                 '5.9', '5.9', '5.8', '5.6', '5.4', '5.2', '5.0', '4.9']
    generate_image_and_get_insertiontext(temps_str, ".", "temperaturverlauf.png")



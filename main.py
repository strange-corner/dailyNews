import tkinter as tk
from tkinter import filedialog, messagebox


# --- Funktion: Einzelnen Artikel erzeugen ---
def save_article():
    title = article_title.get()
    lead = article_lead.get("1.0", "end").strip()
    content = article_content.get("1.0", "end").strip()

    if not title:
        messagebox.showwarning("Fehler", "Titel muss ausgefüllt sein.")
        return

    output_file = filedialog.asksaveasfilename(
        defaultextension=".tex",
        filetypes=[("TeX files", "*.tex")],
        initialfile=f"{title.replace(' ', '_')}.tex"
    )
    if not output_file:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"\\section*{{{title}}}\n")
        if lead:
            f.write(f"\\textbf{{{lead}}}\n\n")
        f.write(f"{content}\n")

    messagebox.showinfo("Erfolg", f"Artikel gespeichert: {output_file}")
    # In Listbox eintragen
    article_listbox.insert(tk.END, output_file)


# --- Funktion: Wetterdatei erzeugen ---
def save_weather():
    w_text = f"{{\\bf Heute:}} Temp {temp_today.get()}°C, Regen {rain_today.get()}%, Wolken {clouds_today.get()}%, Sonne {sun_today.get()}%\n"
    w_text += f"{{\\bf Morgen:}} Temp {temp_tomorrow.get()}°C, Regen {rain_tomorrow.get()}%, Wolken {clouds_tomorrow.get()}%, Sonne {sun_tomorrow.get()}%\n"

    output_file = filedialog.asksaveasfilename(
        defaultextension=".tex",
        filetypes=[("TeX files", "*.tex")],
        initialfile="wetter.tex"
    )
    if not output_file:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(w_text)

    messagebox.showinfo("Erfolg", f"Wetter gespeichert: {output_file}")


# --- Funktion: Tagesausgabe erstellen ---
def generate_today():
    selected_indices = article_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Fehler", "Bitte mindestens einen Artikel auswählen.")
        return

    output_file = filedialog.asksaveasfilename(
        defaultextension=".tex",
        filetypes=[("TeX files", "*.tex")],
        initialfile="today.tex"
    )
    if not output_file:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        # Präambel
        f.write(r"""\documentclass[10pt,a4paper]{article}
\usepackage[ngerman]{babel}
\usepackage{paracol}
\usepackage{titlesec}
\newcommand{\sectionline}{\noindent\rule{\columnwidth}{0.5pt}}
\titleformat{\section}[block]{\bfseries\Large}{}{0pt}{}[\vspace{-4pt}\sectionline]
\titlespacing*{\section}{0pt}{6pt}{12pt}
\pagestyle{empty}
\begin{document}
\begin{paracol}{3}
""")
        # Artikel einfügen
        for idx in selected_indices:
            art_file = article_listbox.get(idx)
            with open(art_file, "r", encoding="utf-8") as af:
                f.write("\n" + af.read() + "\n")

        # Wetter einfügen, falls vorhanden
        try:
            with open("wetter.tex", "r", encoding="utf-8") as wf:
                f.write("\n% --- Wetterblock ---\n")
                f.write(wf.read() + "\n")
        except FileNotFoundError:
            pass

        # Platzhalter für weitere Rubriken
        f.write(r"""
% --- Rubriken ---
% \input{agenda.tex}
% \input{impressum.tex}

\end{paracol}
\end{document}
""")
    messagebox.showinfo("Erfolg", f"Tagesausgabe erstellt: {output_file}")


# --- GUI ---
root = tk.Tk()
root.title("Zeitungs-Generator")

# --- Artikel-Formular ---
article_frame = tk.LabelFrame(root, text="Artikel erstellen", padx=5, pady=5)
article_frame.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(article_frame, text="Titel:").pack(anchor="w")
article_title = tk.Entry(article_frame, width=80)
article_title.pack(fill="x", padx=5, pady=2)

tk.Label(article_frame, text="Lead:").pack(anchor="w")
article_lead = tk.Text(article_frame, height=3)
article_lead.pack(fill="x", padx=5, pady=2)

tk.Label(article_frame, text="Content:").pack(anchor="w")
article_content = tk.Text(article_frame, height=6)
article_content.pack(fill="x", padx=5, pady=2)

tk.Button(article_frame, text="Artikel speichern", command=save_article).pack(pady=5)

# --- Wetterblock ---
weather_frame = tk.LabelFrame(root, text="Wetter", padx=5, pady=5)
weather_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Heute
tk.Label(weather_frame, text="Heute - Temperatur °C:").grid(row=0, column=0, sticky="w")
temp_today = tk.Entry(weather_frame, width=10)
temp_today.grid(row=0, column=1)

tk.Label(weather_frame, text="Regen %:").grid(row=0, column=2, sticky="w")
rain_today = tk.Entry(weather_frame, width=5)
rain_today.grid(row=0, column=3)

tk.Label(weather_frame, text="Wolken %:").grid(row=0, column=4, sticky="w")
clouds_today = tk.Entry(weather_frame, width=5)
clouds_today.grid(row=0, column=5)

tk.Label(weather_frame, text="Sonne %:").grid(row=0, column=6, sticky="w")
sun_today = tk.Entry(weather_frame, width=5)
sun_today.grid(row=0, column=7)

# Morgen
tk.Label(weather_frame, text="Morgen - Temperatur °C:").grid(row=1, column=0, sticky="w")
temp_tomorrow = tk.Entry(weather_frame, width=10)
temp_tomorrow.grid(row=1, column=1)

tk.Label(weather_frame, text="Regen %:").grid(row=1, column=2, sticky="w")
rain_tomorrow = tk.Entry(weather_frame, width=5)
rain_tomorrow.grid(row=1, column=3)

tk.Label(weather_frame, text="Wolken %:").grid(row=1, column=4, sticky="w")
clouds_tomorrow = tk.Entry(weather_frame, width=5)
clouds_tomorrow.grid(row=1, column=5)

tk.Label(weather_frame, text="Sonne %:").grid(row=1, column=6, sticky="w")
sun_tomorrow = tk.Entry(weather_frame, width=5)
sun_tomorrow.grid(row=1, column=7)

tk.Button(weather_frame, text="Wetter speichern", command=save_weather).grid(row=2, column=0, columnspan=8, pady=5)

# --- Tagesausgabe zusammenstellen ---
output_frame = tk.LabelFrame(root, text="Tagesausgabe erstellen", padx=5, pady=5)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(output_frame, text="Vorhandene Artikel:").pack(anchor="w")
article_listbox = tk.Listbox(output_frame, selectmode=tk.MULTIPLE, width=80, height=6)
article_listbox.pack(fill="x", padx=5, pady=5)

tk.Button(output_frame, text="Tagesausgabe erzeugen", command=generate_today).pack(pady=5)

root.mainloop()

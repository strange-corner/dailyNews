import tkinter as tk
from tkinter import filedialog, messagebox


# --- Funktion zum Generieren der .tex-Datei ---
def generate_tex():
    output_file = filedialog.asksaveasfilename(
        defaultextension=".tex", filetypes=[("TeX files", "*.tex")]
    )
    if not output_file:
        return

    num_articles = len(article_entries)

    with open(output_file, "w", encoding="utf-8") as f:
        # Präambel und Template
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
        for idx, entry in enumerate(article_entries, start=1):
            title = entry["title"].get()
            lead = entry["lead"].get("1.0", "end").strip()
            content = entry["content"].get("1.0", "end").strip()
            if title or lead or content:
                f.write(f"\n\\section*{{{title}}}\n")
                if lead:
                    f.write(f"\\textbf{{{lead}}}\n\n")
                f.write(f"{content}\n")

        # Rubriken (einfach Platzhalter)
        f.write(r"""
% --- Rubriken ---
% \input{agenda.tex}
% \input{wetter.tex}
% \input{impressum.tex}

\end{paracol}
\end{document}
""")
    messagebox.showinfo("Erfolg", f".tex-Datei erzeugt:\n{output_file}")


# --- GUI starten ---
root = tk.Tk()
root.title("Zeitungsartikel-Generator")

article_entries = []

def formular():
    frame = tk.LabelFrame(root, text=f"Artikel", padx=5, pady=5)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(frame, text="Titel:").pack(anchor="w")
    title_entry = tk.Entry(frame, width=80)
    title_entry.pack(fill="x", padx=5, pady=2)

    tk.Label(frame, text="Lead:").pack(anchor="w")
    lead_text = tk.Text(frame, height=3)
    lead_text.pack(fill="x", padx=5, pady=2)

    tk.Label(frame, text="Content:").pack(anchor="w")
    content_text = tk.Text(frame, height=6)
    content_text.pack(fill="x", padx=5, pady=2)

    article_entries.append({"title": title_entry, "lead": lead_text, "content": content_text})

    # Button zum Generieren
    tk.Button(root, text="LaTeX-Datei erstellen", command=generate_tex).pack(pady=10)

formular()
root.mainloop()

import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import qrcode
import requests
from tkcalendar import DateEntry

# --- Konstanten / Konfiguration ---
import article_codec
from pageflow import *

LAT = 47.3833  # Beispielkoordinaten Ostschweiz / Herisau (anpassen)
LON = 9.3

pageflow = PageFlow()

# Funktion, um Wetterdaten via Open-Meteo (ICON CH) zu holen
def fetch_weather(date):
    # Open-Meteo API: ICON CH
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "cloudcover_mean",
                  "sunshine_duration"],
        "start_date": date,
        "end_date": date,
        "timezone": "Europe/Zurich",
    }
    r = requests.get(base, params=params)
    r.raise_for_status()
    data = r.json()
    # Extrahieren der Werte
    d = data["daily"]
    return {
        "temp_max": d["temperature_2m_max"][0],
        "temp_min": d["temperature_2m_min"][0],
        "precip": d["precipitation_sum"][0],
        "cloud": d["cloudcover_mean"][0],
        "sunshine": d["sunshine_duration"][0]
    }


def getFolderFromDate():
    date_time = date_entry.get_date()
    folder = date_time.strftime("%y%m_%d")
    return folder


def articleFilenameFromTitle(title: str) -> str:
    return f"a_{title.replace(' ', '_')}.tex"


def download_image(url):
    image = requests.get(url)
    image_name = url.split('/')[-1]
    image_path = os.path.join(getFolderFromDate(), image_name)
    with open(image_path, 'wb') as f:
        for chunk in image.iter_content():
            f.write(chunk)
    return image_name

# --- GUI-Funktionen ---

def save_article():
    title = article_title.get().strip()
    lead = article_lead.get("1.0", "end").strip()
    content = article_content.get("1.0", "end").strip()
    url = article_url.get().strip()
    image_url = image_url_entry.get().strip()
    image_filename = None
    if not title:
        messagebox.showwarning("Fehler", "Titel ist erforderlich")
        return
    if image_url:
        image_filename = download_image(image_url)

    os.makedirs(getFolderFromDate(), exist_ok=True)

    # Dateiname sicher machen
    folder = getFolderFromDate()
    fname = articleFilenameFromTitle(title)
    article_filename = os.path.join(folder, fname)
    article_codec.encode(article_filename, {"title": title, "lead": lead, "content": content, "url": url, "image": image_filename})
    global pageflow
    pageflow.add(Article(fname))
    refresh_article_ui()
    felder_loeschen()


def add_category():
    pageflow.add(CategoryMarker(combobox.get()))
    refresh_article_ui()


def felder_loeschen():
    article_title.delete(0, "end")
    article_lead.delete(1.0, tk.END)
    article_content.delete(1.0, tk.END)


def save_weather_block():
    date = date_entry.get()
    folder = date.replace("-", "")
    folder = folder[2:] + "_" + folder[4:]
    os.makedirs(folder, exist_ok=True)

    # hole Wetter für heute und morgen
    weather_today = fetch_weather(date)
    tomorrow = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    weather_tomorrow = fetch_weather(tomorrow)

    weather_filename = os.path.join(folder, "wetter.tex")
    with open(weather_filename, "w", encoding="utf-8") as f:
        f.write(
            f"\\textbf{{Heute:}} Max {weather_today['temp_max']}°C, Min {weather_today['temp_min']}°C, Regen {weather_today['precip']} mm, Wolken {weather_today['cloud']}%, Sonne {weather_today['sunshine']} h \n")
        f.write(
            f"\\textbf{{Morgen:}} Max {weather_tomorrow['temp_max']}°C, Min {weather_tomorrow['temp_min']}°C, Regen {weather_tomorrow['precip']} mm, Wolken {weather_tomorrow['cloud']}%, Sonne {weather_tomorrow['sunshine']} h \n")
    messagebox.showinfo("Wetter gespeichert", weather_filename)
    refresh_articles()


def refresh_article_ui():
    article_listbox.delete(0, tk.END)
    for elem in pageflow.elements():
        identifier = elem.ident()
        article_listbox.insert(tk.END, identifier)


def refresh_articles():
    global pageflow
    pageflow.refreshArticles(getFolderFromDate())
    refresh_article_ui()


def populate_form(article_filename):
    felder_loeschen()
    article_path = os.path.join(getFolderFromDate(), article_filename)
    article_dict = article_codec.decode(article_path)
    article_title.insert(0, article_dict["title"])
    if "lead" in article_dict:
        article_lead.insert(1.0, article_dict["lead"])
    article_content.insert(1.0, article_dict["content"])


def move_up():
    global pageflow
    sel = article_listbox.curselection()
    if not sel:
        return
    pageflow.move_up(sel)
    refresh_article_ui()
    newSel = [i - 1 for i in sel]
    article_listbox.selection_set(min(newSel), max(newSel))


def move_down():
    global pageflow
    sel = article_listbox.curselection()
    if not sel:
        return
    pageflow.move_dn(sel)
    refresh_article_ui()
    newSel = [i + 1 for i in sel]
    article_listbox.selection_set(min(newSel), max(newSel))


def generate_pdf():
    folder = getFolderFromDate()
    for filename in ("template.tex", "impressum.tex"):
        src_template = os.path.join("template", filename)
        tgt_template = os.path.join(folder, filename)
        shutil.copy(src_template, tgt_template)
    subprocess.run(["pdflatex", "/template.tex"], cwd=folder)


def generate_today():
    folder = getFolderFromDate()
    outfolder = folder
    os.makedirs(outfolder, exist_ok=True)
    today_path = os.path.join(outfolder, "today.tex")

    with open(today_path, "w", encoding="utf-8") as f:
        # Nr. Datum
        date_time = date_entry.get_date()
        f.writelines(
            [f"Nr. {nr_entry.get()} vom " + date_time.strftime("%d. %b. %Y"), "\\vspace{1ex}\n", "\\sectionline\n"])
        # Artikel
        selected_indices = article_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Fehler", "Bitte mindestens einen Artikel auswählen.")
            return
        elements = pageflow.elements()
        for i in selected_indices:
            ele = elements[i]
            if type(ele) == Article:
                f.write("\\input{" + ele.filename + "}\n")
            elif type(ele) == CategoryMarker:
                f.write("\\section*{" + ele.ident() + "}\n")
        # Wetter
        weather_file = os.path.join(folder, "wetter.tex")
        if os.path.isfile(weather_file):
            f.write("\n% Wetter\n")
            f.write("\\input{wetter.tex}\n")
    generate_pdf()
    os.system(os.path.join(folder, "template.pdf"))


previous_selection = set()


def article_selected():
    global previous_selection
    selected_items = set(article_listbox.curselection())
    new_selection = selected_items - previous_selection
    if len(new_selection) > 0:

        selection = new_selection.pop()
        element = pageflow.elements()[selection]
        if type(element) == Article:
            populate_form(element.filename)
    previous_selection = selected_items


# --- GUI Setup ---
root = tk.Tk()
root.title("Zeitungs-Generator mit Wetter & Datum")

# Datumsauswahl
date_frame = tk.Frame(root)
date_frame.pack(padx=10, pady=5)
tk.Label(date_frame, text="Nr.:").pack(side="left")
nr_entry = tk.Entry(date_frame)
nr_entry.pack(side="left")
tk.Label(date_frame, text="Datum:").pack(side="left")
date_entry = DateEntry(date_frame, date_pattern="dd.mm.yyyy")
date_entry.set_date(datetime.now())
date_entry.pack(side="left")
date_entry.bind("<<DateEntrySelected>>", lambda d: refresh_articles())

# Artikelbereich
artf = tk.LabelFrame(root, text="Artikel", padx=5, pady=5)
artf.pack(fill="both", expand=True, padx=10, pady=5)
tk.Label(artf, text="Titel:").pack(anchor="w")
article_title = tk.Entry(artf, width=80)
article_title.pack(fill="x", padx=5, pady=2)
tk.Label(artf, text="Lead:").pack(anchor="w")
article_lead = tk.Text(artf, height=3)
article_lead.pack(fill="x", padx=5, pady=2)
tk.Label(artf, text="Inhalt:").pack(anchor="w")
article_content = tk.Text(artf, height=6)
article_content.pack(fill="x", padx=5, pady=2)
tk.Label(artf, text="URL (optional):").pack(anchor="w")
article_url = tk.Entry(artf, width=80)
article_url.pack(fill="x", padx=5, pady=2)
tk.Label(artf, text="Image-URL (optional):").pack(anchor="w")
image_url_entry = tk.Entry(artf, width=80)
image_url_entry.pack(fill="x", padx=5, pady=2)
tk.Button(artf, text="Artikel speichern", command=save_article).pack(pady=5, side="left")
tk.Button(artf, text="Felder löschen", command=felder_loeschen).pack(pady=5)

rf = tk.LabelFrame(root, text="Rubrik", padx=5, pady=5)
rf.pack(fill="x", expand=True, padx=10, pady=5)
combobox = ttk.Combobox(rf)
combobox.pack(side="left", pady=5)
combobox["values"] = ["Meldungen", "Meinungen"]
tk.Button(rf, text="Rubrik einfügen", command=add_category).pack(pady=5)

# Wetterbereich
wf = tk.LabelFrame(root, text="Wetter (wird automatisch geladen)", padx=5, pady=5)
wf.pack(fill="x", expand=True, padx=10, pady=5)
tk.Button(wf, text="Wetter für Datum speichern", command=save_weather_block).pack()

# Auswahl und Reihenfolge der Artikel
self = tk.LabelFrame(root, text="Artikel für Tagesausgabe", padx=5, pady=5)
self.pack(fill="both", expand=True, padx=10, pady=5)
article_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=60, height=8)
article_listbox.pack(side="left", fill="both", expand=True)
article_listbox.bind("<<ListboxSelect>>", lambda e: article_selected())
btnf = tk.Frame(self)
btnf.pack(side="right", fill="y")
tk.Button(btnf, text="↑", command=move_up).pack(fill="x")
tk.Button(btnf, text="↓", command=move_down).pack(fill="x")
tk.Button(btnf, text="Tagesausgabe erzeugen", command=generate_today).pack(pady=10)

# Beim Start vorhandene Artikel laden
refresh_articles()

print(getFolderFromDate())

root.mainloop()

import shutil
import subprocess
import tkinter as tk
import urllib.parse
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

import config
import myrequests
from tkcalendar import DateEntry
import locale
from urllib.parse import urlparse
from ftplib import FTP_TLS
from PIL import Image

import jotform
import pdf_today
from feed import load_rss

# --- Konstanten / Konfiguration ---
import article_codec
import article_saveload
import online_article
import shortify
from article_codec import articleFilenameFromTitle
from pageflow import *
import wetterdaten
from pdf_today import PdfToday

pageflow = PageFlow()

QUELLENARTEN = {"quelle": "Quelle",
                "weiterlesen": "Weiterlesen bei"}

def getExistingFolderFromDate():
    """ gibt den Ordner zum Datum zurück, erstellt ihn, falls nötig"""
    date_time = date_entry.get_date()
    folder = date_time.strftime("%y%m_%d")
    os.makedirs(folder, exist_ok=True)
    return folder


def download_image(url):
    image = myrequests.get(url)
    image_name = url.split('/')[-1]
    image_name_unquoted = urllib.parse.unquote(image_name)
    image_path = os.path.join(getExistingFolderFromDate(), image_name_unquoted)
    with open(image_path, 'wb') as f:
        for chunk in image.iter_content():
            f.write(chunk)
    return image_name_unquoted


def shrink_image(filename: str)-> str:
    MAXWIDTH = 500
    image_path = os.path.join(getExistingFolderFromDate(), filename)
    img = Image.open(image_path)
    if img.width > MAXWIDTH:
        scale = MAXWIDTH / img.width
        img = img.resize((MAXWIDTH, int(img.height * scale)))
        filename_parts = filename.split('.')
        new_filename = "".join(filename_parts[:-1]) + "k." + filename_parts[-1]
        img.save(os.path.join(getExistingFolderFromDate(), new_filename))
        return new_filename
    return filename

# --- GUI-Funktionen ---


def save_article():
    title = article_title.get().strip()
    lead = article_lead.get("1.0", "end").strip()
    content = article_content.get("1.0", "end").strip()
    url = article_url.get().strip()
    if len(url) > 1 and not url.startswith(shortify.base_url):
        url = shortify.create_shortlink_or_get_from_db(url, title)
    image_url = image_url_entry.get().strip()
    quelle = quelle_entry.get().strip()
    image_filename = None
    quellenArt = comboQuellArt.get()

    if not title:
        messagebox.showwarning("Fehler", "Titel ist erforderlich")
        return
    if not quelle:
        messagebox.showwarning("Warnung", "Quellenangabe fehlt")
    if quellenArt == QUELLENARTEN['weiterlesen'] and not url:
        messagebox.showwarning("Fehler", "Link zum Weiterlesen fehlt")
        return
    if image_url:
        if urlparse(image_url).scheme in ['http', 'https']:
            image_filename = download_image(image_url)
        else:
            image_filename = image_url
        image_filename = shrink_image(image_filename)

    # Dateiname sicher machen
    folder = getExistingFolderFromDate()
    fname = articleFilenameFromTitle(title)
    article_filename = os.path.join(folder, fname)
    article_dict = {"title": title, "lead": lead, "image": image_filename, "content": content, "url": url, "quelle": quelle, "quellenArt": quellenArt}
    article_saveload.article_save(article_filename + ".json", article_dict)
    article_codec.encode(article_filename, article_dict)
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
    article_url.delete(0, "end")
    image_url_entry.delete(0, "end")
    quelle_entry.delete(0, "end")


def save_weather_block():
    folder = getExistingFolderFromDate()
    date = date_entry.get_date()

    # hole Wetter für heute und morgen
    weather = wetterdaten.get_data_for_day(date)

    weather_filename = os.path.join(folder, "wetter.tex")
    with open(weather_filename, "w", encoding="utf-8") as f:
        f.write(f"\\section{{Wetter}}\n")
        for day in weather:
            d = weather[day]
            f.write(f"\\textbf{{{day}}} {d['id_symbol']}, min. {d['id_temp_min']}°C, max. {d['id_temp_max']}°C, Niederschlag {d['id_niederschlag']}mm\\\\ \n")
        f.write(f" (Quelle: MeteoSchweiz)\n")
    messagebox.showinfo("Wetter gespeichert", weather_filename)
    refresh_articles()

def save_agenda_block():
    folder = getExistingFolderFromDate()
    date = date_entry.get_date()

    # fetch data
    agenda_text = jotform.download_and_generate_text(date)
    agenda_filename = os.path.join(folder, "a_agenda.tex")  # a_: als Artikel im Pageflow behandeln
    with open(agenda_filename, "w", encoding="utf-8") as f:
        # encode as article
        f.write(f"\\section{{Agenda}}\n")
        f.write(agenda_text)
        f.write(f"\n\n Event erfassen auf: https://gbsn.ch/agenda\n")
    messagebox.showinfo("Agenda gespeichert.", agenda_filename)
    pageflow.add(Article(agenda_filename))
    refresh_articles()

def refresh_article_ui():
    article_listbox.delete(0, tk.END)
    for elem in pageflow.elements():
        identifier = elem.ident()
        article_listbox.insert(tk.END, identifier)


def refresh_articles():
    pageflow.refreshArticles(getExistingFolderFromDate())
    refresh_article_ui()


def populate_form_from_dict(article_dict: dict):
    felder_loeschen()
    article_title.insert(0, article_dict["title"])
    if "lead" in article_dict:
        article_lead.insert(1.0, article_dict["lead"])
    article_content.insert(1.0, article_dict["content"])
    if "image" in article_dict and article_dict["image"]:
        image_url_entry.insert(0, article_dict["image"])
    if "url" in article_dict:
        article_url.insert(0, article_dict["url"])
    if "quelle" in article_dict:
        quelle_entry.insert(0, article_dict["quelle"])


def populate_form(article_filename):
    article_path = os.path.join(getExistingFolderFromDate(), article_filename)
    article_dict = article_saveload.article_load(f"{article_path}.json")
    populate_form_from_dict(article_dict)


def fetch_crossTeaser():
    url = article_url.get().strip()
    article_data = online_article.fetch_crossteaser_data(url)
    for k in article_data:
        print(k, article_data[k])
    # Map to my fields
    article_data["content"] = article_data["description"]
    article_data["quelle"] = article_data["site_name"]
    link = shortify.create_shortlink_or_get_from_db(article_data["url"], article_data["title"])
    article_data["url"] = link
    if "image" in article_data:
        del(article_data["image"])  # um nicht gegen Copyright zu verstossen
    populate_form_from_dict(article_data)
    comboQuellArt.set(QUELLENARTEN['weiterlesen'])

def copy_online_article():
    url = article_url.get().strip()
    article_data = online_article.copy_online_article(url)
    populate_form_from_dict(article_data)
    comboQuellArt.set(QUELLENARTEN['quelle'])
    pass

def move_up():
    sel = article_listbox.curselection()
    if not sel:
        return
    pageflow.move_up(sel)
    refresh_article_ui()
    newSel = [i - 1 for i in sel]
    article_listbox.selection_set(min(newSel), max(newSel))


def move_down():
    sel = article_listbox.curselection()
    if not sel:
        return
    pageflow.move_dn(sel)
    refresh_article_ui()
    newSel = [i + 1 for i in sel]
    article_listbox.selection_set(min(newSel), max(newSel))

pdf_ausgabe: PdfToday = None

def generate_today():
    global pdf_ausgabe
    pdf_ausgabe = PdfToday(getExistingFolderFromDate(), date_entry.get_date(), nr_entry.get())
    selected_indices = article_listbox.curselection()
    if not selected_indices:
        selected_indices = range(article_listbox.size())
    pdf_ausgabe.generate_today(pageflow, selected_indices)


def upload_today():
    ftp = FTP_TLS(config.ftp_host)
    ftp.login(user=config.ftp_user, passwd=config.ftp_pw)
    # IMPORTANT: secure both control & data channels
    ftp.prot_p()

    with open(pdf_ausgabe.pdf_path, "rb") as file:
        ftp.storbinary(f"STOR {pdf_ausgabe.pdf_filename}", file)

    ftp.quit()
    print(f"Updloaded file {pdf_ausgabe.pdf_path}")


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


rss_articles: list[dict] = []

def load_rss_clicked():
    global rss_articles
    rss_articles = load_rss(rss_url_entry.get())
    rss_listbox.delete(0, tk.END)
    for a in rss_articles:
        rss_listbox.insert(tk.END, a["title"])


def import_rss_article():
    sel: list[int] = rss_listbox.curselection()
    if not sel:
        return

    x: int = sel[0]
    article: dict = rss_articles[x]

    populate_form_from_dict(article)
    comboQuellArt.set(QUELLENARTEN['quelle'])


locale.setlocale(locale.LC_TIME, "de_CH.UTF-8")

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
date_entry.set_date(datetime.now() + timedelta(hours=12))
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

# Quellen / Links / Weiterlesen
quellFrame = tk.Frame(artf)
quellFrame.pack(fill="x")
tk.Label(quellFrame, text="Quelle / URL:").pack(anchor="w")
quelle_entry = tk.Entry(quellFrame)
quelle_entry.pack(side="left", fill="x", expand=True, padx=5, pady=2)
comboQuellArt = ttk.Combobox(quellFrame, state="readonly", values=list(QUELLENARTEN.values()))
comboQuellArt.set("Quelle")
comboQuellArt.pack(side="right", padx=5, pady=5)

tk.Button(artf, text="Artikel speichern", command=save_article).pack(pady=5, side="left")
tk.Button(artf, text="Fetch cross teaser", command=fetch_crossTeaser).pack(pady=5, side="left")
tk.Button(artf, text="Copy online article", command=copy_online_article).pack(pady=5, side="left")
tk.Button(artf, text="Felder löschen", command=felder_loeschen).pack(pady=5)

l2rFrame = tk.Frame(root)
l2rFrame.pack()
rf = tk.LabelFrame(l2rFrame, text="Rubrik", padx=5, pady=5)
rf.pack(side="left", padx=10, pady=5)
combobox = ttk.Combobox(rf)
combobox.pack(side="left", pady=5)
combobox["values"] = ["Meldungen", "Meinungen"]
tk.Button(rf, text="Rubrik einfügen", command=add_category).pack(pady=5)

# Wetterbereich
wf = tk.LabelFrame(l2rFrame, text="Wetter (wird automatisch geladen)", padx=5, pady=5)
wf.pack(side="left", padx=10, pady=5)
tk.Button(wf, text="Wetter für Datum speichern", command=save_weather_block).pack()

# Agenda
af = tk.LabelFrame(l2rFrame, text="Agenda", padx=5, pady=5)
af.pack(side="left", padx=10, pady=5)
tk.Button(af, text="Agenda erstellen", command=save_agenda_block).pack()

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
tk.Button(btnf, text="Tagesausgabe hochladen", command=upload_today).pack(pady=10)

# RSS Feed
rss_frame = tk.LabelFrame(root, text="RSS-Feeds", padx=5, pady=5)
rss_frame.pack(fill="both", padx=10, pady=5)

rss_url_entry = tk.Entry(rss_frame, width=60)
rss_url_entry.insert(0, "https://www.sg.ch/sicherheit/kantonspolizei/_jcr_content/NewsPar.RssFeed.qualident__item0.rdf")
rss_url_entry.pack(side="left", padx=5)

tk.Button(rss_frame, text="RSS laden", command=load_rss_clicked).pack(side="left")

rss_listbox = tk.Listbox(root, height=8, width=90)
rss_listbox.pack(fill="x", padx=10, pady=5)

tk.Button(root, text="Artikel übernehmen", command=import_rss_article).pack(pady=5)

# Beim Start vorhandene Artikel laden
refresh_articles()

root.mainloop()

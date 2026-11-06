import os
if not os.getenv("GITHUB_ACTIONS"):
    import qrcode


def _encode_special_chars(text: str):
    text = text.replace("%", "\\%")
    text = text.replace("&", "\\&")
    text = text.replace("_", "\\_")
    text = _replace_unwanted_unicode_characters(text)
    return text


def _replace_unwanted_unicode_characters(text: str) -> str:
    text = text.replace("\u2005", " ")  # spezielles Leerzeichen Four-Per-Em Space (verwendet auf admin.ch für Zahlen: 10 000)
    text = text.replace("\u0080", "")  # Lückenfüller-Zeichen. gesehen auf sg.ch; https://www.sg.ch/news/sgch_kantonspolizei/2025/12/wald-schoenengrund--verkehrsunfall-zwischen-bagger-und-auto---au.html
    text = text.replace("\u200B", "")  # Zero Width Space (ZWSP). Kommt oft vor bei Stadtpolizei St.Gallen
    return text


def encode(filepath, article: dict, f):
    for part in article:
        if article[part]:
            article[part] = _encode_special_chars(article[part])
    if 'title' in article and article['title']:  # nicht vorh. in Agenda
        f.write(f"\\subsection*{{{article['title']}}}\n")
    if article.get('infobox'):
        f.write("\\begin{infobox}\n")
        f.write(f"{article['infobox']}\n")
        f.write("\\end{infobox}\n")
    if article.get('lead'):
        f.write(f"\\textbf{{{article['lead']}}}\n\n")
    if "image" in article and article["image"]:
        f.write(f"\\begin{{minipage}}{{\\columnwidth}}\n\\includegraphics[width =\\columnwidth]{{{article['image']}}}\n\\end{{minipage}}\n\n")
    f.write(article['content'] + "\n")
    if article.get('quelle'):
        if 'url' in article and article['url']:
            qr_path = f"{filepath}_qr.png"
            href_begin = f"\\href{{https://{article['url']}}}{{"
            # QR-Code erzeugen TODO auslagern aus codec
            if not os.getenv("GITHUB_ACTIONS"):
                qr = qrcode.make(article['url'], border=0)
                qr.save(qr_path)
            # QR in Tex einbinden
            f.write("\\begin{flushright}\n")
            f.write(f"{href_begin}\\includegraphics[width=0.9cm]{{")
            f.write(f"{os.path.basename(qr_path)}")
            f.write("}}\n")  # href_end
            f.write("\\end{flushright}")
            f.write("\\vspace{-1.2cm}\n")
            f.write("\n")
        else:
            href_begin = "{"  # ohne Link
        f.write(f"{article['quellenArt']}:")
        if 'url' in article and article['url']:
            f.write("\\\\")  # wenn QR vorhanden, nutzen wir 2 Zeilen
        else:
            f.write(" ")
        f.write(f"\n{href_begin}{article['quelle']}")
        f.write("}\n")  # href_end
        f.write("\\\\\n\n")  # neue Zeile \\ und neue Zeilen im Quellcode \n


def articleFilenameFromTitle(titlefull: str) -> str:
    title = titlefull[:9]
    title = _replace_unwanted_unicode_characters(title)
    title = title.replace('"', '_')
    title = title.replace('[', '_')
    title = title.replace(']', '_')
    title = title.replace('<', '_')
    title = title.replace('>', '_')
    title = title.replace(':', '_')
    title = title.replace('/', '_')
    title = title.replace('\\', '_')
    title = title.replace('|', '_')
    title = title.replace('?', '_')
    title = title.replace('*', '_')
    return f"a_{title.replace(' ', '_')}{len(titlefull)-10}.tex"

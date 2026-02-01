import os
import re
if not os.getenv("GITHUB_ACTIONS"):
    import qrcode


def _encode_special_chars(text: str):
    text = text.replace("%", "\\%")
    text = text.replace("&", "\\&")
    text = text.replace("\u2005", " ")  # spezielles Leerzeichen Four-Per-Em Space (verwendet auf admin.ch für Zahlen: 10 000)
    text = text.replace("\u0080", "")  # Lückenfüller-Zeichen. gesehen auf sg.ch; https://www.sg.ch/news/sgch_kantonspolizei/2025/12/wald-schoenengrund--verkehrsunfall-zwischen-bagger-und-auto---au.html
    return text


def encode(filepath, article: dict):
    for part in article:
        if article[part]:
            article[part] = _encode_special_chars(article[part])
    with open(filepath, "w", encoding="utf-8") as f:
        if 'title' in article and article['title']:  # nicht vorh. in Agenda
            f.write(f"\\subsection*{{{article['title']}}}\n")
        if article.get('lead'):
            f.write(f"\\textbf{{{article['lead']}}}\n\n")
        if "image" in article and article["image"]:
            f.write(f"\\begin{{minipage}}{{\\columnwidth}}\n\\includegraphics[width =\\columnwidth]{{{article['image']}}}\n\\end{{minipage}}\n\n")
        f.write(article['content'] + "\n")
        if article.get('quelle'):
            if article['url']:
                qr_path = f"{filepath}_qr.png"
                href_begin = f"\\href{{https://{article['url']}}}{{"
                # QR-Code erzeugen TODO auslagern aus codec
                if not os.getenv("GITHUB_ACTIONS"):
                    qr = qrcode.make(article['url'], border=0)
                    qr.save(qr_path)
                # In Tex einbinden
                f.write("\\begin{wrapfigure}{r}{0.9cm}\n")
                f.write("\\vspace{-0.3cm}\n")
                f.write(f"{href_begin}\\includegraphics[width=0.9cm]{{")
                f.write(f"{os.path.basename(qr_path)}")
                f.write("}}\n")  # href_end
                f.write("\\end{wrapfigure}")
                f.write("\\vspace{-0.4cm}\n")
                f.write("\n")
            else:
                href_begin = "{"  # ohne Link
            f.write("{\\raggedright\n")
            f.write(f"{article['quellenArt']}:")
            if article['url']:
                f.write("\\\\")  # wenn QR vorhanden, nutzen wir 2 Zeilen
            else:
                f.write(" ")
            f.write(f"\n{href_begin}{article['quelle']}")
            f.write("}\n")  # href_end
            f.write("}\\\\\n\n")  # raggedright schliessen, neue Zeile \\ und neue Zeilen im Quellcode \n


def articleFilenameFromTitle(titlefull: str) -> str:
    title = titlefull[:9]
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

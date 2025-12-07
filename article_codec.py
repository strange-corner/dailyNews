import os
import re
if not os.getenv("GITHUB_ACTIONS"):
    import qrcode


def _encode_special_chars(text: str):
    return text.replace("%", "\\%")


def encode(filepath, article: dict):
    for part in article:
        if article[part]:
            article[part] = _encode_special_chars(article[part])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"\\subsection*{{{article['title']}}}\n")
        if article['lead']:
            f.write(f"\\textbf{{{article['lead']}}}\n\n")
        if "image" in article and article["image"]:
            f.write(f"\\begin{{minipage}}{{\\columnwidth}}\n\\includegraphics[width =\\columnwidth]{{{article['image']}}}\n\\end{{minipage}}\n\n")
        f.write(article['content'] + "\n")
        if article['url']:
            qr_path = f"{filepath}_qr.png"
            # QR-Code erzeugen TODO auslagern aus codec
            if not os.getenv("GITHUB_ACTIONS"):
                qr = qrcode.make(article['url'])
                qr.save(qr_path)
            # In Tex einbinden
            f.write("\\begin{wrapfigure}[2]{r}{0.9cm}\n")
            f.write("\\vspace{-0.5cm}\n")
            f.write(f"\\href{{https://{article['url']}}}")
            f.write("{\\includegraphics[width=1cm]{")
            f.write(f"{os.path.basename(qr_path)}")
            f.write("}}\n")
            f.write("\\end{wrapfigure}")
            f.write("\n\n")
            f.write("Weiterlesen bei: \n")
            f.write(f"{article['quelle']}")
            f.write("\n")
        else:
            f.write(f"({article['quelle']})")
        f.write("\n")


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

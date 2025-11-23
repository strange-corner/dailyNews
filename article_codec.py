import qrcode
import os
import re

def encode(filepath, article: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"\\subsection*{{{article['title']}}}\n")
        if article['lead']:
            f.write(f"\\textbf{{{article['lead']}}}\n\n")
        f.write(article['content'] + "\n")
        if article['url']:
            # QR-Code erzeugen
            qr = qrcode.make(article['url'])
            qr_path = f"{filepath}_qr.png"
            qr.save(qr_path)
            # In Tex einbinden
            f.write(
                f"\n\\begin{{center}}\\includegraphics[width=3cm]{{{os.path.basename(qr_path)}}}\\\\\nmehr…\\end{{center}}\n")

def decode(filepath: str) -> dict:
    result = dict()
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        line = 0
        title_match = re.match(r"\\subsection\*\{(.*)\}", lines[line])
        line += 1
        if title_match:
            result["title"] = title_match.group(1)
        lead_match = re.match(r"\\textbf\{(.*)\}", lines[line])
        if lead_match:
            result["lead"] = lead_match.group(1)
            line += 2
        result["content"] = lines[line]

    return result
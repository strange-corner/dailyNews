import qrcode
import os
import re


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
        f.write(article['content'] + "\n")
        if article['url']:
            # QR-Code erzeugen
            qr = qrcode.make(article['url'])
            qr_path = f"{filepath}_qr.png"
            qr.save(qr_path)
            # In Tex einbinden
            f.write("\\begin{wrapfigure}[2]{r}{0.9cm}\n")
            f.write("\\vspace{-0.5cm}\n")
            f.write("\\includegraphics[width=1cm]{")
            f.write(f"{os.path.basename(qr_path)}")
            f.write("}\n")
            f.write("\\end{wrapfigure}")
            f.write("\n\n")
            f.write("Weiterlesen bei: \n")
            f.write(f"{article['quelle']}")
            f.write("\n\n")
        if article["image"]:
            f.write(f"\\begin{{minipage}}{{\\columnwidth}}\n\\includegraphics[width =\\columnwidth]{{{article['image']}}}\n\\end{{minipage}}\n")


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
        line += 2
        if line < len(lines):
            image_match = re.match(r"\\includegraphics[width =\\columnwidth]\{(.*)\}", lines[line])
            if image_match:
                result["image"] = image_match.group(1)
                line += 7
        while not re.match(r"Weiterlesen bei: ", lines[line]):
            line += 1
        line += 1
        result['quelle'] = lines[line]
    return result


import unittest


class Test(unittest.TestCase):

    def test_char_replace(self):
        teststr = "Wir brauchen 5 % mehr"

        _encode_special_chars(teststr)

        self.assertEqual("Wir brauchen 5 \\% mehr", _encode_special_chars(teststr))

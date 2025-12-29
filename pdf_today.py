import os
import shutil
import subprocess
from datetime import datetime
from tkinter import messagebox

from pageflow import PageFlow, Article, CategoryMarker


class PdfToday(object):
    """ Repräsentiert eine PDF-Tagesasgabe"""

    def __init__(self, day_folder: str, datum: datetime, nr: str):
        """
        :param day_folder: Datums-Monats-Ordner in der Form 2512. Muss existieren
        :param nr: Ausgabe-Nr
        """
        self.day_folder = day_folder
        self.nr = nr
        self.datum = datum
        self.pdf_path = None
        self.pdf_filename = None


    def generate_pdf(self, outname: str):
        for filename in ("template.tex", "impressum.tex"):
            src_template = os.path.join("template", filename)
            tgt_template = os.path.join(self.day_folder, filename)
            shutil.copy(src_template, tgt_template)
        subprocess.run(["pdflatex", f"-jobname={outname}", "template.tex"], cwd=self.day_folder)


    def generate_today(self, pageflow: PageFlow, selected_indices: list):
        today_path = os.path.join(self.day_folder, "today.tex")

        with open(today_path, "w", encoding="utf-8") as f:
            # Nr. Datum
            if self.nr == "":
                messagebox.showwarning("Fehler", "Bitte Nr eingeben .")
                return

            f.writelines(
                [f"Nr. {self.nr} vom " + self.datum.strftime("%a %#d. %B %Y KW") + str(self.datum.isocalendar()[1]),
                 "\\vspace{1ex}\n", "\\sectionline\n"])
            # Wetter
            if os.path.isfile(os.path.join(self.day_folder, "wetter.tex")):
                f.write("\\input{wetter.tex}\n")
            # Artikel
            elements = pageflow.elements()
            for i in selected_indices:
                ele = elements[i]
                if type(ele) == Article:
                    f.write("\\input{" + ele.filename + "}\n")
                elif type(ele) == CategoryMarker:
                    f.write("\\section*{" + ele.ident() + "}\n")
        ausgabe_name = f"Guebsensee_Journal_{self.day_folder}_Nr{self.nr}"
        self.generate_pdf(ausgabe_name)
        self.pdf_filename = f"{ausgabe_name}.pdf"
        ## PDF zur Anzeige aufrufen:
        self.pdf_path = os.path.join(self.day_folder, self.pdf_filename)
        os.system(self.pdf_path)

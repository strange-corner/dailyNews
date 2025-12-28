import os
import shutil
import subprocess
from datetime import datetime
from tkinter import messagebox

from pageflow import PageFlow, Article, CategoryMarker


class PdfToday(object):
    """ Repräsentiert eine PDF-Tagesasgabe"""

    def __init__(self, month_folder: str, datum: datetime, nr: str):
        """
        :param month_folder: Datums-Monats-Ordner in der Form 2512. Muss existieren
        :param nr: Ausgabe-Nr
        """
        self.month_folder = month_folder
        self.nr = nr
        self.datum = datum


    def generate_pdf(self, outname: str):
        for filename in ("template.tex", "impressum.tex"):
            src_template = os.path.join("template", filename)
            tgt_template = os.path.join(self.month_folder, filename)
            shutil.copy(src_template, tgt_template)
        subprocess.run(["pdflatex", f"-jobname={outname}", "template.tex"], cwd=self.month_folder)


    def generate_today(self, pageflow: PageFlow, selected_indices: list):
        today_path = os.path.join(self.month_folder, "today.tex")

        with open(today_path, "w", encoding="utf-8") as f:
            # Nr. Datum
            if self.nr == "":
                messagebox.showwarning("Fehler", "Bitte Nr eingeben .")
                return

            f.writelines(
                [f"Nr. {self.nr} vom " + self.datum.strftime("%a %#d. %B %Y KW") + str(self.datum.isocalendar()[1]),
                 "\\vspace{1ex}\n", "\\sectionline\n"])
            # Wetter
            if os.path.isfile(os.path.join(self.month_folder, "wetter.tex")):
                f.write("\\input{wetter.tex}\n")
            # Artikel
            elements = pageflow.elements()
            for i in selected_indices:
                ele = elements[i]
                if type(ele) == Article:
                    f.write("\\input{" + ele.filename + "}\n")
                elif type(ele) == CategoryMarker:
                    f.write("\\section*{" + ele.ident() + "}\n")
        ausgabe_name = f"Guebsensee_Nachrichten_{self.month_folder}_Nr{self.nr}"
        self.generate_pdf(ausgabe_name)
        ## PDF zur Anzeige aufrufen:
        os.system(os.path.join(self.month_folder, f"{ausgabe_name}.pdf"))

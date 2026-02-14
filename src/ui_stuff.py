import tkinter as tk
from tkinter import ttk

callbackmethod = None

def open_infobox_popup(root, insert_infobox_into_article):
    popup = tk.Toplevel(root)
    popup.title("Infobox bearbeiten")
    popup.geometry("500x300")
    popup.grab_set()  # modal

    tk.Label(popup, text="Inhalt der Infobox:").pack(anchor="w", padx=10, pady=5)

    text_widget = tk.Text(popup, wrap="word")

    def save_infobox():
        content = text_widget.get("1.0", "end-1c")
        insert_infobox_into_article(content)
        popup.destroy()

    ttk.Button(popup, text="Übernehmen", command=save_infobox).pack(pady=10)
    text_widget.pack(fill="both", expand=True, padx=10, pady=5)

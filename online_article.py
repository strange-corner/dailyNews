import requests
from bs4 import BeautifulSoup


def fetch_crossteaser_data(url: str) -> dict:
    headers = {"User-Agent": "GuebsenseeNachrichten/1.0 (info@gbsn.ch)"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    og_data = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            og_data[prop[3:]] = tag.get("content", "")

    # Änderungswünsche der Urheber
    if 'site_name' in og_data and og_data['site_name'] == "Schweizerzeit Verlags AG":
        og_data['site_name'] = "www.schweizerzeit.ch"

    return og_data

def copy_online_article(url: str) -> dict:
    article_data = dict()
    headers = {"User-Agent": "GuebsenseeNachrichten/1.0 (info@gbsn.ch)"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    article_data['title'] = soup.title.string

    # --- Datum / Vorspann — nehmen wir als den ersten <p>-Absatz nach Titel ---
    first_paragraph = None
    content_paragraphs = []

    # Suche nach allen <p> Tags im Artikelbereich
    all_p = soup.find_all("p")
    if all_p:
        # Der erste Paragraph (nach Titel/Datum) ist typischerweise der Vorspann
        first_paragraph = all_p[0].get_text(strip=True)

        # Alle weiteren Absätze als „Inhalt“
        for p in all_p[1:]:
            text = p.get_text(strip=True)
            if text:
                content_paragraphs.append(text)


    article_data['lead'] = first_paragraph
    article_data['content'] = content_paragraphs
    article_data['quelle'] = "News Service Bund"
    article_data['url'] = url
    return article_data

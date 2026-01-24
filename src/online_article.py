import myrequests
from bs4 import BeautifulSoup


def fetch_crossteaser_data(url: str) -> dict:
    r = myrequests.get(url)
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
    r = myrequests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    article_data = article_from_soup_admin_ch(soup)
    article_data['quelle'] = "News Service Bund"
    article_data['url'] = url
    return article_data


def article_from_soup_admin_ch(soup):
    article_dict = dict()
    lead_section = soup.find("section", identifier="lead-contentpage")
    article_dict['title'] = lead_section.h1.string
    article_dict['lead'] = lead_section.find_all("p")[1].get_text(strip=True)
    content_section = soup.find("section", identifier="section")
    soup = None  # nur noch main_div verwenden

    all_p = content_section.find_all(["p", "h2", "div"])

    # Der zweite Paragraph (nach Titel/Datum) ist typischerweise der Vorspann
    article_dict['content'] = ""
    # Erfahrungsgemäss ist das Bild des Artikels, das erste in der lead_section:
    images = lead_section.find_all(["img"])
    if len(images) >= 1:
        article_dict['image'] = images[0].get("src")
    else:
        # sonst schauen wir noch in der content_section
        images = content_section.find_all(["img"])
        if len(images) >= 1:
            article_dict['image'] = images[0].get("src")
    for p in all_p[2:]:
        if p.name == "h2" and p.get_text(strip=True) == "":
            # nach dem interessanten Inhalt folgt erfahrungsgemäss ein leerer h2
            break
        if p.name == "h2":
            article_dict['content'] += "\\textbf{" + p.get_text(strip=True) + "}\n\n"
        elif p.name == "p":
            article_dict['content'] += p.get_text(strip=True) + "\n\n"
        elif p.name == "div":
            # Erfahrungsgemäss gibt es Tabellenähnliche Angaben in verschachtelten div.
            cascaded_div = p.find("div")
            if cascaded_div:
                for st in cascaded_div.strings:
                    article_dict['content'] += st + "\n"
                article_dict['content'] += "\n"
    return article_dict

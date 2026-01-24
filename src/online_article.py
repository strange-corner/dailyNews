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
    article_dict['title'] = soup.h1.string
    all_p = soup.find_all(["p", "h2"])

    # Der zweite Paragraph (nach Titel/Datum) ist typischerweise der Vorspann
    article_dict['lead'] = all_p[1].get_text(strip=True)
    article_dict['content'] = ""
    for p in all_p[2:]:
        if p.name == "h2" and p.get_text(strip=True) == "":
            # nach dem interessanten Inhalt folgt erfahrungsgemäss ein leerer h2
            break
        if p.name == "h2":
            article_dict['content'] += "\\textbf{" + p.get_text(strip=True) + "}\n\n"
        elif p.name == "p":
            article_dict['content'] += p.get_text(strip=True) + "\n\n"
    return article_dict

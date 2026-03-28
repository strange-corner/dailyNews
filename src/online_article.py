from src import myrequests
from bs4 import BeautifulSoup, NavigableString, Tag, ResultSet
from urllib.parse import urlparse

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
    soup = fetch_soup(url)
    return article_from_soup(soup, url)


def article_from_soup(soup: BeautifulSoup, url: str) -> dict[str, str] | dict:
    if url.startswith("https://www.news.admin.ch"):
        article_data = article_from_soup_admin_ch(soup)
        article_data['quelle'] = "News Service Bund"
        article_data['url'] = url
    elif url.startswith("https://www.stadt.sg.ch"):
        article_data = article_from_soup_stadt_sg_ch(soup)
        article_data['quelle'] = urlparse(url).netloc
        article_data['image'] = urlparse(url).scheme + "://" + urlparse(url).netloc + article_data['image']
        if "stadtpolizei" in url:
            article_data['quelle'] = "Stadtpolizei"
    elif url.startswith("https://www.sg.ch"):
        article_data = article_from_soup_sg_ch(soup)
        article_data['quelle'] = "Kanton SG"
    elif url.startswith("https://www.svp.ch"):
        article_data = article_from_soup_svp_ch(soup)
    elif url.startswith("https://ar.ch/verwaltung/departement-inneres-und-sicherheit/kantonspolizei/"):
        article_data = article_from_soup_kapo_ar(soup)
    else:
        article_data = article_dict_from_soup_default(soup)
        article_data['quelle'] = urlparse(url).netloc
        article_data['url'] = url
    return article_data


def article_from_soup_svp_ch(soup: BeautifulSoup) -> dict[str, str]:
    print("article_from_soup_svp_ch")
    article_dict = dict()
    article_dict['title'] = soup.find("h1").text.strip()
    lead_div = soup.find("div", class_="uk-text-large")
    article_dict['lead'] = lead_div.text.strip()
    lead_div.decompose() # we don't want it in content again
    content_soup = soup.find("div", class_="singleContent")
    content_node = content_soup.find_all(["p", "ul"])
    article_dict['content'] = convert_node(content_node)
    img = content_soup.select_one("img")
    if img:
        article_dict['image'] = img["src"]
    article_dict['quelle'] = "SVP Schweiz"
    return article_dict


def convert_node(node) -> str:
    """Recursively convert HTML node to LaTeX."""

    if isinstance(node, ResultSet):
        arr = [convert_node(n) for n in node]
        return ' '.join(arr)

    # Text node
    if isinstance(node, NavigableString):
        return str(node)

    # Tag node
    if isinstance(node, Tag):
        name = node.name.lower()

        # Fett
        if name in ["b", "strong"]:
            content = "".join(convert_node(c) for c in node.children)
            return r"\textbf{" + content + "}"

        # Absatz
        elif name == "p":
            content = "".join(convert_node(c) for c in node.children)
            return content + "\n\n"

        # Unordered list
        elif name == "ul":
            items = "".join(convert_node(c) for c in node.children)
            return "\\begin{itemize}\n" + items + "\\end{itemize}\n"

        # List item
        elif name == "li":
            content = "".join(convert_node(c) for c in node.children)
            return f"  \\item {content}\n"

        # Line break
        elif name == "br":
            return "\\\\\n"

        # Default: einfach Inhalt durchreichen
        else:
            return "".join(convert_node(c) for c in node.children)

    return ""


def fetch_soup(url: str) -> BeautifulSoup:
    r = myrequests.get(url)
    r.encoding = r.apparent_encoding  # ← wichtig!
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


def article_from_soup_sg_ch(soup: BeautifulSoup) -> dict:
    print("article_from_soup_sg_ch")
    article_dict = dict()
    article_dict['title'] = soup.find("h1").text  #find_all("div", class_="page-header").find("h1").get_text(strip=True)
    article_dict['lead'] = soup.find("div", class_="lead-paragraph").text.strip()
    content_parapgraphs = soup.find("div", class_="content-paragraph")
    article_dict['content'] = ""
    for parapgraph in content_parapgraphs.find_all("p"):
        if parapgraph.find_all("b"):
            article_dict['content'] += "\\textbf"
        article_dict['content'] += "{"
        article_dict['content'] += parapgraph.text
        article_dict['content'] += "}\n\n"
    img = soup.select_one(".news-detail-img img")
    if img:
        article_dict['image'] = "https://sg.ch" + img["src"]
        print("Bidlbescheibung: " + img["alt"])
    return article_dict


def article_from_soup_kapo_ar(soup):
    print("article_from_soup_kapo_ar")
    souproot = soup.find("section", id="Content")
    article_dict = dict()
    article_dict['title'] = souproot.find("h2", itemprop="headline").text
    article_dict['lead'] = souproot.find("div", class_="teaser-text").text
    article_dict['content'] = souproot.find("div", class_="news-text-wrap").text
    img = souproot.select_one("img")
    if img:
        article_dict['image'] = "https://ar.ch" + img["src"]
        print("Bidlbescheibung: " + img["alt"])
    article_dict['quelle'] = "Kapo AR"
    return article_dict


def article_from_soup_stadt_sg_ch(soup):
    print("article_from_soup_stadt_sg_ch")
    article_dict = dict()
    article_dict['title'] = soup.select_one("#content h1").get_text(strip=True)
    article_dict['lead'] = soup.find("p", class_="lead-paragraph").text
    article_dict['content'] = soup.find("div", class_="content-paragraph").text
    img = soup.select_one(".news-detail-img img")
    if img:
        article_dict['image'] = img["src"]
    return article_dict

def article_from_soup_admin_ch(soup):
    print("article_from_soup_admin_ch")
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


def article_dict_from_soup_default(soup):
    print("article_dict_from_soup_default")
    article_dict = dict()
    article_dict['title'] = soup.title.string

    # --- Datum / Vorspann — nehmen wir als den ersten <p>-Absatz nach Titel ---
    first_paragraph = None
    content_paragraphs = []

    # Suche nach allen <p> Tags im Artikelbereich
    all_p = soup.find_all(["p", "h2"])
    if all_p:
        first_paragraph = all_p[0].get_text(strip=True)

        # Alle weiteren Absätze als „Inhalt“
        for p in all_p[1:]:
            text = p.get_text(strip=True)
            if text:
                content_paragraphs.append(text + '\n\n')

    article_dict['lead'] = first_paragraph
    article_dict['content'] = content_paragraphs
    return article_dict
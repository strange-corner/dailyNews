import feedparser
from bs4 import BeautifulSoup
import logging

feedparser.USER_AGENT = "GuebsenseeJournal/1.0 (info@gbsn.ch)"


def _parts_from_feed_summary(artikel_html: str):
    soup = BeautifulSoup(artikel_html, "html.parser")

    paragraphs = soup.find_all(["p", "li"])

    if soup.strong:
        lead = soup.strong.string
    elif paragraphs:
        lead = paragraphs[0].text
    else:
        lead = None

    content = ""
    for paragraph in paragraphs[1:]:
        for br in paragraph.find_all("br"):
            br.replace_with("\n\n")
        content += (paragraph.text + '\n\n')

    if soup.img:
        imgsrc = soup.img["src"]
    else:
        imgsrc = None

    return  lead, content, imgsrc


def load_rss(feed_src: dict[str, str]) -> list[dict]:
    """
    :return: List of article dictionaries
    """
    feed = feedparser.parse(feed_src["url"])
    if feed.status != 200:
        logging.error("Status %d when fetching feed from url %s", feed.status, feed_src)
    articles = []
    for entry in feed.entries:
        for key in entry:
            print(key, entry[key])

        entry_title = entry.get("title", "")
        # Im Feed von Kapo SG steht alles in der Summary; kompletter HTML Artikel inkl Bild
        artikel_inhalt_html = entry.get("summary")
        published = entry.get("published")

        # Dies liefert die 3 Teile bei Kapo SG
        lead, content, imgsrc = _parts_from_feed_summary(artikel_inhalt_html)
        # ansonsten (z.B. News Service Bund) übernehmen wir die Teile direkt.
        if lead is None:
            lead = artikel_inhalt_html
            content = entry.get("summary_detail")  # Überlappungen mit lead. Aber hier nur für das UI


        articles.append({
            "title": entry_title,
            "lead": lead,
            "content": content,
            "image": imgsrc,
            "url": entry.get("link"),
            "published": published,
            "quellenArt": "Quelle",
            "quelle" : feed_src["quelle"]
        })
    return articles

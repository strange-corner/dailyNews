import feedparser
from bs4 import BeautifulSoup

feedparser.USER_AGENT = "GuebsenseeNachrichten/1.0 (info@gbsn.ch)"


def parts_from_feed_summary(artikel_html: str):
    soup = BeautifulSoup(artikel_html, "html.parser")

    lead = soup.strong.string

    paragraphs = soup.find_all(["p", "li"])

    content = ""
    for paragraph in paragraphs[1:]:
        content += (paragraph.text + '\n\n')

    return  lead, content, soup.img["src"]


def load_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        for key in entry:
            print(key, entry[key])

        # Im Feed von Kapo SG steht alles in der Summary; kompletter HTML Artikel inkl Bild
        artikel_inhalt_html = entry.get("summary")

        lead, content, imgsrc = parts_from_feed_summary(artikel_inhalt_html)

        articles.append({
            "title": entry.get("title", ""),
            "lead": lead,
            "content": content,
            "image": imgsrc,
            "quelle" : "Kapo SG"  # TODO: falls weitere Feed-Quellen kommen
        })
    return articles

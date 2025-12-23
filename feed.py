import feedparser
from bs4 import BeautifulSoup

feedparser.USER_AGENT = "GuebsenseeNachrichten/1.0 (info@gbsn.ch)"


def load_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        for key in entry:
            print(key, entry[key])

        # Im Feed von Kapo SG steht alles in der Summary; kompletter HTML Artikel inkl Bild
        artikel_inhalt_html = entry.get("summary")
        soup = BeautifulSoup(artikel_inhalt_html, "html.parser")
        paragraphs = soup.find_all("p")

        content = ""
        for paragraph in paragraphs[1:]:
            content += (paragraph.text + '\n')

        articles.append({
            "title": entry.get("title", ""),
            "lead": paragraphs[0].contents,
            "content": content,
            "image": soup.img["src"],
            "quelle" : "Kapo SG"  # TODO: falls weitere Feed-Quellen kommen
        })
    return articles

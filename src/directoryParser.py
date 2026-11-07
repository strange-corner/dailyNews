from bs4 import BeautifulSoup
from datetime import datetime

from src import online_article


def parse_article_directory(html: str) -> list[dict]:
    """ Liefert eine Liste von Artikel-Referenzen aus einer HTML-Seite"""
    soup = BeautifulSoup(html, 'html.parser')
    return _get_list_of_articles_from_soup(soup)

def _get_list_of_articles_from_soup(soup: BeautifulSoup) -> list[dict]:
    news = soup.select_one("div.news")

    articles = []

    for header in news.select("div.header"):
        heading = header.select_one("h3")

        link = heading.select_one("a[href]")

        if link is None:
            continue

        title = link.get_text(" ", strip=True)
        article_url = link["href"]

        published = header.select_one("span.news-list-date").select_one("time")

        articles.append({"title": title, "article_url": article_url, "published": published.get_text(strip=True)})

        print(title)
        print(article_url)

    return articles


def filter_articles_published_after(articles: list[dict], min_published_date: datetime,) -> list[dict]:
    """
    Filtert Artikel und gibt nur jene zurück, deren 'published'-Datum
    NACH dem gegebenen Datum liegt.
    Erwartetes Datumsformat in 'published': 'dd.mm.yyyy', z.B. '06.11.2026'.
    """
    def _parse_published_date(published_str: str) -> datetime:
        return datetime.strptime(published_str, "%d.%m.%Y")

    return [
        article
        for article in articles
        if _parse_published_date(article["published"]) >= min_published_date
    ]


def fetch_content_of_articles(articles: list[dict]) -> list[dict]:
    for article in articles:
        fetched = online_article.copy_online_article(article["article_url"])
        article.update(fetched)
    return articles
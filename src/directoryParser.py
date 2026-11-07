from urllib.parse import urljoin

from bs4 import BeautifulSoup


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
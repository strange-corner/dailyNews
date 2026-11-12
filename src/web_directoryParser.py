import json
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime

import online_article


class BaseArticleDirectoryParser(ABC):
    @abstractmethod
    def _get_list_of_articles_from_soup(self, soup: BeautifulSoup) -> list[dict]:
        """Return a list of article references parsed from the given soup."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> list[dict]:
        return self._get_list_of_articles_from_soup(soup)


class NewsDivArticleDirectoryParser(BaseArticleDirectoryParser):
    """Concrete parser that expects a structure with 'div.news' containing headers."""

    def _get_list_of_articles_from_soup(self, soup: BeautifulSoup) -> list[dict]:
        news = soup.select_one("div.news")

        articles: list[dict] = []

        for header in news.select("div.header"):
            heading = header.select_one("h3")

            link = heading.select_one("a[href]")

            if link is None:
                continue

            title = link.get_text(" ", strip=True)
            article_url = link["href"]

            published_container = header.select_one("span.news-list-date")
            published_time = published_container.select_one("time") if published_container is not None else None
            published_text = published_time.get_text(strip=True) if published_time is not None else ""

            articles.append({"title": title, "article_url_to_fetch_from": article_url, "published": published_text})

            print(title)
            print(article_url)

        return articles


class HerisauArticleDirectoryParser(BaseArticleDirectoryParser):
    """Parser für die Seite 'Aktuelles Informationen' von herisau.ch (i-CMS Datatable)."""

    def _get_list_of_articles_from_soup(self, soup: BeautifulSoup) -> list[dict]:
        container = soup.select_one("table.icms-dt")
        articles: list[dict] = []

        # Zeilen aus der i-CMS Datatable holen (mit und ohne Wrapper als Fallback)
        rows = []
        if container is not None:
            entities_attr = container.get("data-entities")
            if entities_attr:
                try:
                    entities = json.loads(entities_attr)

                    def _pick(d: dict, keys: list[str]) -> str:
                        for k in keys:
                            v = d.get(k)
                            if v:
                                return v
                        return ""

                    def _trenne_url_und_text(url_text: str) -> tuple[str, str]:
                        soup = BeautifulSoup(url_text, "html.parser")
                        a = soup.select_one("a")
                        url = a["href"]
                        text = a.get_text(strip=True)
                        return text, url

                    data = entities["data"]
                    if isinstance(data, list):
                        for ent in data:
                            if not isinstance(ent, dict):
                                continue
                            title_url = _pick(ent, ["name"])
                            (title, article_url) = _trenne_url_und_text(title_url)
                            published_text = _pick(ent,["datum",])
                            if article_url:
                                articles.append({
                                    "title": str(title).strip(),
                                    "article_url_to_fetch_from": str(article_url).strip(),
                                    "published": str(published_text).strip(),
                                })
                        if articles:
                            return articles
                except Exception:
                    pass
        return articles


class StubArticleDirectoryParser(BaseArticleDirectoryParser):
    """Stub parser used as a fallback if no specialized parser matches."""
    def _get_list_of_articles_from_soup(self, soup: BeautifulSoup) -> list[dict]:
        return []


def _select_parser_for_soup(soup: BeautifulSoup) -> BaseArticleDirectoryParser:
    """
    Wählt die passende Subklasse anhand markanter Struktur:
    - Falls 'div.news' vorhanden ist: NewsDivArticleDirectoryParser.
    - Falls i-CMS/Herisau-Struktur erkannt wird: HerisauArticleDirectoryParser.
    - Sonst Stub.
    """
    # Erkennung für News-Seiten
    if soup.select_one("div.news"):
        return NewsDivArticleDirectoryParser()

    # Erkennung für herisau.ch (i-CMS Datatable)
    if (soup.select_one("table.icms-dt")
        or soup.select_one("td.icms-datatable-col-datum")):
        return HerisauArticleDirectoryParser()

    # Titel-Heuristik als zusätzlicher Fallback
    title_tag = soup.find("title")
    site_title = title_tag.get_text(strip=True) if title_tag else ""
    if "Herisau" in site_title or "Aktuelle" in site_title or "Aktuelles" in site_title:
        return HerisauArticleDirectoryParser()

    return StubArticleDirectoryParser()


    def parse_article_directory(html: str) -> list[dict]:
        """ Liefert eine Liste von Artikel-Referenzen aus einer HTML-Seite"""
        soup = BeautifulSoup(html, 'html.parser')
        parser = _select_parser_for_soup(soup)



def parse_article_directory(html: str) -> list[dict]:
    """ Liefert eine Liste von Artikel-Referenzen aus einer HTML-Seite"""
    soup = BeautifulSoup(html, 'html.parser')
    parser = _select_parser_for_soup(soup)
    return parser.parse(soup)

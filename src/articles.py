import sys
sys.path.append("src")
import article_saveload
import article_codec
import shortify
from urllib.parse import urlparse
from util import *

def save_as_tex_and_json(article_dict: dict[str, str | None], article_filename: str):
    article_saveload.article_save(article_filename + ".json", article_dict)
    with open(article_filename, "w", encoding="utf-8") as f:
        article_codec.encode(article_filename, article_dict, f)

def replace_image_url_with_download_image(article_dict: dict[str, str]):
    _delete_symbolbilder_from_article(article_dict)
    if "image" in article_dict and article_dict['image']:
        url_or_file = article_dict['image']
        if urlparse(url_or_file).scheme in ['http', 'https']:
            image_filename = download_image(url_or_file)
        else:
            image_filename = url_or_file
        image_filename = shrink_image(image_filename)
        article_dict['image'] = image_filename

def replace_article_url_with_shortified_url(article_dict: dict[str, str]):
    if "url" in article_dict and article_dict['url']:
        url = article_dict['url']
        if not url.startswith(shortify.base_url):
            article_dict['url'] = shortify.create_shortlink_or_get_from_db(url, article_dict['title'])

def _delete_symbolbilder_from_article(article_dict: dict[str, str]):
    patterns_lowercase = [
        "symbolbild",
        "_symb_"
    ]
    if "image" in article_dict and article_dict['image']:
        for pattern in patterns_lowercase:
            if pattern in article_dict['image'].lower():
                article_dict['image'] = None
                return

def filter_articles_published_after(articles: list[dict], min_published_date: datetime,) -> list[dict]:
    """
    Filtert Artikel und gibt nur jene zurück, deren 'published'-Datum
    NACH dem gegebenen Datum liegt.
    Erwartete Datumsformate in 'published': 'dd.mm.yyyy' (z.B. '06.11.2026') oder 'yyyy-mm-dd' (z.B. '2026-11-12').
    """

    def _parse_published_date(published_str: str) -> datetime:
        s = published_str.strip()
        try:
            result = datetime.strptime(s, "%d.%m.%Y")
        except ValueError:
            try:
                result = datetime.strptime(s, "%Y-%m-%d")
            except ValueError:
                result = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                # manchmal vorhandene Timezone Info ignorieren wir mal der Einfachheit halber
        return result

    return [
        article
        for article in articles
        if _parse_published_date(article["published"]) >= min_published_date
    ]


def select_articles_admin_ch(article_list):
    return [article for article in article_list if "Öffentliche Warnung" in article["title"]]
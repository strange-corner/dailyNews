from typing import Any
import tomllib
from article_codec import *
from articles import *
from directoryParser import *
from urllib.parse import urlparse

from util import *
from feed import *

def parseConfig() -> dict[str, Any]:
    CONFIG_FILE = "config/config.toml"

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    return config

def fetch_feed_articles(feed_url: str) -> list[dict]:
    articles = load_rss(feed_url)
    articles = filter_articles_older_than(articles, timedelta(days=2))
    for article in articles:
        replace_image_url_with_download_image(article)
        save_article(article)
        print(article)


def fetch_web_articles(url: str):
    htmltext = myrequests.get(url).text
    articles = parse_article_directory(htmltext)
    articles = filter_articles_published_after(articles, datetime.now() - timedelta(days=2))

    parsed_uri = urlparse(url)
    netloc = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    for article in articles:

        article_content = online_article.copy_online_article(netloc + article["article_url"])
        article.update(article_content)
        article["quellenArt"] = "Quelle"
        replace_image_url_with_download_image(article)
        save_article(article)


def save_article(article: dict[str, str]):
    fname = articleFilenameFromTitle(article["title"])
    folder = getCreateFolderFromDate()
    article_filename = os.path.join(folder, fname)
    save_as_tex_and_json(article, article_filename)


if __name__ == "__main__":
    print("Hello Daily Newspaper.")
    workdir = getCreateFolderFromDate()
    print("Working directory is: " + workdir)
    config = parseConfig()

    web_article_directories = config["Feeds"]["web"]
    for web_article_directory_url in web_article_directories:
        fetch_web_articles(web_article_directory_url)

    rssfeed1 = config["Feeds"]["rss"][0]
    print("rssfeed1 is: " + str(rssfeed1))
    fetch_feed_articles(rssfeed1)
from typing import Any
import tomllib

import email_fetcher
from article_codec import *
from articles import *
from directoryParser import *
from urllib.parse import urlparse

from src import wetter_fetcher_and_article
from src.email_article import parse_email_to_article
from util import *
from feed import *

def parseConfig(toml_file) -> dict[str, Any]:
    with open(toml_file, "rb") as f:
        config = tomllib.load(f)
    return config

def fetch_feed_articles(feed: dict[str, str]) -> list[dict]:
    articles = load_rss(feed)
    articles = filter_articles_older_than(articles, getSinceDate())
    for article in articles:
        replace_image_url_with_download_image(article)
        save_article(article)
        print(article)


def fetch_web_articles(url: str):
    htmltext = myrequests.get(url).text
    articles = parse_article_directory(htmltext)
    articles = filter_articles_published_after(articles, getSinceDate())

    parsed_uri = urlparse(url)
    netloc = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    for article in articles:

        article_content = online_article.copy_online_article(netloc + article["article_url"])
        article.update(article_content)
        article["quellenArt"] = "Quelle"
        if "image" in article:
            replace_image_url_with_download_image(article)
        save_article(article)


def create_articles_from_mail():
    secret = parseConfig("config/secret.toml")
    since = getSinceDate()
    emails = email_fetcher.fetch_emails_imap(secret["imap"]["server"], secret["imap"]["user"], secret["imap"]["password"],
                                             since=since)
    for email in emails:
        article = parse_email_to_article(email)
        if not article.zumAussortieren():
            # articles = filter_articles_published_after(articles, datetime.now() - timedelta(days=2))
            save_article(article.to_dict())


def getSinceDate() -> datetime:
    now = datetime.now()
    days_back = 1 if now.weekday() == 6 else 2
    since = now - timedelta(days=days_back)
    return since


def save_article(article: dict[str, str]):
    fname = articleFilenameFromTitle(article["title"])
    folder = getCreateFolderFromDate()
    article_filename = os.path.join(folder, fname)
    save_as_tex_and_json(article, article_filename)


if __name__ == "__main__":
    print("Hello Daily Newspaper.")
    workdir = getCreateFolderFromDate()
    print("Working directory is: " + workdir)
    config = parseConfig("config/config.toml")

    create_articles_from_mail()

    web_article_directories = config["Feeds"]["web"]
    for web_article_directory_url in web_article_directories:
        fetch_web_articles(web_article_directory_url)

    feeds = config["Feeds"]["rss"]
    for rssfeed1 in feeds:
        print("rssfeed1 is: " + str(rssfeed1))
        fetch_feed_articles(rssfeed1)

    wetter_fetcher_and_article.fetch_weather_and_save()
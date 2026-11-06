from typing import Any
import tomllib
from article_codec import *
from articles import *

from util import *
from feed import *

def parseConfig() -> dict[str, Any]:
    CONFIG_FILE = "config/config.toml"

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    return config

def list_feed_entries(feed_url: str) -> list[dict]:
    articles = load_rss(feed_url)
    articles = filter_articles_older_than(articles, timedelta(days=2))
    for article in articles:
        save_article(article)
        print(article)


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
    rssfeed1 = config["Feeds"]["rss"][0]
    print("rssfeed1 is: " + str(rssfeed1))
    list_feed_entries(rssfeed1)
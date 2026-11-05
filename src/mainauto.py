from typing import Any
import tomllib

from util import *
from feed import *

def parseConfig() -> dict[str, Any]:
    CONFIG_FILE = "config/config.toml"

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    return config

def list_feed_entries(feed_url: str) -> list[dict]:
    articles = load_rss(feed_url)
    for article in articles:
        print(article)


if __name__ == "__main__":
    print("Hello Daily Newspaper.")
    workdir = getCreateFolderFromDate()
    print("Working directory is: " + workdir)
    config = parseConfig()
    rssfeed1 = config["Feeds"]["rss"][0]
    print("rssfeed1 is: " + str(rssfeed1))
    list_feed_entries(rssfeed1)
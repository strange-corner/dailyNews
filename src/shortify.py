import requests
import os
if not os.getenv("GITHUB_ACTIONS"):
    from src import config
import sqlite3
import json
from pathlib import Path
from urllib.parse import urlparse

shortify_domain = "gbsn.ch"
base_url = f"https://{shortify_domain}"
api_url = f"{base_url}/wp-json/url-shortify/v1/links/"

THIS_DIR = Path(__file__).parent
cache_db_file = THIS_DIR / "shorturl_cache.sqlite"


def init_db():
    # global db_con
    db_con = sqlite3.connect(cache_db_file)
    db_con.execute("create table if not exists shortlink (url primary key, slug)")
    server_data = get_list()
    for d in server_data:
        query = f"insert into shortlink values (\"{d['url']}\", \"{d['slug']}\") on conflict do nothing"
        print(query)
        db_con.execute(query)
    db_con.commit()
    db_con.close()


def insert_into_db(url: str, slug: str):
    db_con = sqlite3.connect(cache_db_file)
    query = f"insert into shortlink values (\"{url}\", \"{slug}\") on conflict do nothing"
    db_con.execute(query)
    db_con.commit()
    db_con.close()


def dump_db():
    db_con = sqlite3.connect(cache_db_file)
    result = db_con.execute("select * from shortlink")
    resstr = result.fetchall()
    for i in resstr:
        print(i)
    db_con.close()


def get_slug_from_db(url: str) -> str or None:
    """
    :param url: Ziel-URL, oder bereits Shortlink
    :return: Slug des Shortlinks, wenn in DB vorhanden
    """
    db_con = sqlite3.connect(cache_db_file)
    if url.startswith(shortify_domain):
        query = f"select slug from shortlink where slug = '{url.split('/')[-1]}'"
    else:
        purl = urlparse(url)
        if purl.netloc == shortify_domain:
            query = f"select slug from shortlink where slug = '{purl.path[1:]}'"  # [1:], um '/' wegzulassen
        else:
            query = f"select slug from shortlink where url = '{url}'"
    print(query)
    res = db_con.execute(query)
    result = res.fetchone()
    db_con.close()
    return result[0] if result else None


def create_shortlink_or_get_from_db(url: str, title: str) -> str:
    db_slug = get_slug_from_db(url)
    if db_slug:
        result = shortify_domain + "/" + db_slug
    else:
        slug = _create_shortlink(url, title)
        insert_into_db(url, slug)
        result = shortify_domain + "/" + slug
    return result


def get_list() -> dict:
    response = requests.get(api_url, auth=(config.shortify_key["user"], config.shortify_key["pass"]))
    print(response)
    print(response.content)
    json_dict = json.loads(response.content)
    data = json_dict["data"]
    return data
    for i in data:
        print(i)


def _create_shortlink(url: str, title: str) -> str:
    print("Creating new shortlink...")
    body = {
        "url": url,
        "title": title
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(api_url, json=body, headers=headers, auth=(config.shortify_key["user"], config.shortify_key["pass"]))
    print(resp)
    print(resp.status_code, resp.json())
    shortlink = resp.json()["data"]["short_url"]
    result = shortlink.split("/")[-1]
    print("Created ", result)
    return result


if __name__ == "__main__":

    testurl = "https://weltwoche.ch/daily/korruptions-skandal-in-kiew-selenskyj-berater-andrij-jermak-legt-sein-amt-nieder/"
    res = create_shortlink_or_get_from_db(testurl, "WWTEST")
    print(res)

import requests
from bs4 import BeautifulSoup


def fetch_crossteaser_data(url: str) -> dict:
    headers = {"User-Agent": "GuebsenseeNachrichten/1.0 (info@gbsn.ch)"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    og_data = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            og_data[prop[3:]] = tag.get("content", "")

    return og_data

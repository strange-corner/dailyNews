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

    # Änderungswünsche der Urheber
    if og_data['site_name'] == "Schweizerzeit Verlags AG":
        og_data['site_name'] = "www.schweizerzeit.ch"

    return og_data

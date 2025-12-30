# Wrapper to add User Agent in request header

import requests
from requests import Response

HEADERS = {"User-Agent": "GuebsenseeJournal/1.0 (info@gbsn.ch)"}


def get(url: str) -> Response:
    resp = requests.get(url, headers=HEADERS)
    return resp
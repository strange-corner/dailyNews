from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os

def getCreateFolderFromDate(date_time = datetime.now() + timedelta(hours=12)):
    """ gibt den Ordner zum Datum zurück, erstellt ihn, falls nötig"""
    folder = date_time.strftime("%y%m_%d")
    os.makedirs(folder, exist_ok=True)
    return folder

def datetime_from_published_str(published_str: str) -> datetime:
    parseFormat = "%a, %d %b %Y %H:%M:%S %z"
    date = datetime.strptime(published_str, parseFormat)
    return date

def filter_articles_older_than(articles: list[dict[str, str]], delta: timedelta) -> list[dict[str, str]]:
    return [d for d in articles if datetime.now(ZoneInfo("Europe/Berlin")) - datetime_from_published_str(d['published']) < delta]


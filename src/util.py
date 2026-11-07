from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import myrequests
import urllib.parse
from PIL import Image


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


def download_image(url):
    image = myrequests.get(url)
    image_name = url.split('/')[-1]
    image_name_unquoted = urllib.parse.unquote(image_name)
    image_path = os.path.join(getCreateFolderFromDate(), image_name_unquoted)
    with open(image_path, 'wb') as f:
        for chunk in image.iter_content():
            f.write(chunk)
    return image_name_unquoted


def shrink_image(filename: str)-> str:
    MAXWIDTH = 500
    image_path = os.path.join(getCreateFolderFromDate(), filename)
    img = Image.open(image_path)
    if img.width > MAXWIDTH:
        scale = MAXWIDTH / img.width
        img = img.resize((MAXWIDTH, int(img.height * scale)))
        filename_parts = filename.split('.')
        new_filename = "".join(filename_parts[:-1]) + "k.jpg"
        img.save(os.path.join(getCreateFolderFromDate(), new_filename))
        return new_filename
    return filename


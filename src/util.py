from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import myrequests
import urllib.parse
if not os.getenv("GITHUB_ACTIONS"):
    from PIL import Image

def get_default_issue_date_time() -> datetime:
    return datetime.now() + timedelta(hours=12)

def getCreateFolderFromDate(date_time = get_default_issue_date_time()):
    """ gibt den Ordner zum Datum zurück, erstellt ihn, falls nötig"""
    folder = date_time.strftime("%y%m_%d")
    os.makedirs(folder, exist_ok=True)
    return folder


def datetime_from_published_str(published_str: str) -> datetime:
    parseFormat = "%a, %d %b %Y %H:%M:%S %z"
    date = datetime.strptime(published_str, parseFormat)
    return date


def filter_articles_older_than(articles: list[dict[str, str]], since: datetime) -> list[dict[str, str]]:
    # Falls since kein tzinfo hat, auf lokale Zeitzone (z.B. Europe/Zurich) setzen
    if since.tzinfo is None:
        since = since.replace(tzinfo=ZoneInfo("Europe/Zurich"))
    return [
        d for d in articles
        if since <= datetime_from_published_str(d["published"])
    ]


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
        new_filename = _get_image_new_filename_with_suitable_ending(filename)
        img.save(os.path.join(getCreateFolderFromDate(), new_filename))
        return new_filename
    return filename

def _get_image_new_filename_with_suitable_ending(filename: str) -> str:
    filename_parts = filename.split('.')
    extension = filename_parts[-1]
    if len(extension) < 3 or len(extension) > 4:
        # bei speziellen Filenamen, z.B. von herisau.ch, wird einfach eine Endung angehängt
        return filename + ".png"
    else:
        return "".join(filename_parts[:-1]) + "k." + extension


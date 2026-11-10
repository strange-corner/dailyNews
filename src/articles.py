import article_saveload
import article_codec
from urllib.parse import urlparse
from util import *

def save_as_tex_and_json(article_dict: dict[str, str | None], article_filename: str):
    article_saveload.article_save(article_filename + ".json", article_dict)
    with open(article_filename, "w", encoding="utf-8") as f:
        article_codec.encode(article_filename, article_dict, f)

def replace_image_url_with_download_image(article_dict: dict[str, str]):
    _delete_symbolbilder_from_article(article_dict)
    if article_dict['image']:
        url_or_file = article_dict['image']
        if urlparse(url_or_file).scheme in ['http', 'https']:
            image_filename = download_image(url_or_file)
        else:
            image_filename = url_or_file
        image_filename = shrink_image(image_filename)
        article_dict['image'] = image_filename

def _delete_symbolbilder_from_article(article_dict: dict[str, str]):
    patterns_lowercase = [
        "symbolbild"
    ]
    for pattern in patterns_lowercase:
        if pattern in article_dict['image'].lower():
            article_dict['image'] = None
            return


import article_saveload
import article_codec

def save_as_tex_and_json(article_dict: dict[str, str | None], article_filename: str):
    article_saveload.article_save(article_filename + ".json", article_dict)
    with open(article_filename, "w", encoding="utf-8") as f:
        article_codec.encode(article_filename, article_dict, f)



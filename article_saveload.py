import json

def article_save(filepath: str, article: dict):
    """Save a dictionary as a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=4)

def article_load(filepath: str) -> dict:
    """Load a dictionary from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
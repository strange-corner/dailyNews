import html
import imaplib
import os
import re
from datetime import datetime, timedelta
from email.header import decode_header, make_header

from bs4 import BeautifulSoup

from src import article_codec, article_saveload


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


def _sender_name(message) -> str:
    sender = message.get("From") or ""
    if not sender:
        return "E-Mail"
    sender_name = sender.split("<", 1)[0].strip().strip('"')
    return sender_name or sender


def _clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\r", "")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n +", "\n", text)
    return text.strip()


def _extract_message_body(message) -> str:
    if message.is_multipart():
        parts = []
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_type() not in {"text/plain", "text/html"}:
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, errors="replace")
            except Exception:
                text = payload.decode("utf-8", errors="replace")
            if part.get_content_type() == "text/html":
                text = BeautifulSoup(text, "html.parser").get_text("\n", strip=True)
            parts.append(text)
        text = "\n".join(parts)
        return _clean_text(text)

    payload = message.get_payload(decode=True)
    if payload is None:
        return ""
    charset = message.get_content_charset() or "utf-8"
    try:
        return _clean_text(payload.decode(charset, errors="replace"))
    except Exception:
        return _clean_text(payload.decode("utf-8", errors="replace"))


def _to_article_dict(message) -> dict:
    title = _decode_header(message.get("Subject") or "E-Mail ohne Betreff")
    body = _extract_message_body(message)
    sender = _sender_name(message)
    if not body:
        body = "Keine Nachricht enthalten."

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", body) if p.strip()]
    lead = paragraphs[0] if paragraphs else body[:240]
    content = "\n\n".join(paragraphs[1:]) if len(paragraphs) > 1 else ""

    if not content:
        content = body[len(lead):].strip() if len(body) > len(lead) else ""

    if not lead:
        lead = title

    if len(lead) > 220:
        lead = lead[:217].rstrip() + "..."

    return {
        "title": title,
        "lead": lead,
        "content": content,
        "image": None,
        "url": "",
        "quelle": sender,
        "quellenArt": "Quelle",
        "infobox": None,
        "source": "email",
    }


def connect_imap(host: str, username: str, password: str, folder: str = "INBOX"):
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select(folder)
    return mail


def fetch_email_articles(
    host: str,
    username: str,
    password: str,
    folder: str = "INBOX",
    since_days: int = 7,
    only_unseen: bool = True,
):
    if not host or not username or not password:
        raise ValueError("EMAIL_HOST, EMAIL_USER and EMAIL_PASSWORD must be set.")

    mail = connect_imap(host, username, password, folder)
    try:
        cutoff = (datetime.utcnow() - timedelta(days=since_days)).strftime("%d-%b-%Y")
        if only_unseen:
            search_criteria = f'(UNSEEN SINCE "{cutoff}")'
        else:
            search_criteria = f'(SINCE "{cutoff}")'
        status, message_ids = mail.search(None, search_criteria)
        if status != "OK":
            return []

        ids = [msg_id for msg_id in message_ids[0].split() if msg_id]
        articles = []
        for msg_id in ids:
            status, message_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            raw_message = message_data[0][1]
            try:
                import email

                msg = email.message_from_bytes(raw_message)
            except Exception:
                continue
            if msg.get("Subject") is None:
                continue
            articles.append(_to_article_dict(msg))
        return articles
    finally:
        try:
            mail.close()
        except Exception:
            pass
        mail.logout()


def save_email_articles_to_folder(articles: list[dict], base_dir: str, date_value: datetime | None = None):
    if date_value is None:
        date_value = datetime.utcnow()
    folder = date_value.strftime("%y%m_%d")
    target_dir = os.path.join(base_dir, folder)
    os.makedirs(target_dir, exist_ok=True)

    saved = []
    for article in articles:
        filename = article_codec.articleFilenameFromTitle(article["title"])
        article_path = os.path.join(target_dir, filename)
        article_saveload.article_save(article_path + ".json", article)
        with open(article_path, "w", encoding="utf-8") as f:
            article_codec.encode(article_path, article, f)
        saved.append(article_path)
    return saved


def load_email_articles_from_env():
    host = os.environ.get("EMAIL_HOST")
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    folder = os.environ.get("EMAIL_FOLDER", "INBOX")
    days = int(os.environ.get("EMAIL_LOOKBACK_DAYS", "7"))
    return fetch_email_articles(host, user, password, folder=folder, since_days=days, only_unseen=True)


if __name__ == "__main__":
    print("Use this module via fetch_email_articles() or save_email_articles_to_folder().")

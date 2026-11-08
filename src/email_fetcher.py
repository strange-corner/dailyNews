from __future__ import annotations

import imaplib
import socket
from datetime import datetime, date
from email import message_from_bytes
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Any, Iterable, Tuple, Optional

from bs4 import BeautifulSoup


__all__ = ["fetch_emails_imap"]


def _decode_header_value(value: Optional[str]) -> str:
    if value is None:
        return ""
    decoded_parts: Iterable[Tuple[bytes | str, Optional[str]]] = decode_header(value)
    out_chunks: list[str] = []
    for chunk, enc in decoded_parts:
        if isinstance(chunk, bytes):
            try:
                out_chunks.append(chunk.decode(enc or "utf-8", errors="replace"))
            except LookupError:
                out_chunks.append(chunk.decode("utf-8", errors="replace"))
        else:
            out_chunks.append(chunk)
    return "".join(out_chunks).strip()


def _extract_bodies(msg: Message) -> Tuple[str, str]:
    """
    Returns (text_body, html_body). Either can be empty if not available.
    """
    text_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            cdisp = (part.get_content_disposition() or "").lower()
            if cdisp == "attachment":
                continue
            ctype = (part.get_content_type() or "").lower()
            try:
                payload = part.get_payload(decode=True) or b""
            except Exception:
                payload = b""
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except LookupError:
                decoded = payload.decode("utf-8", errors="replace")

            if ctype == "text/plain" and not text_body:
                text_body = decoded
            elif ctype == "text/html" and not html_body:
                html_body = decoded
    else:
        ctype = (msg.get_content_type() or "").lower()
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        try:
            decoded = payload.decode(charset, errors="replace")
        except LookupError:
            decoded = payload.decode("utf-8", errors="replace")
        if ctype == "text/plain":
            text_body = decoded
        elif ctype == "text/html":
            html_body = decoded

    return text_body.strip(), html_body.strip()


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Use newlines to preserve some structure; strip extra whitespace.
    text = soup.get_text("\n")
    lines = [line.strip() for line in text.splitlines()]
    # Collapse multiple blank lines.
    compact: list[str] = []
    blank = False
    for line in lines:
        if line:
            compact.append(line)
            blank = False
        else:
            if not blank:
                compact.append("")
                blank = True
    return "\n".join(compact).strip()


def _format_since_arg(since: datetime | date) -> Tuple[str, str]:
    if isinstance(since, datetime):
        d = since.date()
    else:
        d = since
    # IMAP expects e.g. 01-Nov-2026
    return "SINCE", d.strftime("%d-%b-%Y")


def fetch_emails_imap(
    host: str,
    username: str,
    password: str,
    port: int = 993,
    folder: str = "INBOX",
    use_ssl: bool = True,
    search: Optional[str] = "UNSEEN",
    since: Optional[datetime | date] = None,
    limit: Optional[int] = 50,
    mark_seen: bool = False,
    timeout: Optional[float] = None,
) -> list[dict[str, Any]]:
    """
    Fetch emails from an IMAP mailbox.

    Parameters:
    - host, username, password: IMAP credentials.
    - port: IMAP port (993 for SSL).
    - folder: Mailbox folder to select (default "INBOX").
    - use_ssl: Whether to use IMAP over SSL.
    - search: Additional IMAP search tokens (e.g., "UNSEEN", 'FROM "alice@example.com"').
              Tokens are split on whitespace and passed as separate args.
              If None, uses "ALL".
    - since: If provided, adds a SINCE filter (server local date) to the search.
    - limit: Max number of messages to return (newest first). None for no limit.
    - mark_seen: If True, mark fetched messages as \\Seen.
    - timeout: Optional socket default timeout for this call.

    Returns:
    - List of dicts with fields:
      id, subject, from, to, date, body_text, body_html
    """
    old_timeout = socket.getdefaulttimeout()
    if timeout is not None:
        socket.setdefaulttimeout(timeout)

    imap: imaplib.IMAP4 | imaplib.IMAP4_SSL | None = None
    try:
        if use_ssl:
            imap = imaplib.IMAP4_SSL(host, port)
        else:
            imap = imaplib.IMAP4(host, port)

        imap.login(username, password)

        typ, _ = imap.select(folder, readonly=not mark_seen)
        if typ != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}")

        search_args: list[str] = []
        if search:
            # Split tokens: e.g. 'UNSEEN FROM "alice@example.com"' -> ["UNSEEN", "FROM", '"alice@example.com"']
            # Caller is responsible for quoting values that contain spaces.
            search_args.extend(search.split())
        else:
            search_args.append("ALL")

        if since is not None:
            key, value = _format_since_arg(since)
            search_args.extend([key, value])

        typ, data = imap.search(None, *search_args)
        if typ != "OK":
            raise RuntimeError(f"Search failed with args {search_args!r}")

        all_ids = data[0].split() if data and data[0] else []
        if not all_ids:
            return []

        # Use newest first. IMAP search returns ascending by arrival; take the tail then reverse.
        ids = all_ids[-limit:] if (limit is not None and limit > 0) else all_ids
        ids = list(reversed(ids))

        results: list[dict[str, Any]] = []
        for uid in ids:
            # BODY.PEEK[] avoids setting \\Seen on fetch
            typ, msg_data = imap.fetch(uid, "(BODY.PEEK[] FLAGS)")
            if typ != "OK" or not msg_data:
                continue

            raw_bytes = None
            for part in msg_data:
                if isinstance(part, tuple) and part[1]:
                    raw_bytes = part[1]
                    break
            if raw_bytes is None:
                continue

            msg: Message = message_from_bytes(raw_bytes)

            subject = _decode_header_value(msg["Subject"])
            from_ = _decode_header_value(msg["From"])
            to_ = _decode_header_value(msg["To"])

            date_hdr = msg.get("Date")
            try:
                dt = parsedate_to_datetime(date_hdr) if date_hdr else None
                if dt and dt.tzinfo is None:
                    # Assume naive is in local time; keep as-is
                    pass
            except Exception:
                dt = None

            text_body, html_body = _extract_bodies(msg)
            if not text_body and html_body:
                text_body = _html_to_text(html_body)

            mail_dict: dict[str, Any] = {
                "id": uid.decode(errors="ignore"),
                "subject": subject,
                "from": from_,
                "to": to_,
                "date": dt,
                "body_text": text_body,
                "body_html": html_body,
            }

            if mark_seen:
                try:
                    imap.store(uid, "+FLAGS", "\\Seen")
                except Exception:
                    # Not critical; proceed
                    pass

            results.append(mail_dict)

        return results
    finally:
        try:
            if imap is not None:
                imap.logout()
        except Exception:
            pass
        if timeout is not None:
            socket.setdefaulttimeout(old_timeout)

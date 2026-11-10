from __future__ import annotations

import imaplib
import socket
import mimetypes
import re
from pathlib import Path
from datetime import datetime, date
from email import message_from_bytes
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Any, Iterable, Tuple, Optional

from bs4 import BeautifulSoup


__all__ = ["fetch_emails_imap", "download_image_attachments_imap"]


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


def _safe_filename(name: str, fallback: str = "attachment") -> str:
    """
    Sanitize a filename for safe saving on most filesystems.
    """
    if not name:
        name = fallback
    # Remove NULLs and strip whitespace
    name = name.replace("\x00", "").strip()
    # Replace path separators
    name = name.replace("/", "_").replace("\\", "_").replace(":", "_")
    # Replace disallowed characters
    name = re.sub(r'[^A-Za-z0-9._ \-\(\)\[\]]', "_", name)
    # Avoid empty names
    if not name:
        name = fallback
    # Limit typical filename length
    if len(name) > 200:
        stem, dot, ext = name.rpartition(".")
        if not dot:
            name = name[:200]
        else:
            avail = 200 - len(ext) - 1
            stem = stem[:max(1, avail)]
            name = f"{stem}.{ext}"
    return name


def _ensure_unique_path(path: Path) -> Path:
    """
    If path exists, append -N before extension to make it unique.
    """
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def _collect_image_attachments(msg: Message, include_data: bool = False) -> list[dict[str, Any]]:
    """
    Extract image attachments (including inline images) from a Message.

    Returns a list of dicts:
      filename, content_type, size, content_id, is_inline[, data if include_data=True]
    """
    attachments: list[dict[str, Any]] = []
    counter = 0
    for part in msg.walk():
        # Skip container parts
        if part.is_multipart():
            continue

        ctype = (part.get_content_type() or "").lower()
        if not ctype.startswith("image/"):
            continue

        disp = (part.get_content_disposition() or "").lower()
        is_inline = disp == "inline"
        is_attach_like = disp in ("inline", "attachment", "")
        if not is_attach_like:
            continue

        raw_name = part.get_filename()
        fname = _decode_header_value(raw_name) if raw_name else ""
        subtype = part.get_content_subtype() or "octet-stream"
        guessed_ext = mimetypes.guess_extension(ctype) or f".{subtype}"
        if not guessed_ext.startswith("."):
            guessed_ext = f".{guessed_ext}"
        if not fname:
            counter += 1
            fname = f"image-{counter}{guessed_ext}"

        data = part.get_payload(decode=True) or b""
        cid = part.get("Content-ID") or ""
        cid = cid.strip("<>") if cid else ""

        info: dict[str, Any] = {
            "filename": fname,
            "content_type": ctype,
            "size": len(data),
            "content_id": cid,
            "is_inline": is_inline,
        }
        if include_data:
            info["data"] = data
        attachments.append(info)
    return attachments


def _skip_this_from(from_, subject: str):
    if "MM Kapo AR:" in subject:
        print(subject + "  wird mit Feed bearbeitet")
        return True
    if "MM der Kapo AR:" in subject:
        print(subject + "  wird mit Feed bearbeitet")
        return True
    if "Kommunikation Stadt St.Gallen" in from_:
        print(subject, from_, "  wird mit Feed bearbeitet")
        return True
    if "Kommunikation DSSI_STAPO" in from_:
        print(subject, from_, "  wird mit Feed bearbeitet")
        return True
    return False


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
      id, subject, from, to, date, body_text, body_html, image_attachments
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
            typ, msg_data = imap.fetch(uid, "(BODY.PEEK[] FLAGS)")  # TODO ohne peek
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
            if _skip_this_from(from_, subject):
                continue
            to_ = _decode_header_value(msg["To"])

            date_hdr = msg.get("Date")

            text_body, html_body = _extract_bodies(msg)
            if not text_body and html_body:
                text_body = _html_to_text(html_body)

            images_meta = _collect_image_attachments(msg, include_data=False)

            mail_dict: dict[str, Any] = {
                "id": uid.decode(errors="ignore"),
                "subject": subject,
                "from": from_,
                "to": to_,
                "date": date_hdr,
                "body_text": text_body,
                "body_html": html_body,
                "image_attachments": images_meta,
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


def download_image_attachments_imap(
    host: str,
    username: str,
    password: str,
    uid: str | bytes,
    dest_dir: str | Path,
    *,
    port: int = 993,
    folder: str = "INBOX",
    use_ssl: bool = True,
    overwrite: bool = False,
    timeout: Optional[float] = None,
) -> list[str]:
    """
    Download image attachments (including inline images) from a single email to dest_dir.

    Parameters:
    - uid: The message id as returned by fetch_emails_imap()["id"].
           Note: This is the message sequence number in the current mailbox view.
    - dest_dir: Destination directory (created if missing).
    - overwrite: If True, overwrite existing files. If False, create unique filenames.

    Returns:
    - List of saved file paths (as strings).
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

        typ, _ = imap.select(folder, readonly=True)
        if typ != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}")

        # BODY.PEEK[] to avoid side effects
        typ, msg_data = imap.fetch(uid, "(BODY.PEEK[])")
        if typ != "OK" or not msg_data:
            return []

        raw_bytes = None
        for part in msg_data:
            if isinstance(part, tuple) and part[1]:
                raw_bytes = part[1]
                break
        if raw_bytes is None:
            return []

        msg: Message = message_from_bytes(raw_bytes)
        images = _collect_image_attachments(msg, include_data=True)

        out_dir = Path(dest_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[str] = []
        for img in images:
            fname = _safe_filename(img.get("filename") or "image")
            target = out_dir / fname
            if not overwrite:
                target = _ensure_unique_path(target)

            data = img.get("data", b"")
            with open(target, "wb") as fh:
                fh.write(data)
            saved_paths.append(str(target))

        return saved_paths
    finally:
        try:
            if imap is not None:
                imap.logout()
        except Exception:
            pass
        if timeout is not None:
            socket.setdefaulttimeout(old_timeout)

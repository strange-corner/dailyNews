from __future__ import annotations

import imaplib
import socket
from datetime import datetime, timedelta
from typing import Optional

__all__ = ["delete_emails_older_than_days_imap"]


def delete_emails_older_than_days_imap(
    host: str,
    username: str,
    password: str,
    *,
    days: int = 14,
    port: int = 993,
    folder: str = "INBOX",
    use_ssl: bool = True,
    timeout: Optional[float] = None,
) -> int:
    """
    Löscht alle E-Mails in 'folder', die älter als 'days' Tage sind.

    Ablauf:
    - Verbindet sich mit dem IMAP-Server und wählt den Ordner (schreibend).
    - Sucht Nachrichten mit Kriterium BEFORE <cutoff>.
    - Markiert gefundene Nachrichten als \\Deleted (Batch, mit Fallback pro Nachricht).
    - Führt imap.expunge() aus und gibt die Anzahl gelöschter Nachrichten zurück.

    Parameter:
    - host, username, password: IMAP-Zugangsdaten.
    - days: Altersschwelle in Tagen (Standard 14).
    - port: IMAP-Port (Standard 993 für SSL).
    - folder: Ziel-Ordner (Standard "INBOX").
    - use_ssl: SSL verwenden (True) oder Plain (False).
    - timeout: Optionaler Socket-Timeout in Sekunden nur für diesen Aufruf.

    Rückgabe:
    - Anzahl gelöschter Nachrichten (best effort).
    """
    if days <= 0:
        raise ValueError("days muss > 0 sein")

    # IMAP BEFORE verwendet nur das Datum (serverlokal). Wir bilden UTC-basiert ab.
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)
    before_str = cutoff_date.strftime("%d-%b-%Y")  # z. B. 01-Nov-2026

    old_timeout = socket.getdefaulttimeout()
    if timeout is not None:
        socket.setdefaulttimeout(timeout)

    imap: imaplib.IMAP4 | imaplib.IMAP4_SSL | None = None
    try:
        imap = imaplib.IMAP4_SSL(host, port) if use_ssl else imaplib.IMAP4(host, port)
        imap.login(username, password)

        typ, _ = imap.select(folder, readonly=False)
        if typ != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}")

        typ, data = imap.search(None, "BEFORE", before_str)
        if typ != "OK":
            raise RuntimeError(f"Search failed for BEFORE {before_str!r}")

        ids = data[0].split() if data and data[0] else []
        if not ids:
            return 0

        # Batch-Flaggen versuchen
        deleted_count = 0
        try:
            message_set = ",".join(uid.decode("ascii", "ignore") for uid in ids if uid)
            if message_set:
                typ, _ = imap.store(message_set, "+FLAGS", "\\Deleted")
                if typ == "OK":
                    deleted_count = len(ids)
                else:
                    # Fallback auf Einzelverarbeitung
                    for uid in ids:
                        try:
                            imap.store(uid, "+FLAGS", "\\Deleted")
                            deleted_count += 1
                        except Exception:
                            # einzelne Fehler ignorieren
                            pass
            else:
                return 0
        except Exception:
            # Fallback auf Einzelverarbeitung bei jedem generischen Fehler
            for uid in ids:
                try:
                    imap.store(uid, "+FLAGS", "\\Deleted")
                    deleted_count += 1
                except Exception:
                    pass

        # Endgültig entfernen
        imap.expunge()
        return deleted_count
    finally:
        try:
            if imap is not None:
                imap.logout()
        except Exception:
            pass
        if timeout is not None:
            socket.setdefaulttimeout(old_timeout)

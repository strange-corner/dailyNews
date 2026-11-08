from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Mapping, MutableMapping, Optional, Sequence

__all__ = [
    "Article",
    "parse_email_to_article",
    "SENDER_SECTION_RULES",
]


@dataclass
class Article:
    """
    A simple representation of a parsed article.

    Fields:
    - title: Title of the article (from email subject, with fallback).
    - content: Body text (optionally trimmed by sender-specific patterns).
    - quelle: The source, derived from the email sender ("From").
    - date: Email date, if available.
    """
    title: str
    content: str
    quelle: str
    date: Optional[datetime] = None
    quellenArt: str = "Quelle"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def zumAussortieren(self):
        return any(x in self.title for x in [
            "Einladung zur Medienorientierung",
            "Medieneinladung",
        ])


# Global, in-memory registry of sender-specific section rules.
# Keys are regex patterns matched against the sender string (quelle).
#
# Internally we keep separate mappings for start/end rules per sender:
#   SENDER_SECTION_START_RULES[sender_regex] -> [regex, ...]
#   SENDER_SECTION_END_RULES[sender_regex]   -> [regex, ...]
#
# For backwards-compatibility, SENDER_SECTION_RULES exposes a combined
# view:
#   SENDER_SECTION_RULES[sender_regex] -> { "start": [...], "end": [...] }
SENDER_SECTION_START_RULES: list[str] = [
    "View this post on the web at",
    "Sehr geehrte Medienschaffende"
]
SENDER_SECTION_END_RULES: list[str] = [
    "Impressum\n",
    "** Kontakt",
    "Weitere Informationen",
    "Medienmitteilung als PDF",
    "Für Rückfragen:",
    "Weitere Auskünfte erteilt ",
]
SENDER_SECTION_RULES: dict[str, dict[str, list[str]]] = {}


def _normalize_patterns(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    try:
        return [str(x) for x in val]
    except Exception:
        return [str(val)]


def _first_match_index(lines: list[str], pattern: str, start_at: int = 0) -> int:
    for i in range(start_at, len(lines)):
        line = lines[i]
        if pattern in line:
            return i
    return -1


def _extract_section_by_markers(text: str) -> str:
    """
    Extract text between the first matching start marker (excluded) and the first subsequent end
    marker (excluded). If no start is found, extraction starts at the beginning. If no end is
    found, extraction goes to the end.
    """
    lines = text.splitlines()
    start_idx = 0
    for start_res in SENDER_SECTION_START_RULES:
        i = _first_match_index(lines, start_res, 0)
        if i >= 0:
            start_idx = i + 1
            break

    end_idx = len(lines)
    for end_res in SENDER_SECTION_END_RULES:
        j = _first_match_index(lines, end_res, start_idx)
        if j >= 0:
            end_idx = j
            break

    sliced = lines[start_idx:end_idx]
    return "\n".join(sliced).strip()


def parse_email_to_article(
    email: Mapping[str, Any],
    *,
    sender_patterns: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Article:
    """
    Parse an email-like mapping into an Article.

    Expected keys in email:
    - 'subject' (str)
    - 'from' (str) -> becomes 'quelle'
    - 'date' (datetime | str | None) (optional)
    - 'body_text' (str) -> basis for content extraction

    Sender-specific section extraction:
    - Provide 'sender_patterns' to define start/end regex lists per sender (regex key).
      Example:
        sender_patterns = {
            r"^newsletter@example\\.com$": {
                "start": [r"^Inhalt:?\\s*$"],
                "end": [r"^—\\s*Ende\\s*—$"]
            },
            r".*@domain\\.com$": {
                "start": r"^Startabschnitt$",
                "end": r"^Endeabschnitt$"
            }
        }
    - You can also pre-register rules via register_sender_section_rule().

    Returns:
    - Article instance.
    """
    title = title_from_subject(email)
    quelle = quelle_from_from(email.get("from") or email.get("sender"))
    raw_date = email.get("date")
    date_obj: Optional[datetime]
    if isinstance(raw_date, datetime) or raw_date is None:
        date_obj = raw_date
    else:
        # Best-effort: ignore if not a datetime
        date_obj = None

    body_text = str(email.get("body_text") or "")

    body_text = vorspann_entfernen(body_text, title)

    content = _extract_section_by_markers(body_text)

    return Article(title=title.strip(), content=content, quelle=quelle, date=date_obj)


def quelle_from_from(from_: str) -> str:
    return from_.split("<")[0].strip(" \"\t\n\r")


def title_from_subject(email: Mapping[str, Any]) -> str:
    subject = str(email.get("subject")).strip()
    title = subject.removeprefix("Medienmitteilung:").strip()
    return title


def vorspann_entfernen(text: str, pattern: str) -> str:
    """
    Entfernt den Vorspann bis einschließlich einer Zeile, die ein gegebenes Muster enthält.
    Das Muster wird im Text gesucht, wobei Punktuationszeichen, Bindestriche, Leerzeichen usw.
    ignoriert werden (es wird nur alphanumerisch, case-insensitive verglichen).
    Zusätzlich wird eine Trennlinie aus Dashes (z. B. '-----' oder '———') als alternatives Muster
    akzeptiert. Es wird bis zum frühesten Treffer (Pattern-Zeile oder Trennlinie) abgeschnitten.
    Falls kein Treffer gefunden wird, bleibt der Text unverändert.
    """
    if not text:
        return text

    def _normalize_keep_alnum(s: str) -> str:
        return "".join(ch.lower() for ch in s if ch.isalnum())

    norm_pat = _normalize_keep_alnum(pattern) if pattern else ""
    dash_chars = set("-–—")  # ASCII minus, en dash, em dash

    cut_positions: list[int] = []

    # Zeilenweise durchlaufen und sowohl Pattern-Zeilen als auch Dash-Linien suchen
    cursor = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()

        # 1) Trennlinie aus Dashes?
        if stripped and len(stripped) >= 3 and all(ch in dash_chars for ch in stripped):
            cut_positions.append(cursor + len(line))

        # 2) Pattern-Zeile? (interpunktionstolerant)
        if norm_pat:
            norm_line = _normalize_keep_alnum(line)
            if norm_pat and norm_pat in norm_line:
                # gesamte Zeile entfernen
                cut_positions.append(cursor + len(line))

        cursor += len(line)

    if not cut_positions:
        return text

    # Bis zum frühesten gefundenen Treffer abschneiden
    cut_after = min(cut_positions)
    return text[cut_after:]
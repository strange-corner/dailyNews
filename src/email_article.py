from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Mapping, MutableMapping, Optional, Sequence

__all__ = [
    "Article",
    "parse_email_to_article",
    "register_sender_section_rule",
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


# Global, in-memory registry of sender-specific section rules.
# Keys are regex patterns matched against the sender string (quelle).
# Values:
#   { "start": [regex, ...], "end": [regex, ...] }
SENDER_SECTION_RULES: dict[str, dict[str, list[str]]] = {}


def register_sender_section_rule(
    sender_regex: str, *, start: Sequence[str] | None = None, end: Sequence[str] | None = None,
    append: bool = False,
) -> None:
    """
    Register or update section extraction rules for a given sender (regex).

    Parameters:
    - sender_regex: Regular expression to match against the sender string (quelle).
    - start: One or more regex patterns; first matching line denotes the start marker (excluded).
    - end: One or more regex patterns; first matching line denotes the end marker (excluded).
    - append: If True, extend existing rules; otherwise replace them.
    """
    s_patterns = list(start) if start else []
    e_patterns = list(end) if end else []
    if sender_regex in SENDER_SECTION_RULES and append:
        entry = SENDER_SECTION_RULES[sender_regex]
        entry.setdefault("start", [])
        entry.setdefault("end", [])
        entry["start"].extend(s_patterns)
        entry["end"].extend(e_patterns)
    else:
        SENDER_SECTION_RULES[sender_regex] = {"start": s_patterns, "end": e_patterns}


def _normalize_patterns(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    try:
        return [str(x) for x in val]
    except Exception:
        return [str(val)]


def _merge_sender_patterns(
    local_overrides: Optional[Mapping[str, Mapping[str, Any]]],
) -> dict[str, dict[str, list[str]]]:
    """
    Merge global SENDER_SECTION_RULES with per-call overrides.
    Per-call overrides take precedence if the same key exists.
    """
    merged: dict[str, dict[str, list[str]]] = {}
    # Preserve insertion order: first globals, then overrides to keep caller's order last
    for k, v in SENDER_SECTION_RULES.items():
        merged[k] = {
            "start": list(v.get("start", [])),
            "end": list(v.get("end", [])),
        }
    if local_overrides:
        for k, v in local_overrides.items():
            merged[k] = {
                "start": _normalize_patterns(v.get("start")),
                "end": _normalize_patterns(v.get("end")),
            }
    return merged


def _select_rule_for_sender(
    quelle: str, rules: Mapping[str, Mapping[str, Sequence[str] | str]],
) -> tuple[list[re.Pattern[str]], list[re.Pattern[str]]]:
    """
    Return compiled (start_patterns, end_patterns) for the first matching sender rule.
    If none matches, both lists are empty.
    """
    for sender_regex, spec in rules.items():
        if re.search(sender_regex, quelle or "", flags=re.IGNORECASE):
            starts = _normalize_patterns(spec.get("start"))
            ends = _normalize_patterns(spec.get("end"))
            start_res = [re.compile(p, re.IGNORECASE) for p in starts if p]
            end_res = [re.compile(p, re.IGNORECASE) for p in ends if p]
            return start_res, end_res
    return [], []


def _first_match_index(lines: list[str], patterns: list[re.Pattern[str]], start_at: int = 0) -> int:
    if not patterns:
        return -1
    for i in range(start_at, len(lines)):
        line = lines[i]
        for rx in patterns:
            if rx.search(line):
                return i
    return -1


def _extract_section_by_markers(text: str, start_res: list[re.Pattern[str]],
                                end_res: list[re.Pattern[str]]) -> str:
    """
    Extract text between the first matching start marker (excluded) and the first subsequent end
    marker (excluded). If no start is found, extraction starts at the beginning. If no end is
    found, extraction goes to the end.
    """
    lines = text.splitlines()
    start_idx = 0
    if start_res:
        i = _first_match_index(lines, start_res, 0)
        start_idx = (i + 1) if i >= 0 else 0

    end_idx = len(lines)
    if end_res:
        j = _first_match_index(lines, end_res, start_idx)
        end_idx = j if j >= 0 else len(lines)

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

    merged_rules = _merge_sender_patterns(sender_patterns)
    start_res, end_res = _select_rule_for_sender(quelle, merged_rules)

    content = _extract_section_by_markers(body_text, start_res, end_res) if (start_res or end_res) else body_text.strip()

    return Article(title=title.strip(), content=content, quelle=quelle, date=date_obj)


def quelle_from_from(from_: str) -> str:
    return from_.split("<")[0].strip(" \"\t\n\r")


def title_from_subject(email: Mapping[str, Any]) -> str:
    subject = str(email.get("subject")).strip()
    title = subject.strip("Medienmitteilung:").strip()
    return title


def vorspann_entfernen(text: str, pattern: str) -> str:
    """
    Entfernt den Vorspann bis einschließlich eines gegebenen Musters.
    Das Muster wird im Text gesucht, wobei Punktuationszeichen, Bindestriche, Leerzeichen usw.
    ignoriert werden (es wird nur alphanumerisch, case-insensitive verglichen).
    Zusätzlich wird eine Trennlinie aus Dashes (z. B. '-----' oder '———') als alternatives Muster
    akzeptiert. Es wird bis zum frühesten Treffer (Pattern oder Trennlinie) abgeschnitten.
    Falls kein Treffer gefunden wird, bleibt der Text unverändert.

    Beispiel:
      text="ABC--- Einleitung: Hallo\nInhalt"
      pattern="Einleitung:"
      -> Rückgabe " Hallo\nInhalt" (alles bis inkl. 'Einleitung:' entfernt)
    """
    if not text:
        return text

    def _normalize_keep_alnum_with_map(s: str) -> tuple[str, list[int]]:
        norm_chars: list[str] = []
        idx_map: list[int] = []
        for i, ch in enumerate(s):
            if ch.isalnum():
                norm_chars.append(ch.lower())
                idx_map.append(i)
        return "".join(norm_chars), idx_map

    def _normalize_keep_alnum(s: str) -> str:
        return "".join(ch.lower() for ch in s if ch.isalnum())

    # 1) Versuche, das übergebene Pattern (interpunktionstolerant) zu finden
    cut_after_pat: Optional[int] = None
    norm_text, idx_map = _normalize_keep_alnum_with_map(text)
    norm_pat = _normalize_keep_alnum(pattern) if pattern else ""
    if norm_pat:
        pos = norm_text.find(norm_pat)
        if pos != -1:
            last_norm_idx = pos + len(norm_pat) - 1
            cut_after_pat = idx_map[last_norm_idx] + 1  # inkl. Pattern abschneiden

    # 2) Suche nach einer Trennlinie aus Dashes als alternatives Muster
    dash_chars = set("-–—")  # ASCII minus, en dash, em dash
    cut_after_dash: Optional[int] = None
    cursor = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and len(stripped) >= 3 and all(ch in dash_chars for ch in stripped):
            cut_after_dash = cursor + len(line)
            break
        cursor += len(line)

    if cut_after_pat is None and cut_after_dash is None:
        return text

    cut_after = max(x for x in (cut_after_pat, cut_after_dash) if x is not None)
    return text[cut_after:]
    
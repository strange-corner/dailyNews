import json
from datetime import datetime, timedelta, date
import requests
import os
if not os.getenv("GITHUB_ACTIONS"):
    import config

def extract_events(content):
    events = []

    content_json = json.loads(content)['content']

    for item in content_json:
        answers = item.get("answers", {})

        event = {
            "datum": None,      # datetime
            "titel": None,
            "ort": None,
            "link": None,
            "zeit": None
        }

        for a in answers.values():
            name = a.get("name")

            if name == "datum":
                answer = a.get("answer", {})
                dt_str = answer.get("datetime")

                if dt_str:
                    event["datum"] = datetime.strptime(
                        dt_str, "%Y-%m-%d %H:%M:%S"
                    )

                hour = answer.get("hour")
                minute = answer.get("min")
                if hour and minute and event["datum"]:
                    event["datum"] = event["datum"].replace(
                        hour=int(hour), minute=int(minute)
                    )
                    event["zeit"] = f"{hour}:{minute}"

            elif name == "titelDer":
                event["titel"] = a.get("answer")

            elif name == "veranstaltungsort":
                event["ort"] = a.get("answer")

            elif name == "linkFur":
                event["link"] = a.get("answer")

        events.append(event)

    return events

def generate_text_for_date(events, today: date):
    if today is None:
        today = datetime.today().date()

    tomorrow = today + timedelta(days=1)

    lines = []

    for label, day in [("Heute", today), ("Morgen", tomorrow)]:
        day_events = [
            e for e in events
            if e["datum"] and e["datum"].date() == day
        ]

        if not day_events:
            continue

        parts = []
        for e in day_events:
            info = [
                e["titel"],
                e["ort"],
                e["zeit"]
            ]
            # None-Werte entfernen
            info = [str(x) for x in info if x]
            if e.get("link"):
                info.append(f"{{\\urlstyle{{same}}\\url{{{e["link"]}}} }}\n")
            parts.append(", ".join(info))

        lines.append(f"\\textbf{{{label}:}}\n")
        lines.append("\\begin{itemize}\n")
        for p in parts:
            lines.append("\\item " + p)
        lines.append("\\end{itemize}")

    return "\n".join(lines)


def download_submissions() -> bytes:
    submissions_request = f"https://api.jotform.com/form/{config.jotform_formId}/submissions?apikey={config.jotform_apikey}"
    return requests.get(submissions_request).content

def download_and_generate_text(datum: date):
    submissions = download_submissions()
    events = extract_events(submissions)
    text = generate_text_for_date(events, datum)
    return text
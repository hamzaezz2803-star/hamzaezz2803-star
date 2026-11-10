#!/usr/bin/env python3
"""Read the public GitHub contribution calendar and save it as data/contributions.json.

Uses the same HTML fragment the profile page loads, so no token is needed.
"""
import datetime as dt
import json
import os
import re
import sys
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "hamzaezz2803-star")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "contributions.json")


def scrape():
    html = requests.get(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "profile-cards"},
        timeout=30,
    )
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        tip = tips.get(cell.get("id"), "")
        m = re.match(r"(\d+)", tip)
        days.append({"date": cell["data-date"], "count": int(m.group(1)) if m else 0})
    if not days:
        sys.exit("No calendar found: GitHub markup may have changed.")
    return sorted(days, key=lambda d: d["date"])


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # current streak: today may still be empty, so start from yesterday in that case
    i = len(days) - 1
    if days[i]["count"] == 0:
        i -= 1
    current = 0
    while i >= 0 and days[i]["count"]:
        current += 1
        i -= 1
    return current, longest


def main():
    days = scrape()
    months = OrderedDict()
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    data = {
        "user": USER,
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"]),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "months": [{"month": k, "total": v} for k, v in months.items()],
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"{data['total']} contributions, streak {current}, longest {longest}")


if __name__ == "__main__":
    main()

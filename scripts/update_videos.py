"""Trägt die neuesten YouTube Videos zwischen die VIDEOS Marker im README ein.

Läuft täglich per GitHub Action. Keine Abhängigkeiten außer der Standardbibliothek.
"""

from __future__ import annotations

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCv6ihOMjTq6zdJC7IbCdpKQ"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
README = Path(__file__).resolve().parent.parent / "README.md"
MAX_VIDEOS = 4
PER_ROW = 2

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}

PLACEHOLDER = (
    '<p align="center"><sub>☾ Das erste Video ist in Arbeit. '
    "Sobald es online ist, erscheint es hier automatisch.</sub></p>"
)


def fetch_videos() -> list[dict]:
    req = urllib.request.Request(FEED, headers={"User-Agent": "solo-stack-profile"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    videos = []
    for entry in root.findall("a:entry", NS)[:MAX_VIDEOS]:
        vid = entry.findtext("yt:videoId", namespaces=NS)
        title = entry.findtext("a:title", namespaces=NS) or ""
        published = (entry.findtext("a:published", namespaces=NS) or "")[:10]
        if vid:
            videos.append({"id": vid, "title": title.strip(), "date": published})
    return videos


def fmt_date(iso: str) -> str:
    y, m, d = iso.split("-") if iso.count("-") == 2 else ("", "", "")
    return f"{d}.{m}.{y}" if y else ""


def render(videos: list[dict]) -> str:
    if not videos:
        return PLACEHOLDER
    cells = []
    for v in videos:
        url = f"https://www.youtube.com/watch?v={v['id']}"
        thumb = f"https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg"
        title = html.escape(v["title"])
        cells.append(
            f'<td width="50%" align="center" valign="top">'
            f'<a href="{url}"><img src="{thumb}" alt="{title}" width="100%"></a><br>'
            f'<a href="{url}"><b>{title}</b></a><br><sub>{fmt_date(v["date"])}</sub></td>'
        )
    rows = [
        "<tr>" + "".join(cells[i : i + PER_ROW]) + "</tr>" for i in range(0, len(cells), PER_ROW)
    ]
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    block = render(fetch_videos())
    pattern = re.compile(r"(<!-- VIDEOS:START -->)(.*?)(<!-- VIDEOS:END -->)", re.S)
    if not pattern.search(readme):
        print("Marker fehlen im README", file=sys.stderr)
        return 1
    updated = pattern.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", readme)
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print("README aktualisiert")
    else:
        print("Keine Änderungen")
    return 0


if __name__ == "__main__":
    sys.exit(main())

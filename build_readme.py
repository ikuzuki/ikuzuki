"""Rewrite the writing list in README.md from the site's RSS feed."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://isseikuzuki.co.uk/rss.xml"
README = Path(__file__).parent / "README.md"
LIMIT = 5
BLOCK = re.compile(r"(<!-- writing:start -->).*?(<!-- writing:end -->)", re.DOTALL)


def latest_posts() -> list[str]:
    with urllib.request.urlopen(FEED_URL, timeout=30) as resp:
        channel = ET.fromstring(resp.read()).find("channel")
    items = [
        (
            parsedate_to_datetime(item.findtext("pubDate")),
            item.findtext("title").strip(),
            item.findtext("link").strip(),
        )
        for item in channel.findall("item")
    ]
    items.sort(reverse=True)
    return [
        f"- [{title.replace('[', '(').replace(']', ')')}]({link}) · {date:%d %b %Y}"
        for date, title, link in items[:LIMIT]
    ]


def main() -> None:
    posts = latest_posts()
    if not posts:
        raise SystemExit("feed returned no posts; leaving README untouched")
    text = README.read_text(encoding="utf-8")
    if not BLOCK.search(text):
        raise SystemExit("writing markers not found in README.md")
    README.write_text(
        BLOCK.sub(lambda m: "\n".join([m.group(1), *posts, m.group(2)]), text),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

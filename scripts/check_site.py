"""Check the generated site before deployment; uses only the Python standard library."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "dist"
errors = []


def check_link(source, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return
    path = unquote(parts.path)
    target = ROOT / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not target.is_file() and not (target / "index.html").is_file():
        errors.append(f"{source.relative_to(ROOT)}: missing {url}")


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                check_link(self.source, value)


for required in ("index.html", "notes/index.html", "404.html", "style.css", "atom.xml"):
    if not (ROOT / required).is_file():
        raise SystemExit(f"Missing required build output: {required}")

pages = list(ROOT.rglob("*.html"))
for source in pages:
    parser = Links()
    parser.source = source
    parser.feed(source.read_text(encoding="utf-8"))

feed = ET.parse(ROOT / "atom.xml")
entries = feed.findall("{http://www.w3.org/2005/Atom}entry")
if not entries:
    errors.append("atom.xml: no posts")
for entry in entries:
    link = entry.find("{http://www.w3.org/2005/Atom}link")
    if link is None or not link.get("href"):
        errors.append("atom.xml: entry is missing its post link")
    else:
        url = urlsplit(link.get("href"))
        if url.scheme not in {"http", "https"} or not url.netloc:
            errors.append("atom.xml: entry link must be an absolute HTTP(S) URL")
        elif url.netloc == "akshitkr.com":
            check_link(ROOT / "atom.xml", url.path)

if errors:
    raise SystemExit("\n".join(sorted(set(errors))))
print(f"Checked {len(pages)} HTML pages, local links/assets, and {len(entries)} feed entries.")

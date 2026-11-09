# /// script
# requires-python = ">=3.11"
# dependencies = ["Markdown>=3.7,<4", "PyYAML>=6,<7"]
# ///
"""Build the blog: uv run build.py. Output is disposable HTML in dist/."""

from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from string import Template
from xml.etree import ElementTree as ET
import re
import shutil

import markdown
import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
URL = "https://akshitkr.com"
TEMPLATE = Template((ROOT / "site/page.html").read_text())


def read_post(path):
    _, front, body = path.read_text().split("---", 2)
    return yaml.safe_load(front), body


def render(body):
    # Protect display equations from Markdown's underscore/escape processing.
    equations = []

    def save_math(match):
        equations.append(match.group())
        return f"\n\nMATHPLACEHOLDER{len(equations) - 1}END\n\n"

    body = re.sub(r"\$\$.*?\$\$", save_math, body, flags=re.S)
    html = markdown.markdown(body, extensions=["extra", "sane_lists"])
    for i, equation in enumerate(equations):
        html = html.replace(f"MATHPLACEHOLDER{i}END", escape(equation))
    return html


def write(path, content):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def page(title, path, body, description="Notes by Akshit Kumar.", math=False):
    return TEMPLATE.substitute(
        title=escape(title), canonical=escape(URL + path, quote=True),
        description=escape(description, quote=True), content=body,
        scripts=('<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/'
                 'tex-mml-chtml.js"></script>' if math else ""),
    )


def build():
    posts = []
    for source in sorted((ROOT / "_posts").iterdir()):
        if source.suffix not in {".md", ".markdown"}:
            continue
        meta, body = read_post(source)
        if meta.get("published") is False:
            continue
        year, month, day, slug = source.stem.split("-", 3)
        published = meta.get("date", date(int(year), int(month), int(day)))
        if isinstance(published, str):
            published = datetime.fromisoformat(published)
        if not isinstance(published, datetime):
            published = datetime.combine(published, datetime.min.time())
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        categories = meta.get("categories", [])
        if isinstance(categories, str):
            categories = categories.split()
        # Match the existing Jekyll "pretty" URLs, including category paths.
        slug = slug.strip("-").lower()
        path = "/" + "/".join([
            *categories, published.strftime("%Y/%m/%d"), slug, ""
        ])
        posts.append(dict(meta, url=path, date=published, html=render(body),
                          math=meta.get("math", False) or "$$" in body))
    posts.sort(key=lambda p: p["date"], reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "public", OUT,
                    ignore=shutil.ignore_patterns(".DS_Store", "*~"))
    shutil.copyfile(ROOT / "site/style.css", OUT / "style.css")
    for post in posts:
        stamp = post["date"].date().isoformat()
        body = (f'<article><h1>{escape(post["title"])}</h1>'
                f'<p><time datetime="{stamp}">{stamp}</time></p>'
                f'{post["html"]}</article>')
        write(post["url"].lstrip("/") + "index.html",
              page(post["title"], post["url"], body,
                   post.get("description", post["title"]), post["math"]))
    home = (ROOT / "site/home.html").read_text() + "\n<h2>Notes</h2>\n<ul>\n"
    for post in posts:
        if not post.get("hide_from_home", False):
            stamp = post["date"].date().isoformat()
            home += (f'<li><a href="{escape(post["url"], quote=True)}">'
                     f'{escape(post["title"])}</a> '
                     f'<small><time datetime="{stamp}">{stamp}</time></small></li>\n')
    home += "</ul>\n<h2>Projects</h2>\n<ul>\n"
    for project in yaml.safe_load((ROOT / "_data/projects.yml").read_text()):
        home += (f'<li><a href="{escape(project["url"], quote=True)}">'
                 f'{escape(project["title"])}</a>'
                 f'<p>{escape(project["description"])}</p></li>\n')
    write("index.html", page("Akshit Kumar", "/", home + "</ul>"))
    write("404.html", page("Page not found", "/404.html",
          '<h1>Page not found</h1><p><a href="/">Back to the homepage</a>.</p>'))
    # Preserve old archive and About links.
    write("_redirects", "/page2/ / 301\n/page2 / 301\n"
          "/about/ / 301\n/about / 301\n/about/index.html / 301\n")
    namespace = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", namespace)

    def element(parent, tag, text=None, **attributes):
        child = ET.SubElement(parent, f"{{{namespace}}}{tag}", attributes)
        child.text = text
        return child

    feed = ET.Element(f"{{{namespace}}}feed")
    element(feed, "title", "Akshit Kumar")
    element(feed, "id", URL + "/")
    element(feed, "link", href=URL + "/atom.xml", rel="self")
    element(feed, "link", href=URL + "/")
    element(feed, "updated", posts[0]["date"].isoformat())
    element(element(feed, "author"), "name", "Akshit Kumar")
    for post in posts:
        entry = element(feed, "entry")
        element(entry, "title", post["title"])
        element(entry, "id", URL + post["url"])
        element(entry, "link", href=URL + post["url"])
        element(entry, "updated", post["date"].isoformat())
        element(entry, "content", post["html"], type="html")
    ET.ElementTree(feed).write(OUT / "atom.xml", encoding="utf-8", xml_declaration=True)
    print(f"Built {len(posts)} posts in {OUT}")


if __name__ == "__main__":
    build()

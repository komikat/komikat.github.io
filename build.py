# /// script
# requires-python = ">=3.11"
# dependencies = ["Markdown>=3.7,<4", "PyYAML>=6,<7"]
# ///
"""Build the notebook: uv run build.py. Output is disposable HTML in dist/."""

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
        masthead=('<h1>Akshit Kumar</h1>' if path == "/"
                  else '<a class="home-link" href="/">← Akshit Kumar</a>'),
        scripts=('<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/'
                 'tex-mml-chtml.js"></script>' if math else ""),
    )


def render_entry(title, url, metadata, description="", links=()):
    html = (f'<li><div class="entry-heading"><a href="{escape(url, quote=True)}">'
            f'{escape(title)}</a><span class="entry-meta">{metadata}</span></div>')
    if description:
        html += f'<p class="entry-description">{escape(description)}</p>'
    if links:
        html += '<p class="entry-links">' + ' · '.join(
            f'<a href="{escape(link["url"], quote=True)}">{escape(link["title"])}</a>'
            for link in links
        ) + '</p>'
    return html + '</li>\n'


def note_entry(post, compact=False):
    stamp = post["date"].date().isoformat()
    label = post["date"].strftime("%b %Y") if compact else stamp
    metadata = f'<time datetime="{stamp}">{label}</time>'
    title = post["title"]
    if post.get("external_url"):
        title += " ↗"
        metadata = escape(post["source"]) + " · " + metadata
    return render_entry(title, post["url"], metadata)


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
        posts.append(dict(meta, url=meta.get("external_url", path), date=published, html=render(body),
                          math=meta.get("math", False) or "$$" in body))
    posts.sort(key=lambda p: p["date"], reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "public", OUT,
                    ignore=shutil.ignore_patterns(".DS_Store", "*~"))
    shutil.copyfile(ROOT / "site/style.css", OUT / "style.css")
    for post in posts:
        if post.get("external_url"):
            continue
        stamp = post["date"].date().isoformat()
        body = (f'<article><h1>{escape(post["title"])}</h1>'
                f'<p><time datetime="{stamp}">{stamp}</time></p>'
                f'{post["html"]}</article>')
        write(post["url"].lstrip("/") + "index.html",
              page(post["title"], post["url"], body,
                   post.get("description", post["title"]), post["math"]))
    home = ((ROOT / "site/home.html").read_text()
            + '\n<section class="home-section"><h2>Notes</h2>\n<ul class="entries notes" role="list">\n')
    listed_posts = [p for p in posts if not p.get("hide_from_home", False)]
    home += ''.join(note_entry(post, compact=True) for post in listed_posts[:5])
    home += ('</ul><p class="archive-link"><a href="/notes/">All notes →</a></p>'
             '</section>\n<section class="home-section"><h2>Selected work</h2>\n<ul class="entries" role="list">\n')
    for project in yaml.safe_load((ROOT / "_data/projects.yml").read_text()):
        home += render_entry(project["title"], project["url"], escape(project.get("date", "")),
                            project.get("description", ""), project.get("links", []))
    home += '</ul></section>' + (ROOT / "site/poem.html").read_text()
    write("index.html", page("Akshit Kumar", "/", home))
    archive = '<h1>Notes</h1><ul class="entries notes" role="list">'
    archive += ''.join(note_entry(post) for post in listed_posts)
    write("notes/index.html", page("Notes", "/notes/", archive + '</ul>'))
    write("404.html", page("Page not found", "/404.html",
          '<h1>Page not found</h1><p><a href="/">Back to the homepage</a>.</p>'))
    # Preserve old archive, About, and writing links.
    write("_redirects", "/page2/ / 301\n/page2 / 301\n"
          "/about/ / 301\n/about / 301\n/about/index.html / 301\n"
          "/writing/ /notes/ 301\n/writing /notes/ 301\n/writing/index.html /notes/ 301\n")
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
        link = post["url"] if post.get("external_url") else URL + post["url"]
        element(entry, "title", post["title"])
        element(entry, "id", link)
        element(entry, "link", href=link)
        element(entry, "updated", post["date"].isoformat())
        element(entry, "content", post["html"], type="html")
    ET.ElementTree(feed).write(OUT / "atom.xml", encoding="utf-8", xml_declaration=True)
    print(f"Built {len(posts)} notes in {OUT}")


if __name__ == "__main__":
    build()

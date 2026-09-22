#!/usr/bin/env python3
"""Validate the static site before publishing.

Checks internal links and asset references resolve, JSON-LD parses, canonical
and hreflang tags are self-consistent, and every page is listed in sitemap.xml.

    python3 tools/check_site.py            # local checks only
    python3 tools/check_site.py --external # also probe outbound links
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

DIST = Path(__file__).resolve().parent.parent / "dist"
SITE = "https://qishanlabs.com"

problems: list[str] = []
external: set[str] = set()


def fail(page: Path, message: str) -> None:
    problems.append(f"{page.relative_to(DIST)}: {message}")


class Collector(HTMLParser):
    """Collect links, asset references, ids and head metadata."""

    ATTR_BY_TAG = {
        "a": "href",
        "link": "href",
        "img": "src",
        "script": "src",
        "source": "src",
        "iframe": "src",
    }

    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.canonical: str | None = None
        self.hreflang: dict[str, str] = {}
        self.meta: dict[str, str] = {}
        self.jsonld: list[str] = []
        self.lang: str | None = None
        self.h1 = 0
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if "id" in a:
            self.ids.add(a["id"])
        rel = (a.get("rel") or "").lower() if tag == "link" else ""
        attr = self.ATTR_BY_TAG.get(tag)
        # canonical and hreflang links are absolute by definition; they are
        # validated separately rather than as navigable references.
        if attr and a.get(attr) and rel not in {"canonical", "alternate"}:
            self.refs.append((tag, a[attr]))
        if tag == "link":
            if rel == "canonical":
                self.canonical = a.get("href")
            elif rel == "alternate" and a.get("hreflang"):
                self.hreflang[a["hreflang"]] = a.get("href", "")
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_jsonld and data.strip():
            self.jsonld.append(data)


def resolve(page: Path, href: str) -> Path | None:
    """Map a site-relative href to the file that should serve it."""
    path = urlparse(href).path
    if path.startswith("/"):
        target = DIST / path.lstrip("/")
    else:
        target = (page.parent / path).resolve()
    if target.is_dir() or href.endswith("/"):
        target = target / "index.html"
    return target


def check_page(page: Path) -> Collector:
    parser = Collector()
    parser.feed(page.read_text(encoding="utf-8"))

    route = "/" + str(page.relative_to(DIST).parent).replace(".", "").strip("/")
    route = (route.rstrip("/") + "/").replace("//", "/")

    if parser.h1 != 1:
        fail(page, f"expected exactly one <h1>, found {parser.h1}")
    if not parser.lang:
        fail(page, "missing <html lang>")

    noindex = "noindex" in parser.meta.get("robots", "")
    if not noindex:
        for required in ("description", "og:title", "og:url", "og:image"):
            if not parser.meta.get(required):
                fail(page, f"missing meta {required}")
        if not parser.canonical:
            fail(page, "missing canonical")
        elif parser.canonical != f"{SITE}{route}":
            fail(page, f"canonical {parser.canonical} does not match route {route}")
        if "x-default" not in parser.hreflang:
            fail(page, "missing hreflang x-default")

    for block in parser.jsonld:
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            fail(page, f"invalid JSON-LD: {exc}")

    for tag, href in parser.refs:
        href, fragment = urldefrag(href)
        if href.startswith(("mailto:", "tel:", "data:", "javascript:")):
            continue
        if href.startswith(("http://", "https://")):
            if href.startswith(SITE):
                fail(page, f"absolute self link should be relative: {href}")
            else:
                external.add(href)
            continue
        if not href:
            if fragment and fragment not in parser.ids:
                fail(page, f"fragment #{fragment} has no matching id")
            continue
        target = resolve(page, href.split("?", 1)[0])
        if target is None or not target.exists():
            fail(page, f"<{tag}> broken reference: {href}")

    return parser


def main() -> int:
    pages = sorted(DIST.rglob("index.html")) + [DIST / "404.html"]
    parsed = {page: check_page(page) for page in pages}

    # hreflang pairs must point back at each other.
    by_url = {p.canonical: p for p in parsed.values() if p.canonical}
    for page, parser in parsed.items():
        for lang, href in parser.hreflang.items():
            if lang == "x-default":
                continue
            other = by_url.get(href)
            if other is None:
                fail(page, f"hreflang {lang} points at unknown page {href}")
            elif other.hreflang.get(lang) != href:
                fail(page, f"hreflang {lang} is not reciprocated by {href}")

    # Every indexable page must be in the sitemap, and vice versa.
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    listed = {u.text for u in ET.parse(DIST / "sitemap.xml").getroot().findall("s:url/s:loc", ns)}
    indexable = {
        p.canonical
        for page, p in parsed.items()
        if p.canonical and "noindex" not in p.meta.get("robots", "")
    }
    for missing in sorted(indexable - listed):
        problems.append(f"sitemap.xml: missing {missing}")
    for extra in sorted(listed - indexable):
        problems.append(f"sitemap.xml: lists unknown page {extra}")

    if "--external" in sys.argv:
        import urllib.error
        import urllib.request

        agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"

        def probe(url: str, method: str):
            request = urllib.request.Request(url, method=method, headers={"User-Agent": agent})
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    return response.status
            except urllib.error.HTTPError as exc:
                return exc.code
            except Exception as exc:  # noqa: BLE001 - report and continue
                return f"error {exc}"

        for url in sorted(external):
            status = probe(url, "HEAD")
            if status != 200:  # some hosts reject HEAD from non-browsers
                status = probe(url, "GET")
            if status != 200:
                problems.append(f"external link {url}: {status}")
            print(f"  {status}  {url}")

    print(f"\nchecked {len(pages)} pages, {len(external)} distinct external links")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("no problems found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

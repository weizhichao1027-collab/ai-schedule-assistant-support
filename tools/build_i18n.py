#!/usr/bin/env python3
"""Generate the 11 non-Chinese, non-English locales of the site.

Chinese (zh-Hans) and English pages are hand-maintained and left in place.
This adds zh-Hant, ja, ko, de, fr, es, pt, ru, ar, hi and id, each with a
company home, product page, support page, privacy policy and terms page, and
then rewrites hreflang, the language switcher and sitemap.xml for ALL pages so
the 13 languages cross-link consistently.

    python3 tools/build_i18n.py

Translations of the privacy policy and terms carry a clause stating that the
Chinese and English versions are the authoritative text.
"""

import json
import re
import subprocess
import tempfile
from html import escape
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
RAW = REPO.parent / "多语言商店截图_2026-09-11" / "raw"
SITE = "https://qishanlabs.com"
CSS = "20260922c"
APP = "https://apps.apple.com/app/id6764322744"
MAIL = "weizhichao@qishanlabs.com"
SHOTS = ["hero", "calendar", "accounting", "input", "statistics", "analysis"]

# hreflang code -> (url slug, raw screenshot locale, native name, text direction)
LANGS = [
    ("zh-Hans", "", "zh-Hans", "简体中文", "ltr"),
    ("zh-Hant", "zh-Hant", "zh-Hant", "繁體中文", "ltr"),
    ("en", "en", "en", "English", "ltr"),
    ("ja", "ja", "ja", "日本語", "ltr"),
    ("ko", "ko", "ko", "한국어", "ltr"),
    ("de", "de", "de", "Deutsch", "ltr"),
    ("fr", "fr", "fr", "Français", "ltr"),
    ("es", "es", "es", "Español", "ltr"),
    ("pt-BR", "pt", "pt-BR", "Português", "ltr"),
    ("ru", "ru", "ru", "Русский", "ltr"),
    ("ar", "ar", "ar", "العربية", "rtl"),
    ("hi", "hi", "hi", "हिन्दी", "ltr"),
    ("id", "id", "id", "Indonesia", "ltr"),
]
BY_CODE = {code: (slug, raw, name, direction) for code, slug, raw, name, direction in LANGS}
GENERATED = [code for code, slug, *_ in LANGS if slug and code != "en"]
KINDS = ["home", "product", "support", "privacy", "terms"]


def rel(code: str, kind: str) -> str:
    slug = BY_CODE[code][0]
    tail = {"home": [], "product": ["products", "jotit"], "support": ["support"],
            "privacy": ["privacy"], "terms": ["terms"]}[kind]
    parts = ([slug] if slug else []) + tail
    return "/" + "/".join(parts) + "/" if parts else "/"


def url(code: str, kind: str) -> str:
    return SITE + rel(code, kind)


def kind_of(page: Path) -> str:
    parts = page.relative_to(DIST).parts[:-1]
    rest = parts[1:] if parts and parts[0] in {slug for _, slug, *_ in LANGS if slug} else parts
    return {(): "home", ("products", "jotit"): "product", ("support",): "support",
            ("privacy",): "privacy", ("terms",): "terms"}[rest]


def code_of(page: Path) -> str:
    parts = page.relative_to(DIST).parts[:-1]
    if parts and parts[0] in {slug for _, slug, *_ in LANGS if slug}:
        return next(code for code, slug, *_ in LANGS if slug == parts[0])
    return "zh-Hans"


# --- assets -----------------------------------------------------------------

def build_shots() -> None:
    for code in GENERATED:
        raw_locale = BY_CODE[code][1]
        for name in SHOTS:
            src = Image.open(RAW / raw_locale / f"{name}.png").convert("RGB")
            src = src.resize((520, round(src.height * 520 / src.width)), Image.LANCZOS)
            dest = DIST / "assets" / "shots" / BY_CODE[code][0] / f"{name}.webp"
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                src.save(tmp.name)
                subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", tmp.name, "-o", str(dest)], check=True)
            Path(tmp.name).unlink()


# --- page chrome ------------------------------------------------------------

def hreflang_block(kind: str) -> str:
    lines = [f'<link rel="alternate" hreflang="{code}" href="{url(code, kind)}">' for code, *_ in LANGS]
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{url("zh-Hans", kind)}">')
    return "\n  ".join(lines)


def switcher(current: str, kind: str) -> str:
    items = []
    for code, *_rest in LANGS:
        name = BY_CODE[code][2]
        current_attr = ' aria-current="true"' if code == current else ""
        items.append(f'<li><a href="{rel(code, kind)}" lang="{code}" hreflang="{code}"{current_attr}>{escape(name)}</a></li>')
    label = BY_CODE[current][2]
    return ('<!-- langswitch --><details class="lang"><summary>' + escape(label) +
            '</summary><ul>' + "".join(items) + '</ul></details><!-- /langswitch -->')


def head(code: str, kind: str, title: str, description: str, jsonld: dict) -> str:
    direction = BY_CODE[code][3]
    slug = BY_CODE[code][0]
    canonical = url(code, kind)
    image = f"{SITE}/assets/og-jotit-zh.png" if code.startswith("zh") else f"{SITE}/assets/og-jotit-en.png"
    return f'''<!doctype html>
<html lang="{code}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f7f7fc">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="apple-itunes-app" content="app-id=6764322744">
  <link rel="canonical" href="{canonical}">
  {hreflang_block(kind)}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="JotIt">
  <meta property="og:locale" content="{code}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{image}">
  <link rel="icon" type="image/png" sizes="48x48" href="/assets/favicon-48.png?v={CSS}">
  <link rel="apple-touch-icon" href="/assets/app-icon-192.png?v={CSS}">
  <link rel="stylesheet" href="/style.css?v={CSS}">
  <script type="application/ld+json">
  {json.dumps(jsonld, ensure_ascii=False, indent=2)}
  </script>
</head>
'''


def header(code: str, kind: str, t: dict) -> str:
    slug = BY_CODE[code][0]
    brand_href = rel(code, "product")

    def item(label: str, target: str) -> str:
        current = ' aria-current="page"' if target == kind else ""
        return f'<a href="{rel(code, target)}"{current}>{escape(t[label])}</a>'

    nav = item("nav_product", "product") + item("nav_support", "support") + item("nav_privacy", "privacy") + item("nav_terms", "terms")
    return f'''<body>
  <a class="skip-link" href="#main">{escape(t["skip"])}</a>
  <header class="site-header shell">
    <a class="brand" href="{brand_href}" aria-label="JotIt">
      <img class="brand-icon" src="/assets/app-icon-192.png?v={CSS}" alt="" width="44" height="44">
      <span class="brand-copy"><strong>JotIt</strong><small>{escape(t["brand_sub"])}</small></span>
    </a>
    <nav class="site-nav" aria-label="{escape(t["nav_label"])}">{nav}{switcher(code, kind)}</nav>
  </header>
'''


def footer(code: str, t: dict) -> str:
    links = [("product", "nav_product"), ("support", "nav_support"), ("privacy", "nav_privacy"), ("terms", "nav_terms")]
    nav = "".join(f'<a href="{rel(code, k)}">{escape(t[label])}</a>' for k, label in links)
    return f'''  <footer class="site-footer">
    <div class="shell footer-grid">
      <div><strong>JotIt · Qishan Labs</strong><p>{escape(t["footer_operator"])}</p></div>
      <nav aria-label="footer">{nav}<a href="{APP}">App Store</a><a href="mailto:{MAIL}">{escape(t["footer_contact"])}</a></nav>
    </div>
    <div class="shell footer-bottom"><span>{escape(t["footer_filing"])}</span><span>© 2026 上海祁杉文化传播有限公司</span></div>
  </footer>
</body>
</html>
'''


def badge(label: str) -> str:
    return (f'<a class="store-badge" href="{APP}"><img src="/assets/app-store-badge.svg" '
            f'alt="{escape(label)}" width="162" height="54"></a>')


# --- pages ------------------------------------------------------------------

def jsonld_for(code: str, kind: str, t: dict) -> dict:
    org = {"@type": "Organization", "@id": f"{SITE}/#organization",
           "name": "Shanghai Qishan Cultural Communication Co., Ltd.",
           "alternateName": ["上海祁杉文化传播有限公司", "Qishan Labs"],
           "url": f"{SITE}/", "email": MAIL, "logo": f"{SITE}/assets/app-icon-192.png"}
    node: dict
    if kind == "product":
        node = {"@type": "MobileApplication", "name": "JotIt", "operatingSystem": "iOS 17.0 or later",
                "applicationCategory": "ProductivityApplication", "softwareVersion": "1.0.3",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                "downloadUrl": APP, "inLanguage": code}
    elif kind == "support":
        node = {"@type": "FAQPage", "inLanguage": code, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}}
            for q, a in t["faqs"]]}
    else:
        node = {"@type": "WebPage" if kind in ("privacy", "terms") else "WebSite", "inLanguage": code}
    node.update({"url": url(code, kind), "publisher": {"@id": f"{SITE}/#organization"}})
    crumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Qishan Labs", "item": url(code, "home")},
        {"@type": "ListItem", "position": 2, "name": "JotIt", "item": url(code, "product")}]}
    graph = [node, org, crumb]
    return {"@context": "https://schema.org", "@graph": graph}


def page_product(code: str, t: dict) -> str:
    slug = BY_CODE[code][0]
    gallery = []
    for name, (alt, cap_title, cap) in zip(SHOTS, t["gallery"]):
        gallery.append(
            f'<li><figure><img src="/assets/shots/{slug}/{name}.webp" width="520" height="1130" '
            f'loading="lazy" decoding="async" alt="{escape(alt)}"><figcaption><strong>{escape(cap_title)}</strong>{escape(cap)}</figcaption></figure></li>')
    highlights = "".join(f'<li><span aria-hidden="true">✓</span><div><strong>{escape(h)}</strong><small>{escape(s)}</small></div></li>' for h, s in t["highlights"])
    trust = "".join(f'<div><strong>{escape(a)}</strong><span>{escape(b)}</span></div>' for a, b in t["trust"])
    steps = "".join(f'<li><span>{i}</span><div><h3>{escape(h)}</h3><p>{escape(p)}</p></div></li>' for i, (h, p) in enumerate(t["steps"], 1))
    features = "".join(f'<article><strong>{escape(h)}</strong><p>{escape(p)}</p></article>' for h, p in t["features"])
    principles = "".join(f'<article><span>{escape(tag)}</span><h3>{escape(h)}</h3><p>{escape(p)}</p></article>' for tag, h, p in t["principles"])
    plans = "".join(f'<article><strong>{escape(h)}</strong><p>{escape(p)}</p></article>' for h, p in t["plans"])
    facts = "".join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in t["facts"])
    notes = "".join(f'<li>{escape(n)}</li>' for n in t["rel_items"])
    routes = [("privacy", "01"), ("support", "02"), ("terms", "03")]
    route_html = "".join(
        f'<a class="route-card" href="{rel(code, k)}"><span class="route-number" aria-hidden="true">{n}</span>'
        f'<div><h3>{escape(h)}</h3><p>{escape(p)}</p></div><span class="route-arrow" aria-hidden="true">→</span></a>'
        for (k, n), (h, p) in zip(routes, t["routes"]))
    return f'''<main id="main" class="shell page-main">
    <section class="hero"><div class="hero-copy">
        <p class="eyebrow"><span class="status-dot" aria-hidden="true"></span>{escape(t["eyebrow"])}</p>
        <h1>{escape(t["h1a"])}<span>{escape(t["h1b"])}</span></h1>
        <p class="hero-lede">{escape(t["lede"])}</p>
        <div class="store-actions">{badge(t["badge_alt"])}<a class="button button-secondary" href="#screens">{escape(t["see"])}</a></div>
        <p class="store-note">{escape(t["note"])}</p>
      </div>
      <div class="hero-panel"><div class="app-tile"><img src="/assets/app-icon-192.png?v={CSS}" alt="JotIt" width="112" height="112"><div><strong>JotIt</strong><span>{escape(t["brand_sub"])}</span></div></div><ul class="feature-list">{highlights}</ul></div>
    </section>
    <section class="trust-strip">{trust}</section>
    <section id="screens" class="section-block"><div class="section-heading"><p class="eyebrow">{escape(t["gal_eyebrow"])}</p><h2>{escape(t["gal_h2"])}</h2></div><div class="gallery-scroll" tabindex="0"><ul class="gallery">{"".join(gallery)}</ul></div></section>
    <section class="section-block"><div class="section-heading compact"><p class="eyebrow">{escape(t["how_eyebrow"])}</p><h2>{escape(t["how_h2"])}</h2></div><ol class="steps">{steps}</ol></section>
    <section class="section-block"><div class="section-heading"><p class="eyebrow">{escape(t["feat_eyebrow"])}</p><h2>{escape(t["feat_h2"])}</h2></div><div class="summary-grid">{features}</div></section>
    <section class="principles"><div class="section-heading compact"><p class="eyebrow">{escape(t["priv_eyebrow"])}</p><h2>{escape(t["priv_h2"])}</h2></div><div class="principle-grid">{principles}</div><p class="store-note">{t["priv_note"]}</p></section>
    <section class="section-block"><div class="section-heading"><p class="eyebrow">{escape(t["price_eyebrow"])}</p><h2>{escape(t["price_h2"])}</h2></div><div class="summary-grid">{plans}</div><section class="document-card legal-copy" style="margin-top:20px"><p>{escape(t["price_p1"])}</p><p><strong>{escape(t["price_p2"])}</strong></p><p><a href="{rel(code, "terms")}">{escape(t["price_link"])}</a></p></section></section>
    <section id="facts" class="section-block"><div class="section-heading compact"><p class="eyebrow">{escape(t["facts_eyebrow"])}</p><h2>{escape(t["facts_h2"])}</h2></div><dl class="fact-list">{facts}</dl></section>
    <section class="section-block"><div class="section-heading compact"><p class="eyebrow">{escape(t["rel_eyebrow"])}</p><h2>{escape(t["rel_h2"])}</h2></div><div class="document-card legal-copy"><div class="release-note"><div class="release-version"><strong>{escape(t["rel_ver"])}</strong><span>{escape(t["rel_date"])}</span></div><ul>{notes}</ul></div></div></section>
    <section class="section-block"><div class="section-heading"><p class="eyebrow">{escape(t["routes_eyebrow"])}</p><h2>{escape(t["routes_h2"])}</h2></div><div class="route-grid">{route_html}</div></section>
    <section class="contact-panel"><div><p class="eyebrow">{escape(t["cta_eyebrow"])}</p><h2>{escape(t["cta_h2"])}</h2><p>{escape(t["cta_p"])}</p></div><div class="contact-actions">{badge(t["badge_alt"])}<a class="text-link" href="{rel(code, "support")}">{escape(t["cta_link"])} <span aria-hidden="true">→</span></a></div></section>
  </main>'''


def page_support(code: str, t: dict) -> str:
    faqs = "".join(
        f'<details><summary><span>{escape(q)}</span><i aria-hidden="true"></i></summary><div class="faq-answer"><p>{a}</p></div></details>'
        for q, a in t["faqs"])
    steps = "".join(f'<li><span>{i}</span><div><h3>{escape(h)}</h3><p>{escape(p)}</p></div></li>' for i, (h, p) in enumerate(t["steps"], 1))
    trust = "".join(f'<div><strong>{escape(a)}</strong><span>{escape(b)}</span></div>' for a, b in t["trust"])
    facts = "".join(f'<div><dt>{escape(k)}</dt><dd>{v}</dd></div>' for k, v in t["facts"])
    return f'''<main id="main" class="shell page-main">
    <section class="support-hero"><div>
        <p class="eyebrow">Support</p><h1>{escape(t["h1"])}</h1><p>{escape(t["lede"])}</p>
        <div class="button-row"><a class="button button-primary" href="mailto:{MAIL}">{escape(t["email_btn"])}</a><a class="button button-secondary" href="#faq">{escape(t["faq_btn"])}</a></div>
      </div><div class="support-card"><span class="support-badge"><i aria-hidden="true"></i>{escape(t["badge"])}</span><strong>{MAIL}</strong><p>{escape(t["email_note"])}</p></div>
    </section>
    <section class="trust-strip">{trust}</section>
    <section class="section-block"><div class="section-heading compact"><p class="eyebrow">{escape(t["quick_eyebrow"])}</p><h2>{escape(t["quick_h2"])}</h2></div><ol class="steps">{steps}</ol></section>
    <section id="faq" class="faq-section"><div class="section-heading compact"><p class="eyebrow">{escape(t["faq_eyebrow"])}</p><h2>{escape(t["faq_h2"])}</h2></div><div class="faq-list">{faqs}</div></section>
    <section class="section-block"><div class="section-heading compact"><p class="eyebrow">{escape(t["facts_eyebrow"])}</p><h2>{escape(t["facts_h2"])}</h2></div><dl class="fact-list">{facts}</dl></section>
    <section class="contact-panel"><div><p class="eyebrow">{escape(t["contact_eyebrow"])}</p><h2>{escape(t["contact_h2"])}</h2><p>{escape(t["contact_p"])}</p></div><div class="contact-actions"><a class="button button-primary" href="mailto:{MAIL}">{escape(t["contact_btn"])}</a><a class="text-link" href="{rel(code, "privacy")}">{escape(t["privacy_link"])} <span aria-hidden="true">→</span></a></div><p class="privacy-note">{escape(t["note"])}</p></section>
  </main>'''


def page_legal(code: str, kind: str, t: dict) -> str:
    summary = "".join(f'<article><strong>{escape(h)}</strong><p>{escape(p)}</p></article>' for h, p in t["summary"])
    sections = "".join(
        f'<section><h2><span>{n}</span>{escape(title)}</h2>{body}</section>'
        for n, title, body in t["sections"])
    return f'''<main id="main" class="shell page-main">
    <section class="document-hero"><p class="eyebrow">{escape(t["eyebrow"])}</p><h1>{escape(t["h1"])}</h1><p class="document-lede">{escape(t["lede"])}</p><div class="document-meta">{"".join(f"<span>{escape(s)}</span>" for s in t["meta"])}</div></section>
    <section class="summary-grid">{summary}</section>
    <p class="store-note">{t["notice"]}</p>
    <article class="document-card legal-copy">{sections}<div class="document-end"><p>{escape(t["updated"])}</p><a class="text-link" href="{rel(code, "support")}">{escape(t["support_link"])} <span aria-hidden="true">→</span></a></div></article>
  </main>'''


def page_home(code: str, t: dict) -> str:
    facts = "".join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in t["facts"])
    return f'''<body class="company-site">
  <a class="skip-link" href="#main">{escape(t["skip"])}</a>
  <header class="site-header shell">
    <a class="brand company-brand" href="{rel(code, "home")}" aria-label="Qishan Labs"><span class="company-mark" aria-hidden="true">Q</span><span class="brand-copy"><strong>Qishan</strong><small>QISHAN LABS</small></span></a>
    <nav class="site-nav" aria-label="{escape(t["nav_label"])}"><a href="#products">{escape(t["nav_apps"])}</a><a href="#about">{escape(t["nav_about"])}</a><a href="#contact">{escape(t["nav_contact"])}</a>{switcher(code, "home")}</nav>
  </header>
  <main id="main">
    <section class="company-hero shell"><p class="eyebrow">QISHAN LABS</p><h1>{t["h1"]}</h1><div class="company-intro"><p>{t["intro"]}</p><a class="button button-primary" href="#products">{escape(t["cta"])}</a></div><div class="company-signature"><span lang="zh-Hans">上海祁杉文化传播有限公司</span><span>Shanghai Qishan Cultural Communication Co., Ltd.</span></div></section>
    <section id="products" class="shell company-section"><div class="company-section-title"><p class="eyebrow">{escape(t["prod_eyebrow"])}</p><h2>{escape(t["prod_h2"])}</h2></div>
      <article class="company-product"><div class="product-identity"><img src="/assets/app-icon-192.png?v={CSS}" alt="JotIt" width="112" height="112"><div><h3>JotIt</h3><p>{escape(t["tagline"])}</p><span class="platform-label">{escape(t["platform"])}</span></div></div>
        <div class="product-description"><h4>{escape(t["h4"])}</h4><p>{escape(t["desc"])}</p><div class="store-actions">{badge(t["badge_alt"])}<a class="button button-secondary" href="{rel(code, "product")}">{escape(t["more"])}</a></div><div class="product-links"><a href="{rel(code, "support")}">{escape(t["nav_support"])}</a><a href="{rel(code, "privacy")}">{escape(t["nav_privacy"])}</a><a href="{rel(code, "terms")}">{escape(t["nav_terms"])}</a></div><p class="product-filing">{escape(t["filing"])}</p></div></article></section>
    <section id="about" class="shell company-section company-about"><div class="company-section-title"><p class="eyebrow">{escape(t["about_eyebrow"])}</p><h2>{t["about_h2"]}</h2></div><div class="company-about-copy"><p>{escape(t["about_p1"])}</p><p>{escape(t["about_p2"])}</p><dl class="company-facts">{facts}</dl></div></section>
    <section id="contact" class="shell company-contact"><div><p class="eyebrow">{escape(t["contact_eyebrow"])}</p><h2>{escape(t["contact_h2"])}</h2><p>{escape(t["contact_p"])}</p></div><a href="mailto:{MAIL}">{MAIL}</a></section>
  </main>
  <footer class="site-footer"><div class="shell footer-grid"><div><strong>Qishan Labs</strong><p>Shanghai Qishan Cultural Communication Co., Ltd.</p></div><nav aria-label="footer"><a href="{rel(code, "product")}">JotIt</a><a href="{rel(code, "support")}">{escape(t["nav_support"])}</a><a href="{rel(code, "privacy")}">{escape(t["nav_privacy"])}</a><a href="{rel(code, "terms")}">{escape(t["nav_terms"])}</a><a href="{APP}">App Store</a><a href="mailto:{MAIL}">{escape(t["nav_contact"])}</a></nav></div><div class="shell footer-bottom"><span>© 2026 Shanghai Qishan Cultural Communication Co., Ltd.</span><span>Qishan Labs</span></div></footer>
</body></html>'''


def render(code: str, kind: str, strings: dict) -> str:
    t = strings[code]
    if kind == "home":
        data = jsonld_for(code, kind, t)
        return head(code, kind, t["home_title"], t["home_desc"], data) + page_home(code, t["home"])
    if kind == "product":
        p = t["product"]
        return head(code, kind, p["meta_title"], p["meta_desc"], jsonld_for(code, kind, p)) + header(code, kind, t) + page_product(code, p) + footer(code, t)
    if kind == "support":
        s = t["support"]
        return head(code, kind, s["meta_title"], s["meta_desc"], jsonld_for(code, kind, s)) + header(code, kind, t) + page_support(code, s) + footer(code, t)
    legal = t[kind]
    return head(code, kind, legal["meta_title"], legal["meta_desc"], jsonld_for(code, kind, legal)) + header(code, kind, t) + page_legal(code, kind, legal) + footer(code, t)


# --- patch existing zh / en pages ------------------------------------------

HREFLANG_RE = re.compile(r'^[ \t]*<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', re.M)
SWITCH_RE = re.compile(r'<!-- langswitch -->.*?<!-- /langswitch -->', re.S)
STRAY_LINK_RE = re.compile(r'\s*<a\b[^>]*\bhreflang="[^"]*"[^>]*>.*?</a>', re.S)


def patch_existing() -> int:
    count = 0
    for page in DIST.rglob("index.html"):
        code = code_of(page)
        if code in GENERATED:
            continue
        kind = kind_of(page)
        text = page.read_text(encoding="utf-8")
        text = HREFLANG_RE.sub("", text)
        text = text.replace('<link rel="canonical"', hreflang_block(kind) + '\n  <link rel="canonical"', 1)
        block = switcher(code, kind)
        if "<!-- langswitch -->" in text:
            text = SWITCH_RE.sub(block, text)
        else:
            text = STRAY_LINK_RE.sub("", text)
            text = text.replace("</nav>", block + "</nav>", 1)
        text = text.replace("style.css?v=20260922b", f"style.css?v={CSS}")
        text = text.replace("style.css?v=20260922", f"style.css?v={CSS}")
        page.write_text(text, encoding="utf-8")
        count += 1
    return count


def build_sitemap() -> None:
    ns = 'xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    lastmod = {"privacy": "2026-09-21", "terms": "2026-09-11"}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" {ns}>']
    for kind in KINDS:
        for code, *_ in LANGS:
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{url(c, kind)}"/>' for c, *_ in LANGS)
            links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{url("zh-Hans", kind)}"/>'
            lines.append(f'  <url><loc>{url(code, kind)}</loc><lastmod>{lastmod.get(kind, "2026-09-22")}</lastmod>{links}</url>')
    lines.append("</urlset>\n")
    (DIST / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    from i18n_strings import STRINGS  # noqa: E402  (sibling module)

    build_shots()
    for code in GENERATED:
        for kind in KINDS:
            target = DIST / rel(code, kind).lstrip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(code, kind, STRINGS), encoding="utf-8")
        print("generated", code)
    print("patched existing pages:", patch_existing())
    build_sitemap()


if __name__ == "__main__":
    main()

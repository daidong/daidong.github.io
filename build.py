#!/usr/bin/env python3
"""Pre-render the site's long-form content into static, crawlable HTML.

The paper reports and blog posts are authored as JSON metadata plus a Markdown
body, and until now they were assembled in the browser. That is fine for a
reader and useless for a crawler: search engines and the retrieval bots behind
LLM assistants (GPTBot, OAI-SearchBot, PerplexityBot, Bingbot) mostly do not run
JavaScript, so they saw an empty page at a single query-string URL.

This script renders the same content ahead of time, one directory per item:

    papers/papers.json + papers/<id>.md    ->  papers/<id>/index.html
    blog/posts.json    + blog/<slug>.md    ->  blog/<slug>/index.html

It also refreshes the two listing pages in place, writes sitemap.xml,
robots.txt and llms.txt, and emits redirect stubs for URLs of the retired
Jekyll site (see REDIRECTS) plus the 404 page.

Usage:

    pip install markdown        # once
    python3 build.py            # before every commit that touches content
"""

import html
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

try:
    import markdown
except ImportError:
    sys.exit("build.py needs the Markdown renderer. Run:  pip install markdown")

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://daidong.github.io"

AUTHOR = {
    "name": "Dong Dai",
    "url": SITE + "/",
    "affiliation": "University of Delaware",
    "sameAs": [
        "https://scholar.google.com/citations?user=wGF_4JsAAAAJ&hl=en",
        "https://github.com/daidong",
        "https://github.com/DIR-LAB",
    ],
}

FOOTER = "<footer>&copy; 2025 Dong Dai. University of Delaware.</footer>"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]


# ── small helpers ────────────────────────────────────────────────────────────

def esc(text):
    """Escape for HTML text and attribute values, matching the old esc() in JS."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    existing = None
    if os.path.exists(full):
        with open(full, encoding="utf-8") as fh:
            existing = fh.read()
    if existing == text:
        return False
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def format_date(iso):
    """'2026-06-23' -> '23 Jun, 2026', the same shape the JS produced."""
    d = datetime.strptime(iso, "%Y-%m-%d")
    return "%d %s, %d" % (d.day, MONTHS[d.month - 1], d.year)


def read_time(md_text):
    """Reading estimate, ported from estimateReadTime() in post.html."""
    plain = re.sub(r"```[\s\S]*?```", "", md_text)
    plain = re.sub(r"`[^`]*`", "", plain)
    plain = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", plain)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
    plain = re.sub(r"[#>*_~]", "", plain)
    cjk = len(re.findall(r"[一-鿿]", plain))
    words = len(re.findall(r"\b[\w']+\b", re.sub(r"[一-鿿]", " ", plain)))
    return "%d min read" % max(1, round(max(words / 200.0, cjk / 400.0)))


def slugify(text, used, allow_cjk):
    """Heading anchor, ported from the two slugify() helpers in the page JS.

    Kept byte-identical to the old behaviour so deep links that are already out
    in the world keep landing on the same section.
    """
    keep = r"[^\w㐀-鿿\s-]" if allow_cjk else r"[^\w\s-]"
    base = re.sub(keep, "", text.strip().lower())
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"-+", "-", base)
    base = base.strip("-")
    if not base:
        base = "section"
    slug, n = base, 2
    while slug in used:
        slug, n = "%s-%d" % (base, n), n + 1
    used.add(slug)
    return slug


def has_cjk(text):
    return bool(re.search(r"[㐀-鿿]", text))


def strip_tags(fragment):
    """Plain text of an HTML fragment — used for headings and meta descriptions."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def truncate(text, limit=155):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


# ── Markdown ─────────────────────────────────────────────────────────────────

def render_markdown(md_text):
    return markdown.Markdown(extensions=MD_EXTENSIONS).convert(md_text)


def absolutize(body, md_dir):
    """Rewrite the Markdown's relative asset and page links to site-absolute.

    The Markdown was written against the old flat URLs (post.html at the site
    root, report.html under /papers/). The generated pages sit one level deeper,
    so every relative href would otherwise break.
    """
    def fix(match):
        attr, url = match.group(1), match.group(2)
        # Old query-string URLs -> the pre-rendered directory for the same item,
        # whether they were written relative or as a full daidong.github.io link.
        m = re.match(r"^(?:%s)?(?:\.\./|\./|/)*post\.html\?slug=([^&#\"']+)(#.*)?$"
                     % re.escape(SITE), url)
        if m:
            return '%s="/blog/%s/%s"' % (attr, m.group(1), m.group(2) or "")
        m = re.match(r"^(?:%s)?(?:\.\./|\./|/)*(?:papers/)?report\.html\?id=([^&#\"']+)(#.*)?$"
                     % re.escape(SITE), url)
        if m:
            return '%s="/papers/%s/%s"' % (attr, m.group(1), m.group(2) or "")
        if re.match(r"^(https?:|mailto:|#|/)", url):
            return match.group(0)
        # Everything else resolves the way the browser resolved it before: from
        # the directory the renderer page lived in, clamped at the site root.
        parts = [p for p in (md_dir + "/" + url).split("/") if p not in ("", ".")]
        out = []
        for part in parts:
            if part == "..":
                if out:
                    out.pop()
            else:
                out.append(part)
        return '%s="/%s"' % (attr, "/".join(out))

    return re.sub(r'\b(src|href)="([^"]*)"', fix, body)


def png_size(site_path):
    """Intrinsic pixel size from a PNG header, or None."""
    local = os.path.join(ROOT, site_path.lstrip("/"))
    if not local.lower().endswith(".png") or not os.path.exists(local):
        return None
    with open(local, "rb") as fh:
        header = fh.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big"))


def size_images(body):
    """Give every local image its intrinsic width and height.

    Without them the browser cannot reserve space, so the page reflows as the
    figures arrive — which both hurts Core Web Vitals and makes a deep link to
    a section land in the wrong place. The CSS already sets height:auto, so the
    attributes only supply the aspect ratio.
    """
    def fix(match):
        tag = match.group(0)
        if "width=" in tag:
            return tag
        src = re.search(r'src="([^"]*)"', tag)
        if not src or not src.group(1).startswith("/"):
            return tag
        size = png_size(src.group(1))
        if not size:
            return tag
        return tag[:-1].rstrip("/") + ' width="%d" height="%d" loading="lazy" decoding="async">' % size

    return re.sub(r"<img\b[^>]*>", fix, body)


def add_heading_ids(body, tags, allow_cjk, stop_at_cjk):
    """Give headings stable ids and collect the table of contents.

    stop_at_cjk reproduces post.html: a bilingual post stops its contents list
    at the first Chinese heading instead of listing both languages.
    """
    used, contents, stopped = set(), [], False
    pattern = re.compile(r"<(%s)([^>]*)>(.*?)</\1>" % "|".join(tags), re.S)

    def repl(match):
        nonlocal stopped
        tag, attrs, inner = match.group(1), match.group(2), match.group(3)
        text = strip_tags(inner)
        if stopped or not text:
            return match.group(0)
        if stop_at_cjk and has_cjk(text):
            stopped = True
            return match.group(0)
        slug = slugify(text, used, allow_cjk)
        contents.append({"id": slug, "text": text, "level": int(tag[1])})
        return '<%s id="%s"%s>%s</%s>' % (tag, esc(slug), attrs, inner, tag)

    return pattern.sub(repl, body), contents


def upgrade_figures(body):
    """Image-only paragraphs become <figure>, tables get a scroll wrapper.

    Ported from upgradeFigures() in report.html; the alt text becomes the caption.
    """
    def to_figure(match):
        img = match.group(1)
        src = re.search(r'src="([^"]*)"', img)
        alt = re.search(r'alt="([^"]*)"', img)
        if not src:
            return match.group(0)
        cap = ""
        if alt and alt.group(1):
            cap = "<figcaption>%s</figcaption>" % esc(html.unescape(alt.group(1)))
        return ('<figure><a href="%s" target="_blank" rel="noopener">%s</a>%s</figure>'
                % (src.group(1), img, cap))

    body = re.sub(r"<p>\s*(<img[^>]*/?>)\s*</p>", to_figure, body)
    return re.sub(r"(<table>)", r'<div class="table-wrap">\1', body).replace(
        "</table>", "</table></div>")


def split_lead_callouts(body):
    """Pull leading .tool-callout blocks out, the way post.html does.

    They are announcements, not part of the article, and they belong above the
    TL;DR card rather than inside the prose.
    """
    lead = []
    pattern = re.compile(r'^\s*<div class="tool-callout"[\s\S]*?\n</div>\s*', re.M)
    while True:
        match = pattern.match(body.lstrip("\n"))
        body = body.lstrip("\n")
        if not match:
            break
        lead.append(match.group(0).strip())
        body = body[match.end():]
    return "\n".join(lead), body


# ── shared page chrome ───────────────────────────────────────────────────────

THEME_SVGS = (
    '<svg class="icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
    '<svg class="icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>'
    '<line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>'
    '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>'
    '<line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>'
    '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
)

NAV_ITEMS = [
    ("/", "About"),
    ("/#publications", "Papers"),
    ("/#teaching", "Teaching"),
    ("/#students", "Students"),
    ("/#projects", "Projects"),
    ("/papers/", "Reports"),
    ("/blog.html", "Blog"),
]


def nav(active):
    items = "".join(
        '<li><a href="%s"%s>%s</a></li>'
        % (href, ' class="active"' if label == active else "", label)
        for href, label in NAV_ITEMS
    )
    return (
        '<nav>\n  <div class="nav-inner">\n'
        '    <a class="nav-name" href="/">Dong Dai</a>\n'
        '    <div class="nav-right">\n'
        '      <ul class="nav-links">%s</ul>\n'
        '      <button class="theme-toggle" onclick="toggleTheme()" '
        'aria-label="Toggle theme">%s</button>\n'
        "    </div>\n  </div>\n</nav>" % (items, THEME_SVGS)
    )


FAVICONS = (
    '<link rel="icon" type="image/x-icon" href="/images/favicon/favicon.ico">\n'
    '  <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon/favicon-32x32.png">\n'
    '  <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon/favicon-16x16.png">\n'
    '  <link rel="apple-touch-icon" sizes="180x180" href="/images/favicon/apple-touch-icon.png">'
)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700'
    '&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..800;1,8..60,300..800&display=swap" '
    'rel="stylesheet">'
)

THEME_SCRIPT = """function toggleTheme() {
  var html = document.documentElement;
  var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  var frame = document.querySelector('iframe.giscus-frame');
  if (frame) {
    frame.contentWindow.postMessage({ giscus: { setConfig: { theme: next } } }, 'https://giscus.app');
  }
}
(function() {
  var saved = localStorage.getItem('theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
})();"""


def head(title, description, canonical, stylesheet, jsonld, image=None,
         og_type="article", extra=""):
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<meta name="author" content="%s">' % esc(AUTHOR["name"]),
        '<link rel="canonical" href="%s">' % esc(canonical),
        '<meta property="og:type" content="%s">' % og_type,
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(description),
        '<meta property="og:url" content="%s">' % esc(canonical),
        '<meta property="og:site_name" content="Dong Dai">',
        '<meta name="twitter:card" content="%s">'
        % ("summary_large_image" if image else "summary"),
        '<meta name="twitter:title" content="%s">' % esc(title),
        '<meta name="twitter:description" content="%s">' % esc(description),
    ]
    if image:
        tags.append('<meta property="og:image" content="%s">' % esc(image))
        tags.append('<meta name="twitter:image" content="%s">' % esc(image))
    tags.append(FAVICONS)
    tags.append(FONTS)
    tags.append('<link rel="stylesheet" href="%s">' % stylesheet)
    if extra:
        tags.append(extra)
    tags.append('<script type="application/ld+json">\n%s\n  </script>'
                % json.dumps(jsonld, indent=2, ensure_ascii=False))
    return "<head>\n  " + "\n  ".join(tags) + "\n</head>"


def breadcrumb(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(trail)
        ],
    }


def person_ref():
    return {
        "@type": "Person",
        "@id": SITE + "/#dongdai",
        "name": AUTHOR["name"],
        "url": AUTHOR["url"],
        "affiliation": {"@type": "Organization", "name": AUTHOR["affiliation"]},
    }


# ── paper reports ────────────────────────────────────────────────────────────

ICONS = {
    "arxiv": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    "pdf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "slides": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="12" y1="17" x2="12" y2="21"/><line x1="8" y1="21" x2="16" y2="21"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
}

CONTENTS_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
                 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                 '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/>'
                 '<line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/>'
                 '<line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>')

BOLT_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>')


def icon_for(label):
    key = str(label).lower()
    if "arxiv" in key:
        return ICONS["arxiv"]
    if "pdf" in key or "paper" in key:
        return ICONS["pdf"]
    if "code" in key or "github" in key:
        return ICONS["code"]
    if "slide" in key or "talk" in key:
        return ICONS["slides"]
    return ICONS["link"]


def paper_hero(paper):
    out = ['<header class="hero">']
    if paper.get("venue"):
        out.append('<div class="hero-venue">%s</div>' % esc(paper["venue"]))
    out.append("<h1>%s</h1>" % esc(paper["title"]))
    if paper.get("tagline"):
        out.append('<p class="hero-tagline">%s</p>' % esc(paper["tagline"]))

    out.append('<div class="hero-authors">')
    for a in paper.get("authors", []):
        sup = ",".join(str(x) for x in a.get("affil", []))
        if a.get("mark"):
            sup += a["mark"]
        if a.get("corresponding"):
            sup += "&#9993;"
        out.append('<span class="author">%s%s</span>'
                   % (esc(a["name"]), "<sup>%s</sup>" % sup if sup else ""))
    out.append("</div>")

    if paper.get("affiliations"):
        joined = '<span class="sep">&middot;</span>'.join(
            "<sup>%d</sup>&nbsp;%s" % (i + 1, esc(name))
            for i, name in enumerate(paper["affiliations"]))
        out.append('<div class="hero-affils">%s</div>' % joined)

    notes = []
    if paper.get("authorNote"):
        notes.append(esc(paper["authorNote"]))
    if any(a.get("corresponding") for a in paper.get("authors", [])):
        notes.append("&#9993; corresponding author")
    if notes:
        out.append('<div class="hero-note">%s</div>' % " &nbsp;&middot;&nbsp; ".join(notes))

    links = list(paper.get("links", [])) + [{"label": "BibTeX", "href": "#cite"}]
    out.append('<div class="hero-links">')
    for link in links:
        cls = ' class="primary"' if link.get("primary") else ""
        ext = "" if link["href"].startswith("#") else ' target="_blank" rel="noopener"'
        out.append('<a%s href="%s"%s>%s%s</a>'
                   % (cls, esc(link["href"]), ext, icon_for(link["label"]), esc(link["label"])))
    out.append("</div></header>")
    return "".join(out)


def paper_article_jsonld(paper, url, body_text):
    authors = []
    for a in paper.get("authors", []):
        entry = {"@type": "Person", "name": a["name"]}
        affils = [paper["affiliations"][i - 1] for i in a.get("affil", [])
                  if 0 < i <= len(paper.get("affiliations", []))]
        if affils:
            entry["affiliation"] = [{"@type": "Organization", "name": n} for n in affils]
        if a["name"] == AUTHOR["name"]:
            entry["@id"] = SITE + "/#dongdai"
            entry["sameAs"] = AUTHOR["sameAs"]
        authors.append(entry)

    article = {
        "@type": "ScholarlyArticle",
        "@id": url + "#article",
        "headline": paper["title"],
        "name": paper["title"],
        "description": paper.get("definition") or paper.get("tagline", ""),
        "abstract": paper.get("abstract", ""),
        "author": authors,
        "datePublished": str(paper.get("year", "")),
        "inLanguage": "en",
        "url": url,
        "isAccessibleForFree": True,
    }
    if paper.get("venueFull"):
        article["isPartOf"] = {"@type": "Book", "name": paper["venueFull"]}
    if paper.get("teaser"):
        article["image"] = "%s/papers/%s" % (SITE, paper["teaser"])
    sameas = [l["href"] for l in paper.get("links", [])
              if l["href"].startswith("http")]
    if sameas:
        article["sameAs"] = sameas
    if paper.get("keywords"):
        article["keywords"] = ", ".join(paper["keywords"])
    if paper.get("tldr"):
        article["about"] = [{"@type": "Thing", "name": strip_tags(t)}
                            for t in paper["tldr"]]

    page = {
        "@type": "WebPage",
        "@id": url,
        "url": url,
        "name": "%s — paper report" % (paper.get("short") or paper["title"]),
        "description": truncate(paper.get("definition") or paper.get("tagline", "")),
        "isPartOf": {"@type": "WebSite", "@id": SITE + "/#website"},
        "about": {"@id": url + "#article"},
        "author": person_ref(),
        "inLanguage": "en",
        "wordCount": len(body_text.split()),
        "breadcrumb": breadcrumb([
            ("Dong Dai", SITE + "/"),
            ("Paper reports", SITE + "/papers/"),
            (paper.get("short") or paper["title"], url),
        ]),
    }
    return {"@context": "https://schema.org", "@graph": [article, page]}


def build_paper(paper):
    pid = paper["id"]
    url = "%s/papers/%s/" % (SITE, pid)
    md_text = read("papers/%s.md" % pid)

    body = render_markdown(md_text)
    body = absolutize(body, "papers")
    body, contents = add_heading_ids(body, ["h2"], allow_cjk=False, stop_at_cjk=False)
    body = upgrade_figures(body)
    prose = '<div class="prose">%s</div>' % body

    parts = [paper_hero(paper)]

    if paper.get("highlights"):
        stats = "".join(
            '<div class="stat"><div class="stat-value">%s</div>'
            '<div class="stat-label">%s</div></div>' % (esc(h["value"]), esc(h["label"]))
            for h in paper["highlights"])
        parts.append('<section class="stats" aria-label="Key results">%s</section>' % stats)

    if paper.get("teaser"):
        cap = ('<figcaption>%s</figcaption>' % esc(paper["teaserCaption"])
               if paper.get("teaserCaption") else "")
        parts.append(
            '<figure class="teaser"><a href="/papers/%s" target="_blank" rel="noopener">'
            '<img src="/papers/%s" alt="%s overview"></a>%s</figure>'
            % (esc(paper["teaser"]), esc(paper["teaser"]),
               esc(paper.get("short") or paper["title"]), cap))

    tldr = [t for t in paper.get("tldr", []) if t and t.strip()]
    if tldr or contents:
        overview = ['<section class="overview">']
        if tldr:
            items = "".join("<li>%s</li>" % render_inline(t) for t in tldr)
            overview.append('<div class="card tldr"><p class="card-title">%sKey findings</p>'
                            "<ul>%s</ul></div>" % (BOLT_ICON, items))
        if contents:
            links = "".join(
                '<li><a href="#%s"><span class="num">%d</span>'
                '<span class="txt">%s</span>'
                '<span class="arw" aria-hidden="true">→</span></a></li>'
                % (esc(c["id"]), i + 1, esc(c["text"]))
                for i, c in enumerate(contents))
            overview.append('<nav class="card" aria-label="Contents">'
                            '<p class="card-title">%sContents</p>'
                            '<ol class="contents">%s</ol></nav>' % (CONTENTS_ICON, links))
        overview.append("</section>")
        parts.append("".join(overview))

    if paper.get("abstract"):
        parts.append('<section class="abstract"><p class="card-title">Abstract</p>'
                     "<p>%s</p></section>" % esc(paper["abstract"]))

    parts.append(prose)

    cite = ['<section class="cite" id="cite"><div class="cite-head">',
            '<p class="card-title">Cite this paper</p>']
    if paper.get("bibtex"):
        cite.append('<button class="copy-btn" id="copy-bibtex">Copy</button>')
    cite.append("</div>")
    if paper.get("venueFull"):
        cite.append('<p class="source-note" style="margin-top:0;margin-bottom:0.75rem">%s</p>'
                    % esc(paper["venueFull"]))
    if paper.get("bibtex"):
        cite.append('<pre><code id="bibtex">%s</code></pre>' % esc(paper["bibtex"]))
    cite.append('<p class="source-note">This report summarizes the paper for a general '
                "systems audience. All numbers and quotes are taken from the paper itself; "
                "figures are reproduced from it. For the full method and evaluation, read "
                "the original.</p></section>")
    parts.append("".join(cite))

    description = truncate(paper.get("definition") or paper.get("tagline")
                           or paper.get("abstract", ""))
    title = "%s — Paper Report — Dong Dai" % (paper.get("short") or paper["title"])
    image = "%s/papers/%s" % (SITE, paper["teaser"]) if paper.get("teaser") else None

    script = THEME_SCRIPT + """
(function() {
  var bar = document.getElementById('progress');
  function update() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
(function() {
  var btn = document.getElementById('copy-bibtex');
  var src = document.getElementById('bibtex');
  if (!btn || !src) return;
  btn.addEventListener('click', function() {
    navigator.clipboard.writeText(src.textContent).then(function() {
      btn.textContent = 'Copied';
      setTimeout(function() { btn.textContent = 'Copy'; }, 1600);
    });
  });
})();"""

    page = """<!DOCTYPE html>
<html lang="en" data-theme="light">
%s
<body>

<div class="progress" id="progress"></div>

%s

<main>
  <a class="back-link" href="/papers/">&larr; All paper reports</a>
  <div id="report">%s</div>
</main>

%s

<script>
%s
</script>

</body>
</html>
""" % (head(title, description, url, "/papers/report.css",
           paper_article_jsonld(paper, url, strip_tags(body)), image=image),
       nav("Reports"), size_images("\n".join(parts)), FOOTER, script)

    return write("papers/%s/index.html" % pid, page), url


def render_inline(text):
    """Inline-only Markdown, matching marked.parseInline() for TL;DR bullets."""
    out = render_markdown(text).strip()
    if out.startswith("<p>") and out.endswith("</p>"):
        out = out[3:-4]
    return out


# ── blog posts ───────────────────────────────────────────────────────────────

GISCUS = """(function() {
  var theme = document.documentElement.getAttribute('data-theme') || 'light';
  var s = document.createElement('script');
  s.src = 'https://giscus.app/client.js';
  s.setAttribute('data-repo', 'daidong/daidong.github.io');
  s.setAttribute('data-repo-id', 'R_kgDOID--JQ');
  s.setAttribute('data-category', 'General');
  s.setAttribute('data-category-id', 'DIC_kwDOID--Jc4C4ZAc');
  s.setAttribute('data-mapping', 'specific');
  s.setAttribute('data-term', %s);
  s.setAttribute('data-strict', '0');
  s.setAttribute('data-reactions-enabled', '1');
  s.setAttribute('data-emit-metadata', '0');
  s.setAttribute('data-input-position', 'bottom');
  s.setAttribute('data-theme', theme);
  s.setAttribute('data-lang', 'en');
  s.setAttribute('crossorigin', 'anonymous');
  s.async = true;
  document.getElementById('giscus-container').appendChild(s);
})();"""


def post_jsonld(post, url, body_text):
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": url + "#post",
                "headline": post["title"],
                "name": post["title"],
                "description": post.get("excerpt", ""),
                "datePublished": post["date"],
                "dateModified": post["date"],
                "author": person_ref(),
                "publisher": person_ref(),
                "mainEntityOfPage": {"@id": url},
                "url": url,
                "inLanguage": "en",
                "wordCount": len(body_text.split()),
                "isAccessibleForFree": True,
                "about": [{"@type": "Thing", "name": strip_tags(t)}
                          for t in post.get("tldr", [])],
            },
            {
                "@type": "WebPage",
                "@id": url,
                "url": url,
                "name": post["title"],
                "isPartOf": {"@type": "WebSite", "@id": SITE + "/#website"},
                "breadcrumb": breadcrumb([
                    ("Dong Dai", SITE + "/"),
                    ("Blog", SITE + "/blog.html"),
                    (post["title"], url),
                ]),
            },
        ],
    }


def build_post(post):
    slug = post["slug"]
    url = "%s/blog/%s/" % (SITE, slug)
    md_text = read("blog/%s.md" % slug)

    # The <h1> in the Markdown repeats the title the header already prints.
    body_md = re.sub(r"^#\s+.*\n+", "", md_text, count=1)

    body = render_markdown(body_md)
    # post.html lived at the site root, so the Markdown's relative URLs
    # were always written against "/", not against /blog/.
    body = absolutize(body, "")
    lead, body = split_lead_callouts(body)
    body, contents = add_heading_ids(body, ["h1", "h2"], allow_cjk=True, stop_at_cjk=True)

    parts = ['<div class="post-header"><h1>%s</h1>'
             '<div class="post-meta">%s &middot; %s</div></div>'
             % (esc(post["title"]), format_date(post["date"]), read_time(md_text))]

    if lead:
        parts.append('<div class="prose">%s</div>' % lead)

    tldr = [t for t in post.get("tldr", []) if isinstance(t, str) and t.strip()]
    if not tldr and post.get("excerpt"):
        tldr = [post["excerpt"]]

    if tldr or contents:
        overview = ['<section class="post-overview" aria-label="Post overview">']
        if tldr:
            items = "".join("<li>%s</li>" % render_inline(t) for t in tldr)
            overview.append('<div class="post-overview-card post-tldr-card">'
                            '<p class="post-overview-title">TL;DR</p>'
                            '<ul class="post-tldr">%s</ul></div>' % items)
        if contents:
            links = "".join(
                '<li class="post-contents-level-%d">'
                '<a class="post-contents-link" href="#%s">'
                '<span class="post-contents-number">%d</span>'
                '<span class="post-contents-text">%s</span>'
                '<span class="post-contents-arrow" aria-hidden="true">→</span></a></li>'
                % (c["level"], esc(c["id"]), i + 1,
                   esc(re.sub(r"^\s*\d+\s*[.)]\s*", "", c["text"]).strip()))
                for i, c in enumerate(contents))
            overview.append('<nav class="post-overview-card post-contents-card" '
                            'aria-label="Table of contents">'
                            '<p class="post-overview-title">%sContents</p>'
                            '<ol class="post-contents">%s</ol></nav>'
                            % (CONTENTS_ICON.replace('<svg ', '<svg class="post-overview-icon" '),
                               links))
        overview.append("</section>")
        parts.append("".join(overview))

    parts.append('<div class="prose">%s</div>' % body)

    description = truncate(post.get("excerpt") or strip_tags(body))
    page = """<!DOCTYPE html>
<html lang="en" data-theme="light">
%s
<body>

%s

<main>
  <a class="post-back" href="/blog.html">&larr; All posts</a>
  <div id="post-content">%s</div>
</main>

<div class="giscus-section">
  <div id="giscus-container"></div>
</div>

%s

<script>
%s
%s
</script>

</body>
</html>
""" % (head("%s — Dong Dai" % post["title"], description, url, "/post.css",
           post_jsonld(post, url, strip_tags(body)), og_type="article"),
       nav("Blog"), size_images("\n".join(parts)), FOOTER, THEME_SCRIPT,
       GISCUS % json.dumps(slug))

    return write("blog/%s/index.html" % slug, page), url


# ── listing pages ────────────────────────────────────────────────────────────

def inject(path, marker, fragment):
    """Replace the region between <!--build:marker--> and <!--/build:marker-->.

    The listing pages stay hand-maintained; only the list itself is generated,
    so a crawler sees the entries even though the browser still re-renders them
    from JSON.
    """
    text = read(path)
    start, end = "<!--build:%s-->" % marker, "<!--/build:%s-->" % marker
    if start not in text or end not in text:
        raise SystemExit("%s is missing the %s build markers" % (path, marker))
    head_part, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return write(path, head_part + start + "\n" + fragment + "\n" + end + tail)


def papers_list_html(papers):
    groups = {}
    for p in papers:
        groups.setdefault(str(p.get("year") or str(p.get("date", ""))[:4]), []).append(p)

    out = []
    for year in sorted(groups, reverse=True):
        items = []
        for p in groups[year]:
            card = ['<a class="report-card" href="/papers/%s/">' % esc(p["id"])]
            card.append('<img class="report-thumb" src="/papers/%s" alt="">' % esc(p["teaser"])
                        if p.get("teaser") else "<span></span>")
            card.append("<div>")
            if p.get("venue"):
                card.append('<span class="report-venue">%s</span>' % esc(p["venue"]))
            card.append('<div class="report-title">%s</div>' % esc(p["title"]))
            card.append('<div class="report-authors">%s</div>'
                        % esc(", ".join(a["name"] for a in p.get("authors", []))))
            if p.get("tagline"):
                card.append('<div class="report-tagline">%s</div>' % esc(p["tagline"]))
            if p.get("highlights"):
                stats = "".join('<span class="report-stat"><b>%s</b> %s</span>'
                                % (esc(h["value"]), esc(h["label"]))
                                for h in p["highlights"][:3])
                card.append('<div class="report-stats">%s</div>' % stats)
            card.append("</div></a>")
            items.append("".join(card))
        n = len(groups[year])
        out.append('<section class="year-group"><div class="year-label">%s '
                   "<span>%d report%s</span></div>%s</section>"
                   % (esc(year), n, "s" if n > 1 else "", "".join(items)))
    return "\n".join(out)


def posts_list_html(posts):
    groups = {}
    for p in posts:
        groups.setdefault(p["date"][:4], []).append(p)

    out = []
    for year in sorted(groups, reverse=True):
        items = []
        for p in groups[year]:
            inner = ['<div class="post-item-inner">']
            if p.get("cover"):
                inner.append('<img class="post-cover" src="%s" alt="">' % esc(p["cover"]))
            inner.append('<div class="post-info">')
            inner.append('<div class="post-title">%s</div>' % esc(p["title"]))
            inner.append('<div class="post-meta">%s &middot; %s</div>'
                         % (esc(format_date(p["date"])),
                            esc(read_time(read("blog/%s.md" % p["slug"])))))
            inner.append('<div class="post-excerpt">%s</div>' % esc(p.get("excerpt", "")))
            inner.append("</div></div>")
            items.append('<a class="post-item" href="/blog/%s/">%s</a>'
                         % (esc(p["slug"]), "".join(inner)))
        n = len(groups[year])
        out.append('<div class="year-group"><div class="year-label">%s '
                   "<span>%d post%s</span></div>%s</div>"
                   % (esc(year), n, "s" if n > 1 else "", "".join(items)))
    return "\n".join(out)


# ── redirects for retired URLs, and the 404 page ─────────────────────────────
#
# The site used to be a Jekyll build (academicpages) with pages such as /cv/ and
# /teaching/<course>. Those directories vanished when the static site replaced
# it, but Google still has the URLs and reports them as "Not found (404)" in
# Search Console. GitHub Pages cannot send a real 301, so each retired path gets
# a tiny index.html that redirects with <meta http-equiv="refresh" content="0">
# plus a canonical tag. Google treats an instant meta refresh as a permanent
# redirect and consolidates the old URL into the target.

CV_URL = "https://drive.google.com/file/d/1nN9x9hj9zsfwfYL7wmYkAWIU-8QG182U/view"

REDIRECTS = {
    # old path (no leading slash)      -> destination
    "cv":                              CV_URL,
    "resume":                          CV_URL,
    "teaching":                        SITE + "/#teaching",
    "teaching/2023-spring":            SITE + "/#teaching",
    "teaching/2023-spring-2":          SITE + "/#teaching",
    "teaching/2023-fall-uri":          SITE + "/#teaching",
    "publications":                    SITE + "/#publications",
    "talks":                           SITE + "/",
    "portfolio":                       SITE + "/#projects",
}

STUB_CSS = """
    body { max-width: var(--max-w); margin: 0 auto; padding: 4rem 1rem;
           font-family: 'Source Serif 4', Georgia, serif; }
    h1 { font-size: 1.6rem; margin-bottom: 0.5rem; }
    p { color: var(--sys-text-secondary); }
    a { color: var(--sys-accent-primary); }
"""


def build_redirect(path, target):
    """Write <path>/index.html that forwards to target."""
    old_url = SITE + "/" + path + "/"
    doc = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '  <meta http-equiv="refresh" content="0; url=%s">\n'
        '  <link rel="canonical" href="%s">\n'
        "  <title>Redirecting\u2026</title>\n"
        '  <link rel="stylesheet" href="/post.css">\n'
        "  <style>%s  </style>\n"
        "</head>\n<body>\n"
        "  <h1>This page has moved</h1>\n"
        '  <p>%s now lives at <a href="%s">%s</a>. '
        "You will be taken there automatically.</p>\n"
        "  <script>location.replace(%s);</script>\n"
        "</body>\n</html>\n"
    ) % (esc(target), esc(target), STUB_CSS, esc(old_url), esc(target),
         esc(target), json.dumps(target))
    return write(path + "/index.html", doc), old_url


def build_404():
    """GitHub Pages serves /404.html, with a real 404 status, for unknown paths."""
    doc = (
        "<!doctype html>\n"
        '<html lang="en" data-theme="light">\n<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '  <meta name="robots" content="noindex">\n'
        "  <title>Page not found \u2014 Dong Dai</title>\n"
        "  " + FAVICONS + "\n"
        "  " + FONTS + "\n"
        '  <link rel="stylesheet" href="/post.css">\n'
        "  <style>%s  </style>\n"
        "  <script>%s</script>\n"
        "</head>\n<body>\n"
        "  <h1>Page not found</h1>\n"
        "  <p>The address you followed does not exist on this site any more. "
        'Try the <a href="/">homepage</a>, the <a href="/papers/">paper reports</a> '
        'or the <a href="/blog.html">blog</a>.</p>\n'
        "</body>\n</html>\n"
    ) % (STUB_CSS, THEME_SCRIPT)
    return write("404.html", doc)


# ── sitemap, robots, llms.txt ────────────────────────────────────────────────

def _uncommitted():
    """Paths with changes git has not recorded yet."""
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {line[3:].strip().strip('"') for line in out.splitlines() if line[3:].strip()}


def last_modified(*paths):
    """The date a URL's sources last really changed, for sitemap <lastmod>.

    Stamping today's date on every run would rewrite sitemap.xml daily even
    when nothing changed, and a lastmod that always says "today" is one search
    engines learn to ignore. So: the newest commit date among the sources, or
    today for a source that is still uncommitted.
    """
    dirty = _uncommitted()
    dates = []
    for path in paths:
        if dirty is None or path in dirty:
            dates.append(date.today().isoformat())
            continue
        try:
            out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                                 cwd=ROOT, capture_output=True, text=True,
                                 check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            out = ""
        dates.append(out or date.today().isoformat())
    return max(dates)


def write_sitemap(entries):
    rows = "\n".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
        % (esc(url), lastmod, freq, prio) for url, lastmod, freq, prio in entries)
    return write("sitemap.xml",
                 '<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + rows + "\n</urlset>\n")


def write_robots():
    return write("robots.txt", """# https://daidong.github.io/
# Crawling is welcome, including by the retrieval bots behind LLM assistants.

User-agent: *
Allow: /
Disallow: /papers/report.html
Disallow: /post.html

Sitemap: %s/sitemap.xml
""" % SITE)


def write_llms(papers, posts):
    lines = [
        "# Dong Dai",
        "",
        "> Associate Professor in the Department of Computer and Information Sciences "
        "at the University of Delaware, leading the Data Intelligence Research Lab "
        "(DIRLab). Research on data-intensive and high-performance systems: parallel "
        "file systems, metadata management, graph storage, resource scheduling, and "
        "machine learning for systems.",
        "",
        "Homepage: %s/ — publications, teaching, students, and projects." % SITE,
        "",
        "## Paper reports",
        "",
        "Plain-language walkthroughs of the group's papers. Each page carries the "
        "verbatim abstract, the key findings, the BibTeX entry, and links to the "
        "paper itself.",
        "",
    ]
    for p in papers:
        lines.append("- [%s (%s)](%s/papers/%s/): %s"
                     % (p["title"], p.get("venue", ""), SITE, p["id"],
                        p.get("definition") or p.get("tagline", "")))
    lines += ["", "## Blog", "",
              "Notes on systems research, agentic LLM systems, and academic life.", ""]
    for p in posts:
        lines.append("- [%s](%s/blog/%s/) (%s): %s"
                     % (p["title"], SITE, p["slug"], p["date"], p.get("excerpt", "")))
    lines += ["", "## Optional", "",
              "- [Curriculum vitae](%s/files/dai_cv.pdf)" % SITE,
              "- [Google Scholar](%s)" % AUTHOR["sameAs"][0],
              "- [Group code on GitHub](https://github.com/DIR-LAB)", ""]
    return write("llms.txt", "\n".join(lines))


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    papers = json.loads(read("papers/papers.json"))
    posts = json.loads(read("blog/posts.json"))

    papers.sort(key=lambda p: (int(p.get("year", 0)), str(p.get("date", ""))), reverse=True)
    posts.sort(key=lambda p: p["date"], reverse=True)

    changed = []
    entries = [
        (SITE + "/", last_modified("index.html"), "monthly", "1.0"),
        (SITE + "/papers/",
         last_modified("papers/index.html", "papers/papers.json"), "monthly", "0.8"),
        (SITE + "/blog.html",
         last_modified("blog.html", "blog/posts.json"), "weekly", "0.8"),
    ]

    for paper in papers:
        touched, url = build_paper(paper)
        if touched:
            changed.append(url)
        entries.append((url, last_modified("papers/%s.md" % paper["id"],
                                           "papers/papers.json"), "yearly", "0.9"))

    for post in posts:
        touched, url = build_post(post)
        if touched:
            changed.append(url)
        entries.append((url, last_modified("blog/%s.md" % post["slug"]),
                        "yearly", "0.7"))

    if inject("papers/index.html", "papers-list", size_images(papers_list_html(papers))):
        changed.append("papers/index.html")
    if inject("blog.html", "posts-list", posts_list_html(posts)):
        changed.append("blog.html")
    if write_sitemap(entries):
        changed.append("sitemap.xml")
    if write_robots():
        changed.append("robots.txt")
    if write_llms(papers, posts):
        changed.append("llms.txt")
    for path, target in REDIRECTS.items():
        touched, url = build_redirect(path, target)
        if touched:
            changed.append(url)
    if build_404():
        changed.append("404.html")

    print("%d paper report(s), %d post(s)" % (len(papers), len(posts)))
    if changed:
        print("updated:")
        for item in changed:
            print("  " + item)
    else:
        print("everything already up to date")


if __name__ == "__main__":
    main()

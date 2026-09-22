# daidong.github.io

Personal academic homepage for Dong Dai, hosted on GitHub Pages.

Content is authored as JSON metadata plus a Markdown body, and `build.py`
renders it into static HTML before you commit. The pages used to be assembled in
the browser, which read fine but left crawlers — and the retrieval bots behind
LLM assistants — looking at an empty page. Everything a reader or a bot needs is
now in the HTML that ships.

## The build step

```bash
pip install markdown        # once
python3 build.py            # before every commit that touches content
```

It reads `papers/papers.json` + `papers/<id>.md` and `blog/posts.json` +
`blog/<slug>.md`, and writes:

| Output | What it is |
| --- | --- |
| `papers/<id>/index.html` | One pre-rendered paper report per paper |
| `blog/<slug>/index.html` | One pre-rendered post per post |
| `papers/index.html`, `blog.html` | The listing inside the `<!--build:…-->` markers is refreshed; the rest of the page stays hand-written |
| `sitemap.xml` | Every public URL, for Google Search Console and Bing Webmaster Tools |
| `robots.txt` | Points at the sitemap; hides the two redirect stubs |
| `llms.txt` | A plain-text map of the site for LLM assistants |

Re-running it is safe: files that would not change are left alone, so `git
status` only shows what actually moved.

## Adding a blog post

1. Write the post as Markdown in `blog/` (e.g. `blog/my-new-post.md`).
2. Add an entry to `blog/posts.json`:

```json
{
  "slug": "my-new-post",
  "title": "My New Post",
  "date": "2026-03-15",
  "excerpt": "A short summary shown on the blog listing page.",
  "tldr": ["Up to three sentences that become the TL;DR card."]
}
```

3. Run `python3 build.py`, then commit both the source and the generated
   `blog/my-new-post/index.html`.

Images go in `images/` and are referenced with a path relative to the site root
(e.g. `![alt](images/photo.png)`); `build.py` rewrites them to absolute URLs and
fills in each image's real pixel size so the page does not reflow while it
loads.

## Adding a paper report

See `papers/README.md`.

## Local preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## URLs

Reports and posts each live at their own directory URL:

```
/papers/stellar/
/blog/will-ai-bankrupt-my-lab/
```

`papers/report.html?id=…` and `post.html?slug=…` are the old URLs. They are kept
as `noindex` stubs that forward to the new address, so links already out in the
world — and the giscus comment threads, which are keyed on the slug — keep
working.

## File structure

```
build.py            Pre-renders everything below into static HTML
index.html          Homepage (About, Publications, Teaching, …) — hand-written
blog.html           Blog listing; the list itself is generated
post.html           Redirect stub for the old ?slug= URLs
post.css            Styles for the generated post pages
blog/
  posts.json        Post metadata (slug, title, date, excerpt, tldr)
  <slug>.md         The post body            ← you edit
  <slug>/index.html The rendered post        ← generated
papers/
  papers.json       Report metadata
  <id>.md           The report body          ← you edit
  <id>/index.html   The rendered report      ← generated
  index.html        Report listing; the list itself is generated
  report.html       Redirect stub for the old ?id= URLs
  report.css        Styles for the generated report pages
  figs/<id>/        That paper's figures
sitemap.xml         Generated
robots.txt          Generated
llms.txt            Generated
fonts/              Atkinson Hyperlegible web fonts
images/             Site images (profile photo, blog figures)
files/              Paper PDFs, CV, and other downloadable files
.nojekyll           Tells GitHub Pages to skip Jekyll processing
LICENSE             MIT license
```

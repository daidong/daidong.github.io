# Paper reports

Long-form, plain-language write-ups of our papers, in the style of an academic
project page. Same no-build-step approach as the blog: metadata in JSON, body in
Markdown, rendered client-side.

```
papers/
  papers.json          index metadata for every report
  <id>.md              the report body for one paper
  figs/<id>/*.png      that paper's figures
  index.html           the listing page          →  /papers/
  report.html          the renderer              →  /papers/report.html?id=<id>
```

## Adding a report

1. **Put the figures in `figs/<id>/`.** Downscale first — 1500 px wide is plenty:

   ```python
   from PIL import Image
   im = Image.open(src)
   im.thumbnail((1500, 10000), Image.LANCZOS)
   im.convert('P', palette=Image.ADAPTIVE, colors=256).save(dst, optimize=True)
   ```

   Flatten transparency onto white so the figures read the same in both themes.

2. **Write `<id>.md`.** Only `##` headings become the Contents list, so use them
   for the report's main sections. An image on a line by itself becomes a
   `<figure>`, and its alt text becomes the caption:

   ```markdown
   ![Figure 3. What the reader should notice.](figs/stellar/decision.png)
   ```

   Tables, code blocks, and blockquotes all work. Every number in the report
   must come from the paper.

3. **Add an entry to `papers.json`:**

   | Field | What it does |
   | --- | --- |
   | `id` | URL slug; must match the `.md` filename |
   | `short` | Short name used in the browser tab title |
   | `title`, `venue`, `venueFull`, `year` | Hero and listing |
   | `tagline` | One sentence under the title |
   | `authors` | `{name, affil: [1], mark: "*", corresponding: true}` |
   | `affiliations` | Ordered list; `affil` indexes into it (1-based) |
   | `links` | Buttons: `{label, href, primary}`. Icons are picked from the label |
   | `teaser`, `teaserCaption` | Figure under the hero; also the listing thumbnail |
   | `tldr` | 2–3 bullets, shown in the TL;DR card and the homepage hover card |
   | `highlights` | `{value, label}` stat cards; keep values short |
   | `abstract` | Verbatim from the paper |
   | `bibtex` | Shown with a copy button |

4. **Link it from the homepage.** In `index.html`, add `data-report="<id>"` to
   the publication's `<li>` and a badge link inside `.pub-links`:

   ```html
   <li data-report="stellar">
     ...
     <span class="pub-links">
       <a class="pub-report" href="papers/report.html?id=stellar"> … Read the report</a>
     </span>
   </li>
   ```

   The badge is a plain link and works on its own. A script on the homepage
   reads `papers.json` and adds the hover preview on top of it.

## Local preview

```
python3 -m http.server 8000     # then open http://localhost:8000/papers/
```

# daidong.github.io

Personal academic homepage for Dong Dai, hosted on GitHub Pages.

## Adding a Blog Post

1. Write your post as a Markdown file in `blog/` (e.g. `blog/my-new-post.md`).
2. Add an entry to `blog/posts.json`:

```json
{
  "slug": "my-new-post",
  "title": "My New Post",
  "date": "2026-03-15",
  "excerpt": "A short summary shown on the blog listing page."
}
```

3. Commit and push. The post will appear on the blog page automatically.

Posts can include images — put them in `blog/images/` and reference them with relative paths (e.g. `![alt](images/photo.jpg)`).

## Local Preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## File Structure

```
index.html          Main homepage (About, Publications, Teaching, etc.)
blog.html           Blog listing page
post.html           Blog post viewer (renders Markdown via marked.js)
blog/
  posts.json        Blog post metadata (title, date, slug, excerpt)
  hello-world.md    Example blog post
  images/           Images used in blog posts
fonts/              Atkinson Hyperlegible web fonts
images/             Site images (profile photo)
files/              Paper PDFs, CV, and other downloadable files
.nojekyll           Tells GitHub Pages to skip Jekyll processing
LICENSE             MIT license
```

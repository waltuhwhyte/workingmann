#!/usr/bin/env python3
"""Generate static answer pages from data/keywords.csv."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

BASE_URL = "https://example.com"

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "keywords.csv"
SITE_ROOT = REPO_ROOT / "site"


@dataclass(frozen=True)
class KeywordRow:
    slug: str
    question: str
    short_answer: str
    offer_url: str
    cta_text: str


def load_keywords(path: Path) -> list[KeywordRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"slug", "question", "short_answer", "offer_url", "cta_text"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in keywords.csv: {', '.join(sorted(missing))}")
        rows: list[KeywordRow] = []
        for row in reader:
            rows.append(
                KeywordRow(
                    slug=row["slug"].strip(),
                    question=row["question"].strip(),
                    short_answer=row["short_answer"].strip(),
                    offer_url=row["offer_url"].strip(),
                    cta_text=row["cta_text"].strip(),
                )
            )
        return rows


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def render_page(keyword: KeywordRow) -> str:
    canonical = f"{BASE_URL}/{keyword.slug}/"
    description = keyword.short_answer
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{keyword.question}</title>
  <meta name=\"description\" content=\"{description}\" />
  <link rel=\"canonical\" href=\"{canonical}\" />
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; line-height: 1.5; }}
    .disclosure {{ background: #fff4d1; border: 1px solid #f2d68a; padding: 12px; border-radius: 6px; }}
    .cta {{ display: inline-block; background: #1a56db; color: #fff; padding: 12px 18px; border-radius: 6px; text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <p class=\"disclosure\"><strong>Disclosure:</strong> This page may contain affiliate links. If you choose to purchase, we may earn a commission at no extra cost to you.</p>
  <h1>{keyword.question}</h1>
  <p>{keyword.short_answer}</p>
  <p>
    <a class=\"cta\" href=\"{keyword.offer_url}\" rel=\"sponsored nofollow\">{keyword.cta_text}</a>
  </p>
</body>
</html>
"""


def render_index(rows: Iterable[KeywordRow]) -> str:
    items = "\n".join(
        f"<li><a href=\"{row.slug}/\">{row.question}</a></li>" for row in rows
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Answer Library</title>
  <meta name=\"description\" content=\"Browse quick answers and recommended offers.\" />
  <link rel=\"canonical\" href=\"{BASE_URL}/\" />
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; line-height: 1.5; }}
    input {{ width: 100%; padding: 10px; font-size: 16px; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <h1>Answer Library</h1>
  <p>Search our collection of quick answers.</p>
  <input id=\"search\" type=\"search\" placeholder=\"Search questions...\" />
  <ul id=\"results\">
    {items}
  </ul>
  <script>
    const searchInput = document.getElementById('search');
    const results = document.getElementById('results');
    const items = Array.from(results.querySelectorAll('li'));

    searchInput.addEventListener('input', () => {{
      const query = searchInput.value.toLowerCase().trim();
      items.forEach((item) => {{
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? '' : 'none';
      }});
    }});
  </script>
</body>
</html>
"""


def render_sitemap(rows: Iterable[KeywordRow]) -> str:
    updated = datetime.utcnow().date().isoformat()
    urls = [f"  <url><loc>{BASE_URL}/</loc><lastmod>{updated}</lastmod></url>"]
    urls.extend(
        f"  <url><loc>{BASE_URL}/{row.slug}/</loc><lastmod>{updated}</lastmod></url>"
        for row in rows
    )
    urlset = "\n".join(urls)
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
{urlset}
</urlset>
"""


def render_robots() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {BASE_URL}/sitemap.xml",
            "",
        ]
    )


def build_site() -> None:
    rows = load_keywords(DATA_PATH)
    ensure_directory(SITE_ROOT)

    for row in rows:
        page_dir = SITE_ROOT / row.slug
        ensure_directory(page_dir)
        (page_dir / "index.html").write_text(render_page(row), encoding="utf-8")

    (SITE_ROOT / "index.html").write_text(render_index(rows), encoding="utf-8")
    (SITE_ROOT / "sitemap.xml").write_text(render_sitemap(rows), encoding="utf-8")
    (SITE_ROOT / "robots.txt").write_text(render_robots(), encoding="utf-8")


if __name__ == "__main__":
    build_site()

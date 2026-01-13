# Answer Site Generator

This project generates a minimal static "answer site" for affiliate links using Python 3 (stdlib only).

## Inputs

- `data/keywords.csv` with columns: `slug`, `question`, `short_answer`, `offer_url`, `cta_text`.
- `data/metrics.csv` with columns: `slug`, `impressions`, `clicks`, `conversions`, `last_seen_date`.

## Build the site

From the repo root:

```bash
python3 tools/generate.py
```

Generated output is written to `site/` with:
- `site/index.html`
- `site/<slug>/index.html`
- `site/sitemap.xml`
- `site/robots.txt`

## Generate prune list

```bash
python3 tools/prune.py
```

This writes `data/prune_list.txt` with slugs that meet the pruning criteria.

## Deploy as static hosting

1. Run the generator: `python3 tools/generate.py`.
2. Upload the contents of the `site/` directory to any static host (e.g., S3, Netlify, GitHub Pages).
3. Set your production base URL in `tools/generate.py` (`BASE_URL`) before deploying.

The site is fully static and requires no server-side runtime.

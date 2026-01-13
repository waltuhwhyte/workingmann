#!/usr/bin/env python3
"""Generate a prune list from data/metrics.csv."""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = REPO_ROOT / "data" / "metrics.csv"
PRUNE_PATH = REPO_ROOT / "data" / "prune_list.txt"


def should_prune(impressions: int, clicks: int, conversions: int) -> bool:
    return (impressions >= 300 and clicks == 0) or (clicks >= 50 and conversions == 0)


def build_prune_list() -> list[str]:
    slugs: list[str] = []
    with METRICS_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"slug", "impressions", "clicks", "conversions", "last_seen_date"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in metrics.csv: {', '.join(sorted(missing))}")
        for row in reader:
            impressions = int(row["impressions"].strip() or 0)
            clicks = int(row["clicks"].strip() or 0)
            conversions = int(row["conversions"].strip() or 0)
            if should_prune(impressions, clicks, conversions):
                slugs.append(row["slug"].strip())
    return slugs


def write_prune_list(slugs: list[str]) -> None:
    PRUNE_PATH.write_text("\n".join(slugs) + ("\n" if slugs else ""), encoding="utf-8")


if __name__ == "__main__":
    write_prune_list(build_prune_list())

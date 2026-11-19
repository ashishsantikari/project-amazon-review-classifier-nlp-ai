"""Build a balanced product-category dataset from Amazon Reviews 2023.

Each category file in the dataset is 6-31 GB, so instead of downloading it we
fetch only its first MB_PER_CATEGORY megabytes with an HTTP range request.
Reviews in those files are ordered by user, not by product, so the first chunk
already covers tens of thousands of distinct products.

Output: data/reviews.csv with columns text,label
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd
import requests

BASE_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/"
    "resolve/main/raw/review_categories/{}.jsonl"
)

# label shown in the app  ->  source file in the dataset
CATEGORIES = {
    "electronics": "Electronics",
    "home & kitchen": "Home_and_Kitchen",
    "fashion": "Clothing_Shoes_and_Jewelry",
    "grocery": "Grocery_and_Gourmet_Food",
    "beauty": "Beauty_and_Personal_Care",
    "sports & outdoors": "Sports_and_Outdoors",
    "toys & games": "Toys_and_Games",
    "books": "Books",
    "pet supplies": "Pet_Supplies",
    "automotive": "Automotive",
}

SAMPLES_PER_CATEGORY = 7000
MB_PER_CATEGORY = 15
MIN_WORDS = 8          # very short reviews ("Great!") carry no category signal
SEED = 42

OUT_DIR = Path(__file__).parent / "data"


def fetch_chunk(source: str) -> list[dict]:
    url = BASE_URL.format(source)
    headers = {"Range": f"bytes=0-{MB_PER_CATEGORY * 1_000_000}"}
    resp = requests.get(url, headers=headers, timeout=300)
    resp.raise_for_status()
    lines = resp.content.decode("utf-8", errors="ignore").splitlines()[:-1]  # last line is cut
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    records = []
    for label, source in CATEGORIES.items():
        rows = fetch_chunk(source)
        seen = set()
        pool = []
        for r in rows:
            text = f"{r.get('title', '').strip()}. {r.get('text', '').strip()}"
            text = " ".join(text.replace("<br />", " ").split())
            if len(text.split()) < MIN_WORDS or text in seen:
                continue
            seen.add(text)
            pool.append(text)
        picked = rng.sample(pool, min(SAMPLES_PER_CATEGORY, len(pool)))
        records += [{"text": t, "label": label} for t in picked]
        print(f"{label:<18} downloaded={len(rows):>6}  usable={len(pool):>6}  kept={len(picked)}")

    df = pd.DataFrame(records).sample(frac=1, random_state=SEED)
    df.to_csv(OUT_DIR / "reviews.csv", index=False)
    print(f"\nSaved {len(df)} reviews to {OUT_DIR / 'reviews.csv'}")


if __name__ == "__main__":
    main()

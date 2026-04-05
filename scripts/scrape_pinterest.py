import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
# PINTEREST_BOARD = "https://www.pinterest.com/YOUR_BOARD/your-board-name/"
PINTEREST_BOARD = os.environ.get("PINTEREST_BOARD", "")
OUTPUT_JSON = "data/products.json"

if not PINTEREST_BOARD:
    print("PINTEREST_BOARD not set. Skipping scrape.")
    exit(0)

# --- HELPERS ---
def extract_category(title: str) -> str:
    t = title.lower()
    if any(x in t for x in ["kitchen", "cook", "utensil", "gadgets"]):
        return "kitchen"
    if any(x in t for x in ["beauty", "skincare", "makeup", "cosmetics"]):
        return "beauty"
    if any(x in t for x in ["fashion", "clothing", "apparel", "wear", "dress"]):
        return "fashion"
    if any(x in t for x in ["home", "living", "decor", "furniture"]):
        return "home"
    if any(x in t for x in ["electronic", "gadget", "tech", "phone"]):
        return "electronics"
    if any(x in t for x in ["health", "fitness", "gym", "workout"]):
        return "fitness"
    return "other"

def safe_text(elem) -> str:
    return (elem.get_text(strip=True) or "").replace("\n", " ")[:120]

# --- SCRAPE ---
print("Scraping Pinterest board:", PINTEREST_BOARD)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
res = requests.get(PINTEREST_BOARD, headers=headers, timeout=30)
if res.status_code != 200:
    print("Board fetch failed:", res.status_code)
    exit(1)

soup = BeautifulSoup(res.text, "html.parser")

products = []
pin_anchors = soup.select("a[data-grid-item]") or soup.select("a[href*=\/pin\/]")
for a in pin_anchors[:60]:
    title = safe_text(a)
    if not title or len(title) < 3:
        continue
    img = a.find("img")
    img_url = img["src"] if img and img.has_attr("src") else ""
    cat = extract_category(title)
    products.append({
        "id": hashlib.md5(title.encode()).hexdigest()[:8],
        "title": title,
        "image": img_url,
        "category": cat,
        "pinterest_url": a.get("href", ""),
        "amazon_url": "",
    })

# Save
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"updated": datetime.utcnow().isoformat() + "Z", "products": products}, f, indent=2)
print(f"Scraped {len(products)} pins -> {OUTPUT_JSON}")

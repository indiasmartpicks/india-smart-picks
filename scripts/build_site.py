import json
import os
from datetime import datetime
from pathlib import Path

# --- CONFIG ---
PRODUCTS_JSON = "data/products.json"
TEMPLATE_HTML = "template.html"
OUTPUT_HTML = "index.html"

# --- LOAD ---
if not os.path.exists(PRODUCTS_JSON):
    print("No products.json. Generating demo data.")
    demo = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "products": [
            {"id": "1", "title": "Stainless Steel Cookware Set", "image": "", "category": "kitchen", "amazon_url": ""},
            {"id": "2", "title": "Vitamin C Serum", "image": "", "category": "beauty", "amazon_url": ""},
            {"id": "3", "title": "Summer Cotton Dress", "image": "", "category": "fashion", "amazon_url": ""},
        ]
    }
    os.makedirs(os.path.dirname(PRODUCTS_JSON), exist_ok=True)
    with open(PRODUCTS_JSON, "w") as f:
        json.dump(demo, f, indent=2)

with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

products = data.get("products", [])
updated = data.get("updated", datetime.utcnow().isoformat())

# --- STATS ---
from collections import Counter
cats = Counter(p.get("category", "other") for p in products)
total = len(products)

# --- BUILD ---
html = Path(TEMPLATE_HTML).read_text(encoding="utf-8")

# Replace counters
html = html.replace("{{TOTAL_PICKS}}", str(total))
html = html.replace("{{KITCHEN_COUNT}}", str(cats.get("kitchen", 0)))
html = html.replace("{{BEAUTY_COUNT}}", str(cats.get("beauty", 0)))
html = html.replace("{{FASHION_COUNT}}", str(cats.get("fashion", 0)))
html = html.replace("{{HOME_COUNT}}", str(cats.get("home", 0)))
html = html.replace("{{ELECTRONICS_COUNT}}", str(cats.get("electronics", 0)))
html = html.replace("{{FITNESS_COUNT}}", str(cats.get("fitness", 0)))

# Build product cards
items = []
for p in products[:50]:
    items.append(f"""<article class="card" data-category="{p.get('category','other')}">
    <img src="{p.get('image','') or 'https://via.placeholder.com/300'}" alt="{p.get('title','')}">
    <h3>{p.get('title','')}</h3>
    <p class="cat">{p.get('category','other')}</p>
    <a class="btn" href="{p.get('amazon_url','') or '#'}" target="_blank">View on Amazon</a>
</article>""")

# Inject products grid
grid_html = "\n".join(items)
html = html.replace("{{PRODUCT_GRID}}", grid_html)

# Timestamp
try:
    ts = datetime.fromisoformat(updated.replace("Z", "+00:00")).strftime("%d %b %Y")
except:
    ts = updated[:10]
html = html.replace("{{LAST_UPDATED}}", ts)

# --- WRITE ---
Path(OUTPUT_HTML).write_text(html, encoding="utf-8")
print(f"Built {OUTPUT_HTML} with {total} products.")

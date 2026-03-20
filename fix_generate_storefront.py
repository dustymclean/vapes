import json
import csv
import os
import re
import time

# --- CONFIGURATION & PATHS ---
CSV_PATH = os.path.expanduser("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
BASE_DIR = os.path.expanduser("~/Desktop/Pixies_Vape_Shop")
CAT_DIR = os.path.join(BASE_DIR, "categories")
JS_DIR = os.path.join(BASE_DIR, "js")

def slugify(text):
    """Standard URL slug generator: 'Dab Rigs' -> 'dab-rigs'"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)

def ensure_dirs():
    """Ensure build directories exist."""
    for d in [CAT_DIR, JS_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def get_product_card_html(p, rel_path="./"):
    """
    Generates the HTML for a single product card.
    rel_path: Use './' for root index, '../' for nested categories.
    """
    p_name_esc = p['name'].replace("'", "\\'")
    # The 'linkto' shortcut implementation
    link_html = f'''
    <div class="link-shortcut" title="Copy Direct Link" 
         onclick="event.stopPropagation(); copyDirectLink('{p_name_esc}')">
        <i class="fa-solid fa-link"></i>
    </div>'''
    
    return f'''
    <div class="card" onclick="openModal('{p_name_esc}')">
        {link_html}
        <div class="image-container"><img src="{p['image']}" loading="lazy"></div>
        <div class="brand-badge">{p['brand']}</div>
        <div class="title">{p['name']}</div>
        <div class="price">From ${p['Variants'][0]['price']:.2f}</div>
    </div>'''

def generate_storefront():
    ensure_dirs()
    grouped_products = {}
    master_cats = set()
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERROR: CSV missing at {CSV_PATH}")
        return

    # 1. DATA PROCESSING
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row in reader:
            try:
                retail = float(row.get("Your Retail Price", 0))
                if retail <= 0 or row.get("Status") == "Hidden": continue 

                title = row.get("Product Name", "").strip()
                cat = row.get("Product Type", "Accessories").strip() or "Accessories"
                brand = row.get("Brand", "Premium").strip() or "Premium"
                img_url = row.get("Image URL", "").strip() or "https://via.placeholder.com/400"
                
                master_cats.add(cat)
                if title not in grouped_products:
                    grouped_products[title] = {
                        "name": title, "brand": brand, "category": cat,
                        "image": img_url, "Variants": []
                    }
                
                grouped_products[title]["Variants"].append({
                    "name": row.get("Variant", "Standard"),
                    "sku": row.get("SKU"),
                    "price": retail,
                    "image": img_url,
                    "description": row.get("Description", "").replace('"', '&quot;')
                })
            except: continue

    all_products = list(grouped_products.values())
    
    # 2. EXPORT SHARED DATA
    with open(os.path.join(JS_DIR, "data.js"), "w", encoding="utf-8") as f:
        f.write(f"const allProducts = {json.dumps(all_products)};")

    # 3. COMMON HEAD/CSS TEMPLATE
    def get_head(title, is_nested=False):
        prefix = "../" if is_nested else ""
        return f"""
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: sans-serif; background: #fff; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 20px; padding: 20px; }}
        .card {{ position: relative; border: 1px solid #eee; border-radius: 12px; padding: 15px; text-align: center; cursor: pointer; transition: 0.3s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }}
        .card img {{ max-width: 100%; height: 160px; object-fit: contain; }}
        .brand-badge {{ font-size: 0.7em; color: #aaa; text-transform: uppercase; margin-top: 10px; }}
        .title {{ font-weight: bold; margin: 5px 0; font-size: 0.9em; height: 2.4em; overflow: hidden; }}
        .price {{ font-weight: 800; color: #111; }}
        
        /* The Link Shortcut Icon */
        .link-shortcut {{
            position: absolute; top: 10px; right: 10px; background: #fff; width: 30px; height: 30px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 0.8em; color: #888; border: 1px solid #eee; z-index: 5; transition: 0.2s;
        }}
        .link-shortcut:hover {{ background: #111; color: #fff; border-color: #111; }}
    </style>
</head>"""

    # 4. BUILD CATEGORY PAGES
    for cat in master_cats:
        cat_slug = slugify(cat)
        cat_prods = [p for p in all_products if p['category'] == cat]
        
        html = f"""<!DOCTYPE html>
<html>
{get_head(f"Pixie's Pantry | {cat}", True)}
<body>
    <div class="container">
        <nav style="padding: 20px 0;"><a href="../index.html">← Master Catalog</a></nav>
        <h1>{cat}</h1>
        <div class="grid">
            {"".join([get_product_card_html(p, "../") for p in cat_prods])}
        </div>
    </div>
    <script src="../js/data.js"></script>
    <script src="../js/app.js"></script>
    <script>
        function copyDirectLink(name) {{
            const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            const url = window.location.origin + "/index.html?p=" + slug;
            navigator.clipboard.writeText(url).then(() => alert("Link Copied!"));
        }}
    </script>
</body>
</html>"""
        with open(os.path.join(CAT_DIR, f"{cat_slug}.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # 5. BUILD MASTER INDEX
    index_html = f"""<!DOCTYPE html>
<html>
{get_head("Pixie's Pantry | Master Catalog", False)}
<body>
    <div class="container">
        <header style="padding: 40px 0; text-align: center;">
            <h1>Pixie's Pantry</h1>
            <p>Browse {len(all_products)} premium products</p>
        </header>
        <div class="grid">
            {"".join([get_product_card_html(p, "./") for p in all_products])}
        </div>
    </div>
    <script src="js/data.js"></script>
    <script src="js/app.js"></script>
</body>
</html>"""
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"✅ Build Complete: {len(all_products)} products synced across {len(master_cats)} category pages.")

if __name__ == "__main__":
    generate_storefront()
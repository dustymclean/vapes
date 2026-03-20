import json
import csv
import os
import hashlib
import time

# --- PATHS ---
# Update these if your file names or locations are different
csv_path = os.path.expanduser("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
html_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/index.html")
log_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/build_manifest.log")

def generate_storefront():
    start_time = time.time()
    grouped_products = {}
    error_count = 0
    processed_count = 0

    if not os.path.exists(csv_path):
        print(f"❌ DATABASE ERROR: Source CSV missing at {csv_path}")
        return

    # 1. PROCESS DATABASE (CSV)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row in reader:
            try:
                # Margin Guardian: Ensure sustainability
                wholesale = float(row.get("Wholesale Cost", 0) or 0)
                retail = float(row.get("Your Retail Price", 0) or 0)
                if retail <= 0 or (retail - wholesale) / retail < 0.20:
                    continue

                title = row.get("Product Name", "").strip()
                cat = row.get("Product Type", "Accessories").strip() or "Accessories"
                sku = row.get("SKU", "").strip()
                
                if not sku or sku.lower() == "none":
                    sku = "GEN-" + hashlib.md5((title + row.get("Variant","")).encode()).hexdigest()[:8].upper()
                
                img_url = row.get("Image URL", "") or "https://via.placeholder.com/250?text=No+Image"
                
                if title not in grouped_products:
                    grouped_products[title] = {
                        "Product Name": title,
                        "Brand": row.get("Brand", "Premium") or "Premium",
                        "Category": cat,
                        "Description": row.get("Description", "").replace('"', '&quot;').replace('\n', '<br>'),
                        "Featured": row.get("Featured", "No") == "Yes",
                        "Primary Image": img_url,
                        "Variants": []
                    }
                
                grouped_products[title]["Variants"].append({
                    "name": row.get("Variant", "").strip() or "Standard",
                    "sku": sku,
                    "price": retail,
                    "image": img_url
                })
                processed_count += 1
            except Exception as e:
                error_count += 1

    all_products_array = list(grouped_products.values())
    
    # 2. PRE-PROCESS JSON (Prevents Python < 3.12 SyntaxErrors)
    safe_products_json = json.dumps(all_products_array).replace('</', '<\\/')

    # 3. RESTORE THE BEAUTIFUL INTERFACE (HTML/CSS)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixie's Pantry Vape Shop</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #ffffff; color: #111; margin: 0; padding: 0; display: flex; min-height: 100vh; overflow-x: hidden; }}
        .sidebar {{ width: 320px; background: #f9f9f9; padding: 30px 20px; border-right: 1px solid #eaeaea; position: fixed; height: 100vh; overflow-y: auto; box-sizing: border-box; display: flex; flex-direction: column; gap: 15px; z-index: 10; }}
        .sidebar h2 {{ font-size: 1.4em; text-transform: uppercase; letter-spacing: 2px; margin: 0; font-weight: 800; color: #111; }}
        .sidebar h3 {{ font-size: 0.75em; text-transform: uppercase; letter-spacing: 1.5px; margin: 25px 0 10px 0; color: #111; border-bottom: 2px solid #111; padding-bottom: 5px; }}
        .nav-list {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 1px; }}
        .nav-item {{ padding: 5px 12px; cursor: pointer; font-size: 0.8em; color: #666; border-radius: 4px; transition: all 0.2s; }}
        .nav-item:hover {{ background: #eee; color: #111; }}
        .nav-item.active {{ background: #111; color: #fff; font-weight: bold; }}
        .main-content {{ flex-grow: 1; margin-left: 320px; padding: 40px 50px; box-sizing: border-box; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 25px; }}
        .card {{ background: #fff; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #f0f0f0; transition: all 0.2s; cursor: pointer; display: flex; flex-direction: column; }}
        .image-container img {{ max-width: 100%; max-height: 180px; object-fit: contain; }}
        .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; align-items: center; justify-content: center; }}
        .modal-content {{ background: #fff; width: 900px; max-width: 95%; height: 600px; border-radius: 12px; display: flex; position: relative; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Pixie's Pantry</h2>
        <div class="filter-group">
            <h3>Quick Filter</h3>
            <input type="text" id="searchInput" placeholder="Search brands, gear..." oninput="applyFilters()">
        </div>
        <div id="category-filter-list"></div>
    </div>

    <div class="main-content">
        <h1 id="page-title">Hardware Catalog</h1>
        <p id="item-count" style="color:#888; font-size: 0.9em;"></p>
        <div id="product-grid" class="grid"></div>
    </div>

    <div class="modal-overlay" id="product-modal">
        <div class="modal-content">
            <button onclick="closeModal()" style="position:absolute; top:20px; right:20px; border:none; background:none; font-size:2em;">&times;</button>
            <div style="display:flex; width:100%; height:100%;">
                <div style="flex:1; background:#f9f9f9; display:flex; align-items:center; justify-content:center; padding:30px;">
                    <img id="modal-img" style="max-width:100%; max-height:400px; object-fit:contain;">
                </div>
                <div style="flex:1.2; padding:40px; overflow-y:auto;">
                    <h2 id="modal-title"></h2>
                    <div id="modal-price" style="font-size:2em; font-weight:bold; margin:20px 0;"></div>
                    <div id="modal-desc" style="color:#666; line-height:1.6;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const allProducts = {safe_products_json};
        
        function initStore() {{
            renderCategories();
            applyFilters();
        }}

        function renderCategories() {{
            const cats = [...new Set(allProducts.map(p => p.Category))].sort();
            const list = document.getElementById('category-filter-list');
            list.innerHTML = cats.map(c => `<li class="nav-item" onclick="setFilter('${{c}}')">${{c}}</li>`).join('');
        }}

        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const filtered = allProducts.filter(p => p['Product Name'].toLowerCase().includes(search));
            renderGrid(filtered);
        }}

        function renderGrid(products) {{
            const grid = document.getElementById('product-grid');
            grid.innerHTML = products.map(p => `
                <div class="card" onclick="openModal('${{p['Product Name'].replace(/'/g, "\\\\'")}}')">
                    <div class="image-container"><img src="${{p['Primary Image']}}"></div>
                    <div style="font-weight:bold; margin-top:10px;">${{p['Product Name']}}</div>
                    <div style="color:#d4af37; margin-top:5px;">$${{p.Variants[0].price.toFixed(2)}}</div>
                </div>
            `).join('');
            document.getElementById('item-count').innerText = products.length + " products found";
        }}

        function openModal(name) {{
            const p = allProducts.find(x => x['Product Name'] === name);
            if(!p) return;
            document.getElementById('modal-img').src = p['Primary Image'];
            document.getElementById('modal-title').innerText = p['Product Name'];
            document.getElementById('modal-price').innerText = "$" + p.Variants[0].price.toFixed(2);
            document.getElementById('modal-desc').innerHTML = p.Description;
            document.getElementById('product-modal').style.display = 'flex';
        }}

        function closeModal() {{ document.getElementById('product-modal').style.display = 'none'; }}
        
        window.onload = initStore;
    </script>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    duration = time.time() - start_time
    status_msg = f"{time.ctime()} | SUCCESS | Processed: {processed_count} | Defects: {error_count} | Speed: {processed_count/duration:.2f} items/sec"
    with open(log_path, "a") as log: log.write(status_msg + "\\n")
    print(status_msg)

if __name__ == "__main__":
    generate_storefront()
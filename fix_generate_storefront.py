import json
import csv
import os
import hashlib
import time

# --- PATHS ---
csv_path = os.path.expanduser("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
html_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/index.html")
log_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/build_manifest.log")

# --- MASTER CATEGORIZATION ---
CATEGORY_STRUCTURE = {
    "GENERAL": ["All gear", "Featured"],
    "BONGS": ["Beaker", "Straight Tube", "Gravity", "Modular", "Silicone", "Glass"],
    "DAB RIGS": ["Glass", "Silicone", "Recycler", "Mini Rigs"],
    "VAPORIZERS": ["Handheld", "Desktop", "Enails & Erigs", "Vape Pens", "Dab Pens", "Dry Herb", "Wax", "Dual Function"],
    "BUBBLERS": ["Upright", "Sherlock", "Hammer", "Mini", "Mini Joint"],
    "HAND PIPES": ["Spoon", "Sherlock & Gandalf", "Steamroller", "One Hitters & Chillums", "Nectar Collectors & Dab Straws", "Glass", "Silicone"],
    "ROLLING SUPPLIES": ["Papers/Pre-Rolls/Wraps", "Trays", "Grinders", "Tips/Filters", "Machines"],
    "DABBING TOOLS": ["Quartz Bangers & Nails", "Carb Caps", "Torches", "Dabbers & Hot Knifes", "Non-Stick Wax Storage", "Timers/Thermometers", "Mats/Pads"],
    "VAPE ACCESSORIES": ["Atomizers & Coils", "Bubblers & Glass Attachments", "Parts & Adapters", "Cases & Travel Gear", "Mouthpieces & Tips", "Vape To Bong Adapters", "Balloon Bags", "Whips/Wands/Tubing", "Chargers", "Replacement Batteries"],
    "WHOLESALE": ["POP Displays"]
}

def generate_storefront():
    start_time = time.time()
    grouped_products = {}
    master_brands = set()
    processed_count = 0

    if not os.path.exists(csv_path):
        print(f"❌ DATABASE ERROR: CSV missing at {csv_path}")
        return

    # 1. PROCESS DATABASE & GROUP VARIANTS
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row in reader:
            try:
                retail = float(row.get("Your Retail Price", 0) or 0)
                if retail <= 0 or row.get("Status") == "Hidden": continue 

                title = row.get("Product Name", "").strip()
                cat = row.get("Product Type", "Accessories").strip() or "Accessories"
                brand = row.get("Brand", "Premium").strip() or "Premium"
                variant_name = row.get("Variant", "").strip() or "Standard"
                img_url = row.get("Image URL", "").strip() or "https://via.placeholder.com/400"
                
                # UNIQUE DESCRIPTION per item
                unique_desc = row.get("Description", "").replace('"', '&quot;').replace('\n', '<br>')
                
                master_brands.add(brand)
                
                if title not in grouped_products:
                    grouped_products[title] = {
                        "name": title,
                        "brand": brand,
                        "category": cat,
                        "featured": row.get("Featured") == "Yes",
                        "image": img_url,
                        "Variants": [] # Capital 'V' for app.js compatibility
                    }
                
                grouped_products[title]["Variants"].append({
                    "name": variant_name,
                    "sku": row.get("SKU"),
                    "price": retail,
                    "image": img_url,
                    "description": unique_desc
                })
                processed_count += 1
            except:
                continue

    all_products_array = list(grouped_products.values())
    
    # CRITICAL: Process JSON outside f-string to avoid backslash SyntaxErrors
    json_products = json.dumps(all_products_array).replace('</', '<\\/')
    json_cats = json.dumps(CATEGORY_STRUCTURE)
    json_brands = json.dumps(sorted(list(master_brands)))

    # 2. GENERATE FULL HTML PAGE
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixie's Pantry | Hardware Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #ffffff; color: #111; margin: 0; display: flex; min-height: 100vh; overflow-x: hidden; }}
        .sidebar {{ width: 320px; background: #f9f9f9; padding: 30px 20px; border-right: 1px solid #eaeaea; position: fixed; height: 100vh; overflow-y: auto; box-sizing: border-box; display: flex; flex-direction: column; gap: 15px; z-index: 10; }}
        .sidebar h2 {{ font-size: 1.4em; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }}
        .sidebar h3 {{ font-size: 0.75em; text-transform: uppercase; border-bottom: 2px solid #111; padding-bottom: 5px; margin-top: 25px; }}
        .group-label {{ font-size: 0.7em; font-weight: 900; color: #aaa; text-transform: uppercase; margin-top: 15px; margin-bottom: 5px; }}
        .nav-list {{ list-style: none; padding: 0; margin: 0; }}
        .nav-item {{ padding: 6px 12px; cursor: pointer; font-size: 0.8em; color: #666; border-radius: 4px; transition: 0.2s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .nav-item:hover, .nav-item.active {{ background: #111; color: #fff; font-weight: bold; }}
        .main-content {{ flex-grow: 1; margin-left: 320px; padding: 40px 50px; box-sizing: border-box; }}
        .banner {{ background: #111; color: #fff; padding: 12px; text-align: center; font-weight: bold; letter-spacing: 2px; font-size: 0.85em; margin: -40px -50px 30px -50px; position: sticky; top: 0; z-index: 5; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 25px; }}
        .card {{ background: #fff; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #f0f0f0; transition: all 0.2s; cursor: pointer; height: 100%; display: flex; flex-direction: column; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.06); }}
        .image-container img {{ max-width: 100%; max-height: 180px; object-fit: contain; }}
        .cart-toggle {{ position: fixed; bottom: 30px; right: 30px; background: #111; color: #fff; border: none; padding: 15px 25px; border-radius: 30px; font-weight: bold; cursor: pointer; z-index: 1000; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }}
        .cart-panel {{ position: fixed; top: 0; right: -450px; width: 400px; height: 100%; background: #fff; box-shadow: -5px 0 30px rgba(0,0,0,0.1); z-index: 2001; transition: right 0.3s ease; display: flex; flex-direction: column; }}
        .cart-panel.open {{ right: 0; }}
        .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; align-items: center; justify-content: center; backdrop-filter: blur(5px); }}
        .modal-content {{ background: #fff; width: 950px; max-width: 95%; height: 650px; border-radius: 12px; display: flex; overflow: hidden; position: relative; }}
        select {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em; margin: 15px 0; outline: none; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; font-size: 0.75em; font-weight: 900; color: #888; text-transform: uppercase; margin-bottom: 5px; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .address-row {{ display: flex; gap: 10px; }}
        @media (max-width: 768px) {{ .sidebar {{ display: none; }} .main-content {{ margin-left: 0; }} }}
    </style>
</head>
<body>

    <div class="sidebar">
        <div><h2>Pixie's Pantry</h2><p style="font-size: 0.8em; color: #888;">Group Buy Catalog</p></div>
        <input type="text" id="searchInput" placeholder="Search brands, gear..." oninput="applyFilters()" style="padding:10px; border:1px solid #ddd; border-radius:4px;">
        <div id="category-menu"></div>
        <h3>Shop By Brand</h3>
        <ul class="nav-list" id="brand-menu"></ul>
    </div>

    <div class="main-content">
        <div class="banner">DISCORD GROUP BUY | FAST SHIPPING FROM MISSISSIPPI</div>
        <h1 id="page-title">Hardware Catalog</h1>
        <p id="item-count" style="color:#888; font-size: 0.9em; margin-bottom: 20px;"></p>
        <div id="product-grid" class="grid"></div>
    </div>

    <div class="modal-overlay" id="product-modal" onclick="if(event.target.id==='product-modal') closeModal()">
        <div class="modal-content">
            <button onclick="closeModal()" style="position:absolute; top:20px; right:20px; border:none; background:none; font-size:2em; color:#888; cursor:pointer;">&times;</button>
            <div style="display:flex; width:100%; height:100%; flex-wrap:wrap;">
                <div style="flex:1; min-width:300px; background:#f9f9f9; display:flex; align-items:center; justify-content:center; padding:30px;">
                    <img id="modal-img" style="max-width:100%; max-height:450px; object-fit:contain;">
                </div>
                <div style="flex:1.2; min-width:300px; padding:40px; overflow-y:auto;">
                    <div id="modal-brand" class="brand-badge"></div>
                    <h2 id="modal-title" style="font-weight:800; margin-bottom:10px;"></h2>
                    <div id="variant-area"></div>
                    <div id="modal-price" style="font-size:2.2em; font-weight:bold; margin-bottom:15px;"></div>
                    <button id="add-btn" style="width:100%; background:#111; color:#fff; border:none; padding:18px; font-weight:bold; border-radius:6px; cursor:pointer;">Add to Order</button>
                    <div id="modal-desc" style="color:#666; line-height:1.6; margin-top:30px; padding-top:20px; border-top:1px solid #eee; font-size:0.95em;"></div>
                </div>
            </div>
        </div>
    </div>

    <button class="cart-toggle" onclick="toggleCart()">🛒 CART (<span id="cart-count">0</span>)</button>

    <div class="cart-panel" id="cart-panel">
        <div style="padding:25px; background:#f9f9f9; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
            <h2 style="margin:0; font-size:1.2em;">YOUR ORDER</h2>
            <button onclick="toggleCart()" style="border:none; background:none; font-size:1.5em; cursor:pointer;">&times;</button>
        </div>
        <div id="cart-items" style="flex-grow:1; overflow-y:auto; padding:25px;"></div>
        <div style="padding:25px; border-top:1px solid #eee;">
            <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.2em; margin-bottom:20px;">
                <span>Subtotal:</span><span id="cart-total">$0.00</span>
            </div>
            <form action="https://formspree.io/f/xjgaaroa" method="POST" id="checkout-form">
                <div class="form-group"><label>Discord Username</label><input type="text" name="discord" placeholder="User#1234" required></div>
                <h4 style="font-size:0.7em; color:#aaa; text-transform:uppercase; margin:20px 0 10px;">Shipping Address</h4>
                <div class="form-group"><label>Full Name</label><input type="text" name="ship_name" required></div>
                <div class="form-group"><label>Street</label><input type="text" name="ship_street" required></div>
                <div class="address-row">
                    <input type="text" name="ship_city" placeholder="City" required style="flex:2; padding:10px; border:1px solid #ddd; border-radius:4px;">
                    <input type="text" name="ship_state" placeholder="State" required style="flex:1; padding:10px; border:1px solid #ddd; border-radius:4px;">
                </div>
                <div class="form-group" style="margin-top:10px;"><label>Zip</label><input type="text" name="ship_zip" required></div>
                <input type="hidden" name="Order Details" id="order-payload">
                <button type="submit" style="width:100%; background:#111; color:#fff; border:none; padding:15px; font-weight:bold; border-radius:4px; margin-top:10px;">Submit Order sheet</button>
            </form>
        </div>
    </div>

    <script>
        const allProducts = {json_products};
        const CATEGORIES = {json_cats};
        const BRANDS = {json_brands};
        
        let cart = JSON.parse(localStorage.getItem('pixies_cart')) || [];
        let activeFilter = "All gear";
        let activeBrand = "All";

        function init() {{
            const catMenu = document.getElementById('category-menu');
            for (const [group, items] of Object.entries(CATEGORIES)) {{
                let html = `<div class="group-label">${{group}}</div><ul class="nav-list">`;
                items.forEach(item => {{
                    html += `<li class="nav-item ${{activeFilter === item ? 'active' : ''}}" onclick="setFilter('cat', '${{item}}', this)">${{item}}</li>`;
                }});
                catMenu.innerHTML += html + '</ul>';
            }}
            
            const brandMenu = document.getElementById('brand-menu');
            brandMenu.innerHTML = `<li class="nav-item active" onclick="setFilter('brand', 'All', this)">All Brands</li>`;
            BRANDS.forEach(b => {{ brandMenu.innerHTML += `<li class="nav-item" onclick="setFilter('brand', '${{b}}', this)">${{b}}</li>`; }});
            
            updateCartUI();
            applyFilters();
        }}

        function setFilter(type, val, el) {{
            if(type === 'cat') activeFilter = val; else activeBrand = val;
            const parent = el.closest('ul') || el.closest('.sidebar');
            parent.querySelectorAll('.nav-item').forEach(li => li.classList.remove('active'));
            el.classList.add('active');
            applyFilters();
        }}

        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const filtered = allProducts.filter(p => {{
                const nameMatch = p.name.toLowerCase().includes(search) || p.brand.toLowerCase().includes(search);
                let catMatch = activeFilter === "All gear" || p.category.toLowerCase().includes(activeFilter.toLowerCase());
                if(activeFilter === "Featured") catMatch = p.featured;
                const brandMatch = activeBrand === "All" || p.brand === activeBrand;
                return nameMatch && catMatch && brandMatch;
            }});
            renderGrid(filtered);
            document.getElementById('page-title').innerText = activeBrand !== "All" ? activeBrand : activeFilter;
        }}

        function renderGrid(products) {{
            const grid = document.getElementById('product-grid');
            grid.innerHTML = products.map(p => `
                <div class="card" onclick="openModal('${{p.name.replace(/'/g, "\\\\'")}}')">
                    <div class="image-container"><img src="${{p.image}}" loading="lazy"></div>
                    <div class="brand-badge">${{p.brand}}</div>
                    <div class="title">${{p.name}}</div>
                    <div style="font-weight:bold; margin-top:auto;">From $${{p.Variants[0].price.toFixed(2)}}</div>
                </div>
            `).join('');
            document.getElementById('item-count').innerText = products.length + " products synced";
        }}

        function openModal(name) {{
            const p = allProducts.find(x => x.name === name);
            if(!p) return;
            document.getElementById('modal-title').innerText = p.name;
            document.getElementById('modal-brand').innerText = p.brand;
            
            const vArea = document.getElementById('variant-area');
            if(p.Variants.length > 1) {{
                vArea.innerHTML = `<label style="font-size:0.7em; font-weight:900; color:#aaa;">COLOR / OPTION</label>
                                   <select id="v-select" onchange="updateUI('${{name.replace(/'/g, "\\\\'")}}')">
                                   ${{p.Variants.map((v, i) => `<option value="${{i}}">${{v.name}}</option>`).join('')}}</select>`;
            }} else {{ vArea.innerHTML = ''; }}
            
            updateUI(name);
            document.getElementById('product-modal').style.display = 'flex';
        }}

        function updateUI(name) {{
            const p = allProducts.find(x => x.name === name);
            const sel = document.getElementById('v-select');
            const variant = p.Variants[sel ? sel.value : 0];
            
            document.getElementById('modal-img').src = variant.image;
            document.getElementById('modal-price').innerText = "$" + variant.price.toFixed(2);
            document.getElementById('modal-desc').innerHTML = variant.description;
            document.getElementById('add-btn').onclick = () => addToCart(p.name, variant);
        }}

        function toggleCart() {{ document.getElementById('cart-panel').classList.toggle('open'); }}
        function closeModal() {{ document.getElementById('product-modal').style.display = 'none'; }}

        function addToCart(name, variant) {{
            cart.push({{ name, variant: variant.name, price: variant.price, sku: variant.sku }});
            localStorage.setItem('pixies_cart', JSON.stringify(cart));
            updateCartUI(); toggleCart(); closeModal();
        }}

        function updateCartUI() {{
            const container = document.getElementById('cart-items');
            let total = 0;
            container.innerHTML = cart.map((item, i) => {{
                total += item.price;
                return `<div style="margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:10px;">
                        <div style="font-weight:bold; font-size:0.85em;">${{item.name}}</div>
                        <div style="font-size:0.75em; color:#888;">${{item.variant}} ($${{item.price.toFixed(2)}})</div>
                        <button onclick="removeItem(${{i}})" style="color:red; background:none; border:none; font-size:0.7em; cursor:pointer;">Remove</button>
                        </div>`;
            }}).join('');
            document.getElementById('cart-total').innerText = "$" + total.toFixed(2);
            document.getElementById('cart-count').innerText = cart.length;
            
            let summary = "ORDER SUMMARY:\\n";
            cart.forEach(item => summary += `- ${{item.name}} (${{item.variant}}) SKU: ${{item.sku}}\\n`);
            document.getElementById('order-payload').value = summary;
        }}

        function removeItem(i) {{ cart.splice(i, 1); localStorage.setItem('pixies_cart', JSON.stringify(cart)); updateCartUI(); }}

        window.onload = init;
    </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Build Success | {processed_count} variations synced | Shop generated at {html_path}")

if __name__ == "__main__":
    generate_storefront()
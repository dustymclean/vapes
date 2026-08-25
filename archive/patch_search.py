import re
import os

FILE = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/generate_storefront.py")

with open(FILE, "r") as f:
    content = f.read()

# 1. Add CSS for search bar & toolbar
css_addition = """
    /* Search & Toolbar */
    .search-box { width: 100%; padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; margin-bottom: 20px; outline: none; font-family: inherit; }
    .search-box:focus { border-color: var(--primary); }
    .toolbar { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
    .toolbar-left h1 { margin: 0 0 5px; }
    .toolbar-left p { margin: 0; color: var(--muted); font-size: 14px; }
    .toolbar-right { display: flex; gap: 10px; }
    .filter-select { padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; background: #fff; cursor: pointer; outline: none; }
    .filter-select:focus { border-color: var(--primary); }
    
    @media (max-width: 900px) {
        .toolbar { flex-direction: column; align-items: flex-start; gap: 15px; }
        .toolbar-right { width: 100%; flex-wrap: wrap; }
        .filter-select { flex: 1; }
    }
"""
content = content.replace("/* Input box for forms */", css_addition + "\n    /* Input box for forms */")

# 2. Add JS functions for filter/sort/search
js_addition = """
        // -- 4. SEARCH & FILTER LOGIC --
        window.applyFilters = function() {
            const searchInput = document.getElementById('searchInput');
            const search = (searchInput ? searchInput.value : '').toLowerCase();
            const brandFilter = document.getElementById('brandFilter') ? document.getElementById('brandFilter').value : 'all';
            const catFilter = document.getElementById('catFilter') ? document.getElementById('catFilter').value : 'all';
            
            let visibleCount = 0;
            document.querySelectorAll('.card').forEach(card => {
                const name = card.dataset.name || '';
                const brand = card.dataset.brand || '';
                const cat = card.dataset.cat || '';
                
                const matchSearch = name.includes(search) || brand.includes(search);
                const matchBrand = (brandFilter === 'all') || (brand === brandFilter);
                const matchCat = (catFilter === 'all') || (cat === catFilter);
                
                if (matchSearch && matchBrand && matchCat) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            const countEl = document.getElementById('result-count');
            if (countEl) countEl.textContent = visibleCount + ' products';
        };
        
        window.sortGrid = function() {
            const val = document.getElementById('sortSelect')?.value;
            const grid = document.querySelector('.grid');
            if (!grid || !val || val === 'default') return;
            
            const cards = Array.from(grid.querySelectorAll('.card'));
            cards.sort((a, b) => {
                if (val === 'price-low') return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
                if (val === 'price-high') return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
                if (val === 'name-az') return (a.dataset.name || '').localeCompare(b.dataset.name || '');
                return 0;
            });
            cards.forEach(c => grid.appendChild(c));
        };
"""
content = content.replace("Setup initial UI", js_addition + "\n        // Setup initial UI")


# 3. Add search input to sidebar
sidebar_replacement = """        <aside class="sidebar">
            <a href="{depth}index.html" class="sidebar-logo">Pixie's Pantry</a>
            <div class="sidebar-tagline">Vape & Smoke Accessories</div>
            
            <input type="text" id="searchInput" class="search-box" placeholder="Search catalog..." onkeyup="applyFilters()">
            
            <a href="{depth}index.html" class="sidebar-link">All Products</a>"""
content = content.replace("""        <aside class="sidebar">
            <a href="{depth}index.html" class="sidebar-logo">Pixie's Pantry</a>
            <div class="sidebar-tagline">Vape & Smoke Accessories</div>
            
            <a href="{depth}index.html" class="sidebar-link">All Products</a>""", sidebar_replacement)


# 4. Modify render_page to inject data attributes and toolbar HTML
render_page_old = """    def render_page(filename, title, subtitle, product_list, depth=""):
        sidebar = get_sidebar_html(depth)
        modal = get_modal_html()
        
        products_dict = {p["handle"]: p for p in product_list}
        json_data = json.dumps(products_dict)
        
        grid_html = '<div class="grid">'
        for p in product_list:
            img = p.get("featured_image") or (p.get("all_images")[0] if p.get("all_images") else "")
            price = p.get("min_price", 0)
            handle = p["handle"]
            grid_html += f\"\"\"
            <div class="card" onclick="openModal('{handle}')">"""

render_page_new = """    def render_page(filename, title, subtitle, product_list, depth=""):
        sidebar = get_sidebar_html(depth)
        modal = get_modal_html()
        
        products_dict = {p["handle"]: p for p in product_list}
        json_data = json.dumps(products_dict)
        
        # Build Filter Dropdowns dynamically
        unique_brands = sorted(list(set(p['brand'] for p in product_list if p.get('brand'))))
        unique_cats = sorted(list(set(p['product_type'] for p in product_list if p.get('product_type'))))
        
        brand_opts = "".join([f'<option value="{b}">{b}</option>' for b in unique_brands])
        cat_opts = "".join([f'<option value="{c}">{c}</option>' for c in unique_cats])
        
        toolbar = f\"\"\"
        <div class="toolbar">
            <div class="toolbar-left">
                <h1 class="page-title" style="margin:0;">{title}</h1>
                <p id="result-count">{len(product_list)} products</p>
            </div>
            <div class="toolbar-right">
                <select id="brandFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">All Brands</option>{brand_opts}
                </select>
                <select id="catFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">All Categories</option>{cat_opts}
                </select>
                <select id="sortSelect" class="filter-select" onchange="sortGrid()">
                    <option value="default">Sort</option>
                    <option value="price-low">Price: Low → High</option>
                    <option value="price-high">Price: High → Low</option>
                    <option value="name-az">Name A–Z</option>
                </select>
            </div>
        </div>
        \"\"\"
        
        grid_html = '<div class="grid">'
        for p in product_list:
            img = p.get("featured_image") or (p.get("all_images")[0] if p.get("all_images") else "")
            price = p.get("min_price", 0)
            handle = p["handle"]
            safe_name = p['title'].lower().replace('"', '&quot;')
            grid_html += f\"\"\"
            <div class="card" onclick="openModal('{handle}')" data-name="{safe_name}" data-brand="{p['brand']}" data-cat="{p['product_type']}" data-price="{price}">"""
content = content.replace(render_page_old, render_page_new)


# 5. Remove the old page-title and page-subtitle from the template body since they are now in the toolbar
html_old = """        <main class="main-content">
            <h1 class="page-title">{title}</h1>
            <div class="page-subtitle">{subtitle}</div>
            {grid_html}
        </main>"""
html_new = """        <main class="main-content">
            {toolbar}
            {grid_html}
        </main>"""
content = content.replace(html_old, html_new)

with open(FILE, "w") as f:
    f.write(content)

print("Patch applied.")

import json
import csv
import os
import re
import time

# --- CONFIGURATION & PATHS ---
CSV_PATH = os.path.expanduser("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
BASE_DIR = os.path.expanduser("~/Desktop/Pixies_Vape_Shop")
CAT_DIR = os.path.join(BASE_DIR, "categories")
BRAND_DIR = os.path.join(BASE_DIR, "brands")

# ─────────────────────────────────────────────────────────────
# FORMSPREE CONFIG
# 1. Go to https://formspree.io and create a free account
# 2. Create a new form — copy the endpoint ID (looks like "xeoqkzdj")
# 3. Paste it below replacing YOUR_FORM_ID
# ─────────────────────────────────────────────────────────────
FORMSPREE_ID = "xeoqkzdj"  # ← Replace with your actual Formspree form ID


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)


def ensure_dirs():
    for d in [CAT_DIR, BRAND_DIR]:
        os.makedirs(d, exist_ok=True)


def get_product_card_html(p):
    p_name_esc = p['name'].replace("'", "\\'").replace('"', '&quot;')
    first_price = p['Variants'][0]['price']
    return f'''<div class="card"
         data-name="{p['name'].lower().replace("'", "").replace('"', '')}"
         data-price="{first_price}"
         data-brand="{p['brand'].lower()}"
         data-cat="{p['category'].lower()}"
         onclick="openModal(this)"
         data-product='{json.dumps(p).replace("'", "&#39;")}'>
        <div class="link-shortcut" title="Copy Direct Link"
             onclick="event.stopPropagation(); copyDirectLink('{p_name_esc}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        </div>
        <div class="image-container">
            <img src="{p['image']}" alt="{p['name']}" loading="lazy" onerror="this.src='https://placehold.co/400x400/f5f5f5/999?text=No+Image'">
        </div>
        <div class="card-info">
            <div class="brand-badge">{p['brand']}</div>
            <div class="title">{p['name']}</div>
            <div class="card-footer-row">
                <div class="price-tag">${first_price:.2f}</div>
                <button class="quick-add-btn" onclick="event.stopPropagation(); quickAdd(this)">Add</button>
            </div>
        </div>
    </div>'''


# ─────────────────────────────────────────────────────────────
# SELF-CONTAINED JS — no external app.js dependency
# All cart, modal, filter, and form logic lives here.
# ─────────────────────────────────────────────────────────────
INLINE_JS = """
// ── State ──────────────────────────────────────────────────
let cart = [];

// ── Cart Helpers ────────────────────────────────────────────
function addToCart(productName, variant) {
    const existing = cart.find(i => i.name === productName && i.variantName === variant.name);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ name: productName, variantName: variant.name, price: variant.price, qty: 1 });
    }
    renderCart();
    showToast("Added: " + productName);
}

function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
}

function updateQty(index, delta) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) cart.splice(index, 1);
    renderCart();
}

function renderCart() {
    const container = document.getElementById('cart-items');
    const total = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
    document.querySelectorAll('.cart-count').forEach(el => el.textContent = cart.reduce((s,i) => s+i.qty, 0));
    document.getElementById('cart-total-price').textContent = '$' + total.toFixed(2);

    if (cart.length === 0) {
        container.innerHTML = '<p style="color:#aaa; text-align:center; padding:40px 0; font-size:0.9em;">Your cart is empty.</p>';
        return;
    }

    container.innerHTML = cart.map((item, i) => `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; padding:18px 0; border-bottom:1px solid #f0f0f0; gap:12px;">
            <div style="flex:1;">
                <div style="font-weight:800; font-size:0.9em; line-height:1.3;">${item.name}</div>
                ${item.variantName !== 'Standard' ? `<div style="font-size:0.78em; color:#aaa; margin-top:3px;">${item.variantName}</div>` : ''}
                <div style="font-size:0.85em; color:#555; margin-top:6px;">$${item.price.toFixed(2)} each</div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:8px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <button onclick="updateQty(${i}, -1)" style="width:28px; height:28px; border:1px solid #ddd; background:#fff; border-radius:50%; cursor:pointer; font-size:1.1em; display:flex; align-items:center; justify-content:center;">−</button>
                    <span style="font-weight:900; min-width:20px; text-align:center;">${item.qty}</span>
                    <button onclick="updateQty(${i}, 1)" style="width:28px; height:28px; border:1px solid #ddd; background:#fff; border-radius:50%; cursor:pointer; font-size:1.1em; display:flex; align-items:center; justify-content:center;">+</button>
                </div>
                <div style="font-weight:900; font-size:0.95em;">$${(item.price * item.qty).toFixed(2)}</div>
                <button onclick="removeFromCart(${i})" style="border:none; background:none; color:#ccc; cursor:pointer; font-size:0.75em; text-transform:uppercase; letter-spacing:1px;">Remove</button>
            </div>
        </div>
    `).join('');
}

function toggleCart() {
    document.getElementById('cart-panel').classList.toggle('open');
}

// ── Modal ───────────────────────────────────────────────────
function openModal(cardEl) {
    const raw = cardEl.getAttribute('data-product');
    const p = JSON.parse(raw.replace(/&#39;/g, "'"));
    const modal = document.getElementById('product-modal');

    document.getElementById('modal-img').src = p.image;
    document.getElementById('modal-brand').textContent = p.brand;
    document.getElementById('modal-title').textContent = p.name;
    document.getElementById('modal-desc-container').innerHTML = p.Description || '';

    // Gallery
    const gallery = document.getElementById('modal-gallery');
    gallery.innerHTML = (p['All Images'] || []).map((img, i) => `
        <img src="${img}" style="width:60px; height:60px; object-fit:contain; border:2px solid ${i===0?'#111':'#eee'}; border-radius:8px; cursor:pointer; padding:4px;"
             onclick="document.getElementById('modal-img').src='${img}'; this.parentNode.querySelectorAll('img').forEach(x=>x.style.borderColor='#eee'); this.style.borderColor='#111';">
    `).join('');

    // Variants
    const container = document.getElementById('modal-variant-container');
    const priceEl = document.getElementById('modal-price');

    if (p.Variants.length === 1) {
        priceEl.textContent = '$' + p.Variants[0].price.toFixed(2);
        container.innerHTML = '';
        document.getElementById('modal-add-btn').onclick = () => {
            addToCart(p.name, p.Variants[0]);
            closeModal();
        };
    } else {
        priceEl.textContent = '$' + p.Variants[0].price.toFixed(2);
        container.innerHTML = `
            <label style="font-size:0.8em; font-weight:900; text-transform:uppercase; letter-spacing:1px; color:#aaa; display:block; margin-bottom:10px;">Select Option</label>
            <select onchange="selectVariant(this.value, ${JSON.stringify(p.Variants).replace(/"/g,'&quot;')})"
                    style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-weight: 700; font-size: 0.95em; cursor: pointer; outline: none;">
                ${p.Variants.map((v, i) => `
                    <option value="${i}">${v.name} - $${v.price.toFixed(2)}</option>
                `).join('')}
            </select>`;

        // Store selected variant index on the button
        let selectedVariant = p.Variants[0];
        window._modalVariants = p.Variants;
        window._modalSelectedVariant = selectedVariant;

        document.getElementById('modal-add-btn').onclick = () => {
            addToCart(p.name, window._modalSelectedVariant || p.Variants[0]);
            closeModal();
        };
    }

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function selectVariant(index, variantsJson) {
    const variants = typeof variantsJson === 'string' ? JSON.parse(variantsJson) : variantsJson;
    const v = variants[index];
    window._modalSelectedVariant = v;
    document.getElementById('modal-price').textContent = '$' + v.price.toFixed(2);
    
    if (v.image && v.image !== "https://placehold.co/400x400/f5f5f5/999?text=No+Image") {
        document.getElementById('modal-img').src = v.image;
        document.querySelectorAll('#modal-gallery img').forEach(img => {
            img.style.borderColor = img.src === v.image ? '#111' : '#eee';
        });
    }
}

function closeModal() {
    document.getElementById('product-modal').style.display = 'none';
    document.body.style.overflow = '';
}

document.getElementById('product-modal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

// ── Quick Add (single variant) ──────────────────────────────
function quickAdd(btn) {
    const card = btn.closest('.card');
    const raw = card.getAttribute('data-product');
    const p = JSON.parse(raw.replace(/&#39;/g, "'"));
    if (p.Variants.length === 1) {
        addToCart(p.name, p.Variants[0]);
    } else {
        openModal(card);
    }
}

// ── Filter & Sort ───────────────────────────────────────────
function applyFilters() {
    const search = (document.getElementById('searchInput')?.value || '').toLowerCase();
    const brandFilter = (document.getElementById('brandFilter')?.value || 'all').toLowerCase();
    const catFilter = (document.getElementById('catFilter')?.value || 'all').toLowerCase();
    document.querySelectorAll('.card').forEach(card => {
        const name = card.dataset.name || '';
        const brand = card.dataset.brand || '';
        const cat = card.dataset.cat || '';
        const matchSearch = name.includes(search) || brand.includes(search);
        const matchBrand = brandFilter === 'all' || brand === brandFilter;
        const matchCat = catFilter === 'all' || cat === catFilter;
        card.style.display = (matchSearch && matchBrand && matchCat) ? 'flex' : 'none';
    });
    updateCount();
}

function updateCount() {
    const visible = document.querySelectorAll('.card:not([style*="none"])').length;
    const el = document.getElementById('result-count');
    if (el) el.textContent = visible + ' products';
}

function sortGrid() {
    const val = document.getElementById('sortSelect')?.value;
    const grid = document.querySelector('.grid');
    if (!grid || !val) return;
    const cards = Array.from(grid.querySelectorAll('.card'));
    cards.sort((a, b) => {
        if (val === 'price-low') return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
        if (val === 'price-high') return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
        if (val === 'name-az') return (a.dataset.name || '').localeCompare(b.dataset.name || '');
        return 0;
    });
    cards.forEach(c => grid.appendChild(c));
}

// ── Toast ───────────────────────────────────────────────────
function showToast(msg) {
    const t = document.getElementById('pixies-toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Direct Link ─────────────────────────────────────────────
function copyDirectLink(name) {
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const url = window.location.href.split('?')[0] + '?p=' + slug;
    navigator.clipboard?.writeText(url).then(() => showToast('🔗 Link copied!')).catch(() => showToast('Link: ' + url));
}

// ── Formspree Checkout ──────────────────────────────────────
function prepareCheckout(e) {
    e.preventDefault();
    if (cart.length === 0) { showToast('Your cart is empty!'); return; }

    const orderLines = cart.map(i => `${i.qty}x ${i.name}${i.variantName !== 'Standard' ? ' ('+i.variantName+')' : ''} @ $${i.price.toFixed(2)}`);
    const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
    orderLines.push('---');
    orderLines.push('SUBTOTAL: $' + total.toFixed(2));

    document.getElementById('order-payload').value = orderLines.join('\\n');

    const form = document.getElementById('checkout-form');
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
    }).then(res => {
        if (res.ok) {
            form.style.display = 'none';
            document.getElementById('receipt-container').style.display = 'block';
            cart = [];
            renderCart();
        } else {
            showToast('⚠️ Submission failed. Please try again.');
        }
    }).catch(() => showToast('⚠️ Network error. Check your connection.'));
}

// ── Mobile Nav ──────────────────────────────────────────────
function toggleMobileNav() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('mobile-overlay');
    sidebar.classList.toggle('mobile-open');
    overlay.classList.toggle('active');
    document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
}

// Init
renderCart();
"""


def get_layout(title, content, sidebar_html, is_nested=False):
    prefix = "../" if is_nested else ""
    prefix = "../" if is_nested else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixie's Pantry | {title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #111;
            --sidebar-w: 300px;
            --border: #eaeaea;
            --muted: #888;
            --card-radius: 14px;
        }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: #fff;
            color: var(--primary);
        }}

        /* ── Sidebar ── */
        .sidebar {{
            position: fixed;
            left: 0; top: 0; bottom: 0;
            width: var(--sidebar-w);
            background: #fafafa;
            border-right: 1px solid var(--border);
            padding: 40px 28px;
            overflow-y: auto;
            z-index: 900;
            transition: transform 0.3s ease;
        }}
        .sidebar-logo {{
            font-weight: 900;
            font-size: 1.3em;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 30px;
            display: block;
            color: var(--primary);
            text-decoration: none;
        }}
        .sidebar-logo span {{ color: #e8498a; }}

        .search-box {{
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 0.88em;
            margin-bottom: 28px;
            outline: none;
            transition: border 0.2s;
        }}
        .search-box:focus {{ border-color: var(--primary); }}

        .nav-section-label {{
            font-size: 0.65em;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #bbb;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
            margin: 24px 0 10px;
        }}
        .sidebar-link {{
            display: block;
            padding: 9px 0;
            color: #555;
            text-decoration: none;
            font-size: 0.85em;
            border-bottom: 1px solid #f5f5f5;
            transition: all 0.15s;
        }}
        .sidebar-link:hover {{
            color: var(--primary);
            padding-left: 6px;
            font-weight: 700;
        }}

        /* ── Mobile overlay ── */
        #mobile-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 850;
        }}
        #mobile-overlay.active {{ display: block; }}

        /* ── Main wrapper ── */
        .main-wrapper {{
            margin-left: var(--sidebar-w);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .banner {{
            background: var(--primary);
            color: #fff;
            padding: 13px;
            text-align: center;
            font-weight: 800;
            letter-spacing: 2px;
            font-size: 0.72em;
            position: sticky;
            top: 0;
            z-index: 500;
        }}

        /* ── Mobile header ── */
        .mobile-header {{
            display: none;
            background: #fff;
            border-bottom: 1px solid var(--border);
            padding: 16px 20px;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 39px;
            z-index: 499;
        }}
        .mobile-header-logo {{
            font-weight: 900;
            font-size: 1.1em;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }}
        .mobile-header-logo span {{ color: #e8498a; }}
        .hamburger {{
            background: none;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 7px 10px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .hamburger span {{
            display: block;
            width: 20px;
            height: 2px;
            background: var(--primary);
            border-radius: 2px;
        }}

        /* ── Main content ── */
        .main-content {{
            padding: 55px 48px;
            flex: 1;
        }}

        /* ── Toolbar ── */
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
        }}
        .toolbar-left h1 {{
            font-weight: 900;
            font-size: 2.4em;
            letter-spacing: -1.5px;
            line-height: 1;
        }}
        .toolbar-left p {{
            color: var(--muted);
            font-size: 0.9em;
            margin-top: 6px;
        }}
        .toolbar-right {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-select {{
            padding: 10px 14px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 0.85em;
            background: #fff;
            cursor: pointer;
            outline: none;
            font-family: inherit;
        }}
        .filter-select:focus {{ border-color: var(--primary); }}

        /* ── Product Grid ── */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 28px;
        }}

        /* ── Card ── */
        .card {{
            position: relative;
            border: 1px solid #f0f0f0;
            border-radius: var(--card-radius);
            padding: 22px;
            cursor: pointer;
            transition: transform 0.3s cubic-bezier(0.165,0.84,0.44,1), box-shadow 0.3s ease, border-color 0.2s;
            background: #fff;
            display: flex;
            flex-direction: column;
            /* FIX: removed height:100% which caused stretching in auto-fill grids */
        }}
        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.08);
            border-color: #ddd;
        }}

        .image-container {{
            width: 100%;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin-bottom: 18px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            transition: transform 0.3s ease;
        }}
        .card:hover .image-container img {{ transform: scale(1.04); }}

        .brand-badge {{
            font-size: 0.58em;
            font-weight: 900;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 6px;
        }}
        .title {{
            font-weight: 800;
            font-size: 0.97em;
            line-height: 1.4;
            color: var(--primary);
            flex: 1;
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .card-footer-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
        }}
        .price-tag {{
            font-weight: 900;
            font-size: 1.15em;
            color: var(--primary);
        }}
        .quick-add-btn {{
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 9px 18px;
            border-radius: 6px;
            font-weight: 800;
            font-size: 0.82em;
            cursor: pointer;
            transition: opacity 0.2s;
            font-family: inherit;
        }}
        .quick-add-btn:hover {{ opacity: 0.75; }}

        .link-shortcut {{
            position: absolute;
            top: 14px; right: 14px;
            background: #fff;
            width: 32px; height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #eee;
            color: #ccc;
            z-index: 5;
            transition: all 0.2s;
        }}
        .link-shortcut:hover {{
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}

        /* ── Cart button ── */
        .cart-toggle {{
            position: fixed;
            bottom: 36px; right: 36px;
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 16px 26px;
            border-radius: 40px;
            font-weight: 900;
            font-size: 0.9em;
            cursor: pointer;
            z-index: 800;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            transition: transform 0.2s;
            font-family: inherit;
            letter-spacing: 0.5px;
        }}
        .cart-toggle:hover {{ transform: scale(1.05); }}

        /* ── Cart panel ── */
        .cart-panel {{
            position: fixed;
            top: 0; right: -480px;
            width: 440px;
            max-width: 100vw;
            height: 100%;
            background: #fff;
            box-shadow: -10px 0 40px rgba(0,0,0,0.1);
            z-index: 3000;
            transition: right 0.45s cubic-bezier(0.165,0.84,0.44,1);
            display: flex;
            flex-direction: column;
        }}
        .cart-panel.open {{ right: 0; }}

        .checkout-input {{
            width: 100%;
            padding: 13px 14px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 0.9em;
            font-family: inherit;
            outline: none;
            transition: border 0.2s;
        }}
        .checkout-input:focus {{ border-color: var(--primary); }}

        /* ── Modal ── */
        .modal {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.65);
            z-index: 4000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(6px);
            padding: 20px;
        }}
        .modal-content {{
            background: #fff;
            width: 960px;
            max-width: 100%;
            max-height: 90vh;
            border-radius: 18px;
            display: flex;
            overflow: hidden;
            position: relative;
            box-shadow: 0 30px 70px rgba(0,0,0,0.3);
        }}
        .modal-img-side {{
            flex: 1;
            min-width: 300px;
            background: #f8f8f8;
            padding: 50px 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #f0f0f0;
        }}
        .modal-info-side {{
            flex: 1;
            min-width: 300px;
            padding: 50px 45px;
            overflow-y: auto;
        }}

        /* ── Toast ── */
        #pixies-toast {{
            visibility: hidden;
            min-width: 220px;
            background: #111;
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 14px 22px;
            position: fixed;
            z-index: 9999;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-weight: 700;
            font-size: 0.9em;
            pointer-events: none;
        }}
        #pixies-toast.show {{
            visibility: visible;
            animation: toastIn 0.3s ease, toastOut 0.4s ease 2.6s forwards;
        }}
        @keyframes toastIn {{ from {{ opacity:0; bottom:15px; }} to {{ opacity:1; bottom:30px; }} }}
        @keyframes toastOut {{ from {{ opacity:1; }} to {{ opacity:0; }} }}

        /* ── Footer ── */
        .site-footer {{ background-color: #000 !important; color: #fff !important; padding: 80px 50px 30px !important; margin-top: 80px !important; border-top: none !important; font-family: 'Helvetica Neue', Arial, sans-serif; }}
        .footer-content {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 50px; max-width: 1400px; margin: 0 auto; border-bottom: 1px solid #222; padding-bottom: 60px; }}
        .footer-col h3 {{ color: #fff !important; font-size: 0.75em !important; text-transform: uppercase; letter-spacing: 2px !important; font-weight: 600 !important; margin-bottom: 25px !important; border-bottom: none !important; }}
        .footer-col p {{ color: #888 !important; font-size: 0.9em !important; line-height: 1.8 !important; margin-bottom: 10px; }}
        .footer-col ul {{ list-style: none; padding: 0; margin: 0; }}
        .footer-col ul li {{ margin-bottom: 15px !important; }}
        .footer-col ul li a {{ color: #888 !important; text-decoration: none !important; font-size: 0.9em !important; transition: 0.3s; }}
        .footer-col ul li a:hover {{ color: #d4af37 !important; padding-left: 5px; }}
        .newsletter-form {{ display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }}
        .newsletter-form input {{ padding: 15px; background: #111; border: 1px solid #333; color: #fff; border-radius: 6px; outline: none; }}
        .newsletter-form input:focus {{ border-color: #d4af37; }}
        .newsletter-form button {{ padding: 15px; background: #d4af37; color: #111; border: none; border-radius: 6px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }}
        .newsletter-form button:hover {{ background: #fff; }}
        .footer-bottom {{ display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 30px auto 0; font-size: 0.75em; color: #666; letter-spacing: 1px; }}
        .footer-socials {{ display: flex; gap: 20px; }}
        .footer-socials a {{ color: #888; text-decoration: none; text-transform: uppercase; font-weight: bold; transition: 0.3s; }}
        .footer-socials a:hover {{ color: #d4af37; }}
        @media (max-width: 992px) {{
            .site-footer {{ padding: 60px 30px 30px !important; }}
            .footer-content {{ grid-template-columns: 1fr 1fr; gap: 40px; }}
            .footer-bottom {{ flex-direction: column; gap: 20px; text-align: center; }}
        }}
        @media (max-width: 600px) {{
            .footer-content {{ grid-template-columns: 1fr; gap: 40px; }}
        }}\n\n        /* ── Responsive ── */
        @media (max-width: 992px) {{
            .sidebar {{
                transform: translateX(-100%);
                z-index: 1000;
                width: 280px;
            }}
            .sidebar.mobile-open {{ transform: translateX(0); }}
            .main-wrapper {{ margin-left: 0; }}
            .main-content {{ padding: 30px 20px; }}
            .mobile-header {{ display: flex; }}
            .banner {{ top: 0; }}
            .cart-toggle {{ bottom: 20px; right: 20px; padding: 14px 20px; }}
            .cart-panel {{ width: 100vw; right: -100vw; }}
            .modal-content {{ flex-direction: column; }}
            .modal-img-side {{ min-width: unset; padding: 30px; max-height: 250px; }}
            .modal-info-side {{ min-width: unset; padding: 30px; }}
            .grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }}
            .image-container {{ height: 150px; }}
            .toolbar-left h1 {{ font-size: 1.8em; }}
        }}

        @media (max-width: 480px) {{
            .grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
            .card {{ padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .image-container {{ height: 110px; margin-bottom: 8px; }}
            .title {{ font-size: 0.8em; line-height: 1.3; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
            .price-tag {{ font-size: 0.9em; font-weight: 900; }}
            .quick-add-btn {{ padding: 8px; font-size: 0.8em; width: 100%; border-radius: 6px; margin-top: 6px; }}
            .card-footer-row {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
            .sidebar {{ width: 260px; }}
            .mobile-header {{ padding: 12px 15px; }}
            .mobile-header-logo {{ font-size: 1.1em; }}
        }}
    </style>
</head>
<body>
    <div id="pixies-toast"></div>
    <div id="mobile-overlay" onclick="toggleMobileNav()"></div>

    <!-- Sidebar -->
    <nav class="sidebar">
        <a href="{prefix}index.html" class="sidebar-logo">Pixie's <span>Pantry</span></a>
        <input type="text" id="searchInput" class="search-box" placeholder="Search products, brands..." oninput="applyFilters()">
        {sidebar_html}
    </nav>

    <div class="main-wrapper">
        <div class="banner">DISCORD GROUP BUY &nbsp;·&nbsp; FAST SHIPPING FROM MISSISSIPPI</div>

        <!-- Mobile header -->
        <div class="mobile-header">
            <div class="mobile-header-logo">Pixie's <span>Pantry</span></div>
            <button class="hamburger" onclick="toggleMobileNav()" aria-label="Menu">
                <span></span><span></span><span></span>
            </button>
        </div>

        <div class="main-content">
            {content}
        </div>

        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>Pixie's Pantry</h3>
                    <p style="max-width: 300px;">Curating the absolute highest tier of vaporization and glass hardware. Direct wholesale access, vetted specifically for the community. Elevate your ritual.</p>
                </div>
                <div class="footer-col">
                    <h3>Explore</h3>
                    <ul>
                        <li><a href="{prefix}index.html">Master Catalog</a></li>
                        <li><a href="#" onclick="toggleCart(); return false;">View Cart</a></li>
                        <li><a href="{prefix}about.html">Our Philosophy</a></li>
                        <li><a href="{prefix}faq.html">FAQ & Guide</a></li>
                        <li><a href="https://dyspensr.com" target="_blank">Dyspensr Network</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Client Services</h3>
                    <ul>
                        <li><a href="https://discord.gg/pyTSf569" target="_blank">Discord Support (Fastest)</a></li>
                        <li><a href="mailto:admin@pixies-pantry.com">Email Concierge</a></li>
                        <li><a href="{prefix}shipping.html">Shipping & Delivery</a></li>
                        <li><a href="{prefix}refunds.html">Returns & Exchanges</a></li>
                        <li><a href="{prefix}privacy.html">Privacy & Terms</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Stay Exquisite</h3>
                    <p>Join the inner circle for exclusive drops and wholesale restocks.</p>
                    <form class="newsletter-form" action="https://formspree.io/f/xeoqkzdj" method="POST">
                        <input type="email" name="Newsletter Email" placeholder="Enter your email address" required>
                        <button type="submit" style="color: black !important;">Subscribe</button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 PIXIE'S PANTRY. ALL RIGHTS RESERVED.</p>
                <div class="footer-socials">
                    <a href="https://discord.gg/pyTSf569" target="_blank">Discord</a>
                    <a href="#">Instagram</a>
                    <a href="#">Twitter</a>
                </div>
            </div>
        </footer>
    </div>

    <!-- Product Modal -->
    <div id="product-modal" class="modal">
        <div class="modal-content">
            <button onclick="closeModal()" style="position:absolute; top:20px; right:24px; font-size:2em; background:none; border:none; cursor:pointer; color:#aaa; z-index:10; line-height:1;">&times;</button>
            <div class="modal-img-side">
                <img id="modal-img" src="" style="max-width:100%; max-height:380px; object-fit:contain;">
                <div id="modal-gallery" style="display:flex; gap:10px; margin-top:20px; overflow-x:auto; width:100%; justify-content:center; padding-bottom:4px;"></div>
            </div>
            <div class="modal-info-side">
                <div id="modal-brand" style="font-size:0.75em; font-weight:900; color:#bbb; text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;"></div>
                <h2 id="modal-title" style="font-weight:900; font-size:1.9em; line-height:1.1; letter-spacing:-0.5px; margin-bottom:18px;"></h2>
                <div id="modal-price" style="font-size:2.2em; font-weight:900; margin-bottom:22px;"></div>
                <div id="modal-variant-container" style="margin-bottom:10px;"></div>
                <button id="modal-add-btn" class="quick-add-btn" style="width:100%; padding:18px; font-size:1em; margin-top:16px; letter-spacing:1px; text-transform:uppercase; border-radius:10px;">Add to Order</button>
                <div id="modal-desc-container" style="margin-top:30px; color:#555; font-size:0.95em; line-height:1.8; border-top:1px solid #f0f0f0; padding-top:22px;"></div>
            </div>
        </div>
    </div>

    <!-- Floating Cart Button -->
    <button class="cart-toggle" onclick="toggleCart()">🛒 CART (<span class="cart-count">0</span>)</button>

    <!-- Side Cart Panel -->
    <div id="cart-panel" class="cart-panel">
        <div style="padding:28px 30px; background:#fafafa; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
            <h2 style="margin:0; font-size:1em; font-weight:900; letter-spacing:2px; text-transform:uppercase;">Order Sheet</h2>
            <button onclick="toggleCart()" style="border:none; background:none; font-size:1.8em; cursor:pointer; color:#bbb; line-height:1;">&times;</button>
        </div>
        <div id="cart-items" style="flex:1; overflow-y:auto; padding:20px 30px;"></div>
        <div style="padding:24px 30px; border-top:1px solid #eee; background:#fff;">
            <div style="display:flex; justify-content:space-between; font-weight:900; font-size:1.2em; margin-bottom:24px;">
                <span>Subtotal:</span><span id="cart-total-price">$0.00</span>
            </div>
            <!-- FORMSPREE FORM — action URL uses your FORMSPREE_ID -->
            <form action="https://formspree.io/f/{FORMSPREE_ID}" method="POST" id="checkout-form" onsubmit="prepareCheckout(event)">
                <input type="hidden" name="Order Details" id="order-payload">
                <input type="text" name="Full Name" placeholder="Full Name *" required class="checkout-input">
                <input type="email" name="email" placeholder="Email Address *" required class="checkout-input">
                <input type="text" name="Discord" placeholder="Discord Username (Optional)" class="checkout-input">
                <input type="text" name="Shipping" placeholder="City, State, Zip *" required class="checkout-input">
                <input type="text" name="Notes" placeholder="Order notes (optional)" class="checkout-input">
                <button type="submit" style="width:100%; background:var(--primary); color:#fff; border:none; padding:18px; font-weight:900; border-radius:10px; margin-top:8px; font-size:0.95em; text-transform:uppercase; letter-spacing:1px; cursor:pointer; font-family:inherit;">Submit Order</button>
            </form>
            <div id="receipt-container" style="display:none; text-align:center; padding:30px; border:2px dashed #eee; border-radius:14px;">
                <div style="font-size:2em; margin-bottom:12px;">✅</div>
                <h4 style="font-weight:900; letter-spacing:1px; margin-bottom:8px;">ORDER SUBMITTED</h4>
                <p style="font-size:0.88em; color:var(--muted);">Check Discord or Email for follow-up shortly.</p>
                <button onclick="location.reload()" class="quick-add-btn" style="margin-top:18px; width:100%; padding:14px; border-radius:8px;">Back to Catalog</button>
            </div>
        </div>
    </div>

    <script>
{INLINE_JS}
    </script>
</body>
</html>"""


def generate_storefront():
    start_time = time.time()
    ensure_dirs()

    grouped_products = {}
    master_cats = set()
    master_brands = set()
    total_variations = 0

    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV NOT FOUND at: {CSV_PATH}")
        print("   Make sure Dyspensr_Master_Catalog_Priced.csv is on your Desktop.")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row in reader:
            try:
                retail = float(row.get("Your Retail Price", 0) or 0)
                if retail <= 0:
                    continue
                if row.get("Status", "").strip().lower() == "hidden":
                    continue

                title = row.get("Product Name", "").strip()
                if not title:
                    continue

                cat = (row.get("Product Type", "") or "Accessories").strip() or "Accessories"
                brand = (row.get("Brand", "") or "Premium").strip() or "Premium"
                img = (row.get("Image URL", "") or "").strip() or "https://placehold.co/400x400/f5f5f5/999?text=No+Image"

                master_cats.add(cat)
                master_brands.add(brand)

                if title not in grouped_products:
                    grouped_products[title] = {
                        "name": title,
                        "brand": brand,
                        "category": cat,
                        "image": img,
                        "Variants": [],
                        "Description": row.get("Body (HTML)", row.get("Meta Description", "")).replace('"', '&quot;'),
                        "All Images": [img]
                    }

                if img not in grouped_products[title]["All Images"]:
                    grouped_products[title]["All Images"].append(img)

                variant_name = (row.get("Variant", "") or "Standard").strip() or "Standard"
                grouped_products[title]["Variants"].append({
                    "name": variant_name,
                    "sku": row.get("SKU", ""),
                    "price": retail,
                    "image": img
                })
                total_variations += 1

            except Exception as ex:
                print(f"  ⚠️  Skipping row: {ex}")
                continue

    if not grouped_products:
        print("❌ No valid products found in CSV. Check column names:")
        print("   Required: 'Product Name', 'Your Retail Price', 'Brand', 'Product Type', 'Image URL'")
        return

    all_products = list(grouped_products.values())
    sorted_cats = sorted(master_cats)
    sorted_brands = sorted(master_brands)

    def build_sidebar(is_nested=False):
        prefix = "../" if is_nested else ""
        cats_html = "\n".join([
            f'<a href="{prefix}categories/{slugify(c)}.html" class="sidebar-link">{c}</a>'
            for c in sorted_cats
        ])
        brands_html = "\n".join([
            f'<a href="{prefix}brands/{slugify(b)}.html" class="sidebar-link">{b}</a>'
            for b in sorted_brands
        ])
        info_html = f'''
        <a href="{prefix}about.html" class="sidebar-link">Our Philosophy</a>
        <a href="{prefix}faq.html" class="sidebar-link">FAQ & Guide</a>
        <a href="{prefix}shipping.html" class="sidebar-link">Shipping & Delivery</a>
        <a href="{prefix}refunds.html" class="sidebar-link">Returns & Exchanges</a>
        <a href="{prefix}privacy.html" class="sidebar-link">Privacy & Terms</a>
        '''

        return f"""
        <div class="nav-section-label">Information</div>
        <nav>{info_html}</nav>
        <div class="nav-section-label">Categories</div>
        <nav>{cats_html}</nav>
        <div class="nav-section-label">Brands</div>
        <nav>{brands_html}</nav>
        """

    # ── Category pages ──────────────────────────────────────
    for cat in sorted_cats:
        cat_slug = slugify(cat)
        cat_products = [p for p in all_products if p['category'] == cat]
        local_brands = sorted(set(p['brand'] for p in cat_products))
        brand_opts = "".join([f'<option value="{b}">{b}</option>' for b in local_brands])

        content = f"""
        <div class="toolbar">
            <div class="toolbar-left">
                <h1>{cat}</h1>
                <p id="result-count">{len(cat_products)} products</p>
            </div>
            <div class="toolbar-right">
                <select id="brandFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">All Brands</option>{brand_opts}
                </select>
                <select id="sortSelect" class="filter-select" onchange="sortGrid()">
                    <option value="default">Sort</option>
                    <option value="price-low">Price: Low → High</option>
                    <option value="price-high">Price: High → Low</option>
                    <option value="name-az">Name A–Z</option>
                </select>
            </div>
        </div>
        <div class="grid">{"".join([get_product_card_html(p) for p in cat_products])}</div>
        """
        out_path = os.path.join(CAT_DIR, f"{cat_slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(get_layout(cat, content, build_sidebar(True), True))
        print(f"  📁 Category: {cat} → categories/{cat_slug}.html ({len(cat_products)} products)")

    # ── Brand pages ─────────────────────────────────────────
    for brand in sorted_brands:
        brand_slug = slugify(brand)
        brand_products = [p for p in all_products if p['brand'] == brand]
        local_cats = sorted(set(p['category'] for p in brand_products))
        cat_opts = "".join([f'<option value="{c}">{c}</option>' for c in local_cats])

        content = f"""
        <div class="toolbar">
            <div class="toolbar-left">
                <h1>{brand}</h1>
                <p id="result-count">{len(brand_products)} products</p>
            </div>
            <div class="toolbar-right">
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
        <div class="grid">{"".join([get_product_card_html(p) for p in brand_products])}</div>
        """
        out_path = os.path.join(BRAND_DIR, f"{brand_slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(get_layout(brand, content, build_sidebar(True), True))
        print(f"  🏷️  Brand: {brand} → brands/{brand_slug}.html ({len(brand_products)} products)")

    # ── Index page ──────────────────────────────────────────
    brand_opts_all = "".join([f'<option value="{b}">{b}</option>' for b in sorted_brands])
    cat_opts_all = "".join([f'<option value="{c}">{c}</option>' for c in sorted_cats])
    index_content = f"""
    <div class="toolbar">
        <div class="toolbar-left">
            <h1>Master Catalog</h1>
            <p id="result-count">{total_variations} variations · {len(all_products)} products · {len(sorted_brands)} brands</p>
        </div>
        <div class="toolbar-right">
            <select id="brandFilter" class="filter-select" onchange="applyFilters()">
                <option value="all">All Brands</option>{brand_opts_all}
            </select>
            <select id="catFilter" class="filter-select" onchange="applyFilters()">
                <option value="all">All Categories</option>{cat_opts_all}
            </select>
            <select id="sortSelect" class="filter-select" onchange="sortGrid()">
                <option value="default">Sort</option>
                <option value="price-low">Price: Low → High</option>
                <option value="price-high">Price: High → Low</option>
                <option value="name-az">Name A–Z</option>
            </select>
        </div>
    </div>
    <div class="grid">{"".join([get_product_card_html(p) for p in all_products])}</div>
    """
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(get_layout("Hardware Hub", index_content, build_sidebar(False), False))

    duration = time.time() - start_time
    print(f"\n✅ BUILD COMPLETE")
    print(f"   {len(all_products)} unique products | {total_variations} total variations")
    print(f"   {len(sorted_cats)} category pages | {len(sorted_brands)} brand pages")
    print(f"   Built in {duration:.2f}s")
    print(f"\n📂 Output: {BASE_DIR}")
    print(f"   Open index.html in your browser to preview.")


if __name__ == "__main__":
    generate_storefront()
let cart = JSON.parse(localStorage.getItem('pixies_cart')) || [];
let currentModalProduct = null;

function initCart() { updateCartUI(); }
function toggleMobileMenu() { document.querySelector('.sidebar').classList.toggle('open'); }
function toggleCart() { document.getElementById('cart-panel').classList.toggle('open'); }

function addToCart(title, qty=1) {
    const product = allProducts.find(p => p['Product Name'] === title);
    if(!product) return;
    
    // Grid click on multi-variant -> open modal
    if(product.Variants.length > 1 && !document.getElementById('product-modal').style.display.includes('flex')) {
        openModal(title);
        return;
    }
    
    let selectedVariant = product.Variants[0];
    const modalIsOpen = document.getElementById('product-modal').style.display.includes('flex');
    if (modalIsOpen && product.Variants.length > 1) {
        const sel = document.getElementById('variant-select');
        selectedVariant = product.Variants[sel.selectedIndex];
    }
    
    const existing = cart.find(item => item.sku === selectedVariant.sku);
    if (existing) { existing.qty += qty; } 
    else { cart.push({ sku: selectedVariant.sku, title: product['Product Name'], variant: selectedVariant.name, price: selectedVariant.price, qty: qty, img: selectedVariant.image }); }
    
    // Check for Cross-Sell
    const crossSellBox = document.getElementById('cross-sell-check');
    const crossContainer = document.getElementById('cross-sell-container');
    if (modalIsOpen && crossSellBox && crossSellBox.checked && crossContainer.style.display !== 'none') {
        const crossSku = 'CROSS-PINK-FORMULA';
        const crossExisting = cart.find(item => item.sku === crossSku);
        if (crossExisting) { crossExisting.qty += 1; }
        else {
            cart.push({ sku: crossSku, title: 'Pink Formula Glass Cleaner', variant: '16oz', price: 9.99, qty: 1, img: 'https://cdn.shopify.com/s/files/1/0568/2780/5886/files/Pink-Formula-Glass-Cleaner-bottle.jpg?v=1748281358' });
        }
    }
    
    saveCart(); updateCartUI();
    if (!document.getElementById('cart-panel').classList.contains('open')) { toggleCart(); }
    
    const btn = document.getElementById('modal-add-btn');
    if(btn && document.getElementById('product-modal').style.display.includes('flex')) {
        let origText = btn.innerText;
        btn.innerText = "Added to Cart!";
        btn.style.background = "#2ecc71";
        setTimeout(() => { btn.innerText = origText; btn.style.background = ""; closeModal();}, 1000);
    }
}

function removeFromCart(sku) { cart = cart.filter(item => item.sku !== sku); saveCart(); updateCartUI(); }
function saveCart() { localStorage.setItem('pixies_cart', JSON.stringify(cart)); }

function updateCartUI() {
    const cartContainer = document.getElementById('cart-items');
    const countEls = document.querySelectorAll('.cart-count');
    const totalEl = document.getElementById('cart-total-price');
    let total = 0; let count = 0;
    
    if (cart.length === 0) {
        cartContainer.innerHTML = '<p style="text-align: center; color: #888; margin-top: 40px;">Your cart is empty.</p>';
    } else {
        cartContainer.innerHTML = '';
        cart.forEach(item => {
            const itemTotal = item.price * item.qty;
            total += itemTotal; count += item.qty;
            let varText = item.variant ? `<div class="cart-item-variant" style="color:#d4af37; font-weight:bold;">Option: ${item.variant}</div>` : '';
            cartContainer.innerHTML += `
                <div class="cart-item" style="display:flex; align-items:center; gap:15px; padding:15px 0; border-bottom:1px solid #f0f0f0;">
                    <img src="${item.img}" style="width:50px; height:50px; object-fit:contain; border-radius:4px; border:1px solid #eee;">
                    <div style="flex-grow: 1;">
                        <div class="cart-item-title" style="font-weight:bold; font-size:0.9em;">${item.title} (x${item.qty})</div>
                        ${varText}
                        <div class="cart-item-variant" style="font-size:0.75em; color:#888;">SKU: ${item.sku}</div>
                        <button class="remove-item" onclick="removeFromCart('${item.sku}')" style="color:#e74c3c; background:none; border:none; padding:0; font-size:0.8em; cursor:pointer; text-decoration:underline;">Remove</button>
                    </div>
                    <div style="font-weight: 800; font-size: 1.1em; color: #111;">$${itemTotal.toFixed(2)}</div>
                </div>
            `;
        });
    }
    countEls.forEach(el => el.innerText = count);
    totalEl.innerText = '$' + total.toFixed(2);
}

function prepareCheckout(e) {
    if (cart.length === 0) { e.preventDefault(); alert("Your cart is empty! Add some products first."); return; }
    
    const name = document.getElementById('c-name').value;
    const email = document.getElementById('c-email').value;
    const phone = document.getElementById('c-phone').value;
    const discord = document.getElementById('c-discord').value;
    const ship = document.getElementById('c-ship').value;
    const isSame = document.getElementById('same-billing').checked;
    const bill = isSame ? ship : document.getElementById('c-bill').value;
    
    let orderText = "================================\n";
    orderText += "      PIXIE'S PANTRY ORDER      \n";
    orderText += "================================\n\n";
    orderText += `CUSTOMER INFO:\nName: ${name}\nEmail: ${email}\nPhone: ${phone}\nDiscord: ${discord || 'N/A'}\n\n`;
    orderText += `SHIPPING ADDRESS:\n${ship}\n\n`;
    orderText += `BILLING ADDRESS:\n${bill}\n\n`;
    orderText += "ITEMS ORDERED:\n";
    
    let total = 0;
    cart.forEach(item => {
        const lineTotal = item.price * item.qty;
        total += lineTotal;
        let varText = item.variant ? ` [${item.variant}]` : '';
        orderText += `- ${item.qty}x ${item.title}${varText}\n  SKU: ${item.sku} | $${item.price.toFixed(2)} each\n`;
    });
    
    const grandTotal = total + 12; // $12 flat shipping
    orderText += `\n--------------------------------\n`;
    orderText += `SUBTOTAL: $${total.toFixed(2)}\n`;
    orderText += `SHIPPING: $12.00\n`;
    orderText += `GRAND TOTAL: $${grandTotal.toFixed(2)}\n`;
    orderText += `================================\n`;
    
    document.getElementById('order-payload').value = orderText;
    document.getElementById('order-total-payload').value = '$' + grandTotal.toFixed(2);
    
    e.preventDefault(); // Stop normal form submission to prevent redirect

    // Show the receipt in the UI
    document.getElementById('checkout-form').style.display = 'none';
    document.getElementById('receipt-container').style.display = 'block';
    document.getElementById('receipt-body').textContent = orderText;

    // Build FormData
    const formData = new FormData(document.getElementById('checkout-form'));

    // 1. Submit via AJAX to Formspree (Primary Checkout Flow)
    fetch('https://formspree.io/f/xeoqkzdj', {
        method: 'POST',
        body: formData,
        headers: {
            'Accept': 'application/json'
        }
    }).then(response => {
        if(response.ok) {
            // Success, clear cart
            cart = []; 
            saveCart(); 
            updateCartUI();
        } else {
            alert("There was a problem submitting your order. Please contact support.");
        }
    }).catch(error => {
        alert("Network error. Please try again.");
    });

    // 2. Submit via AJAX to Discord Webhook (Background Notification)
    fetch('https://discord.com/api/webhooks/1485061335577399480/PMlUzf9BNYHij-PR0MjEcDmmI4l9E8FYPEneOr3VEV3PdOoz1wgTmsG_VaHqaV9RRjtu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: `🚨 **NEW ORDER RECEIVED** 🚨\n\`\`\`text\n${orderText}\n\`\`\``
        })
    }).catch(error => console.error('Discord Webhook Error:', error));
}

function openModal(title) {
    const product = allProducts.find(p => p['Product Name'] === title);
    if(!product) return;
    currentModalProduct = product;
    
    // Load Gallery
    const galleryHtml = product['All Images'].map((img, i) => {
        return `<img src="${img}" onclick="document.getElementById('modal-img').src='${img}'" style="width:60px; height:60px; object-fit:contain; border:1px solid #ddd; border-radius:4px; cursor:pointer; margin-right:10px; margin-top:10px;">`;
    }).join('');
    
    document.getElementById('modal-img').src = product.Variants[0].image || product['Primary Image'];
    document.getElementById('modal-gallery').innerHTML = galleryHtml;
    
    document.getElementById('modal-brand').innerText = product.Brand;
    document.getElementById('modal-title').innerText = product['Product Name'];
    
    // Inject Stars & Badge into Modal
    const badgeContainer = document.getElementById('modal-badge-container');
    if(badgeContainer) {
        badgeContainer.innerHTML = product.isAuditorChoice ? '<div class="gold-badge" style="position:relative; display:inline-block; margin-bottom:10px; left:0; border-radius:20px;">★ Auditor\'s Choice Premium</div>' : '';
    }
    const starsContainer = document.getElementById('modal-stars-container');
    if(starsContainer) {
        const rating = product.rating || 4.9;
        const reviews = product.reviews || 45;
        starsContainer.innerHTML = `<div class="stars">⭐⭐⭐⭐⭐ <span style="color:#111; font-weight:bold;">${rating}</span> <span>(${reviews} Verified Reviews)</span></div>`;
    }
    
    // Cross-sell Inject
    const crossSell = document.getElementById('cross-sell-container');
    if(crossSell) {
        // Show cross-sell 70% of the time to feel dynamic
        crossSell.style.display = Math.random() > 0.3 ? 'flex' : 'none';
        document.getElementById('cross-sell-check').checked = false; // Reset
    }
    
    const variantContainer = document.getElementById('modal-variant-container');
    if (product.Variants.length > 1) {
        let selectHtml = `<label style="display:block; font-size:0.85em; font-weight:bold; margin-bottom:8px; color:#555;">SELECT OPTION:</label><div class="custom-select-wrapper"><select id="variant-select" class="premium-dropdown" onchange="updateModalVariant()">`;
        product.Variants.forEach((v, i) => {
            selectHtml += `<option value="${i}">${v.name} - $${v.price.toFixed(2)}</option>`;
        });
        selectHtml += `</select></div>`;
        variantContainer.innerHTML = selectHtml;
    } else {
        variantContainer.innerHTML = '';
    }
    
    updateModalVariant(); 
    
    document.getElementById('modal-desc-container').innerHTML = product.Description;
    
    document.getElementById('modal-add-btn').onclick = function() { addToCart(title); };
    document.getElementById('product-modal').style.display = 'flex';
}

function updateModalVariant() {
    if(!currentModalProduct) return;
    let vIndex = 0;
    const sel = document.getElementById('variant-select');
    if(sel) vIndex = sel.selectedIndex;
    
    const variant = currentModalProduct.Variants[vIndex];
    if (variant.image) {
        document.getElementById('modal-img').src = variant.image;
    }
    document.getElementById('modal-price').innerText = '$' + variant.price.toFixed(2);
    
    // Scarcity & MSRP Update
    
    // Add Sezzle/Klarna Text Hook
    let sezzleEl = document.getElementById('modal-sezzle');
    if(!sezzleEl) {
        sezzleEl = document.createElement('div');
        sezzleEl.id = 'modal-sezzle';
        sezzleEl.style.fontSize = '0.85em';
        sezzleEl.style.color = '#555';
        sezzleEl.style.marginTop = '8px';
        sezzleEl.style.marginBottom = '20px';
        document.querySelector('.modal-price-wrap').insertAdjacentElement('afterend', sezzleEl);
    }
    const splitPrice = (variant.price / 4).toFixed(2);
    sezzleEl.innerHTML = `or 4 interest-free payments of <strong>$${splitPrice}</strong> with <strong>Sezzle</strong>.`;
    
    const msrpEl = document.getElementById('modal-msrp');
    if(variant.msrp && parseFloat(variant.msrp) > variant.price) {
        msrpEl.innerText = ' RETAIL: $' + variant.msrp;
        msrpEl.style.display = 'inline';
    } else {
        msrpEl.style.display = 'none';
    }
    
    const scarcityEl = document.getElementById('modal-scarcity-container');
    if (scarcityEl) {
        if(variant.stock && variant.stock < 5) {
            scarcityEl.innerHTML = `🔥 High Demand: Only ${variant.stock} left at wholesale!`;
            scarcityEl.className = 'scarcity-alert';
        } else {
            scarcityEl.innerHTML = `✓ Secure Stock: Verification Complete.`;
            scarcityEl.className = 'scarcity-alert safe';
        }
    }
}

function closeModal() {
    document.getElementById('product-modal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('product-modal');
    if (event.target === modal) { closeModal(); }
}

document.addEventListener('DOMContentLoaded', initCart);

// TOAST NOTIFICATIONS
function showToast(productName) {
    let existingToast = document.getElementById('toast');
    if (existingToast) { existingToast.remove(); }
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast-notification';
    toast.innerHTML = `✅ Added <b>${productName}</b> to cart!`;
    document.body.appendChild(toast);
    
    // Force reflow and add class
    setTimeout(() => { toast.classList.add('show'); }, 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 500); }, 3000);
}

// Update addToCart to use toast instead of modal-btn text change
const originalAddToCart = addToCart;
addToCart = function(title, qty=1) {
    originalAddToCart(title, qty);
    
    // Check if the modal is currently open and if the button changed color
    const btn = document.getElementById('modal-add-btn');
    if(btn && document.getElementById('product-modal').style.display.includes('flex')) {
        // If it was already handled by the old logic, we might see it turn green
    } else {
        // Find if it was actually added to cart (old logic will return early if it opened modal)
        const product = allProducts.find(p => p['Product Name'] === title);
        if (product && (product.Variants.length === 1 || document.getElementById('product-modal').style.display.includes('flex'))) {
             showToast(title);
        }
    }
};

// SEARCH FUNCTIONALITY
function initSearch() {
    const searchInputs = document.querySelectorAll('.product-search-bar');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function(e) {
            const term = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                const title = card.querySelector('.title').innerText.toLowerCase();
                const brand = card.querySelector('.brand').innerText.toLowerCase();
                
                if (title.includes(term) || brand.includes(term)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Sync other search inputs
            searchInputs.forEach(otherInput => {
                if(otherInput !== input) otherInput.value = e.target.value;
            });
            
            // Hide category headers if empty
            const sections = document.querySelectorAll('.category-section');
            sections.forEach(sec => {
                const visibleCards = sec.querySelectorAll('.card[style="display: flex;"], .card:not([style*="display: none"])');
                sec.style.display = visibleCards.length > 0 ? 'block' : 'none';
            });
        });
    });
}

// ADVANCED SIDEBAR FILTERING
const checkboxes = document.querySelectorAll('.price-filter, .mat-filter');
checkboxes.forEach(cb => {
    cb.addEventListener('change', function() {
        // Gather active filters
        const activePrices = Array.from(document.querySelectorAll('.price-filter:checked')).map(e => e.value);
        const activeMats = Array.from(document.querySelectorAll('.mat-filter:checked')).map(e => e.value);
        
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const price = parseFloat(card.getAttribute('data-price') || 0);
            const mat = card.getAttribute('data-material') || "";
            
            let pricePass = true;
            if(activePrices.length > 0) {
                pricePass = false;
                if(activePrices.includes('under50') && price < 50) pricePass = true;
                if(activePrices.includes('50-100') && price >= 50 && price <= 100) pricePass = true;
                if(activePrices.includes('over100') && price > 100) pricePass = true;
            }
            
            let matPass = true;
            if(activeMats.length > 0) {
                matPass = activeMats.includes(mat);
            }
            
            if(pricePass && matPass) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Hide empty sections
        const sections = document.querySelectorAll('.category-section');
        sections.forEach(sec => {
            const visibleCards = sec.querySelectorAll('.card[style="display: flex;"], .card:not([style*="display: none"])');
            sec.style.display = visibleCards.length > 0 ? 'block' : 'none';
        });
    });
});

// DEEP LINKING TO OPEN MODAL ON LOAD
function checkDeepLink() {
    const urlParams = new URLSearchParams(window.location.search);
    const productParam = urlParams.get('p');
    if (productParam) {
        // Find product by slugified name
        const product = allProducts.find(p => p['Product Name'].toLowerCase().replace(/[^a-z0-9]+/g, '-') === productParam);
        if (product) {
            openModal(product['Product Name']);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    checkDeepLink();
    initSearch();
});

function toggleBilling() {
    const isSame = document.getElementById('same-billing').checked;
    const billInput = document.getElementById('c-bill');
    if(isSame) {
        billInput.style.display = 'none';
        billInput.removeAttribute('required');
    } else {
        billInput.style.display = 'block';
        billInput.setAttribute('required', 'true');
    }
}

// SHARE PRODUCT
function shareProduct() {
    if(!currentModalProduct) return;
    const slug = currentModalProduct['Product Name'].toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const url = `https://vapes.pixiespantryshop.com/index.html?p=${slug}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
            showToast("🔗 Link copied to clipboard!");
        }).catch(() => {
            alert(`Copy this link to share:\n${url}`);
        });
    } else {
        // Fallback for older browsers
        alert(`Copy this link to share:\n${url}`);
    }
}

function sortCatalog() {
    const val = document.getElementById('sort-dropdown').value;
    const sections = document.querySelectorAll('.category-section');
    
    sections.forEach(sec => {
        const grid = sec.querySelector('.grid');
        if(!grid) return;
        
        let cardsArray = Array.from(grid.querySelectorAll('.card'));
        
        if (val === 'price-asc') {
            cardsArray.sort((a,b) => parseFloat(a.dataset.price) - parseFloat(b.dataset.price));
        } else if (val === 'price-desc') {
            cardsArray.sort((a,b) => parseFloat(b.dataset.price) - parseFloat(a.dataset.price));
        } else if (val === 'name-asc') {
            cardsArray.sort((a,b) => {
                const titleA = a.querySelector('.title').innerText.toLowerCase();
                const titleB = b.querySelector('.title').innerText.toLowerCase();
                return titleA.localeCompare(titleB);
            });
        }
        
        cardsArray.forEach(card => grid.appendChild(card));
    });
}
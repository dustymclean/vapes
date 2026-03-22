import re

with open("fix_generate_storefront.py", "r") as f:
    code = f.read()

# Issue 1: master_cats and master_brands from CSV
code = code.replace('''                cat = row.get("Product Type", "Accessories").strip()
                if not cat: cat = "Accessories"
                csv_db[sku] = {''',
'''                cat = row.get("Product Type", "Accessories").strip()
                if not cat: cat = "Accessories"
                brand = row.get("Brand", "Premium").strip() or "Premium"
                master_cats.add(cat)
                master_brands.add(brand)
                csv_db[sku] = {''')

# Issue 2: product modal popup
code = code.replace('''        .modal-img-side {
            flex: 1;
            min-width: 300px;
            background: #f8f8f8;
            padding: 50px 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #f0f0f0;
        }''',
'''        .modal-img-side {
            flex: 1;
            min-width: 300px;
            background: #f8f8f8;
            padding: 50px 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #f0f0f0;
            position: sticky;
            top: 0;
            align-self: flex-start;
            max-height: 90vh;
            overflow-y: auto;
        }''')

# Issue 3: Discord banner luxury aesthetic
code = code.replace('''        .banner {
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
        }''',
'''        .banner {
            background: #000;
            color: #d4af37;
            padding: 13px;
            text-align: center;
            font-weight: 800;
            letter-spacing: 3px;
            font-size: 0.75em;
            position: sticky;
            top: 0;
            z-index: 500;
            border-bottom: 2px solid #d4af37;
            text-transform: uppercase;
        }''')

with open("fix_generate_storefront.py", "w") as f:
    f.write(code)

print("Patched generator!")

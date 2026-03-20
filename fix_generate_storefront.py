import csv
import os
import hashlib
import time

# Paths
csv_path = os.path.expanduser("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
html_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/index.html")
log_path = os.path.expanduser("~/Desktop/Pixies_Vape_Shop/build_manifest.log")

def generate_storefront():
    start_time = time.time()
    processed_count = 0
    error_count = 0
    
    if not os.path.exists(csv_path):
        print(f"❌ CRITICAL ERROR: Source CSV missing at {csv_path}")
        return

    products_html = ""
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # MARGIN GUARDIAN: Skip items with less than 20% profit margin
                # Industry standard for e-commerce sustainability
                wholesale = float(row.get("Wholesale Cost", 0))
                retail = float(row.get("Your Retail Price", 0))
                if retail <= 0 or (retail - wholesale) / retail < 0.20:
                    error_count += 1
                    continue

                sku = row.get("SKU") or f"GEN-{hashlib.md5(row['Product Name'].encode()).hexdigest()[:6]}"
                
                # HTML template for the product card
                products_html += f"""
                <div class="product-card" data-category="{row['Category']}">
                    <img src="{row['Image URL']}" alt="{row['Product Name']}">
                    <h3>{row['Product Name']}</h3>
                    <p class="price">${retail:.2f}</p>
                    <button onclick="addToCart('{sku}')">Add to Cart</button>
                </div>
                """
                processed_count += 1
            except:
                error_count += 1

    # Final Assembly
    full_html = f"<html><body><div id='storefront'>{products_html}</div></body></html>"
    
    with open(html_path, "w") as f:
        f.write(full_html)

    # THROUGHPUT METRICS & AUDIT LOG
    duration = time.time() - start_time
    throughput = processed_count / duration if duration > 0 else 0
    
    status_msg = (f"{time.ctime()} | SUCCESS | Processed: {processed_count} | "
                  f"Defects: {error_count} | Speed: {throughput:.2f} items/sec")
    
    with open(log_path, "a") as log:
        log.write(status_msg + "\n")
    
    print(status_msg)

if __name__ == "__main__":
    generate_storefront()

import os

from fix_generate_storefront import get_layout, build_sidebar, sorted_cats, sorted_brands

BASE_DIR = os.path.expanduser("~/Desktop/Pixies_Vape_Shop")

pages = {
    "about.html": "Our Philosophy",
    "faq.html": "FAQ & Guide",
    "shipping.html": "Shipping & Delivery",
    "refunds.html": "Returns & Exchanges",
    "privacy.html": "Privacy & Terms",
}

for page_name, title in pages.items():
    file_path = os.path.join(BASE_DIR, page_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        in_content = False
        content_lines = []
        for line in lines:
            if '<footer class="site-footer">' in line or '<footer class="site-footer" style="margin-top: 80px;' in line:
                break
            if in_content:
                content_lines.append(line)
            if '<div class="main-content">' in line:
                in_content = True
        
        # In case the last div is left open, let's fix that.
        # Actually, get_layout wraps in <div class="main-content">
        # So we just take the inner HTML.
        content = "".join(content_lines).strip()
        
        # Sometimes there's an extra </div> at the end of content_lines because it closes main-content.
        # We can remove the last </div> if it's there.
        if content.endswith("</div>"):
            content = content[:-6].strip()

        # Re-generate the page
        new_html = get_layout(title, content, build_sidebar(False), False)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"Patched {page_name}")


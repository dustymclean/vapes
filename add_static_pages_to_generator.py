import os

with open("fix_generate_storefront.py", "r") as f:
    code = f.read()

static_pages_logic = """
    # ── Static Pages ─────────────────────────────────────────
    static_pages = {
        "about.html": "Our Philosophy",
        "faq.html": "FAQ & Guide",
        "shipping.html": "Shipping & Delivery",
        "refunds.html": "Returns & Exchanges",
        "privacy.html": "Privacy & Terms",
    }
    for page_name, title in static_pages.items():
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
            
            content = "".join(content_lines).strip()
            # remove closing div if it exists at the end
            if content.endswith("</div>"):
                content = content[:-6].strip()
                
            new_html = get_layout(title, content, build_sidebar(False), False)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"  📄 Static Page: {page_name} updated.")

    duration = time.time() - start_time
"""

code = code.replace("    duration = time.time() - start_time", static_pages_logic)

with open("fix_generate_storefront.py", "w") as f:
    f.write(code)

print("Injected static pages logic!")

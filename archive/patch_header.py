import os

FILES = [
    os.path.expanduser("~/Desktop/Pixies_Vape_Shop/generate_storefront.py"),
    os.path.expanduser("~/Desktop/Synergy_Shop/generate_storefront.py")
]

CSS_ADDITION = """
    /* Banner */
    .banner { background: #000; color: #fff; text-align: center; padding: 10px; font-size: 11px; font-weight: 900; letter-spacing: 2px; position: fixed; top: 0; left: 0; right: 0; z-index: 1000; text-transform: uppercase; border-bottom: 2px solid var(--gold); }
    .banner a { color: var(--gold); text-decoration: none; transition: 0.3s; }
    .banner a:hover { color: #fff; }
    .sidebar { top: 36px; /* Offset for banner */ }
    .main-wrapper { margin-top: 36px; /* Offset for banner */ }
    @media (max-width: 900px) { .sidebar { top: 0; } }
"""

BANNER_HTML = '<div class="banner">JOIN THE DISCORD FOR EXCLUSIVE WHOLESALE PRICING &nbsp;·&nbsp; <a href="https://discord.gg/dm8deA2u" target="_blank">DISCORD.GG/DM8DEa2U</a></div>'

for file in FILES:
    if not os.path.exists(file):
        continue
    with open(file, "r") as f:
        content = f.read()

    # 1. Inject CSS
    if "/* Banner */" not in content:
        content = content.replace("/* Floating Cart */", CSS_ADDITION + "\n    /* Floating Cart */")

    # 2. Inject HTML (just after <body>)
    if 'class="banner"' not in content:
        content = content.replace('<body>\n    {sidebar}', f'<body>\n    {BANNER_HTML}\n    {{sidebar}}')
        # Catch static pages that don't use {sidebar} replacement in the loop
        content = content.replace('<body>\n    <aside class="sidebar">', f'<body>\n    {BANNER_HTML}\n    <aside class="sidebar">')

    with open(file, "w") as f:
        f.write(content)

print("Banners patched.")

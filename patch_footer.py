import os
import re

FILES = [
    os.path.expanduser("~/Desktop/Pixies_Vape_Shop/generate_storefront.py"),
    os.path.expanduser("~/Desktop/Synergy_Shop/generate_storefront.py")
]

CSS_ADDITION = """
    /* Footer */
    .site-footer { background-color: #000; color: #fff; padding: 80px 50px 30px; margin-top: 80px; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .footer-content { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 50px; max-width: 1400px; margin: 0 auto; border-bottom: 1px solid #222; padding-bottom: 60px; }
    .footer-col h3 { color: #fff; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; margin: 0 0 25px; }
    .footer-col p { color: #888; font-size: 13px; line-height: 1.8; margin: 0 0 10px; }
    .footer-col ul { list-style: none; padding: 0; margin: 0; }
    .footer-col ul li { margin-bottom: 15px; }
    .footer-col ul li a { color: #888; text-decoration: none; font-size: 13px; transition: 0.3s; }
    .footer-col ul li a:hover { color: var(--gold); }
    .newsletter-form { display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }
    .newsletter-form input { padding: 15px; background: #111; border: 1px solid #333; color: #fff; border-radius: 6px; outline: none; font-family: inherit; }
    .newsletter-form input:focus { border-color: var(--gold); }
    .newsletter-form button { padding: 15px; background: var(--gold); color: #000; border: none; border-radius: 6px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; font-family: inherit; }
    .newsletter-form button:hover { background: #fff; }
    .footer-bottom { display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 30px auto 0; font-size: 11px; color: #666; letter-spacing: 1px; text-transform: uppercase; font-weight: 800; }
    .footer-socials { display: flex; gap: 20px; }
    .footer-socials a { color: #888; text-decoration: none; transition: 0.3s; }
    .footer-socials a:hover { color: var(--gold); }
    
    @media (max-width: 992px) {
        .site-footer { padding: 60px 30px 30px; }
        .footer-content { grid-template-columns: 1fr 1fr; gap: 40px; }
        .footer-bottom { flex-direction: column; gap: 20px; text-align: center; }
    }
    @media (max-width: 600px) {
        .footer-content { grid-template-columns: 1fr; gap: 40px; }
    }
"""

FOOTER_HTML = """
        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>Pixie's Pantry</h3>
                    <p style="max-width: 300px;">Curating the absolute highest tier of vaporization and glass hardware. Direct wholesale access, vetted specifically for the community. Elevate your ritual.</p>
                </div>
                <div class="footer-col">
                    <h3>Explore</h3>
                    <ul>
                        <li><a href="{depth}index.html">Master Catalog</a></li>
                        <li><a href="javascript:void(0)" onclick="document.getElementById('cart-float').click()">View Cart</a></li>
                        <li><a href="{depth}community.html">Community Pricing</a></li>
                        <li><a href="https://dyspensr.com" target="_blank">Dyspensr Network</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Client Services</h3>
                    <ul>
                        <li><a href="https://discord.gg/dm8deA2u" target="_blank">Discord Support (Fastest)</a></li>
                        <li><a href="mailto:admin@pixies-pantry.com">Email Concierge</a></li>
                        <li><a href="{depth}shipping.html">Shipping & Delivery</a></li>
                        <li><a href="{depth}refunds.html">Returns & Exchanges</a></li>
                        <li><a href="{depth}privacy.html">Privacy & Terms</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Stay Exquisite</h3>
                    <p>Join the inner circle for exclusive drops and wholesale restocks.</p>
                    <form class="newsletter-form" action="https://formspree.io/f/xeoqkzdj" method="POST">
                        <input type="email" name="Newsletter Email" placeholder="Enter your email address" required>
                        <button type="submit">Subscribe</button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 PIXIE'S PANTRY. ALL RIGHTS RESERVED.</p>
                <div class="footer-socials">
                    <a href="https://discord.gg/dm8deA2u" target="_blank">Discord</a>
                    <a href="#">Instagram</a>
                    <a href="#">Twitter</a>
                </div>
            </div>
        </footer>
"""

for file in FILES:
    if not os.path.exists(file):
        continue
    with open(file, "r") as f:
        content = f.read()

    # 1. Inject CSS
    if "/* Footer */" not in content:
        content = content.replace("/* Floating Cart */", CSS_ADDITION + "\n    /* Floating Cart */")

    # 2. Inject Footer HTML into the template layout
    if '<footer class="site-footer">' not in content:
        old_body_end = """        </main>
    </div>
    {modal}"""
        new_body_end = f"""        </main>
        {FOOTER_HTML}
    </div>
    {{modal}}"""
        content = content.replace(old_body_end, new_body_end)
        
        # Also need to fix it for community.html, login.html, signup.html since they bypass the render_page wrapper
        old_community_end = """        </main>
    </div>
</body>"""
        new_community_end = f"""        </main>
        {FOOTER_HTML.replace("{depth}", "")}
    </div>
</body>"""
        content = content.replace(old_community_end, new_community_end)

    with open(file, "w") as f:
        f.write(content)

print("Footers patched.")

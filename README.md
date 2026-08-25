# vapes.pixiespantryshop.com

This subdomain is a **redirect only**. Every route sends the visitor to
`https://pixies-pantry.com/shop/` (meta refresh + JS that preserves any query string
and hash; `404.html` catches deep links to retired pages).

The previous catalog site lives in `archive/` for reference and is no longer served.
If anything starts pushing "Auto-update: catalog refresh" commits here again, turn that
job off — it would overwrite the redirect.

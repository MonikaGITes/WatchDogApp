# screenshot PDP
# integrations/product_snapshot.py

from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


def capture_product_snapshot(url: str) -> str:
    screenshots_dir = Path("storage/screenshots/product")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    ts = int(datetime.utcnow().timestamp())
    filename = f"product_{ts}.png"
    out_path = screenshots_dir / filename

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1800})
        page.goto(url, wait_until="networkidle")

        page.evaluate("""
            document.querySelectorAll(
                '[id*="cookie"], [aria-label*="cookie"], .cookie, .consent'
            ).forEach(e => e.remove());
        """)

        page.screenshot(path=str(out_path), full_page=True)
        browser.close()

    return str(out_path)
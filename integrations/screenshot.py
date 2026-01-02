from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime


def capture_screenshot(url: str) -> str:
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    filename = f"screenshot_{int(datetime.utcnow().timestamp())}.png"
    out_path = screenshots_dir / filename

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 2000})

        page.goto(url, wait_until="domcontentloaded")
        # page.wait_for_selector('[data-testid="product-price"]', timeout=2000)

        page.evaluate("""
            const selectors = [
                '[id*="cookie"]',
                '.cookies',
                '.cookie-modal',
                '.cmpbox',
                '#onetrust-banner-sdk',
                '[aria-label*="cookie"]'
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });
        """)

        page.screenshot(path=str(out_path), full_page=True)
        browser.close()

    return str(out_path)
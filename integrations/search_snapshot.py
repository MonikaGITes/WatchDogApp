# screenshot wyszukiwarki
# integrations/search_snapshot.py

from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import urllib.parse


def capture_search_snapshot(query: str) -> str:
    screenshots_dir = Path("storage/screenshots/search")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    ts = int(datetime.utcnow().timestamp())
    filename = f"search_{ts}.png"
    out_path = screenshots_dir / filename

    search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(search_url, wait_until="networkidle")

        # miękkie usunięcie cookie bannerów
        page.evaluate("""
            document.querySelectorAll(
                '[id*="cookie"], [aria-label*="cookie"], .cookie, .consent'
            ).forEach(e => e.remove());
        """)

        page.screenshot(path=str(out_path))
        browser.close()

    return str(out_path)
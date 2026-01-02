from datetime import datetime
from integrations.screenshot import capture_screenshot
from integrations.ocr import extract_text
from integrations.parser_vision import parse_vision
from db.database import get_connection


def add_product(url: str) -> dict:
    acquisition = acquire_product_data(url)
    raw = extract_raw_data(acquisition)
    normalized = normalize_extraction(raw)
    decision = decide_price(normalized)
    return persist_product(url, acquisition, normalized, decision)


def acquire_product_data(url: str) -> dict:
    return {
        "screenshot_path": capture_screenshot(url),
        "timestamp": datetime.utcnow()
    }


def extract_raw_data(acquisition: dict) -> dict:
    text = extract_text(acquisition["screenshot_path"])
    parsed = parse_vision(text)
    return parsed


def normalize_extraction(raw: dict) -> dict:
    return {
        "title": raw["title"],
        "availability": raw["availability"],
        "currency": raw["currency"],
        "price_candidates": sorted(raw["prices"]),
    }


def decide_price(normalized: dict) -> dict:
    prices = normalized["price_candidates"]

    if not prices:
        return {
            "current_price": None,
            "original_price": None,
            "is_promo": False,
            "currency": normalized["currency"],
        }

    current = prices[0]
    original = prices[1] if len(prices) > 1 else None

    return {
        "current_price": current,
        "original_price": original,
        "is_promo": original is not None,
        "currency": normalized["currency"],
    }


def persist_product(url: str, acquisition: dict, normalized: dict, decision: dict) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    now = acquisition["timestamp"].isoformat()

    cur.execute("SELECT id FROM products WHERE url = ?", (url,))
    row = cur.fetchone()

    if row:
        product_id = row[0]
        cur.execute(
            "UPDATE products SET last_checked_at=? WHERE id=?",
            (now, product_id)
        )
    else:
        cur.execute("""
            INSERT INTO products (url, title, availability, created_at, last_checked_at)
            VALUES (?, ?, ?, ?, ?)
        """, (url, normalized["title"], normalized["availability"], now, now))
        product_id = cur.lastrowid

    cur.execute("""
        INSERT INTO prices (product_id, price, currency, checked_at)
        VALUES (?, ?, ?, ?)
    """, (product_id, decision["current_price"], decision["currency"], now))

    conn.commit()
    conn.close()

    return {
        "product_id": product_id,
        "url": url,
        "title": normalized["title"],
        "current_price": decision["current_price"],
        "original_price": decision["original_price"],
        "currency": decision["currency"],
        "is_promo": decision["is_promo"],
        "availability": normalized["availability"],
        "checked_at": now,
    }
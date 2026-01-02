"""
pipeline/monitor.py

GŁÓWNY SILNIK MONITOROWANIA CEN

Flow:
query → search snapshot → parse ceny → compare → (opcjonalnie) product snapshot
"""

from datetime import datetime
from typing import List, Dict, Optional

from db.database import get_connection
from integrations.search_snapshot import capture_search_snapshot
from integrations.parser_vision import parse_search_results
from integrations.product_snapshot import capture_product_snapshot
from integrations.ocr import extract_from_image
from domain.pricing import decide_price_change


# -------------------------------------------------------
# MODELE WEJŚCIA
# -------------------------------------------------------

def load_products_to_monitor() -> List[Dict]:
    """
    Pobiera produkty do monitorowania z DB.
    Każdy rekord MUSI zawierać:
    - id
    - query
    - target_price
    - last_known_price
    """
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, query, target_price, last_known_price
        FROM products
        WHERE is_active = 1
    """).fetchall()

    conn.close()

    return [
        {
            "product_id": r[0],
            "query": r[1],
            "target_price": r[2],
            "last_known_price": r[3],
        }
        for r in rows
    ]


# -------------------------------------------------------
# GŁÓWNY MONITOR
# -------------------------------------------------------

def monitor():
    """
    Główna pętla monitorowania.
    Wywoływana:
    - ręcznie
    - cronem
    - schedulerem
    """

    products = load_products_to_monitor()

    if not products:
        print("🟡 Brak produktów do monitorowania.")
        return

    for product in products:
        try:
            monitor_single_product(product)
        except Exception as e:
            print(f"❌ Błąd monitorowania produktu {product['product_id']}: {e}")


# -------------------------------------------------------
# LOGIKA JEDNEGO PRODUKTU
# -------------------------------------------------------

def monitor_single_product(product: Dict):
    product_id = product["product_id"]
    query = product["query"]
    target_price = product["target_price"]
    last_price = product["last_known_price"]

    print(f"\n🔍 Monitoruję: {query}")

    # 1️⃣ SEARCH SNAPSHOT
    search_image = capture_search_snapshot(query)

    # 2️⃣ PARSOWANIE WYNIKÓW
    results = parse_search_results(search_image)

    if not results:
        print("⚠️ Brak wyników w wyszukiwarce.")
        return

    # 3️⃣ NAJLEPSZA CENA
    best_offer = min(results, key=lambda r: r["price"])
    current_price = best_offer["price"]
    source_url = best_offer["url"]

    print(f"💰 Cena z wyszukiwarki: {current_price} zł")

    # 4️⃣ DECYZJA
    decision = decide_price_change(
        current_price=current_price,
        last_price=last_price,
        target_price=target_price
    )

    # zapis ceny z wyszukiwarki (cache)
    save_search_price(product_id, current_price)

    if decision["action"] == "skip":
        print("⏭️ Brak istotnej zmiany ceny.")
        return

    # 5️⃣ SNAPSHOT PRODUKTU
    print("📸 Cena spełnia warunek — snapshot produktu")
    product_image = capture_product_snapshot(source_url)

    ocr_data = extract_from_image(product_image)

    persist_price_event(
        product_id=product_id,
        price=current_price,
        snapshot_path=product_image,
        raw_text=ocr_data.get("raw_text"),
        source_url=source_url
    )

    print("✅ Zapisano zmianę ceny")


# -------------------------------------------------------
# PERSISTENCJA
# -------------------------------------------------------

def save_search_price(product_id: int, price: float):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE products
        SET last_known_price = ?, last_checked_at = ?
        WHERE id = ?
    """, (price, datetime.utcnow().isoformat(), product_id))

    conn.commit()
    conn.close()


def persist_price_event(
    product_id: int,
    price: float,
    snapshot_path: str,
    raw_text: Optional[str],
    source_url: str
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prices (
            product_id,
            price,
            checked_at,
            snapshot_path,
            source_url,
            raw_text
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        price,
        datetime.utcnow().isoformat(),
        snapshot_path,
        source_url,
        raw_text
    ))

    conn.commit()
    conn.close()
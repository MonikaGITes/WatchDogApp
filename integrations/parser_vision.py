#integrations/parser_vision
import re

def extract_title(text: str) -> str:
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if any(x in l.lower() for x in ["zł", "pln", "%", "rata"]):
            continue
        if len(l) > 6:
            return l[:200]
    return "Produkt"


def extract_prices(text: str) -> list[float]:
    matches = re.findall(r"(\d[\d\s]*[,\.\s]\d{2})\s*zł", text.lower())
    prices = []
    for m in matches:
        try:
            prices.append(float(m.replace(" ", "").replace(",", ".")))
        except ValueError:
            pass
    return prices


def extract_availability(text: str) -> str:
    t = text.lower()
    unavailable = [
        "niedostępny", "wyprzedane", "brak w magazynie",
        "chwilowo", "out of stock"
    ]
    return "unavailable" if any(x in t for x in unavailable) else "available"


def parse_vision(text: str) -> dict:
    return {
        "title": extract_title(text),
        "prices": extract_prices(text),
        "availability": extract_availability(text),
        "currency": "PLN",
        "raw_text": text,
    }
# integrations/parser_vision.py

def parse_search_results(image_path: str) -> list[dict]:
    """
    Minimalna wersja v1:
    OCR → ceny → zwróć listę ofert
    """
    from integrations.ocr import extract_from_image

    data = extract_from_image(image_path)
    prices = data.get("prices", [])

    results = []
    for price in prices:
        results.append({
            "price": price,
            "url": None  # URL pozyskamy później / opcjonalnie
        })

    return results
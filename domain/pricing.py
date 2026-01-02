# LOGIKA BIZNESOWA (serce)
# decyzja: która cena jest właściwa
# domain/pricing.py

def decide_price_change(
    current_price: float,
    last_price: float | None,
    target_price: float | None
) -> dict:

    if last_price is None:
        return {"action": "skip", "reason": "no_previous_price"}

    if current_price >= last_price:
        return {"action": "skip", "reason": "price_not_lower"}

    if target_price is not None and current_price > target_price:
        return {"action": "skip", "reason": "above_target"}

    return {
        "action": "snapshot",
        "reason": "price_drop"
    }
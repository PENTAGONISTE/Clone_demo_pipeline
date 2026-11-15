import httpx

from app import config


def max_loans(age: int, has_late_fees: bool) -> int:
    """Moins de 12 ans : 3 livres. De 12 à 17 ans : 5. Adulte : 8.
    Un adhérent qui a des pénalités impayées ne peut rien emprunter."""
    if age < 0:
        raise ValueError("age must be >= 0")
    if has_late_fees:
        return 0
    if age < 12:
        return 3
    if age <= 17:
        return 5
    return 8


def fetch_late_fees(member_id: int) -> float:
    if not config.PAYMENT_SERVICE_URL:
        return 0.0
    response = httpx.get(f"{config.PAYMENT_SERVICE_URL}/members/{member_id}/fees", timeout=5)
    response.raise_for_status()
    return float(response.json()["amount"])


def can_borrow(member_id: int, age: int, active_loans: int) -> bool:
    return active_loans < max_loans(age, fetch_late_fees(member_id) > 0)

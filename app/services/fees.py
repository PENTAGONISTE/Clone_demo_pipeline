def compute_late_fee(days: int, rate: float = 0.5, cap: float = 10) -> float:
    """Pénalité de retard : rate par jour, plafonnée à cap."""
    if days < 0:
        raise ValueError("days must be >= 0")
    fee = days * rate
    # Bug volontaire pour la séance : le plafond n'est pas appliqué.
    return fee

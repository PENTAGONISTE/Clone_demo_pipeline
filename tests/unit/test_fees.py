import pytest

from app.services.fees import compute_late_fee


def test_no_fee_without_delay():
    assert compute_late_fee(0) == 0


@pytest.mark.parametrize(("days", "expected"), [(1, 0.5), (4, 2.0), (10, 5.0)])
def test_fee_is_proportional_to_delay(days, expected):
    assert compute_late_fee(days) == expected


def test_negative_days_are_rejected():
    with pytest.raises(ValueError):
        compute_late_fee(-1)

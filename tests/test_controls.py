from pathlib import Path

import pytest

from pricedin.controls import (
    analyst_rate,
    implied_spread,
    load_control,
    royalty_value,
    schedule_from_reserves,
)

ROOT = Path(__file__).resolve().parents[1]


def test_spread_round_trip() -> None:
    oz = (1000.0, 1000.0, 500.0)
    price = royalty_value(0.02, oz, 1800.0, 0.01, 0.0, 0.07)
    assert implied_spread(price, 0.02, oz, 1800.0, 0.01) == pytest.approx(0.07, abs=1e-9)


def test_zero_spread_and_zero_yield_value_is_undiscounted_at_spot() -> None:
    oz = (1000.0, 2000.0)
    assert royalty_value(0.01, oz, 1500.0, 0.03, 0.0, 0.0) == pytest.approx(0.01 * 3000 * 1500)


def test_analyst_rate_matches_flat_discounting() -> None:
    oz = (1000.0, 1000.0)
    price = 0.01 * 1000 * 1500 * (1 / 1.1 + 1 / 1.1**2)
    assert analyst_rate(price, 0.01, oz, 1500.0) == pytest.approx(0.10, abs=1e-9)


def test_price_outside_range_rejected() -> None:
    with pytest.raises(ValueError, match="no root"):
        implied_spread(1e12, 0.01, (1000.0,), 1500.0, 0.0)


def test_tier_two_schedule() -> None:
    assert schedule_from_reserves(250.0, 100.0) == (100.0, 100.0, 50.0)
    with pytest.raises(ValueError):
        schedule_from_reserves(0.0, 1.0)


def test_wharf_control_file_is_consistent() -> None:
    c = load_control(ROOT / "controls" / "wharf.yaml")
    recoverable = 768_000 * 0.79
    assert c.payable_gold_oz == pytest.approx(schedule_from_reserves(recoverable, 85_000))
    assert c.schedule_sensitivities["guidance_low"] == pytest.approx(
        schedule_from_reserves(recoverable, 80_000)
    )
    assert c.price.value == pytest.approx(1_000_000 + 4_964_152 + 149_102)
    s = implied_spread(
        c.price.value,
        c.royalty_rate.value,
        c.payable_gold_oz,
        c.gold_spot.value,
        c.real_rate.value,
    )
    assert 0.0 < s < 1.0

"""Sum-of-parts adapter: producing value, residual band and treasury method."""

import numpy as np
import pytest

from pricedin.sum_of_parts import (
    Part,
    ProducingAsset,
    producing_value,
    residual_band,
    treasury_shares,
)


def _asset(**kw: object) -> ProducingAsset:
    base: dict[str, object] = {
        "times": np.array([0.5, 1.5]),
        "gold_revenue": np.array([100.0, 100.0]),
        "after_tax": np.array([40.0, 40.0]),
        "deck": 1600.0,
        "linked_share": 0.025,
        "tax_rate": 0.35,
    }
    base.update(kw)
    return ProducingAsset(**base)  # type: ignore[arg-type]


def test_study_deck_and_zero_drift_return_the_study_flows() -> None:
    a = _asset()
    value = producing_value(a, 1600.0, 0.0, 0.05)
    assert value == pytest.approx(40 / 1.05**0.5 + 40 / 1.05**1.5)


def test_price_change_moves_value_by_the_after_tax_margin() -> None:
    a = _asset()
    up = producing_value(a, 1760.0, 0.0, 0.0) - producing_value(a, 1600.0, 0.0, 0.0)
    assert up == pytest.approx(2 * 10.0 * 0.975 * 0.65)


def test_drift_raises_later_prices() -> None:
    a = _asset()
    assert producing_value(a, 1600.0, 0.02, 0.0) > producing_value(a, 1600.0, 0.0, 0.0)


def test_residual_band_takes_each_part_at_the_opposite_end() -> None:
    band = residual_band(1000.0, [Part("a", 300.0, 300.0), Part("b", 0.0, 200.0)])
    assert (band.low, band.high) == (500.0, 700.0)


def test_negative_part_adds_back() -> None:
    band = residual_band(1000.0, [Part("G&A", -100.0, -100.0)])
    assert band.low == band.high == 1100.0


def test_treasury_counts_only_in_the_money() -> None:
    shares, proceeds = treasury_shares(100.0, [(10.0, 2.0), (5.0, 5.0)], 3.0)
    assert (shares, proceeds) == (110.0, 20.0)


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        Part("x", 2.0, 1.0)
    with pytest.raises(ValueError):
        _asset(times=np.array([0.5]))
    with pytest.raises(ValueError):
        _asset(tax_rate=1.2)

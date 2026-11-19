"""The monthly-average volatility correction (ADR 0057)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pricedin.volatility import (
    AVERAGING_VARIANCE_RATIO,
    annualised_vol,
    averaging_variance_ratio,
    trailing_vol,
)


def _gbm_monthly_averages(sigma: float, years: int, days: int, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    n = years * 12 * days
    dt = 1.0 / (12 * days)
    steps = rng.normal(-0.5 * sigma**2 * dt, sigma * math.sqrt(dt), n)
    prices = 1000.0 * np.exp(np.cumsum(steps))
    return [float(m) for m in prices.reshape(-1, days).mean(axis=1)]


def test_closed_form_ratio() -> None:
    assert averaging_variance_ratio(1) == pytest.approx(1.0)
    assert averaging_variance_ratio(21) == pytest.approx(0.6674, abs=1e-4)
    with pytest.raises(ValueError):
        averaging_variance_ratio(0)


def test_simulated_ratio_is_two_thirds() -> None:
    """Averaging a simulated GBM monthly leaves about 2/3 of the true variance."""
    ratios = []
    for seed in range(20):
        avg = _gbm_monthly_averages(0.15, 40, 21, seed)
        raw = annualised_vol(avg, correct_averaging=False)
        ratios.append((raw / 0.15) ** 2)
    assert np.mean(ratios) == pytest.approx(AVERAGING_VARIANCE_RATIO, abs=0.03)


def test_correction_recovers_the_true_volatility() -> None:
    vols = [annualised_vol(_gbm_monthly_averages(0.15, 40, 21, s)) for s in range(20)]
    assert np.mean(vols) == pytest.approx(0.15, abs=0.006)


def test_trailing_window_uses_no_later_month() -> None:
    series = {f"{2000 + i // 12}-{i % 12 + 1:02d}": 1000.0 * 1.01 ** (i % 3) for i in range(300)}
    v = trailing_vol(series, "2015-06")
    later = dict(series, **{"2015-07": 5000.0})
    assert trailing_vol(later, "2015-06") == v
    with pytest.raises(ValueError):
        trailing_vol(series, "2005-06")

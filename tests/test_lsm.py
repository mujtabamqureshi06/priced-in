"""Tests for least-squares Monte Carlo (#76)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pricedin.lsm import value_option
from pricedin.price_models import GBM

S0, K, R, SIGMA, T, STEPS = 36.0, 40.0, 0.06, 0.2, 1.0, 50


def _paths(n: int, seed: int, steps: int = STEPS) -> np.ndarray:
    dt = T / steps
    gbm = GBM(S0, R * dt, SIGMA * math.sqrt(dt))
    return gbm.simulate(steps, n, np.random.default_rng(seed), antithetic=True)


def _put(k: int, s: np.ndarray) -> np.ndarray:
    return np.maximum(K - s, 0.0)


def _bs_put(s: float, k: float, r: float, sigma: float, t: float) -> float:
    d1 = (math.log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    return k * math.exp(-r * t) * _norm_cdf(-d2) - s * _norm_cdf(-d1)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _quantlib_american_put() -> float:
    ql = pytest.importorskip("QuantLib")
    today = ql.Date(1, 1, 2025)
    ql.Settings.instance().evaluationDate = today
    dc = ql.Actual365Fixed()
    maturity = today + ql.Period(365, ql.Days)
    process = ql.BlackScholesProcess(
        ql.QuoteHandle(ql.SimpleQuote(S0)),
        ql.YieldTermStructureHandle(ql.FlatForward(today, R, dc, ql.Continuous)),
        ql.BlackVolTermStructureHandle(ql.BlackConstantVol(today, ql.NullCalendar(), SIGMA, dc)),
    )
    option = ql.VanillaOption(
        ql.PlainVanillaPayoff(ql.Option.Put, K), ql.AmericanExercise(today, maturity)
    )
    option.setPricingEngine(ql.FdBlackScholesVanillaEngine(process, 2000, 2000))
    return float(option.NPV())


def test_one_exercise_date_is_european() -> None:
    paths = _paths(100_000, 1, steps=1)
    res = value_option(paths, _put, math.exp(-R * T))
    assert abs(res.value - _bs_put(S0, K, R, SIGMA, T)) < 3 * res.standard_error


def test_american_put_matches_quantlib() -> None:
    """Longstaff and Schwartz (2001) Table 1 setting, valued out of sample."""
    reference = _quantlib_american_put()
    res = value_option(
        _paths(100_000, 2), _put, math.exp(-R * T / STEPS), out_of_sample=_paths(100_000, 3)
    )
    # Out of sample the rule is suboptimal, so the estimate is low-biased by a few cents.
    assert reference - 0.05 < res.value < reference + 3 * res.standard_error


def test_american_put_exceeds_european() -> None:
    res = value_option(_paths(50_000, 4), _put, math.exp(-R * T / STEPS))
    assert res.value > _bs_put(S0, K, R, SIGMA, T) + 0.1


def test_rule_never_stops_out_of_the_money() -> None:
    paths = _paths(20_000, 5)
    res = value_option(paths, _put, math.exp(-R * T / STEPS))
    rows = np.flatnonzero(res.stop_step > 0)
    stopped = paths[rows, res.stop_step[rows]]
    assert np.all(stopped < K)


def test_immediate_exercise_is_taken_when_worth_more() -> None:
    res = value_option(_paths(10_000, 6), _put, math.exp(-R * T / STEPS), immediate=100.0)
    assert res.value == 100.0
    assert res.standard_error == 0.0


def test_rejects_bad_inputs() -> None:
    with pytest.raises(ValueError, match="at least one step"):
        value_option(np.ones((10, 1)), _put, 0.99)
    with pytest.raises(ValueError, match="discount"):
        value_option(np.ones((10, 3)), _put, 0.0)

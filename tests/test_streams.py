"""Tests for the gold stream claim (#80)."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from pricedin.engine import Market, Risks, StreamClaim, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.inversion import stream_frontier

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def south_railroad() -> Case:
    return load_case(ROOT / "cases" / "south_railroad.yaml")


def _cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _closed_form(case: Case, market: Market, stream: StreamClaim, start: int) -> float:
    """Strip of Black-Scholes calls: each delivered ounce is worth max(P - c, 0)."""
    ounces = case.schedule.columns["payable_gold_koz"].values
    total = 0.0
    for i, oz in enumerate(ounces):
        t = start + i
        strike = stream.transfer_price * (1.0 + stream.transfer_escalation) ** t
        forward = market.gold_spot * math.exp(market.drift * t)
        if t == 0 or market.volatility == 0.0:
            call = max(forward - strike, 0.0)
        else:
            s = market.volatility * math.sqrt(t)
            d1 = (math.log(forward / strike) + 0.5 * s * s) / s
            call = forward * _cdf(d1) - strike * _cdf(d1 - s)
        total += stream.share * oz * call / (1.0 + market.discount_rate + stream.spread) ** t
    return total


def test_stream_matches_strip_of_calls(south_railroad: Case) -> None:
    market = Market.market_consistent(1900.0, 0.01, 0.0, 0.25)
    stream = StreamClaim(share=0.05, transfer_price=1700.0, transfer_escalation=0.0, spread=0.03)
    res = simulate(
        south_railroad,
        market,
        Timing(years_to_start=2),
        Risks(),
        stream=stream,
        n_paths=40_000,
        seed=3,
    )
    assert res.stream_value is not None
    mean, se = res.estimate(res.stream_value)
    assert abs(mean - _closed_form(south_railroad, market, stream, 2)) < 4 * se


def test_zero_transfer_price_is_a_gold_share(south_railroad: Case) -> None:
    """With no transfer price the stream is worth its share of gold ounces at market value."""
    market = Market.market_consistent(1900.0, 0.01, 0.0, 0.0)
    stream = StreamClaim(share=0.1, transfer_price=0.0)
    res = simulate(south_railroad, market, Timing(), Risks(), stream=stream, n_paths=2, seed=1)
    assert res.stream_value is not None
    expected = _closed_form(south_railroad, market, stream, 0)
    assert res.stream_value.mean() == pytest.approx(expected)


def test_stream_frontier_recovers_known_odds(south_railroad: Case) -> None:
    market = Market.market_consistent(1900.0, 0.01, 0.0, 0.15)
    stream = StreamClaim(share=0.05, transfer_price=500.0, spread=0.04)
    timing = Timing(years_to_start=2)
    full = simulate(south_railroad, market, timing, Risks(), stream=stream, n_paths=4_000, seed=7)
    assert full.stream_value is not None
    price = 0.6 * float(full.stream_value.mean())
    f = stream_frontier(
        south_railroad,
        market,
        timing,
        Risks(stage_odds=0.6),
        stream,
        price,
        max_delay=2,
        n_paths=4_000,
        seed=7,
    )
    assert f.zero_delay_odds == pytest.approx(0.6)
    assert f.shape == "rising"


def test_failing_paths_pay_nothing(south_railroad: Case) -> None:
    market = Market.market_consistent(1900.0, 0.01, 0.0, 0.15)
    res = simulate(
        south_railroad,
        market,
        Timing(),
        Risks(stage_odds=0.5),
        stream=StreamClaim(0.05, 500.0),
        n_paths=1_000,
        seed=2,
    )
    assert res.stream_value is not None
    assert np.all(res.stream_value[~res.passed_gates] == 0.0)

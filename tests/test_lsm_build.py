"""Tests for the least-squares Monte Carlo build decision (WP 3.2, ADR 0038)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import Case, load_case

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def osino() -> Case:
    return load_case(ROOT / "cases" / "osino_twin_hills.yaml")


def _market(y: float, vol: float, r: float = 0.02) -> Market:
    return Market.market_consistent(
        gold_spot=1900.0, real_rate=r, convenience_yield=y, volatility=vol
    )


LSM = Risks(build_rule=True, build_decision="lsm")
FIXED = Risks(build_rule=True)
TIMING = Timing(years_to_start=1, max_wait=5)


def test_high_convenience_yield_builds_at_once(osino: Case) -> None:
    """When waiting loses value (prices drift down), a profitable project builds at once."""
    res = simulate(osino, _market(0.08, 0.0), TIMING, LSM, n_paths=200, seed=1)
    assert np.all(res.build_year == TIMING.build_ready)


def test_waiting_is_chosen_when_it_adds_value(osino: Case) -> None:
    """With y = 0 and no spread, delay lowers the value of capital but not of revenue."""
    res = simulate(osino, _market(0.0, 0.0), TIMING, LSM, n_paths=200, seed=1)
    assert np.all(res.build_year == TIMING.build_ready + TIMING.max_wait)


def test_lsm_value_at_least_fixed_rule(osino: Case) -> None:
    """The fitted rule should not lose value against the hurdle rule on the same paths."""
    market = _market(0.01, 0.15)
    lsm = simulate(osino, market, TIMING, LSM, n_paths=4_000, seed=3)
    fixed = simulate(osino, market, TIMING, FIXED, n_paths=4_000, seed=3)
    m_lsm, se_lsm = lsm.estimate(lsm.project_value)
    m_fix, se_fix = fixed.estimate(fixed.project_value)
    assert m_lsm >= m_fix - 3 * np.hypot(se_lsm, se_fix)


def test_failing_paths_never_build(osino: Case) -> None:
    risks = Risks(stage_odds=0.5, build_rule=True, build_decision="lsm")
    res = simulate(osino, _market(0.01, 0.15), TIMING, risks, n_paths=1_000, seed=5)
    assert np.all(res.build_year[~res.passed_gates] == -1)
    built = res.build_year[res.built]
    assert int(np.min(built)) >= TIMING.build_ready
    assert int(np.max(built)) <= TIMING.build_ready + TIMING.max_wait


def test_build_ready_at_time_zero(osino: Case) -> None:
    res = simulate(osino, _market(0.08, 0.0), Timing(0, max_wait=3), LSM, n_paths=100, seed=2)
    assert np.all(res.build_year == 0)


def test_decision_rate_override(osino: Case) -> None:
    """A higher decision rate makes waiting costly, so the rule builds at once."""
    risks = Risks(build_rule=True, build_decision="lsm", lsm_rate=0.10)
    res = simulate(osino, _market(0.0, 0.0), TIMING, risks, n_paths=200, seed=1)
    assert np.all(res.build_year == TIMING.build_ready)

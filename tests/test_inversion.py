import itertools
from pathlib import Path

import numpy as np
import pytest

from pricedin.engine import Market, Risks, RoyaltyClaim, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.inversion import Frontier, FrontierPoint, royalty_frontier

ROOT = Path(__file__).resolve().parents[1]
CLAIM = RoyaltyClaim(rate=0.00633, coverage=0.35, amr_per_year=97.0, spread=0.03)
MARKET = Market.market_consistent(1898.5, -0.0082, 0.0, 0.148)
TIMING = Timing(years_to_start=4, max_wait=5)
RISKS = Risks(build_rule=True)


@pytest.fixture(scope="module")
def south_railroad() -> Case:
    return load_case(ROOT / "cases" / "south_railroad.yaml")


def _point(d: int, q: float, step_se: float = 0.01) -> FrontierPoint:
    return FrontierPoint(d, q, 0.0, q, 1.0, 0.0, step_se)


def test_synthetic_recovery_exact_on_common_paths(south_railroad: Case) -> None:
    base = royalty_frontier(
        south_railroad, MARKET, TIMING, RISKS, CLAIM, price=1.0, max_delay=4, n_paths=2_000
    )
    target = base.points[3]
    q_true = 0.55
    price = q_true * target.value_if_passed + (1 - q_true) * target.value_if_failed
    again = royalty_frontier(
        south_railroad, MARKET, TIMING, RISKS, CLAIM, price=price, max_delay=4, n_paths=2_000
    )
    assert again.points[3].gate_odds == pytest.approx(q_true, rel=1e-12)


def test_synthetic_recovery_from_an_independent_full_simulation(south_railroad: Case) -> None:
    q_true, d_true = 0.6, 2
    truth = simulate(
        south_railroad,
        MARKET,
        Timing(years_to_start=4, added_delay=d_true, max_wait=5),
        Risks(stage_odds=q_true, build_rule=True),
        royalty=CLAIM,
        n_paths=60_000,
        seed=99,
    )
    assert truth.royalty_value is not None
    price, se_price = truth.estimate(truth.royalty_value)
    frontier = royalty_frontier(
        south_railroad,
        MARKET,
        TIMING,
        RISKS,
        CLAIM,
        price=price,
        max_delay=3,
        n_paths=20_000,
        seed=1,
    )
    pt = frontier.points[d_true]
    gap = pt.value_if_passed - pt.value_if_failed
    tolerance = 4 * np.hypot(pt.gate_odds_se, se_price / gap)
    assert abs(pt.gate_odds - q_true) < tolerance


def test_odds_rise_with_delay_when_waiting_costs(south_railroad: Case) -> None:
    frontier = royalty_frontier(
        south_railroad, MARKET, TIMING, RISKS, CLAIM, price=1500.0, max_delay=8, n_paths=2_000
    )
    assert frontier.shape == "rising"
    odds = [p.gate_odds for p in frontier.points]
    assert odds[-1] > odds[0]
    assert len({p.value_if_failed for p in frontier.points}) == 1


def test_failure_after_delay_sensitivity_lets_advances_grow(south_railroad: Case) -> None:
    timing = Timing(years_to_start=4, max_wait=5, failure_after_delay=True)
    claim = RoyaltyClaim(rate=0.00633, coverage=0.35, amr_per_year=97.0, spread=0.0)
    frontier = royalty_frontier(
        south_railroad, MARKET, timing, RISKS, claim, price=1500.0, max_delay=6, n_paths=2_000
    )
    failed = [p.value_if_failed for p in frontier.points]
    assert all(b > a for a, b in itertools.pairwise(failed))
    assert frontier.shape == "not monotone"


def test_delay_is_free_with_no_spread_lease_rate_or_advances(south_railroad: Case) -> None:
    market = Market.market_consistent(1898.5, 0.0152, 0.0, 0.0)
    claim = RoyaltyClaim(rate=0.00633, coverage=0.35)
    frontier = royalty_frontier(
        south_railroad,
        market,
        Timing(years_to_start=4),
        Risks(),
        claim,
        price=1000.0,
        max_delay=5,
        n_paths=1,
    )
    odds = [p.gate_odds for p in frontier.points]
    np.testing.assert_allclose(odds, odds[0], rtol=1e-12)
    assert frontier.shape == "flat"
    assert frontier.certain_build_delay is None or odds[0] >= 1


def test_certain_build_delay_interpolates() -> None:
    f = Frontier(price=1.0, points=(_point(0, 0.6), _point(1, 0.8), _point(2, 1.2)))
    assert f.certain_build_delay == pytest.approx(1.5)
    assert f.zero_delay_odds == 0.6
    assert Frontier(1.0, (_point(0, 1.1), _point(1, 1.3))).certain_build_delay == 0.0
    assert Frontier(1.0, (_point(0, 0.2), _point(1, 0.3))).certain_build_delay is None


def test_shape_allows_for_monte_carlo_noise() -> None:
    falling = Frontier(1.0, (_point(0, 0.6), _point(1, 0.5), _point(2, 0.7)))
    assert falling.shape == "not monotone"
    flat = Frontier(1.0, (_point(0, 0.60), _point(1, 0.595), _point(2, 0.61)))
    assert flat.shape == "flat"
    rising = Frontier(1.0, (_point(0, 0.60), _point(1, 0.595), _point(2, 0.70)))
    assert rising.shape == "rising"


def test_points_above_one_are_not_solvable() -> None:
    assert not _point(0, 1.2).solvable
    assert not _point(0, -0.1).solvable
    assert _point(0, 0.4).solvable


def test_break_even_spread_gives_unit_odds_at_zero_delay(south_railroad: Case) -> None:
    from dataclasses import replace

    from pricedin.inversion import break_even_spread, zero_delay_odds_curve

    s = break_even_spread(south_railroad, MARKET, TIMING, RISKS, CLAIM, price=2079.0, n_paths=1_000)
    assert s is not None
    f = royalty_frontier(
        south_railroad,
        MARKET,
        TIMING,
        RISKS,
        replace(CLAIM, spread=s),
        2079.0,
        max_delay=0,
        n_paths=1_000,
    )
    assert f.zero_delay_odds == pytest.approx(1.0, abs=1e-3)
    curve = zero_delay_odds_curve(
        south_railroad, MARKET, TIMING, RISKS, CLAIM, 2079.0, (0.0, 0.05, 0.10), n_paths=500
    )
    odds = [q for _, q in curve]
    assert odds[0] < odds[1] < odds[2]


def test_break_even_none_when_price_out_of_range(south_railroad: Case) -> None:
    from pricedin.inversion import break_even_spread

    assert (
        break_even_spread(south_railroad, MARKET, TIMING, RISKS, CLAIM, price=1e9, n_paths=200)
        is None
    )


def test_equity_frontier_synthetic_recovery() -> None:
    from pricedin.engine import Financing
    from pricedin.inversion import equity_frontier

    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    market = Market.market_consistent(1960.6, 0.0152, 0.0, 0.141)
    timing = Timing(years_to_start=1, max_wait=5)
    risks = Risks(build_rule=True)
    fin = Financing(0.0, 0.1054)
    q_true, d_true = 0.7, 2
    truth = simulate(
        case,
        market,
        replace_timing(timing, d_true),
        Risks(stage_odds=q_true, build_rule=True),
        financing=fin,
        n_paths=40_000,
        seed=9,
    )
    assert truth.equity_value is not None
    price, se_price = truth.estimate(truth.equity_value)
    f = equity_frontier(case, market, timing, risks, fin, price, max_delay=3, n_paths=20_000)
    pt = f.points[d_true]
    assert abs(pt.gate_odds - q_true) < 4 * np.hypot(pt.gate_odds_se, se_price / pt.value_if_passed)
    assert f.shape in ("rising", "flat", "not monotone")


def replace_timing(t: Timing, d: int) -> Timing:
    from dataclasses import replace

    return replace(t, added_delay=d)

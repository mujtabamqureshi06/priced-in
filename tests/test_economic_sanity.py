"""Economic sanity: values move the right way when one input moves.

Each test changes one input on common random numbers (same seed) and checks the sign
of the change. These are the monotonicity properties a reader would expect of any
valuation engine: value rises with price, falls with capital overrun, delay and stage
risk; a royalty is worth no more than on a certain, on-time project; equity falls as
dilution rises; implied odds rise with the price paid.
"""

from pathlib import Path

import pytest

from pricedin.engine import Financing, Market, Overrun, Risks, RoyaltyClaim, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.inversion import equity_frontier, royalty_frontier
from pricedin.priors import ShiftedLognormal, load_priors

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 4_000, 7


@pytest.fixture(scope="module")
def case() -> Case:
    return load_case(ROOT / "cases" / "south_railroad_fs2022.yaml")


@pytest.fixture(scope="module")
def overrun() -> Overrun:
    dist = load_priors(ROOT / "data" / "priors.yaml").get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    return Overrun(dist, 0.914)


def _market(spot: float = 1800.0, rate: float = 0.01) -> Market:
    return Market.market_consistent(spot, rate, 0.0, 0.15)


def _value(case: Case, market: Market, timing: Timing, risks: Risks) -> float:
    return float(simulate(case, market, timing, risks, n_paths=N, seed=SEED).project_value.mean())


def test_value_rises_with_gold_price(case: Case) -> None:
    values = [
        _value(case, _market(p), Timing(years_to_start=1), Risks()) for p in (1400, 1800, 2200)
    ]
    assert values[0] < values[1] < values[2]


def test_value_falls_with_delay(case: Case) -> None:
    """With flat prices, delay lowers value. Under a market-consistent drift with zero
    convenience yield it need not: waiting then lowers the value of costs but not of
    revenue (documented in the Osino case note)."""
    m = Market.study_deck(case)
    values = [_value(case, m, Timing(years_to_start=y), Risks()) for y in (0, 2, 4)]
    assert values[0] > values[1] > values[2]


def test_value_falls_with_stage_risk(case: Case) -> None:
    t = Timing(years_to_start=1)
    values = [_value(case, _market(), t, Risks(stage_odds=q)) for q in (1.0, 0.7, 0.4)]
    assert values[0] > values[1] > values[2]


def test_value_falls_with_overrun(case: Case, overrun: Overrun) -> None:
    t = Timing(years_to_start=1)
    assert _value(case, _market(), t, Risks(overrun=overrun)) < _value(case, _market(), t, Risks())


def test_royalty_never_exceeds_certain_on_time_value(case: Case, overrun: Overrun) -> None:
    claim = RoyaltyClaim(rate=0.01, coverage=1.0, spread=0.03)
    m = _market()
    certain = simulate(
        case, m, Timing(years_to_start=1), Risks(), royalty=claim, n_paths=N, seed=SEED
    )
    risky = simulate(
        case,
        m,
        Timing(years_to_start=1, added_delay=2, max_wait=5),
        Risks(stage_odds=0.7, overrun=overrun, build_rule=True),
        royalty=claim,
        n_paths=N,
        seed=SEED,
    )
    assert certain.royalty_value is not None and risky.royalty_value is not None
    assert risky.royalty_value.mean() < certain.royalty_value.mean()


def test_equity_falls_as_dilution_rises(case: Case) -> None:
    t, m = Timing(years_to_start=1), _market()
    values = []
    for discount in (0.0, 0.1, 0.2):
        res = simulate(
            case, m, t, Risks(), financing=Financing(0.0, discount), n_paths=N, seed=SEED
        )
        assert res.equity_value is not None
        values.append(float(res.equity_value.mean()))
    assert values[0] > values[1] > values[2]


def test_implied_odds_rise_with_price_paid(case: Case) -> None:
    t, m = Timing(years_to_start=1), _market(rate=0.05)
    odds = [
        equity_frontier(case, m, t, Risks(), Financing(), price, max_delay=0, n_paths=N, seed=SEED)
        .points[0]
        .gate_odds
        for price in (50_000.0, 100_000.0, 150_000.0)
    ]
    assert odds[0] < odds[1] < odds[2]


def test_royalty_odds_rise_with_price_paid(case: Case) -> None:
    claim = RoyaltyClaim(rate=0.01, coverage=1.0, spread=0.03)
    t, m = Timing(years_to_start=1), _market()
    odds = [
        royalty_frontier(case, m, t, Risks(), claim, price, max_delay=0, n_paths=N, seed=SEED)
        .points[0]
        .gate_odds
        for price in (2_000.0, 4_000.0, 6_000.0)
    ]
    assert odds[0] < odds[1] < odds[2]

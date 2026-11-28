from pathlib import Path

import numpy as np
import pytest

from pricedin.inputs import Case, load_case
from pricedin.project import (
    _adjusted_tax,
    discount_factors,
    npv,
    period_times,
    schedule_cash_flows,
    usd_millions_per_unit,
)

CASES = Path(__file__).resolve().parents[1] / "cases"


@pytest.fixture(scope="module")
def south_railroad() -> Case:
    return load_case(CASES / "south_railroad.yaml")


@pytest.fixture(scope="module")
def osino() -> Case:
    return load_case(CASES / "osino_twin_hills.yaml")


def _flat(case: Case, price: float, n_paths: int = 1) -> np.ndarray:
    return np.full((n_paths, len(case.schedule.periods)), price)


@pytest.mark.parametrize("case_name", ["south_railroad", "osino"])
def test_study_deck_reproduces_study_table_exactly(
    case_name: str, request: pytest.FixtureRequest
) -> None:
    case: Case = request.getfixturevalue(case_name)
    cf = schedule_cash_flows(case, _flat(case, case.study.price_deck["gold"].value, 3))
    cols = case.schedule.columns
    for row in cf.pre_tax:
        np.testing.assert_allclose(row, cols["cash_flow_pre_tax"].values, atol=1e-9)
    for row in cf.after_tax:
        np.testing.assert_allclose(row, cols["cash_flow_after_tax"].values, atol=1e-9)


# Published after-tax NPV5 at other gold prices (US$ millions), used to measure the error
# of the marginal-tax approximation. South Railroad: PFS Table 22-6 (silver moves with
# gold at a fixed ratio). Osino: DFS Table 22.4.2, 5% row.
SOUTH_RAILROAD_AFTER_TAX = {1200: 142.4, 1300: 204.0, 1500: 325.9, 1600: 386.5}
SOUTH_RAILROAD_PRE_TAX = {1200: 181.6, 1300: 256.5, 1500: 406.3, 1600: 481.2}
OSINO_AFTER_TAX = {1500: 256, 1600: 346, 1700: 436, 1800: 524, 1900: 612, 2000: 700}


@pytest.mark.parametrize(("price", "published"), sorted(OSINO_AFTER_TAX.items()))
def test_osino_after_tax_matches_published_sensitivity(
    osino: Case, price: float, published: float
) -> None:
    value = npv(schedule_cash_flows(osino, _flat(osino, price)).after_tax, osino, 0.05)[0]
    assert value == pytest.approx(published, rel=0.005)


@pytest.mark.parametrize(("price", "published"), sorted(SOUTH_RAILROAD_PRE_TAX.items()))
def test_south_railroad_pre_tax_matches_published_sensitivity(
    south_railroad: Case, price: float, published: float
) -> None:
    cf = schedule_cash_flows(
        south_railroad, _flat(south_railroad, price), other_revenue_ratio=price / 1400
    )
    assert npv(cf.pre_tax, south_railroad, 0.05)[0] / 1000 == pytest.approx(published, rel=0.002)


@pytest.mark.parametrize(("price", "published"), sorted(SOUTH_RAILROAD_AFTER_TAX.items()))
def test_south_railroad_after_tax_within_documented_error(
    south_railroad: Case, price: float, published: float
) -> None:
    """Documented limitation: one blended rate with full carry-forward gives -2.3% to
    +5.2% here, because Nevada's net proceeds tax does not carry losses forward."""
    cf = schedule_cash_flows(
        south_railroad, _flat(south_railroad, price), other_revenue_ratio=price / 1400
    )
    assert npv(cf.after_tax, south_railroad, 0.05)[0] / 1000 == pytest.approx(published, rel=0.06)


def test_value_rises_with_gold_price(osino: Case) -> None:
    prices = np.vstack([_flat(osino, p)[0] for p in (1300.0, 1750.0, 2500.0)])
    values = npv(schedule_cash_flows(osino, prices).after_tax, osino, 0.05)
    assert values[0] < values[1] < values[2]


def test_tax_credit_carries_forward() -> None:
    study = np.array([10.0, 10.0, 10.0])
    change = np.array([[-25.0, 0.0, 0.0]])
    # Period 0 owes -15: pays 0, carries 15. Period 1 owes 10: credit covers it, 5 left.
    # Period 2 owes 10: 5 of credit used, pays 5.
    np.testing.assert_allclose(_adjusted_tax(study, change), [[0.0, 0.0, 5.0]])


def test_discount_factors_follow_study_timing(south_railroad: Case) -> None:
    f = discount_factors(south_railroad, 0.05)
    assert f[0] == 1.0
    assert f[1] == pytest.approx(1 / 1.05)


def test_rejects_misaligned_prices(osino: Case) -> None:
    with pytest.raises(ValueError, match="must have shape"):
        schedule_cash_flows(osino, np.full((1, 3), 1750.0))


def test_rejects_non_positive_prices(osino: Case) -> None:
    prices = _flat(osino, 1750.0)
    prices[0, 2] = 0.0
    with pytest.raises(ValueError, match="positive"):
        schedule_cash_flows(osino, prices)


def _with_discounting(case: Case, **changes: object) -> Case:
    raw = case.model_dump()
    raw["study"]["discounting"].update(changes)
    return Case.model_validate(raw)


def test_default_timing_unchanged(south_railroad: Case) -> None:
    n = len(south_railroad.schedule.periods)
    np.testing.assert_allclose(period_times(south_railroad), np.arange(n, dtype=float))


def test_first_column_discounted_a_year(south_railroad: Case) -> None:
    case = _with_discounting(south_railroad, t0_years=1.0)
    n = len(case.schedule.periods)
    np.testing.assert_allclose(period_times(case), np.arange(n, dtype=float) + 1.0)
    base = npv(np.ones((1, n)), south_railroad, 0.05)
    assert npv(np.ones((1, n)), case, 0.05)[0] == pytest.approx(base[0] / 1.05)


def test_mid_year_from_the_first_column(south_railroad: Case) -> None:
    case = _with_discounting(south_railroad, t0_years=0.5)
    n = len(case.schedule.periods)
    np.testing.assert_allclose(period_times(case), np.arange(n, dtype=float) + 0.5)


def test_leading_periods_share_t0(south_railroad: Case) -> None:
    # Three pre-production years at the valuation date, then mid-year from year 1.
    case = _with_discounting(south_railroad, periods_at_t0=3, convention="mid_year")
    t = period_times(case)
    np.testing.assert_allclose(t[:3], 0.0)
    np.testing.assert_allclose(t[3:6], [0.5, 1.5, 2.5])


def test_canadian_dollar_case_needs_a_rate(south_railroad: Case) -> None:
    raw = south_railroad.model_dump()
    raw["schedule"]["money_units"] = "C$ thousands"
    with pytest.raises(ValueError, match="need fx_usd_per_unit"):
        Case.model_validate(raw)
    src = raw["study"]["discount_rate"]["source"]
    raw["schedule"]["fx_usd_per_unit"] = {"value": 0.75, "units": "US$ per C$", "source": src}
    case = Case.model_validate(raw)
    assert usd_millions_per_unit(case) == pytest.approx(0.75e-3)


def test_us_dollar_case_rejects_a_rate(south_railroad: Case) -> None:
    raw = south_railroad.model_dump()
    src = raw["study"]["discount_rate"]["source"]
    raw["schedule"]["fx_usd_per_unit"] = {"value": 1.0, "units": "US$ per US$", "source": src}
    with pytest.raises(ValueError, match="only for non-US"):
        Case.model_validate(raw)
    assert usd_millions_per_unit(south_railroad) == pytest.approx(1e-3)

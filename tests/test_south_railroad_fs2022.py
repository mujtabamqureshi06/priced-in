"""South Railroad 2022 feasibility study case: transcription, timing and tax checks."""

from pathlib import Path

import numpy as np
import pytest

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.project import discount_factors, npv, period_times, schedule_cash_flows

ROOT = Path(__file__).resolve().parents[1]

# Table 22-6, p. 22-5 (US$ millions, silver held at US$21.50).
PRE_TAX = {1400: 173.9, 1500: 259.9, 1800: 517.9, 1899: 603.0}
AFTER_TAX = {1400: 141.6, 1500: 211.2, 1800: 418.7, 1899: 486.4}


@pytest.fixture(scope="module")
def case() -> Case:
    return load_case(ROOT / "cases" / "south_railroad_fs2022.yaml")


def _flat(case: Case, price: float) -> np.ndarray:
    return np.full((1, len(case.schedule.periods)), price)


def test_mid_year_timing(case: Case) -> None:
    t = period_times(case)
    assert t[0] == 0.0
    np.testing.assert_allclose(t[1:4], [0.5, 1.5, 2.5])
    assert discount_factors(case, 0.05)[1] == pytest.approx(1.05**-0.5)


@pytest.mark.parametrize(
    ("column", "rate", "published"),
    [
        ("cash_flow_pre_tax", 0.05, 388866),
        ("cash_flow_pre_tax", 0.10, 307248),
        ("cash_flow_after_tax", 0.05, 314791),
        ("cash_flow_after_tax", 0.10, 247592),
    ],
)
def test_table_reproduces_all_four_published_npvs(
    case: Case, column: str, rate: float, published: float
) -> None:
    flows = np.asarray(case.schedule.columns[column].values, dtype=float)
    assert float(flows @ discount_factors(case, rate)) == pytest.approx(published, abs=1.0)


def test_cash_flow_identity(case: Case) -> None:
    """Pre-tax cash flow = revenue - costs - capital + working capital, each year."""
    c = {k: np.asarray(v.values, dtype=float) for k, v in case.schedule.columns.items()}
    built = (
        c["revenue"]
        - c["operating_cost"]
        - c["existing_royalties"]
        - c["salvage"]
        - c["reclamation"]
        - c["initial_capex"]
        - c["sustaining_capex"]
        + c["working_capital"]
    )
    np.testing.assert_allclose(built, c["cash_flow_pre_tax"], atol=2.0)
    np.testing.assert_allclose(
        c["cash_flow_pre_tax"] - c["taxes"], c["cash_flow_after_tax"], atol=2.0
    )


@pytest.mark.parametrize(("price", "published"), sorted(PRE_TAX.items()))
def test_pre_tax_matches_published_sensitivity(case: Case, price: float, published: float) -> None:
    value = npv(schedule_cash_flows(case, _flat(case, price)).pre_tax, case, 0.05)[0] / 1000
    assert value == pytest.approx(published, abs=1.5)


@pytest.mark.parametrize(("price", "published"), sorted(AFTER_TAX.items()))
def test_after_tax_matches_published_sensitivity(
    case: Case, price: float, published: float
) -> None:
    value = npv(schedule_cash_flows(case, _flat(case, price)).after_tax, case, 0.05)[0] / 1000
    assert value == pytest.approx(published, abs=1.0)


def test_engine_with_all_risks_off_returns_the_study_npv(case: Case) -> None:
    res = simulate(case, Market.study_deck(case), Timing(), Risks(), n_paths=5)
    assert res.project_value[0] == pytest.approx(case.study.npv_after_tax.value, abs=1.0)


def test_delay_shifts_mid_year_flows_by_whole_years(case: Case) -> None:
    market = Market.study_deck(case)
    now = simulate(case, market, Timing(), Risks(), n_paths=3).project_value[0]
    later = simulate(case, market, Timing(years_to_start=1), Risks(), n_paths=3).project_value[0]
    assert later == pytest.approx(now / 1.05)

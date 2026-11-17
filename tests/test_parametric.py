from dataclasses import replace
from datetime import date
from typing import Any

import numpy as np
import pytest

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.parametric import Headline, _irr, _npv, _schedule, build_case, calibrate

BASE = Headline(
    initial_capex=300.0,
    preproduction_years=2,
    life_years=10,
    payable_koz_per_year=150.0,
    aisc_per_oz=1100.0,
    gold_deck=1800.0,
    tax_rate=0.30,
    discount_rate=0.05,
    npv_after_tax=0.0,
    irr_after_tax=0.0,
)


def _headline_from(k: float, g: float) -> Headline:
    """A headline whose NPV and IRR come from a known schedule."""
    s = _schedule(BASE, k, g)
    return replace(BASE, npv_after_tax=_npv(s.after_tax, 0.05), irr_after_tax=_irr(s.after_tax))


@pytest.mark.parametrize(("k", "g"), [(1.0, 0.0), (0.9, -0.4), (1.15, 0.3)])
def test_calibration_recovers_known_parameters(k: float, g: float) -> None:
    h = _headline_from(k, g)
    s = calibrate(h)
    assert s.cost_factor == pytest.approx(k, abs=1e-4)
    assert s.tilt == pytest.approx(g, abs=1e-3)
    assert _npv(s.after_tax, 0.05) == pytest.approx(h.npv_after_tax, abs=0.3)
    assert _irr(s.after_tax) == pytest.approx(h.irr_after_tax, abs=5e-4)
    assert s.payable_koz.sum() == pytest.approx(150.0 * 10)


def test_built_case_reproduces_the_study_npv_in_the_engine() -> None:
    h = _headline_from(0.95, -0.2)
    case = build_case(
        h,
        case_id="synthetic_gold",
        name="Synthetic gold project",
        operator="Synthetic Ltd",
        jurisdiction="Nowhere",
        as_of=date(2020, 1, 1),
        stage="PFS",
        document_title="Synthetic study",
        document_url="https://example.org/study",
        document_date=date(2020, 1, 1),
        location="Table 1",
    )
    res = simulate(case, Market.study_deck(case), Timing(), Risks(), n_paths=3)
    np.testing.assert_allclose(res.project_value, h.npv_after_tax, atol=0.01)


def test_unmatched_headline_is_rejected() -> None:
    with pytest.raises(ValueError, match="no schedule matches"):
        calibrate(replace(BASE, npv_after_tax=900.0, irr_after_tax=0.06))


@pytest.mark.parametrize(
    "change",
    [
        {"preproduction_years": 0},
        {"life_years": 1},
        {"initial_capex": -1.0},
        {"tax_rate": 1.0},
        {"npv_after_tax": 10.0, "irr_after_tax": 0.04},
    ],
)
def test_invalid_headlines_are_rejected(change: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        replace(BASE, **change)


def test_osino_headline_schedule_tracks_the_transcribed_case() -> None:
    """Informative check, not the Phase 4 validation (ADR 0051): within 2% at three spreads."""
    from pathlib import Path

    from pricedin.inputs import load_case
    from pricedin.snapshots import load_snapshot

    root = Path(__file__).resolve().parents[1]
    case = load_case(root / "cases" / "osino_twin_hills.yaml")
    cols = case.schedule.columns
    scale = 1e-3 if case.schedule.money_units == "US$ thousands" else 1.0
    koz = np.array(cols["payable_gold_koz"].values)
    revenue = np.array(cols["gold_revenue"].values) * scale
    capex = np.array(cols["initial_capex"].values) * scale
    pre_tax = np.array(cols["cash_flow_pre_tax"].values) * scale
    producing = koz > 0
    other_costs = (revenue - pre_tax - capex)[producing].sum()
    headline = Headline(
        initial_capex=float(capex.sum()),
        preproduction_years=int(np.flatnonzero(producing)[0]),
        life_years=int(producing.sum()),
        payable_koz_per_year=float(koz[producing].mean()),
        aisc_per_oz=float(other_costs / koz[producing].sum() * 1000.0),
        gold_deck=case.study.price_deck["gold"].value,
        tax_rate=case.study.marginal_tax_rate.value,
        discount_rate=case.study.discount_rate.value,
        npv_after_tax=480.0,
        irr_after_tax=case.study.irr_after_tax.value,
    )
    built = build_case(
        headline,
        case_id="osino_parametric",
        name="Twin Hills, parametric",
        operator="Osino Resources",
        jurisdiction="Namibia",
        as_of=case.as_of,
        stage="FS",
        document_title="Twin Hills DFS",
        document_url="https://www.sedarplus.ca",
        document_date=case.as_of,
        location="headline figures",
    )
    snap = load_snapshot(root / "data" / "snapshots" / "2023-07-13.yaml")
    base = Market.market_consistent(
        snap.value("gold_spot"), snap.value("real_yield_10y"), 0.0, snap.value("realised_vol_10y")
    )
    for spread in (0.0, 0.05, 0.10):
        market = replace(base, discount_rate=base.discount_rate + spread)
        transcribed = simulate(case, market, Timing(), Risks(), n_paths=5000, seed=1)
        parametric = simulate(built, market, Timing(), Risks(), n_paths=5000, seed=1)
        ratio = parametric.project_value.mean() / (transcribed.project_value.mean() * scale)
        assert abs(ratio - 1.0) < 0.02

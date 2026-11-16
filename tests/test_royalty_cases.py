"""Tests for royalty cases on multi-metal schedules (WP 2.6)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from pricedin.price_models import CorrelatedGBM
from pricedin.royalty_cases import (
    MetalsMarket,
    break_even_spread,
    load_royalty_case,
    odds_frontier,
    pre_tax_npv,
    royalty_value,
    simulated_royalty_value,
    usd_nsr,
)

ROOT = Path(__file__).resolve().parents[1]
CASE = load_royalty_case(ROOT / "cases" / "sorby_hills.yaml")


def _deck_market(r: float = 0.0) -> MetalsMarket:
    """Spot equal to the long-run deck, no growth: reproduces the study's own prices."""
    return MetalsMarket(
        spots={"silver": 27.5, "lead": 2251.0},
        real_rate=r,
        convenience_yields={"silver": float(np.log1p(r)), "lead": float(np.log1p(r))},
    )


def test_deck_reproduces_payable_metal_totals() -> None:
    """Revenue x fx / deck price gives the study's payable metal (Table A11)."""
    fx = np.asarray(CASE.deck.usd_per_local)
    silver = CASE.column("silver_revenue") * fx / np.asarray(CASE.deck.prices["silver"])
    lead = CASE.column("lead_revenue") * fx / np.asarray(CASE.deck.prices["lead"])
    assert silver.sum() == pytest.approx(CASE.study.payable_metal["silver_moz"].value, rel=0.01)
    assert lead.sum() * 1000 == pytest.approx(CASE.study.payable_metal["lead_kt"].value, rel=0.01)


def test_nsr_at_the_deck_equals_the_study_rows() -> None:
    """At the study's own prices, NSR is revenue less TC and RC, in US$ at the deck rate."""
    deck = {m: np.asarray(v) for m, v in CASE.deck.prices.items()}
    nsr = usd_nsr(CASE, deck)
    fx = np.asarray(CASE.deck.usd_per_local)
    expected = (
        CASE.column("total_revenue")
        - CASE.column("lead_treatment")
        - CASE.column("silver_refining")
    ) * fx
    # Total revenue is the report's own row; the metal rows add to it within rounding.
    assert nsr == pytest.approx(expected, abs=1.5)


def test_study_npv_reconciles_within_its_unstated_convention() -> None:
    reported = CASE.study.npv_pre_tax.value
    assert pre_tax_npv(CASE, 0.08) == pytest.approx(reported, rel=0.01)


def test_revenue_value_is_independent_of_the_real_rate() -> None:
    """Market-consistent: with y = 0 and no spread, discounting cancels price growth.

    Fixed US$ deductions do not grow, so they are left out here; they make the full
    value depend weakly on the rate.
    """
    a = MetalsMarket({"silver": 60.0, "lead": 1900.0}, 0.0, {"silver": 0.0, "lead": 0.0})
    b = MetalsMarket({"silver": 60.0, "lead": 1900.0}, 0.03, {"silver": 0.0, "lead": 0.0})
    va = royalty_value(CASE, a, years_to_first_production=2, spread=0.0, deductions=[])
    vb = royalty_value(CASE, b, years_to_first_production=2, spread=0.0, deductions=[])
    assert va == pytest.approx(vb, rel=1e-12)


def test_closed_form_matches_monte_carlo() -> None:
    market = MetalsMarket({"silver": 60.0, "lead": 1900.0}, 0.03, {"silver": 0.0, "lead": 0.01})
    exact = royalty_value(CASE, market, years_to_first_production=2, spread=0.05)
    mean, se = simulated_royalty_value(
        CASE,
        market,
        {"silver": 0.33, "lead": 0.22},
        [[1.0, 0.4], [0.4, 1.0]],
        years_to_first_production=2,
        spread=0.05,
        n_paths=40_000,
        seed=7,
    )
    assert abs(mean - exact) < 4 * se


def test_delay_lowers_value_and_raises_implied_odds() -> None:
    market = MetalsMarket({"silver": 60.0, "lead": 1900.0}, 0.03, {"silver": 0.0, "lead": 0.0})
    frontier = odds_frontier(
        CASE, market, years_to_first_production=2, spread=0.10, max_delay=3, price=8.0
    )
    values = [p.value_if_passed for p in frontier.points]
    assert values == sorted(values, reverse=True)
    assert frontier.shape == "rising"


def test_synthetic_recovery() -> None:
    """A price built from known odds returns those odds."""
    market = MetalsMarket({"silver": 50.0, "lead": 2000.0}, 0.02, {"silver": 0.0, "lead": 0.0})
    v = royalty_value(CASE, market, years_to_first_production=2, spread=0.06)
    frontier = odds_frontier(
        CASE, market, years_to_first_production=2, spread=0.06, max_delay=0, price=0.7 * v
    )
    assert frontier.zero_delay_odds == pytest.approx(0.7)


def test_break_even_spread_prices_exactly() -> None:
    market = MetalsMarket({"silver": 50.0, "lead": 2000.0}, 0.02, {"silver": 0.0, "lead": 0.0})
    s = break_even_spread(CASE, market, years_to_first_production=2, price=9.0)
    assert s is not None
    v = royalty_value(CASE, market, years_to_first_production=2, spread=s)
    assert v == pytest.approx(9.0, abs=1e-5)
    assert break_even_spread(CASE, market, years_to_first_production=2, price=1e6) is None


def test_silver_only_reading_is_smaller() -> None:
    market = MetalsMarket({"silver": 60.0, "lead": 1900.0}, 0.03, {"silver": 0.0, "lead": 0.0})
    both = royalty_value(CASE, market, years_to_first_production=2, spread=0.05)
    silver = royalty_value(
        CASE,
        market,
        years_to_first_production=2,
        spread=0.05,
        metals=["silver"],
        deductions=["silver_refining"],
    )
    assert 0 < silver < both


def test_correlated_gbm_moments() -> None:
    model = CorrelatedGBM((100.0, 50.0), (0.02, -0.01), (0.3, 0.2), ((1.0, 0.6), (0.6, 1.0)))
    paths = model.simulate(1, 200_000, np.random.default_rng(1))
    assert paths.shape == (2, 200_000, 2)
    assert paths[0, :, 1].mean() == pytest.approx(100.0 * np.exp(0.02), rel=0.01)
    r = np.log(paths[:, :, 1] / paths[:, :, 0])
    assert np.corrcoef(r)[0, 1] == pytest.approx(0.6, abs=0.01)


def test_correlated_gbm_rejects_bad_matrix() -> None:
    with pytest.raises(ValueError, match="symmetric"):
        CorrelatedGBM((1.0, 1.0), (0.0, 0.0), (0.1, 0.1), ((1.0, 0.5), (0.4, 1.0)))
    with pytest.raises(ValueError, match="semi-definite"):
        CorrelatedGBM((1.0, 1.0), (0.0, 0.0), (0.1, 0.1), ((1.0, 2.0), (2.0, 1.0)))


def test_case_rejects_look_ahead(tmp_path: Path) -> None:
    text = (ROOT / "cases" / "sorby_hills.yaml").read_text(encoding="utf-8")
    bad = tmp_path / "bad.yaml"
    bad.write_text(text.replace("as_of: 2026-09-28", "as_of: 2026-01-01"), encoding="utf-8")
    with pytest.raises(ValueError, match="ADR 0007"):
        load_royalty_case(bad)


def test_sorby_hills_headline_break_even() -> None:
    """Pins the ADR 0035 headline: the price equals the on-schedule value at about 2.3%."""
    from pricedin.snapshots import load_snapshot

    snap = load_snapshot(ROOT / "data" / "snapshots" / "2026-09-28.yaml")
    market = MetalsMarket(
        {"silver": snap.value("silver_spot"), "lead": snap.value("lead_cash")},
        snap.value("real_yield_10y"),
        {"silver": 0.0, "lead": 0.0},
    )
    s = break_even_spread(CASE, market, years_to_first_production=2)
    assert s == pytest.approx(0.0233, abs=0.0005)

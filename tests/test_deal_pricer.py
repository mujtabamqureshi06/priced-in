"""Tests for the Phase 6 deal pricer (protocol 8.2 to 8.4, 8.6), on synthetic cases only."""

from __future__ import annotations

import itertools
import math
from types import SimpleNamespace
from typing import cast

import numpy as np
import pytest

from pricedin import deal_pricer as dp
from pricedin.engine import Market, RoyaltyClaim, StreamClaim, _royalty_pv, _stream_pv
from pricedin.inputs import Case
from pricedin.price_models import GBM

INC = dp.Incidence((0.1, 0.2, 0.3, 0.5))


def mc(spot: float = 2000.0, r: float = 0.015, vol: float = 0.15) -> Market:
    return dp.market_inputs(spot, r, vol)


def decided() -> dp.DecisionTiming:
    return dp.decision_timing(None, 0.0, already_decided=True)


def decided_value(model: dp.CashFlowModel, spread: float) -> float:
    return model.value(decided().scenario_probs(), spread)[0]


# --- 1. Decision distribution ---------------------------------------------------------


def test_cdf_linear_between_points() -> None:
    f = INC.cdf([0.0, 6.0, 12.0, 18.0, 30.0, 48.0, 60.0])
    assert f == pytest.approx([0.0, 0.05, 0.1, 0.15, 0.25, 0.4, 0.5])


def test_cdf_extension_at_36_to_60_hazard() -> None:
    # S36 = 0.7, S60 = 0.5: survival falls by a factor 5/7 every 24 months beyond 60.
    f = INC.cdf([72.0, 84.0, 108.0])
    assert f == pytest.approx(
        [1 - 0.5 * math.sqrt(5 / 7), 1 - 0.5 * (5 / 7), 1 - 0.5 * (5 / 7) ** 2]
    )
    assert INC.monthly_hazard() == pytest.approx(math.log(0.7 / 0.5) / 24)


def test_cdf_flat_beyond_60_when_no_hazard_and_one_when_all_decided() -> None:
    assert dp.Incidence((0.1, 0.2, 0.4, 0.4)).cdf(90.0)[0] == pytest.approx(0.4)
    assert dp.Incidence((0.5, 0.8, 0.9, 1.0)).cdf(70.0)[0] == pytest.approx(1.0)


def test_window_at_study_date_needs_no_extension() -> None:
    t = dp.decision_timing(INC, 0.0)
    assert t.probs == pytest.approx([0.0, 0.1, 0.1, 0.1, 0.1, 0.1])
    assert not t.needs_extension
    assert t.p_none == pytest.approx(0.5)


def test_window_conditioned_on_age_and_extended() -> None:
    t = dp.decision_timing(INC, 12.0)
    f72 = 1 - 0.5 * math.sqrt(5 / 7)
    expected = [0.0, 0.1 / 0.9, 0.1 / 0.9, 0.1 / 0.9, 0.1 / 0.9, (f72 - 0.5) / 0.9]
    assert t.probs == pytest.approx(expected)
    assert t.needs_extension
    assert t.p_decision == pytest.approx((f72 - 0.1) / 0.9)


def test_decision_already_made_is_year_zero() -> None:
    t = decided()
    assert t.probs[0] == 1.0
    assert t.p_decision == 1.0
    assert t.scenario_probs()[-1] == 0.0


@pytest.mark.parametrize("seed", range(20))
def test_probabilities_sum_to_at_most_one(seed: int) -> None:
    rng = np.random.default_rng(seed)
    inc = dp.Incidence.from_array(np.sort(rng.uniform(0, 0.95, 4)))
    t = dp.decision_timing(inc, float(rng.uniform(0, 120)), window_years=10)
    assert (t.probs >= -1e-15).all()
    assert t.p_decision <= 1.0 + 1e-12
    assert t.scenario_probs().sum() == pytest.approx(1.0)


def test_incidence_validation() -> None:
    with pytest.raises(ValueError, match="non-decreasing"):
        dp.Incidence((0.2, 0.1, 0.3, 0.4))
    with pytest.raises(ValueError, match="missing"):
        dp.Incidence((0.1, 0.2, 0.3, float("nan")))
    with pytest.raises(ValueError, match="F\\("):
        dp.decision_timing(dp.Incidence((1.0, 1.0, 1.0, 1.0)), 12.0)
    with pytest.raises(ValueError, match="age_months"):
        dp.decision_timing(INC, -1.0)


def _entries() -> tuple[np.ndarray, np.ndarray, list[str]]:
    # Project "x" decides at 6 months in both its entries; the others are censored at 70.
    time = np.array([6.0, 6.0, 70.0, 70.0, 70.0, 30.0])
    event = np.array([True, True, False, False, False, True])
    cluster = ["x", "x", "b", "c", "d", "e"]
    return time, event, cluster


def test_leave_one_project_out() -> None:
    time, event, cluster = _entries()
    full = dp.leave_project_out(time, event, cluster, None)
    out = dp.leave_project_out(time, event, cluster, "x")
    assert full.values[0] == pytest.approx(2 / 6)
    # Without x: 4 entries, one event at 30 months: F = 0, 0, 1/4, 1/4.
    assert out.values == pytest.approx((0.0, 0.0, 0.25, 0.25))


def test_bootstrap_replicates_leave_project_out() -> None:
    time, event, cluster = _entries()
    reps = dp.incidence_replicates(time, event, cluster, n_boot=200, seed=1, exclude_project="x")
    assert reps.shape == (200, 4)
    assert (reps[:, :2] == 0.0).all()  # x's 6-month decisions never appear
    again = dp.incidence_replicates(time, event, cluster, n_boot=200, seed=1, exclude_project="x")
    assert np.array_equal(reps, again, equal_nan=True)


# --- 2. Values ------------------------------------------------------------------------


SCHED = np.array([100.0, 120.0, 80.0])


def test_royalty_closed_form_equals_direct_sum() -> None:
    m = mc()
    terms = dp.RoyaltyTerms(rate=0.02, kind="GRR", coverage=0.5)
    model = dp.cash_flow_model(terms, SCHED, m, preproduction_years=1.0)
    s = 0.04
    direct = 0.0
    for j, oz in enumerate(SCHED, start=1):
        t = 1.0 + j
        direct += 0.02 * 0.5 * oz * 2000.0 * math.exp(m.drift * t) / (1 + 0.015 + s) ** t
    assert decided_value(model, s) == pytest.approx(direct, rel=1e-12)
    # The engine's royalty arithmetic on the expected price path agrees.
    years = 1.0 + np.arange(1, 4, dtype=float)
    payments = (0.02 * 0.5 * SCHED * 2000.0 * np.exp(m.drift * years))[None, :]
    engine = _royalty_pv(payments, years, 0, RoyaltyClaim(0.02, 0.5, spread=s), m.discount_rate)
    assert decided_value(model, s) == pytest.approx(float(engine[0]), rel=1e-12)


def test_royalty_value_is_mixture_over_decision_years() -> None:
    m = mc()
    terms = dp.RoyaltyTerms(rate=0.02, kind="GRR")
    model = dp.cash_flow_model(terms, SCHED, m, preproduction_years=2.0)
    t = dp.decision_timing(INC, 12.0)
    mixed = model.value(t.scenario_probs(), 0.03)[0]
    parts = 0.0
    for k in range(6):
        p = np.zeros(7)
        p[k] = 1.0
        parts += t.scenario_probs()[k] * model.value(p, 0.03)[0]
    assert mixed == pytest.approx(parts, rel=1e-12)
    # Later decisions are worth less at a positive spread.
    one = [model.value(np.eye(7)[k], 0.03)[0] for k in range(6)]
    assert all(a > b for a, b in itertools.pairwise(one))


def test_royalty_does_not_depend_on_real_rate_at_zero_spread() -> None:
    """ADR 0024: with y = 0 and s = 0, discounting at r cancels the drift."""
    terms = dp.RoyaltyTerms(rate=0.03, kind="GRR")
    values = [
        decided_value(dp.cash_flow_model(terms, SCHED, mc(r=r), preproduction_years=1.0), 0.0)
        for r in (-0.01, 0.0, 0.02)
    ]
    assert values == pytest.approx([0.03 * SCHED.sum() * 2000.0] * 3)


def test_flat_deck_at_k_equals_market_consistent_at_k_one_plus_r() -> None:
    """ADR 0045: s = k(1 + r) is exact for a revenue claim."""
    terms = dp.RoyaltyTerms(rate=0.02, kind="GRR")
    k, r = 0.05, 0.015
    flat = dp.cash_flow_model(terms, SCHED, Market.flat(2000.0, 0.0), preproduction_years=1.0)
    cons = dp.cash_flow_model(terms, SCHED, mc(r=r), preproduction_years=1.0)
    assert decided_value(flat, k) == pytest.approx(
        decided_value(cons, dp.spread_from_rate(k, r)), rel=1e-12
    )


def test_nsr_offsite_costs_and_gross_flag() -> None:
    m = mc(vol=0.0)
    nsr = dp.RoyaltyTerms(rate=0.02, offsite_cost_per_oz=50.0)
    model = dp.cash_flow_model(nsr, SCHED, m, preproduction_years=1.0)
    t = 1.0 + np.arange(1, 4)
    fwd = 2000.0 * np.exp(m.drift * t)
    expected = float(np.sum(0.02 * SCHED * (fwd - 50.0) / 1.045**t))
    assert decided_value(model, 0.03) == pytest.approx(expected, rel=1e-12)
    gross = dp.cash_flow_model(dp.RoyaltyTerms(rate=0.02), SCHED, m, preproduction_years=1.0)
    assert any("upper bound" in f for f in gross.flags)
    assert decided_value(gross, 0.03) > decided_value(model, 0.03)


def _fake_case(koz: np.ndarray) -> Case:
    columns = {"payable_gold_koz": SimpleNamespace(values=list(koz))}
    return cast(
        Case,
        SimpleNamespace(schedule=SimpleNamespace(money_units="US$ thousands", columns=columns)),
    )


@pytest.mark.parametrize("escalation", [0.0, 0.01])
def test_stream_call_strip_matches_engine_monte_carlo(escalation: float) -> None:
    m = dp.market_inputs(1900.0, 0.01, 0.25)
    koz = np.array([50.0, 60.0, 60.0, 40.0])
    terms = dp.StreamTerms(
        share=0.06, payment="lesser_of_fixed_and_spot", fixed_price=1700.0, escalation=escalation
    )
    model = dp.cash_flow_model(terms, koz, m, preproduction_years=1.0)
    closed = decided_value(model, 0.03)
    years = 1.0 + np.arange(1, koz.size + 1, dtype=float)
    prices = GBM(m.gold_spot, m.drift, m.volatility).simulate(
        int(years[-1]), 100_000, np.random.default_rng(5)
    )
    claim = StreamClaim(
        share=0.06, transfer_price=1700.0, transfer_escalation=escalation, spread=0.03
    )
    pv = _stream_pv(_fake_case(koz), claim, prices[:, years.astype(int)], years, m.discount_rate)
    se = float(pv.std(ddof=1) / np.sqrt(pv.size))
    assert closed > 0
    assert abs(closed - float(pv.mean())) < 4 * se
    assert any("approximate" in f for f in model.flags)


def test_stream_zero_volatility_is_intrinsic() -> None:
    m = dp.market_inputs(1000.0, 0.0, 0.0, 0.0)
    terms = dp.StreamTerms(share=0.1, payment="lesser_of_fixed_and_spot", fixed_price=1200.0)
    model = dp.cash_flow_model(terms, SCHED, m, preproduction_years=1.0)
    assert decided_value(model, 0.0) == 0.0


def test_stream_share_of_spot_and_fixed_payment() -> None:
    m = mc(vol=0.3)
    t = 1.0 + np.arange(1, 4)
    fwd = 2000.0 * np.exp(m.drift * t)
    disc = 1.045**-t
    share = dp.StreamTerms(share=0.05, payment="share_of_spot", spot_share=0.2)
    v = decided_value(dp.cash_flow_model(share, SCHED, m, preproduction_years=1.0), 0.03)
    assert v == pytest.approx(float(np.sum(0.05 * SCHED * 0.8 * fwd * disc)))
    fixed = dp.StreamTerms(
        share=0.05, payment="fixed", fixed_price=400.0, escalation=0.02, inflation=0.03
    )
    strike = 400.0 * 1.02**t / 1.03**t
    v = decided_value(dp.cash_flow_model(fixed, SCHED, m, preproduction_years=1.0), 0.03)
    assert v == pytest.approx(float(np.sum(0.05 * SCHED * (fwd - strike) * disc)))


def test_stream_escalation_from_production() -> None:
    m = dp.market_inputs(1000.0, 0.0, 0.0, 0.0)
    terms = dp.StreamTerms(
        share=1.0,
        payment="fixed",
        fixed_price=100.0,
        escalation=0.1,
        escalation_from="production",
    )
    model = dp.cash_flow_model(terms, np.ones(2), m, preproduction_years=2.0)
    # Production starts at t = 2; payments at t = 3, 4 with strikes 100 x 1.1 and 100 x 1.21.
    assert decided_value(model, 0.0) == pytest.approx((1000 - 110) + (1000 - 121))


def test_royalty_rate_step_down() -> None:
    terms = dp.RoyaltyTerms(
        rate=0.03, kind="GRR", steps=(dp.RateStep(threshold=150.0, rate=0.015),)
    )
    w = dp.claim_ounces(terms, np.array([100.0, 100.0, 100.0]))
    assert w == pytest.approx([3.0, 50 * 0.03 + 50 * 0.015, 1.5])


def test_royalty_step_thresholds_count_covered_ounces() -> None:
    terms = dp.RoyaltyTerms(
        rate=0.02, kind="GRR", coverage=0.5, steps=(dp.RateStep(threshold=50.0, rate=0.0),)
    )
    assert dp.claim_ounces(terms, np.array([100.0, 100.0])) == pytest.approx([1.0, 0.0])


def test_stream_delivery_step_down_delivered_and_produced() -> None:
    sched = np.array([100.0, 100.0, 100.0])
    delivered = dp.StreamTerms(
        share=0.1, payment="share_of_spot", steps=(dp.DeliveryStep(15.0, 0.05),)
    )
    assert dp.claim_ounces(delivered, sched) == pytest.approx([10.0, 7.5, 5.0])
    produced = dp.StreamTerms(
        share=0.1,
        payment="share_of_spot",
        steps=(dp.DeliveryStep(15.0, 0.05),),
        step_basis="produced",
    )
    assert dp.claim_ounces(produced, sched) == pytest.approx([5.75, 5.0, 5.0])
    capped = dp.StreamTerms(
        share=0.1,
        payment="share_of_spot",
        steps=(dp.DeliveryStep(20.0, 0.0), dp.DeliveryStep(25.0, 0.05)),
    )
    assert dp.claim_ounces(capped, sched) == pytest.approx([10.0, 10.0, 0.0])


def test_cap_on_cumulative_payments() -> None:
    m = dp.market_inputs(1000.0, 0.0, 0.0, 0.0)
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", cap=2500.0)
    model = dp.cash_flow_model(terms, np.array([10.0, 10.0, 10.0]), m, preproduction_years=1.0)
    # Payments of 1,000 at t = 2, 3, 4, capped at 2,500 in total.
    v, se = model.value(decided().scenario_probs(), 0.05)
    assert v == pytest.approx(1000 / 1.05**2 + 1000 / 1.05**3 + 500 / 1.05**4)
    assert se == 0.0


def test_cap_fixed_in_nominal_terms() -> None:
    m = dp.market_inputs(1000.0, 0.0, 0.0, 0.0)
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", cap=2000.0, inflation=0.1)
    model = dp.cash_flow_model(terms, np.array([10.0, 10.0, 10.0]), m, preproduction_years=1.0)
    # Nominal payments 1,000 x 1.1^t at t = 2, 3: 1,210 then 790 to reach the cap.
    expected = 1000.0 + 790.0 / 1.1**3
    assert decided_value(model, 0.0) == pytest.approx(expected)


def test_non_binding_cap_monte_carlo_matches_closed_form() -> None:
    m = mc(vol=0.2)
    plain = dp.RoyaltyTerms(rate=0.02, offsite_cost_per_oz=30.0)
    capped = dp.RoyaltyTerms(rate=0.02, offsite_cost_per_oz=30.0, cap=1e12)
    a = dp.cash_flow_model(plain, SCHED, m, preproduction_years=1.0)
    b = dp.cash_flow_model(capped, SCHED, m, preproduction_years=1.0, n_paths=40_000, seed=3)
    probs = dp.decision_timing(INC, 6.0).scenario_probs()
    va = a.value(probs, 0.04)[0]
    vb, se = b.value(probs, 0.04)
    assert se > 0
    assert abs(va - vb) < 4 * se
    reps = np.tile(np.array(INC.values), (3, 1))
    out = dp.price_range(b, np.array([0.02, 0.04, 0.06]), replicates=reps, age_months=6.0)
    assert out.n_paths == 40_000
    assert (out.standard_errors > 0).all()
    assert (out.standard_errors < 0.01 * out.values).all()


AMR_M = dp.market_inputs(1000.0, 0.0, 0.0, 0.0)
TEN = np.array([10.0, 10.0, 10.0])


def test_advance_not_credited() -> None:
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", advance=dp.AdvanceMinimum(300.0, credited=False))
    model = dp.cash_flow_model(terms, TEN, AMR_M, preproduction_years=2.0)
    disc = 1.05 ** -np.arange(1, 6, dtype=float)
    expected = 300 * (disc[0] + disc[1]) + 1000 * (disc[2] + disc[3] + disc[4])
    assert decided_value(model, 0.05) == pytest.approx(expected)


def test_advance_credited_in_money() -> None:
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", advance=dp.AdvanceMinimum(300.0))
    model = dp.cash_flow_model(terms, TEN, AMR_M, preproduction_years=2.0, n_paths=8)
    disc = 1.05 ** -np.arange(1, 6, dtype=float)
    expected = 300 * (disc[0] + disc[1]) + 400 * disc[2] + 1000 * (disc[3] + disc[4])
    assert decided_value(model, 0.05) == pytest.approx(expected)


def test_advance_credited_matches_engine() -> None:
    """Same crediting arithmetic as engine._royalty_pv on a deterministic path."""
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", advance=dp.AdvanceMinimum(300.0), inflation=0.02)
    model = dp.cash_flow_model(terms, TEN, AMR_M, preproduction_years=2.0, n_paths=4)
    claim = RoyaltyClaim(
        rate=0.1, coverage=1.0, amr_per_year=300.0, amr_inflation=0.02, spread=0.05
    )
    years = np.array([3.0, 4.0, 5.0])
    engine = _royalty_pv(np.full((1, 3), 1000.0), years, 2, claim, 0.0)
    assert decided_value(model, 0.05) == pytest.approx(float(engine[0]))


def test_advance_until_window_closes_without_decision() -> None:
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR", advance=dp.AdvanceMinimum(100.0, credited=False))
    model = dp.cash_flow_model(terms, TEN, AMR_M, preproduction_years=1.0)
    never = dp.decision_timing(dp.Incidence((0.0, 0.0, 0.0, 0.0)), 24.0)
    assert never.p_none == 1.0
    v = model.value(never.scenario_probs(), 0.05)[0]
    assert v == pytest.approx(sum(100 / 1.05**m for m in range(1, 6)))


def test_advance_in_ounces_credited() -> None:
    terms = dp.RoyaltyTerms(
        rate=0.1, kind="GRR", advance=dp.AdvanceMinimum(0.5, unit="ounces", credited=True)
    )
    model = dp.cash_flow_model(terms, TEN, AMR_M, preproduction_years=2.0)
    # 0.5 oz at t = 1, 2 (500 each); royalty ounces 1, 1, 1 less 1 oz credited at t = 3.
    disc = 1.05 ** -np.arange(1, 6, dtype=float)
    expected = 500 * (disc[0] + disc[1]) + 0 * disc[2] + 1000 * (disc[3] + disc[4])
    assert decided_value(model, 0.05) == pytest.approx(expected)


def test_monte_carlo_error_above_one_percent_raises() -> None:
    terms = dp.RoyaltyTerms(rate=0.02, kind="GRR", cap=1e12)
    model = dp.cash_flow_model(terms, SCHED, mc(vol=0.6), preproduction_years=1.0, n_paths=10)
    with pytest.raises(ValueError, match="raise n_paths"):
        dp.price_range(
            model, np.array([0.03]), replicates=None, age_months=0.0, already_decided=True
        )


def test_unimplemented_terms_are_not_priced() -> None:
    terms = dp.RoyaltyTerms(rate=0.02, other_terms=("sliding scale on gold price",))
    with pytest.raises(NotImplementedError, match=r"not priced: .*sliding scale"):
        dp.cash_flow_model(terms, SCHED, mc())
    stream = dp.StreamTerms(share=0.1, payment="share_of_spot", other_terms=("debt-linked step",))
    with pytest.raises(NotImplementedError, match="debt-linked"):
        dp.cash_flow_model(stream, SCHED, mc())


def test_flags_for_buybacks_and_default_preproduction() -> None:
    fixed = dp.cash_flow_model(
        dp.RoyaltyTerms(rate=0.02, kind="GRR", buyback="fixed_price"), SCHED, mc()
    )
    assert any("fixed-price buy-back ignored" in f for f in fixed.flags)
    assert any("one year assumed" in f for f in fixed.flags)
    fmv = dp.RoyaltyTerms(rate=0.02, kind="GRR", buyback="fair_market_value")
    plain = dp.RoyaltyTerms(rate=0.02, kind="GRR")
    a = dp.cash_flow_model(fmv, SCHED, mc(), preproduction_years=1.0)
    b = dp.cash_flow_model(plain, SCHED, mc(), preproduction_years=1.0)
    assert decided_value(a, 0.03) == decided_value(b, 0.03)
    assert dp.cash_flow_model(plain, SCHED, mc(), preproduction_years=1.0).flags == ()


# --- 3. Spread ------------------------------------------------------------------------


def test_spread_conversion() -> None:
    assert dp.real_from_nominal(0.07, 0.02) == pytest.approx(1.07 / 1.02 - 1)
    assert dp.spread_from_rate(0.05, 0.01) == pytest.approx(0.0505)
    assert dp.spread_from_rate(0.05, -0.01) == pytest.approx(0.0495)


ROWS = (
    dp.SpreadRow("A", 0.04, 0.04),
    dp.SpreadRow("A", 0.06, 0.06),
    dp.SpreadRow("B", 0.02, 0.08),
    dp.SpreadRow("C", 0.05, 0.05),
)


def test_prior_weights_companies_equally() -> None:
    values, weights = dp.spread_prior(ROWS)
    assert values == pytest.approx([0.04, 0.06, 0.02, 0.08, 0.05])
    assert weights == pytest.approx([1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 3])
    draws = dp.sample_spreads(ROWS, 60_000, np.random.default_rng(0))
    assert np.mean(draws == 0.05) == pytest.approx(1 / 3, abs=0.01)
    assert np.mean(draws == 0.08) == pytest.approx(1 / 6, abs=0.01)


def test_prior_minimum() -> None:
    assert not dp.meets_minimum(ROWS)  # 5 rates (a range counts twice), 3 companies
    seven = (*ROWS, dp.SpreadRow("D", 0.03, 0.07))
    assert not dp.meets_minimum(seven)  # 7 rates, 4 companies
    assert dp.meets_minimum((*seven, dp.SpreadRow("D", 0.05, 0.05)))  # 8 rates, 4 companies


# --- 4. Draw loop ---------------------------------------------------------------------


def test_price_range_pairs_draws_and_reports_percentiles() -> None:
    terms = dp.RoyaltyTerms(rate=0.02, kind="GRR")
    model = dp.cash_flow_model(terms, SCHED, mc(), preproduction_years=1.0)
    rng = np.random.default_rng(4)
    n = 300
    spreads = dp.sample_spreads(ROWS, n, rng)
    reps = np.sort(rng.uniform(0.0, 0.8, (n, 4)), axis=1)
    out = dp.price_range(model, spreads, replicates=reps, age_months=18.0)
    for i in (0, 7, 299):
        t = dp.decision_timing(dp.Incidence.from_array(reps[i]), 18.0)
        assert out.values[i] == pytest.approx(model.value(t.scenario_probs(), spreads[i])[0])
    assert (out.p10, out.p50, out.p90) == pytest.approx(
        tuple(np.percentile(out.values, [10, 50, 90]))
    )
    assert out.p10 <= out.p50 <= out.p90
    assert (out.standard_errors == 0).all() and out.n_paths == 0
    assert out.needs_extension


def test_percentiles_hand_case() -> None:
    terms = dp.RoyaltyTerms(rate=0.1, kind="GRR")
    model = dp.cash_flow_model(terms, np.array([10.0]), AMR_M, preproduction_years=0.0)
    # Decision already made; one payment of 1,000 at t = 1: value 1000 / (1 + s).
    spreads = np.linspace(0.0, 0.10, 11)
    out = dp.price_range(model, spreads, replicates=None, age_months=0.0, already_decided=True)
    vals = 1000 / (1 + spreads)
    assert out.p50 == pytest.approx(1000 / 1.05)
    assert out.p10 == pytest.approx(vals[9])  # 10th percentile of 11 points is the 2nd lowest
    assert out.p90 == pytest.approx(vals[1])


def test_price_range_rejects_missing_replicate() -> None:
    model = dp.cash_flow_model(
        dp.RoyaltyTerms(rate=0.02, kind="GRR"), SCHED, mc(), preproduction_years=1.0
    )
    reps = np.array([[0.1, 0.2, 0.3, np.nan]])
    with pytest.raises(ValueError, match="missing horizon"):
        dp.price_range(model, np.array([0.03]), replicates=reps, age_months=0.0)


# --- 5. Contingent amounts (8.6) ------------------------------------------------------


def test_contingent_epv_hand_case() -> None:
    t = dp.decision_timing(INC, 0.0)  # 0.1 in each of years 1..5
    end = {"decision_point": 1.0}  # end-of-year dating (sensitivity)
    on_decision = dp.contingent_epv(1000.0, t, trigger="decision", real_rate=0.02, **end)
    assert on_decision == pytest.approx(sum(100 / 1.02**k for k in range(1, 6)))
    on_production = dp.contingent_epv(
        1000.0, t, trigger="first_production", real_rate=0.02, preproduction_years=1.0, **end
    )
    assert on_production == pytest.approx(sum(100 / 1.02**k for k in range(2, 6)))
    any_decision = dp.contingent_epv(
        1000.0,
        t,
        trigger="first_production",
        real_rate=0.02,
        preproduction_years=1.0,
        trigger_in_window=False,
        **end,
    )
    assert any_decision == pytest.approx(sum(100 / 1.02**k for k in range(2, 7)))
    mid = dp.contingent_epv(1000.0, t, trigger="decision", real_rate=0.02)
    assert mid == pytest.approx(sum(100 / 1.02 ** (k - 0.5) for k in range(1, 6)))
    mid_prod = dp.contingent_epv(
        1000.0, t, trigger="first_production", real_rate=0.02, preproduction_years=1.0
    )
    assert mid_prod == pytest.approx(sum(100 / 1.02 ** (k + 0.5) for k in range(1, 5)))
    assert dp.contingent_epv(1000.0, decided(), trigger="decision", real_rate=0.02) == 1000.0


def test_decision_point_mid_year_is_worth_more_than_end_of_year() -> None:
    claim = dp.RoyaltyTerms(rate=0.02, kind="GRR")
    market = dp.Market(gold_spot=1500.0, drift=0.0, volatility=0.0, discount_rate=0.05)
    mid = dp.cash_flow_model(claim, [100.0, 100.0], market, preproduction_years=1.0)
    end = dp.cash_flow_model(
        claim, [100.0, 100.0], market, preproduction_years=1.0, decision_point=1.0
    )
    # scenario k = 1: first payment at 0.5 + 1 + 1 = 2.5 (mid) and 3.0 (end)
    assert 2.5 in mid.times
    assert 3.0 in end.times


def test_advance_limited_by_years_and_total() -> None:
    market = dp.Market(gold_spot=1500.0, drift=0.0, volatility=0.0, discount_rate=0.0)
    sched = [100.0]

    def no_decision_row(adv: dp.AdvanceMinimum) -> float:
        claim = dp.RoyaltyTerms(rate=0.02, kind="GRR", advance=adv)
        model = dp.cash_flow_model(claim, sched, market, preproduction_years=1.0)
        return float(model.mean[-1].sum())

    assert no_decision_row(dp.AdvanceMinimum(10.0, credited=False)) == pytest.approx(50.0)
    assert no_decision_row(dp.AdvanceMinimum(10.0, credited=False, max_years=2)) == pytest.approx(
        20.0
    )
    assert no_decision_row(
        dp.AdvanceMinimum(10.0, credited=False, max_total=25.0)
    ) == pytest.approx(25.0)


def test_unspecified_threshold_basis_is_not_priced() -> None:
    claim = dp.RoyaltyTerms(
        rate=0.02, kind="GRR", steps=(dp.RateStep(100.0, 0.01),), step_basis="unspecified"
    )
    with pytest.raises(NotImplementedError, match="not priced"):
        dp.check_implemented(claim)


def test_max_relative_se_is_the_largest_draw() -> None:
    out = dp.PriceRange(
        values=np.array([100.0, 50.0, 0.0]),
        standard_errors=np.array([0.5, 0.4, 0.0]),
        spreads=np.zeros(3),
        n_paths=20_000,
        p10=0.0,
        p50=50.0,
        p90=100.0,
        needs_extension=False,
    )
    assert out.max_relative_se == pytest.approx(0.008)

from pathlib import Path

import numpy as np
import pytest

from pricedin.engine import Market, Overrun, Risks, RoyaltyClaim, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.project import npv, schedule_cash_flows

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def south_railroad() -> Case:
    return load_case(ROOT / "cases" / "south_railroad.yaml")


@pytest.fixture(scope="module")
def osino() -> Case:
    return load_case(ROOT / "cases" / "osino_twin_hills.yaml")


@pytest.fixture(scope="module")
def overrun() -> Overrun:
    priors = load_priors(ROOT / "data" / "priors.yaml")
    dist = priors.get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    factor = priors.get("capex.inflation_adjustment").distribution
    return Overrun(ratio=dist, real_factor=float(factor.value))  # type: ignore[union-attr]


def _study_npv(case: Case) -> float:
    return case.study.npv_after_tax.value


def _capex(case: Case) -> np.ndarray:
    cols = case.schedule.columns
    capex = np.asarray(cols["initial_capex"].values, dtype=float)
    if "expansion_capex" in cols:
        capex = capex + np.asarray(cols["expansion_capex"].values, dtype=float)
    return capex


@pytest.mark.parametrize("case_name", ["south_railroad", "osino"])
def test_all_risks_off_reproduces_study_npv(case_name: str, request: pytest.FixtureRequest) -> None:
    case: Case = request.getfixturevalue(case_name)
    res = simulate(case, Market.study_deck(case), Timing(), Risks(), n_paths=5)
    deck = np.full((1, len(case.schedule.periods)), case.study.price_deck["gold"].value)
    exact = npv(schedule_cash_flows(case, deck).after_tax, case, case.study.discount_rate.value)
    np.testing.assert_allclose(res.project_value, exact[0], rtol=1e-12)
    tolerance = 1.0 if case.schedule.money_units == "US$ thousands" else 2.0
    assert res.project_value[0] == pytest.approx(_study_npv(case), abs=tolerance)
    assert res.built.all()
    assert (res.build_year == 0).all()


def test_delay_discounts_by_whole_years(south_railroad: Case) -> None:
    market = Market.study_deck(south_railroad)
    base = simulate(south_railroad, market, Timing(), Risks(), n_paths=2)
    late = simulate(
        south_railroad, market, Timing(years_to_start=1, added_delay=2), Risks(), n_paths=2
    )
    rate = south_railroad.study.discount_rate.value
    np.testing.assert_allclose(late.project_value, base.project_value / (1 + rate) ** 3)
    assert (late.build_year == 3).all()


def test_stage_gates_scale_value_by_the_odds(south_railroad: Case) -> None:
    res = simulate(
        south_railroad,
        Market.study_deck(south_railroad),
        Timing(),
        Risks(stage_odds=0.6),
        n_paths=40_000,
        seed=1,
    )
    share = res.built.mean()
    se = np.sqrt(0.6 * 0.4 / res.n_paths)
    assert abs(share - 0.6) < 4 * se
    assert (res.project_value[~res.built] == 0).all()
    mean, se_value = res.estimate(res.project_value)
    assert abs(mean - 0.6 * _study_npv(south_railroad)) < 4 * se_value + 1.0


def test_overrun_lowers_value_by_expected_extra_capital(osino: Case, overrun: Overrun) -> None:
    market = Market.study_deck(osino)
    base = simulate(osino, market, Timing(), Risks(), n_paths=10).project_value[0]
    res = simulate(osino, market, Timing(), Risks(overrun=overrun), n_paths=200_000, seed=3)
    d = overrun.ratio
    expected_ratio = overrun.real_factor * (d.shift + np.exp(d.mu + d.sigma**2 / 2))
    rate = osino.study.discount_rate.value
    pv_capex = float(_capex(osino) @ (1 + rate) ** -np.arange(len(osino.schedule.periods)))
    expected = base - (expected_ratio - 1) * pv_capex
    mean, se = res.estimate(res.project_value)
    assert abs(mean - expected) < 4 * se


def test_build_rule_extremes(south_railroad: Case) -> None:
    market = Market.study_deck(south_railroad)
    timing = Timing(years_to_start=1, max_wait=3)
    never = simulate(south_railroad, market, timing, Risks(build_rule=True, build_hurdle=1e12))
    assert not never.built.any()
    assert (never.project_value == 0).all()
    always = simulate(south_railroad, market, timing, Risks(build_rule=True, build_hurdle=-1e12))
    assert always.built.all()
    assert (always.build_year == 1).all()


def test_build_rule_waits_for_a_better_price(south_railroad: Case) -> None:
    market = Market(gold_spot=900.0, drift=0.0, volatility=0.25, discount_rate=0.05)
    res = simulate(
        south_railroad,
        market,
        Timing(max_wait=10),
        Risks(build_rule=True),
        n_paths=5_000,
        seed=7,
    )
    late = res.build_year[res.built]
    assert (late > 0).any()
    assert 0 < res.built.mean() < 1


def test_build_rule_does_not_see_the_overrun(south_railroad: Case, overrun: Overrun) -> None:
    market = Market(gold_spot=1100.0, drift=0.0, volatility=0.2, discount_rate=0.05)
    timing = Timing(max_wait=5)
    a = simulate(south_railroad, market, timing, Risks(build_rule=True), n_paths=2_000, seed=4)
    b = simulate(
        south_railroad,
        market,
        timing,
        Risks(build_rule=True, overrun=overrun),
        n_paths=2_000,
        seed=4,
    )
    np.testing.assert_array_equal(a.build_year, b.build_year)


def test_royalty_without_advances_matches_hand_calculation(south_railroad: Case) -> None:
    claim = RoyaltyClaim(rate=0.00633, coverage=0.35, spread=0.02)
    res = simulate(
        south_railroad,
        Market.study_deck(south_railroad),
        Timing(years_to_start=1),
        Risks(),
        royalty=claim,
        n_paths=2,
    )
    gold = np.asarray(south_railroad.schedule.columns["gold_revenue"].values, dtype=float)
    years = 1 + np.arange(len(gold))
    expected = float(0.00633 * 0.35 * gold @ (1.07**-years))
    assert res.royalty_value is not None
    np.testing.assert_allclose(res.royalty_value, expected)


def test_royalty_advances_credited_and_not_credited(south_railroad: Case) -> None:
    timing = Timing(years_to_start=3)
    market = Market.study_deck(south_railroad)
    gold = np.asarray(south_railroad.schedule.columns["gold_revenue"].values, dtype=float)
    years = 3 + np.arange(len(gold))
    first = int(np.flatnonzero(gold > 0)[0])
    n_adv = 3 + first - 1
    advance = 100.0
    advances = advance * float((1.05 ** -np.arange(1, n_adv + 1)).sum())
    payments = 0.01 * gold

    plain = simulate(
        south_railroad,
        market,
        timing,
        Risks(),
        royalty=RoyaltyClaim(rate=0.01, coverage=1.0, amr_per_year=advance, amr_credited=False),
        n_paths=1,
    ).royalty_value
    assert plain is not None
    assert plain[0] == pytest.approx(float(payments @ 1.05**-years) + advances)

    credited = simulate(
        south_railroad,
        market,
        timing,
        Risks(),
        royalty=RoyaltyClaim(rate=0.01, coverage=1.0, amr_per_year=advance, amr_credited=True),
        n_paths=1,
    ).royalty_value
    assert credited is not None
    recovered = payments.copy()
    left = advance * n_adv
    for t in range(len(recovered)):
        take = min(left, recovered[t])
        recovered[t] -= take
        left -= take
    assert credited[0] == pytest.approx(float(recovered @ 1.05**-years) + advances)
    assert credited[0] < plain[0]


def test_advances_paid_on_paths_that_are_never_built(south_railroad: Case) -> None:
    claim = RoyaltyClaim(rate=0.01, coverage=1.0, amr_per_year=100.0)
    market = Market.study_deck(south_railroad)
    failed = simulate(
        south_railroad,
        market,
        Timing(years_to_start=2),
        Risks(stage_odds=0.0),
        royalty=claim,
        n_paths=3,
    )
    assert failed.royalty_value is not None
    np.testing.assert_allclose(failed.royalty_value, 100 / 1.05 + 100 / 1.05**2)

    expired = simulate(
        south_railroad,
        market,
        Timing(years_to_start=1, max_wait=2),
        Risks(build_rule=True, build_hurdle=1e12),
        royalty=claim,
        n_paths=3,
    )
    assert expired.royalty_value is not None
    np.testing.assert_allclose(expired.royalty_value, sum(100 / 1.05**k for k in (1, 2, 3)))


def test_same_seed_same_result(south_railroad: Case, overrun: Overrun) -> None:
    market = Market.market_consistent(1890.0, 0.0, 0.0, 0.15)
    risks = Risks(stage_odds=0.8, overrun=overrun, build_rule=True)
    timing = Timing(years_to_start=1, max_wait=4)
    a = simulate(south_railroad, market, timing, risks, n_paths=500, seed=11)
    b = simulate(south_railroad, market, timing, risks, n_paths=500, seed=11)
    c = simulate(south_railroad, market, timing, risks, n_paths=500, seed=12)
    np.testing.assert_array_equal(a.project_value, b.project_value)
    assert not np.array_equal(a.project_value, c.project_value)


def test_market_consistent_drift() -> None:
    m = Market.market_consistent(1800.0, 0.01, 0.002, 0.15)
    assert m.drift == pytest.approx(np.log(1.01) - 0.002)
    assert m.discount_rate == 0.01


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        Timing(added_delay=-1)
    with pytest.raises(ValueError, match="stage_odds"):
        Risks(stage_odds=1.2)


def test_decision_rate_changes_only_the_build_choice(south_railroad: Case) -> None:
    market = Market(gold_spot=1050.0, drift=0.0, volatility=0.0, discount_rate=0.05)
    timing = Timing(max_wait=0)
    study_rate = simulate(south_railroad, market, timing, Risks(build_rule=True), n_paths=2)
    strict = simulate(
        south_railroad, market, timing, Risks(build_rule=True, decision_rate=0.5), n_paths=2
    )
    assert study_rate.built.all()
    assert not strict.built.any()


def test_window_and_advance_diagnostics(south_railroad: Case) -> None:
    claim = RoyaltyClaim(rate=0.01, coverage=1.0, amr_per_year=100.0)
    market = Market.study_deck(south_railroad)
    expired = simulate(
        south_railroad,
        market,
        Timing(max_wait=2),
        Risks(build_rule=True, build_hurdle=1e12),
        royalty=claim,
        n_paths=4,
    )
    assert expired.window_expired_share == 1.0
    assert expired.advance_share == pytest.approx(1.0)
    built = simulate(south_railroad, market, Timing(), Risks(), royalty=claim, n_paths=4)
    assert built.window_expired_share == 0.0
    assert built.advance_share is not None and 0.0 <= built.advance_share < 0.05
    no_claim = simulate(south_railroad, market, Timing(), Risks(), n_paths=2)
    assert no_claim.advance_share is None


def test_timing_priors_registered() -> None:
    priors = load_priors(ROOT / "data" / "priors.yaml")
    assert priors.get("timing.years_to_start.south_railroad").distribution.value == 4  # type: ignore[union-attr]
    assert priors.get("timing.years_to_start.osino_twin_hills").distribution.value == 1  # type: ignore[union-attr]
    assert priors.get("build.window_years").status == "J"


def test_fixed_nominal_advances_lose_real_value(south_railroad: Case) -> None:
    market = Market.study_deck(south_railroad)
    timing = Timing(years_to_start=2)
    infl = 0.03
    claim = RoyaltyClaim(rate=0.0, coverage=1.0, amr_per_year=100.0, amr_inflation=infl)
    res = simulate(south_railroad, market, timing, Risks(stage_odds=0.0), royalty=claim, n_paths=1)
    assert res.royalty_value is not None
    expected = sum(100 / (1 + infl) ** k / 1.05**k for k in (1, 2))
    assert res.royalty_value[0] == pytest.approx(expected)


def test_credited_nominal_total_recovered_in_real_terms(south_railroad: Case) -> None:
    market = Market.study_deck(south_railroad)
    timing = Timing(years_to_start=3)
    gold = np.asarray(south_railroad.schedule.columns["gold_revenue"].values, dtype=float)
    years = 3 + np.arange(len(gold))
    n_adv = 3 + int(np.flatnonzero(gold > 0)[0]) - 1
    infl, adv = 0.02, 50_000.0
    claim = RoyaltyClaim(rate=0.01, coverage=1.0, amr_per_year=adv, amr_inflation=infl)
    res = simulate(south_railroad, market, timing, Risks(), royalty=claim, n_paths=1)
    pay = 0.01 * gold
    left = adv * n_adv
    for t in range(len(pay)):
        idx = (1 + infl) ** years[t]
        take = min(left / idx, pay[t])
        pay[t] -= take
        left -= take * idx
    advances = sum(adv / (1 + infl) ** k / 1.05**k for k in range(1, n_adv + 1))
    assert res.royalty_value is not None
    assert res.royalty_value[0] == pytest.approx(float(pay @ 1.05**-years) + advances)

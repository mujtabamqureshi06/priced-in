from pathlib import Path

import pytest

from pricedin.engine import Market, Overrun, Risks, Timing
from pricedin.inputs import Case, load_case
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.report import project_waterfall

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def osino() -> Case:
    return load_case(ROOT / "cases" / "osino_twin_hills.yaml")


def _overrun() -> Overrun:
    dist = load_priors(ROOT / "data" / "priors.yaml").get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    return Overrun(ratio=dist, real_factor=0.914)


def test_steps_sum_to_total(osino: Case) -> None:
    market = Market.market_consistent(1960.6, 0.0152, 0.0, 0.141)
    steps = project_waterfall(
        osino,
        market,
        Timing(years_to_start=1, max_wait=5),
        Risks(stage_odds=0.88, overrun=_overrun(), build_rule=True),
        n_paths=2_000,
    )
    assert steps[0].value == osino.study.npv_after_tax.value
    total = sum(s.change for s in steps[1:])
    assert total == pytest.approx(steps[-1].value - steps[0].value)
    assert [s.label for s in steps][5] == "Ramp-up"
    assert steps[5].change == 0.0


def test_all_risks_off_at_study_rate_returns_step_zero(osino: Case) -> None:
    deck = Market.study_deck(osino)
    steps = project_waterfall(osino, deck, Timing(), Risks(), n_paths=3)
    for s in steps[1:]:
        assert s.value == pytest.approx(steps[0].value, abs=2.0)


def test_shapley_steps_sum_to_the_same_total(osino: Case) -> None:
    from pricedin.report import shapley_waterfall

    market = Market.market_consistent(1960.6, 0.0152, 0.0, 0.141)
    timing = Timing(years_to_start=1, max_wait=5)
    risks = Risks(stage_odds=0.88, overrun=_overrun(), build_rule=True)
    seq = project_waterfall(osino, market, timing, risks, n_paths=1_000, seed=2)
    shap = shapley_waterfall(osino, market, timing, risks, n_paths=1_000, seed=2)
    assert [s.label for s in shap] == [s.label for s in seq]
    assert shap[-1].value == pytest.approx(seq[-1].value)
    assert sum(s.change for s in shap[1:]) == pytest.approx(shap[-1].value - shap[0].value)
    for a, b in zip(seq[:3], shap[:3], strict=True):
        assert a.value == b.value


def test_shapley_matches_sequential_for_a_lone_risk(osino: Case) -> None:
    """With only stage failure on, its step is the same in either method."""
    from pricedin.report import shapley_waterfall

    market = Market.market_consistent(1960.6, 0.0152, 0.0, 0.0)
    timing = Timing(years_to_start=0)
    risks = Risks(stage_odds=0.6)
    seq = project_waterfall(osino, market, timing, risks, n_paths=500, seed=3)
    shap = shapley_waterfall(osino, market, timing, risks, n_paths=500, seed=3)
    by_label = {s.label: s.change for s in shap}
    seq_label = {s.label: s.change for s in seq}
    assert by_label["Stage failure"] == pytest.approx(seq_label["Stage failure"])
    assert by_label["Capital cost overrun"] == pytest.approx(0.0)
    assert by_label["Base timing"] == pytest.approx(0.0)


def test_shapley_is_order_independent_where_sequential_is_not(osino: Case) -> None:
    """Stage failure scales everything after it, so its sequential step depends on order."""
    from pricedin.report import shapley_waterfall

    market = Market.market_consistent(1960.6, 0.0152, 0.0, 0.141)
    timing = Timing(years_to_start=1, max_wait=5)
    risks = Risks(stage_odds=0.5, overrun=_overrun(), build_rule=True)
    shap = shapley_waterfall(osino, market, timing, risks, n_paths=1_000, seed=4)
    seq = project_waterfall(osino, market, timing, risks, n_paths=1_000, seed=4)
    shap_overrun = next(s.change for s in shap if s.label == "Capital cost overrun")
    seq_overrun = next(s.change for s in seq if s.label == "Capital cost overrun")
    # Sequentially the overrun is charged before stage failure halves it; Shapley shares it.
    assert abs(shap_overrun) < abs(seq_overrun)

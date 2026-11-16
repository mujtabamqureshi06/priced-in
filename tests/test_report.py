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

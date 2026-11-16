from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import load_case
from pricedin.report import Step
from pricedin.sensitivity import build_year_distribution, project_readout, tornado

ROOT = Path(__file__).resolve().parents[1]


def test_tornado_orders_by_swing_and_rejects_unknown() -> None:
    def f(p: Mapping[str, Any]) -> float:
        return float(2 * p["a"] + p["b"])

    alts = {"b": (("lo", 0.0), ("hi", 2.0)), "a": (("lo", 0.0), ("hi", 2.0))}
    bars = tornado(f, {"a": 1.0, "b": 1.0}, alts)
    assert [b.name for b in bars] == ["a", "b"]
    assert bars[0].swing == pytest.approx(4.0)
    assert bars[0].base == pytest.approx(3.0)
    with pytest.raises(KeyError):
        tornado(f, {"a": 1.0, "b": 1.0}, {"c": (("lo", 0), ("hi", 1))})


def test_build_year_distribution_sums_to_one() -> None:
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    market = Market(gold_spot=1200.0, drift=0.0, volatility=0.25, discount_rate=0.02)
    res = simulate(
        case,
        market,
        Timing(years_to_start=1, max_wait=5),
        Risks(stage_odds=0.8, build_rule=True),
        n_paths=2_000,
        seed=3,
    )
    dist = build_year_distribution(res)
    assert sum(dist.values()) == pytest.approx(1.0)
    assert dist["never built"] > 0.2


def test_readout_numbers_match_steps() -> None:
    steps = (
        Step("Study NPV", 100.0, 0.0, 0.0),
        Step("Base timing", 90.0, -10.0, 0.0),
        Step("Stage failure", 60.0, -30.0, 0.0),
    )
    text = project_readout("Case X", "US$ millions", steps)
    assert "60 US$ millions" in text and "100 US$ millions" in text
    assert "-40%" in text
    assert "stage failure, which lowers value by 30" in text

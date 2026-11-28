"""Tests for the study-entry tool (``pricedin.entry_tool``)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pricedin import defaults, entry_tool
from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.parametric import Headline, build_case
from pricedin.priors import load_priors

ROOT = Path(__file__).resolve().parents[1]
PRIORS = load_priors(ROOT / "data" / "priors.yaml")
FIGURES = {
    "initial_capex": 300.0,
    "preproduction_years": 2,
    "life_years": 10,
    "payable_koz_per_year": 150.0,
    "aisc_per_oz": 1100.0,
    "gold_deck": 1800.0,
    "tax_rate": 0.3,
    "discount_rate": 0.05,
    "npv_after_tax": 400.0,
    "irr_after_tax": 0.25,
}
MARKET = {"gold_spot": 2000.0, "real_rate": 0.015, "volatility": 0.15}


def test_matches_direct_engine_run() -> None:
    out = entry_tool.evaluate(FIGURES, "FS", MARKET, PRIORS, n_paths=4_000)
    case = build_case(
        Headline(**FIGURES),  # type: ignore[arg-type]
        case_id="x",
        name="x",
        operator="x",
        jurisdiction="x",
        as_of=date(2000, 1, 1),
        stage="FS",
        document_title="x",
        document_url="https://example.org/x",
        document_date=date(2000, 1, 1),
        location="x",
    )
    m = Market.market_consistent(2000.0, 0.015, 0.0, 0.15)
    r = simulate(
        case,
        m,
        Timing(years_to_start=1, max_wait=0),
        Risks(stage_odds=1.0, overrun=defaults.overrun(PRIORS, "FS"), build_rule=True),
        financing=defaults.equity_financing(PRIORS),
        n_paths=4_000,
        seed=1,
    )
    assert out["value_if_built"] == pytest.approx(r.estimate(r.project_value)[0], rel=1e-12)
    assert out["share_built"] == pytest.approx(float(r.built.mean()))


def test_output_is_json_and_deterministic() -> None:
    a = entry_tool.evaluate(FIGURES, "PFS", MARKET, PRIORS, n_paths=2_000)
    b = entry_tool.evaluate(FIGURES, "PFS", MARKET, PRIORS, n_paths=2_000)
    assert json.loads(json.dumps(a)) == a == b
    assert a["basis"] == "after-tax"
    assert a["builder_error"]["median"] == 0.032
    assert a["notes"] == []


def test_pea_uses_pfs_overrun() -> None:
    pea = entry_tool.evaluate(FIGURES, "PEA", MARKET, PRIORS, n_paths=2_000)
    pfs = entry_tool.evaluate(FIGURES, "PFS", MARKET, PRIORS, n_paths=2_000)
    assert pea["value_if_built"] == pfs["value_if_built"]


def test_higher_gold_raises_value() -> None:
    lo = entry_tool.evaluate(FIGURES, "FS", MARKET, PRIORS, n_paths=2_000)
    hi = entry_tool.evaluate(FIGURES, "FS", {**MARKET, "gold_spot": 2400.0}, PRIORS, n_paths=2_000)
    assert hi["value_if_built"] > lo["value_if_built"]


def test_marginal_project_is_flagged() -> None:
    figs = {**FIGURES, "npv_after_tax": 100.0, "irr_after_tax": 0.12}
    out = entry_tool.evaluate(figs, "FS", MARKET, PRIORS, n_paths=2_000)
    assert len(out["notes"]) == 1


@pytest.mark.parametrize(
    ("figures", "stage", "market"),
    [
        ({**FIGURES, "grade": 1.0}, "FS", MARKET),
        (FIGURES, "BFS", MARKET),
        (FIGURES, "FS", {"gold_spot": 2000.0, "real_rate": 0.01}),
        ({**FIGURES, "irr_after_tax": 0.04}, "FS", MARKET),
    ],
)
def test_rejects_bad_input(
    figures: dict[str, object], stage: str, market: dict[str, float]
) -> None:
    with pytest.raises(ValueError):
        entry_tool.evaluate(figures, stage, market, PRIORS, n_paths=500)

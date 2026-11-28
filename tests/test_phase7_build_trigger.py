"""Synthetic tests for the Phase 7 build-trigger script (no study inputs used)."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from pricedin.parametric import Headline
from pricedin.priors import load_priors

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bt", ROOT / "scripts" / "phase7_build_trigger.py")
assert spec is not None and spec.loader is not None
bt = importlib.util.module_from_spec(spec)
sys.modules["bt"] = bt
spec.loader.exec_module(bt)

PRIORS = load_priors(ROOT / "data" / "priors.yaml")
H = Headline(
    initial_capex=300.0,
    preproduction_years=2,
    life_years=10,
    payable_koz_per_year=150.0,
    aisc_per_oz=1100.0,
    gold_deck=1500.0,
    tax_rate=0.3,
    discount_rate=0.05,
    npv_after_tax=250.0,
    irr_after_tax=0.2,
)
M = bt.MarketRow(gold_spot=1500.0, real_rate=0.01, volatility=0.16)


def test_panel_reconciles_on_public_labels() -> None:
    with open(bt.LABELS, newline="") as fh:
        labels = [
            r
            for r in csv.DictReader(fh)
            if r["panel"] in ("primary", "both") and r["project_id"] not in bt.EXCLUDED
        ]
    rows = bt.panel_quarters(labels)
    n = len({r["project_id"] for r in rows})
    assert (n, len(rows), sum(int(r["y"]) for r in rows)) == bt.EXPECTED


def test_trigger_is_the_boundary() -> None:
    g = bt.trigger(H, "FS", M, PRIORS)
    assert g is not None and bt.G_LO < g < H.gold_deck
    lo = bt.trigger(H, "FS", M, PRIORS)
    assert lo == pytest.approx(g)


def test_trigger_moves_with_costs_and_capital() -> None:
    base = bt.trigger(H, "FS", M, PRIORS)
    up = bt.trigger(H, "FS", M, PRIORS, cost_scale=1 + bt.COST_SHIFT)
    down = bt.trigger(H, "FS", M, PRIORS, cost_scale=1 - bt.COST_SHIFT)
    assert base is not None and up is not None and down is not None
    assert down < base < up


def test_synthetic_recovery(tmp_path: Path) -> None:
    """Decisions generated to follow log(spot/G*) give a positive coefficient."""
    rng = np.random.default_rng(3)
    quarters = []
    t = bt.quarter_end_on_or_after(__import__("datetime").date(2012, 1, 1))
    for _ in range(40):
        quarters.append(t)
        t = bt.next_quarter_end(t)
    spot = 1300 * np.exp(np.cumsum(rng.normal(0, 0.08, len(quarters))))
    with open(tmp_path / "m.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quarter_end", "gold_spot", "real_rate", "volatility", "cpi"])
        for q, s in zip(quarters, spot, strict=True):
            w.writerow([q.isoformat(), s, 0.01, 0.16, 100.0])
    labels: list[dict[str, str]] = []
    heads: list[dict[str, object]] = []
    i = 0
    while len(labels) < 70:
        npv = float(rng.uniform(120, 400))
        figs = {**H.__dict__, "npv_after_tax": npv, "irr_after_tax": 0.08 + npv / 2500}
        try:
            g = bt.trigger(Headline(**figs), "FS", M, PRIORS)
        except ValueError:
            continue
        assert g is not None
        i += 1
        start = int(rng.integers(0, 20))
        entry = quarters[start]
        outcome, when = "non_event", ""
        for k in range(start, min(start + 12, len(quarters) - 1)):
            p = 1 - np.exp(-np.exp(-2.5 + 3.0 * np.log(spot[k] / g)))
            if rng.random() < p:
                outcome, when = "construction_decision", bt.add_months(quarters[k], 2).isoformat()
                break
        labels.append(
            {
                "project_id": f"p{i}",
                "entry_study": "FS",
                "entry_study_date": entry.isoformat(),
                "outcome": outcome,
                "outcome_date": when,
            }
        )
        heads.append({"project_id": f"p{i}", "study_month": entry.isoformat()[:7], **figs})
    with open(tmp_path / "h.csv", "w", newline="") as fh:
        dw = csv.DictWriter(fh, fieldnames=list(heads[0]))
        dw.writeheader()
        dw.writerows(heads)
    setattr(bt, "N_BOOT", 50)  # noqa: B010
    res = bt.run(str(tmp_path / "h.csv"), str(tmp_path / "m.csv"), labels, synthetic=True)
    primary = res["primary"]
    assert primary["decisions"] >= bt.MIN_EVENTS
    assert primary["coef"][0] > 0

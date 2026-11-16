"""Regenerate the Osino Twin Hills forward valuation tables (#64). Prints Markdown.

Usage: uv run python scripts/osino_case.py
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pricedin.engine import Financing, Market, Overrun, Risks, Timing, simulate
from pricedin.inputs import load_case
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.report import project_waterfall, shapley_waterfall
from pricedin.sensitivity import build_year_distribution, project_readout, tornado
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 20_000, 1


def main() -> None:
    """Print the tables."""
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    priors = load_priors(ROOT / "data" / "priors.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2023-07-13.yaml")
    dist = priors.get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    overrun = Overrun(dist, 0.914)
    odds = priors.get("stage.fs_to_build").distribution.value  # type: ignore[union-attr]

    base: dict[str, Any] = {
        "stage_odds": odds,
        "years_to_start": 1,
        "max_wait": 5,
        "convenience_yield": 0.0,
        "volatility": snap.value("realised_vol_10y"),
        "overrun": True,
        "decision_rate": None,
    }

    def run(p: Mapping[str, Any], financing: Financing | None = None) -> Any:
        market = Market.market_consistent(
            snap.value("gold_spot"),
            snap.value("real_yield_10y"),
            p["convenience_yield"],
            p["volatility"],
        )
        risks = Risks(
            stage_odds=p["stage_odds"],
            overrun=overrun if p["overrun"] else None,
            build_rule=True,
            decision_rate=p["decision_rate"],
        )
        timing = Timing(years_to_start=p["years_to_start"], max_wait=p["max_wait"])
        return (
            market,
            timing,
            risks,
            simulate(case, market, timing, risks, financing=financing, n_paths=N, seed=SEED),
        )

    market, timing, risks, res = run(base, Financing(0.0, 0.1054))
    steps = project_waterfall(case, market, timing, risks, n_paths=N, seed=SEED)
    print("| Step | Value (US$M) | Change | Std. error |\n|---|---|---|---|")
    for s in steps:
        note = f" ({s.note})" if s.note else ""
        print(f"| {s.label}{note} | {s.value:,.1f} | {s.change:+,.1f} | {s.standard_error:.1f} |")
    print("\n" + project_readout("Osino Twin Hills", "US$ million", steps))
    shapley = shapley_waterfall(case, market, timing, risks, n_paths=N, seed=SEED)
    print("\n| Risk step | Sequential change | Shapley change (std. error) |\n|---|---|---|")
    seq = {s.label: s.change for s in steps}
    for s in shapley[3:]:
        print(f"| {s.label} | {seq[s.label]:+,.1f} | {s.change:+,.1f} ({s.standard_error:.1f}) |")

    assert res.equity_value is not None
    eq, eq_se = res.estimate(res.equity_value)
    print(f"\nEquity claim, all-equity funding at a 10.54% discount: {eq:,.1f} (se {eq_se:.1f})")
    for debt in (0.3, 0.6):
        r = run(base, Financing(debt, 0.1054))[3]
        print(f"  debt {debt:.0%}: {r.estimate(r.equity_value)[0]:,.1f}")

    print("\n| Build timing | Share of paths |\n|---|---|")
    for k, v in build_year_distribution(res).items():
        print(f"| {k} | {v:.1%} |" if v >= 0.0005 else f"| {k} | under 0.1% |")

    def value(p: Mapping[str, Any]) -> float:
        r = run(p)[3]
        return float(r.project_value.mean())

    alts = {
        "stage_odds": (("0.75 (AMC)", 0.75), ("0.95 (stress)", 0.95)),
        "years_to_start": (("0 years", 0), ("2 years", 2)),
        "overrun": (("off", False), ("on (base)", True)),
        "convenience_yield": (("0% (base)", 0.0), ("1%", 0.01)),
        "volatility": (("GVZ 12.7%", snap.value("gvz")), ("20%", 0.20)),
        "max_wait": (("5 years (base)", 5), ("10 years", 10)),
        "decision_rate": (("study 5% (base)", None), ("8.9% (CIM FS)", 0.089)),
    }
    print("\n| Input | Low | High | Value at low | Value at high | Swing |")
    print("|---|---|---|---|---|---|")
    for b in tornado(value, base, alts):
        print(
            f"| {b.name} | {b.low_label} | {b.high_label} | {b.low:,.1f} | "
            f"{b.high:,.1f} | {b.swing:,.1f} |"
        )


if __name__ == "__main__":
    main()

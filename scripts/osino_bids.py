"""What the Dundee and Shanjin bids imply for Osino Twin Hills (ADRs 0031, 0032).

Each bid is compared with the project claim (the acquirer funds construction). Without
a calibrated project-level spread, the implied odds absorb the acquirer's required
return, so each bid is shown as zero-delay odds against a real spread on net project
cash flows, with the break-even spread marked. Usage: uv run python scripts/osino_bids.py
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pricedin.engine import Financing, Market, Overrun, Risks, Timing
from pricedin.inputs import Case, load_case
from pricedin.inversion import equity_frontier
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 20_000, 1
# (label, snapshot, equity value C$M, net cash C$M and its date)
BIDS = (
    ("Dundee Precious Metals, 2023-12-18", "2023-12-18.yaml", 287.0, 8.339, "2023-09-30"),
    ("Shanjin (Yintai), 2024-02-23", "2024-02-23.yaml", 368.0, 9.343, "2023-12-31"),
)
REFERENCE_RATES = {
    "DFS discount rate 5% real": 0.05,
    "CIM survey FS-stage gold 8.9% real (Smith 2013)": 0.089,
    "Lopatnikov and Rumyantsev (2025) 16% real WACC for Osino": 0.16,
}


def zero_delay_odds(
    case: Case, market: Market, timing: Timing, risks: Risks, price: float, spread: float
) -> float:
    """Zero-delay implied odds with project cash flows discounted at r + spread."""
    m = replace(market, discount_rate=market.discount_rate + spread)
    f = equity_frontier(
        case, m, timing, risks, Financing(), price, max_delay=0, n_paths=N, seed=SEED
    )
    return f.zero_delay_odds


def main() -> None:
    """Print the tables."""
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    priors = load_priors(ROOT / "data" / "priors.yaml")
    dist = priors.get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    risks = Risks(overrun=Overrun(dist, 0.914), build_rule=True)
    timing = Timing(years_to_start=1, max_wait=5)
    grid = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15)
    for label, snap_file, equity, cash, cash_date in BIDS:
        snap = load_snapshot(ROOT / "data" / "snapshots" / snap_file)
        fx, r = snap.value("usdcad"), snap.value("real_yield_10y")
        market = Market.market_consistent(
            snap.value("gold_spot"), r, 0.0, snap.value("realised_vol_10y")
        )
        price = (equity - cash) / fx
        print(
            f"\n{label}: project price C${equity - cash:.1f}M = US${price:.1f}M "
            f"(net cash at {cash_date}; USD/CAD {fx})"
        )
        print("| Real spread | Zero-delay odds |\n|---|---|")
        for s in grid:
            q = zero_delay_odds(case, market, timing, risks, price, s)
            print(f"| {s:.0%} | {q:.2f} |" if q <= 1 else f"| {s:.0%} | no solution |")
        lo, hi = 0.0, 0.5
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if zero_delay_odds(case, market, timing, risks, price, mid) < 1:
                lo = mid
            else:
                hi = mid
        print(f"Break-even spread: {0.5 * (lo + hi):.1%}")
        for name, rate in REFERENCE_RATES.items():
            s = rate - r
            q = zero_delay_odds(case, market, timing, risks, price, s)
            shown = f"{q:.2f}" if q <= 1 else "no solution"
            print(f"  {name}: spread {s:.1%}, odds {shown}")


if __name__ == "__main__":
    main()

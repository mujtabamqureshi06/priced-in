"""Regenerate the Sorby Hills royalty results (ADR 0035). Prints Markdown tables.

Usage: uv run python scripts/sorby_hills_case.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from pricedin.controls import implied_spread, load_control
from pricedin.royalty_cases import (
    MetalsMarket,
    break_even_spread,
    load_royalty_case,
    odds_frontier,
    royalty_value,
)
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE_START = 2  # first production row paid two years after the deal (ADR 0035)
# OR Royalties (formerly Osisko), audited statements for 2025 (filed Feb 2026), Note 12:
# post-tax real discount rate 5.1%; statutory rate 26.5%.
OSISKO_POST_TAX, OSISKO_TAX = 0.051, 0.265
LME_TENOR = 0.25  # years, LME 3-month


@dataclass(frozen=True)
class Sensitivity:
    """One sensitivity row."""

    label: str
    market: MetalsMarket
    start: int = BASE_START
    metals: list[str] | None = None
    deductions: list[str] | None = None


def _odds(q: float) -> str:
    return f"{q:.2f}" if q <= 1 else "above certain value"


def main() -> None:
    """Print the tables."""
    case = load_royalty_case(ROOT / "cases" / "sorby_hills.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2026-09-28.yaml")
    r = snap.value("real_yield_10y")
    spots = {"silver": snap.value("silver_spot"), "lead": snap.value("lead_cash")}

    def market(y_silver: float = 0.0, y_lead: float = 0.0) -> MetalsMarket:
        return MetalsMarket(spots, r, {"silver": y_silver, "lead": y_lead})

    base = market()
    price = case.royalty.price.value

    wharf = load_control(ROOT / "controls" / "wharf.yaml")
    s_wharf = implied_spread(
        wharf.price.value,
        wharf.royalty_rate.value,
        wharf.payable_gold_oz,
        wharf.gold_spot.value,
        wharf.real_rate.value,
    )
    anchors = {
        "OR Royalties 2025, post-tax real 5.1%, raw": OSISKO_POST_TAX - r,
        "OR Royalties 2025, pre-tax equivalent 6.94%": OSISKO_POST_TAX / (1 - OSISKO_TAX) - r,
        "Wharf control (Metalla, 2020)": s_wharf,
    }

    print(
        f"Price US${price:.1f}M; real rate {r:.2%}; silver {spots['silver']}, lead {spots['lead']}"
    )
    be = break_even_spread(case, base, years_to_first_production=BASE_START)
    print(f"Break-even spread: {be:.2%}" if be is not None else "Break-even spread: none")
    print()
    print("| Real spread | Certain on-time value (US$M) | Implied odds of reaching production |")
    print("|---|---|---|")
    rows = [(f"{s:.1%}", s) for s in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16)]
    rows += [(f"{name} ({s:.1%})", s) for name, s in anchors.items()]
    for label, s in rows:
        v = royalty_value(case, base, years_to_first_production=BASE_START, spread=s)
        print(f"| {label} | {v:.2f} | {_odds(price / v)} |")

    print()
    print("Odds against added delay at the OR Royalties raw anchor")
    print()
    raw = anchors["OR Royalties 2025, post-tax real 5.1%, raw"]
    anchor = anchors["OR Royalties 2025, pre-tax equivalent 6.94%"]
    frontier = odds_frontier(
        case, base, years_to_first_production=BASE_START, spread=raw, max_delay=3
    )
    print("| Added delay (years) | Value (US$M) | Implied odds |")
    print("|---|---|---|")
    for p in frontier.points:
        print(f"| {p.added_delay} | {p.value_if_passed:.2f} | {_odds(p.gate_odds)} |")

    tbill = snap.value("tbill_3m")
    y_lead_lme = (
        math.log1p(tbill * LME_TENOR) - math.log(snap.value("lead_3m") / snap.value("lead_cash"))
    ) / LME_TENOR
    lead_y = f"Lead y from LME cash to 3-month ({y_lead_lme:.1%}), short-tenor proxy"
    tc_rc = ["lead_treatment", "silver_refining"]
    sensitivities = [
        Sensitivity("Base (all metals, TC and RC deducted, y = 0, first year paid at t = 2)", base),
        Sensitivity("First production year paid at t = 1", base, start=1),
        Sensitivity("Logistics also deducted", base, deductions=[*tc_rc, "logistics"]),
        Sensitivity("Silver only", base, metals=["silver"], deductions=["silver_refining"]),
        Sensitivity("y = +2% (silver and lead)", market(0.02, 0.02)),
        Sensitivity("y = -2% (silver and lead)", market(-0.02, -0.02)),
        Sensitivity(lead_y, market(0.0, y_lead_lme)),
    ]
    print()
    print("| Sensitivity | Value at pre-tax anchor (US$M) | Break-even spread |")
    print("|---|---|---|")
    for sens in sensitivities:
        v = royalty_value(
            case,
            sens.market,
            years_to_first_production=sens.start,
            spread=anchor,
            metals=sens.metals,
            deductions=sens.deductions,
        )
        b = break_even_spread(
            case,
            sens.market,
            years_to_first_production=sens.start,
            metals=sens.metals,
            deductions=sens.deductions,
        )
        b_text = f"{b:.1%}" if b is not None else "none (price above value at 0%)"
        print(f"| {sens.label} | {v:.2f} | {b_text} |")


if __name__ == "__main__":
    main()

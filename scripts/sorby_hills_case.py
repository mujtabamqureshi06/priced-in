"""Regenerate the Sorby Hills royalty results (ADRs 0035, 0045). Prints Markdown tables.

Reference rates (OR Royalties) are read the way their source applied them: metal
prices flat in real terms at the source's deck (silver; lead at spot), discounted at the
stated rate (ADR 0045). The
spread curve, the break-even spread and the sensitivities are in market-consistent
mode. The result assumes the royalty covers silver and lead revenue, an inference;
Vox calls it a silver royalty (see the case note), so "Silver only" is shown too.

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
    royalty_value,
)
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE_START = 2  # first production row paid two years after the deal (ADR 0035)
# OR Royalties (formerly Osisko), audited statements for 2025 (filed Feb 2026), Note 12:
# post-tax real discount rate 5.1%; statutory rate 26.5%.
# Goodwill test on fair value less costs of disposal; long-term silver US$42/oz (no lead
# price is stated, so lead is held at spot).
OSISKO_POST_TAX, OSISKO_TAX = 0.051, 0.265
OR_SILVER_DECK = 42.0
LME_TENOR = 0.25  # years, LME 3-month
SENSITIVITY_SPREAD = 0.06  # a round spread for comparing sensitivities


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
    decks = {
        "OR Royalties' silver deck, lead at spot": {
            "silver": OR_SILVER_DECK,
            "lead": spots["lead"],
        },
        "spot": spots,
    }
    references = {
        "OR Royalties 2025, post-tax real 5.1%": OSISKO_POST_TAX,
        "OR Royalties 2025, pre-tax equivalent 6.94%": OSISKO_POST_TAX / (1 - OSISKO_TAX),
    }

    print(
        f"Price US${price:.1f}M; real rate {r:.2%}; silver {spots['silver']}, lead {spots['lead']}"
    )
    be = break_even_spread(case, base, years_to_first_production=BASE_START)
    print(f"Break-even spread: {be:.2%}" if be is not None else "Break-even spread: none")
    print()
    print("| Real spread (market-consistent) | Certain on-time value (US$M) | Implied odds |")
    print("|---|---|---|")
    rows = [(f"{s:.1%}", s) for s in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16)]
    rows.append((f"Wharf control (Metalla, 2020) ({s_wharf:.1%})", s_wharf))
    for label, s in rows:
        v = royalty_value(case, base, years_to_first_production=BASE_START, spread=s)
        print(f"| {label} | {v:.2f} | {_odds(price / v)} |")

    print()
    print("| Reference rate | Metals flat at | Certain on-time value (US$M) | Implied odds |")
    print("|---|---|---|---|")
    for name, k in references.items():
        for deck_name, deck in decks.items():
            flat = MetalsMarket(deck, 0.0, {"silver": 0.0, "lead": 0.0})
            for metals, deductions, tag in (
                (None, None, "silver and lead"),
                (["silver"], ["silver_refining"], "silver only"),
            ):
                v = royalty_value(
                    case,
                    flat,
                    years_to_first_production=BASE_START,
                    spread=k,
                    metals=metals,
                    deductions=deductions,
                )
                print(f"| {name}, {tag} | {deck_name} | {v:.2f} | {_odds(price / v)} |")

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
    print("| Sensitivity (market-consistent) | Value at a 6% spread (US$M) | Break-even spread |")
    print("|---|---|---|")
    for sens in sensitivities:
        v = royalty_value(
            case,
            sens.market,
            years_to_first_production=sens.start,
            spread=SENSITIVITY_SPREAD,
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

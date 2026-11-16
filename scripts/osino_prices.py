"""What the Osino prices imply for Twin Hills (ADRs 0031 to 0033).

Three prices, all with balance-sheet items from Osino's interim statements at
September 30, 2023 (the latest published before each date):

- the undisturbed market value on December 15, 2023, compared with the equity claim
  with dilution (ADR 0030), less corporate G&A (ADR 0033);
- Dundee Precious Metals' offer (December 18, 2023) and Shanjin's (February 23, 2024),
  compared with the project claim, since the acquirer funds construction (ADR 0031).

Each is shown as zero-delay implied odds against a real spread on net project cash
flows, with the break-even spread (ADR 0032). Usage: uv run python scripts/osino_prices.py
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from pricedin.engine import Financing, Market, Overrun, Risks, Timing
from pricedin.inputs import load_case
from pricedin.inversion import equity_frontier
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 20_000, 1
YEARS_TO_START = 1
# Osino interim statements, Sept 30, 2023 (C$ million): cash, Nebari credit facility,
# leases, other financial liabilities (deferred consideration and leases).
NET_DEBT = 19.676 + 0.084 + 2.668 - 8.339
OPTIONS, OPTION_PRICE = 9.431, 1.02  # millions, C$ weighted average
WARRANTS, WARRANT_PRICE = 9.252, 1.28
BASIC_SHARES = 159.514
GA_PER_YEAR = 5.449 / 0.75  # nine-month corporate G&A, annualised (C$ million)
UNDISTURBED_PRICE = 1.553 / 1.372  # implied by DPM's stated 37.2% premium to the close


@dataclass(frozen=True)
class Price:
    """One observed price and how it maps to a claim."""

    label: str
    snapshot: str
    project_price_cad: float
    claim: str  # "project" or "equity"


def proceeds(share_price: float) -> float:
    """Exercise proceeds of in-the-money options and warrants (C$ million)."""
    total = 0.0
    for count, strike in ((OPTIONS, OPTION_PRICE), (WARRANTS, WARRANT_PRICE)):
        if share_price > strike:
            total += count * strike
    return total


def undisturbed() -> Price:
    """December 15, 2023 market value, treasury method on in-the-money securities."""
    p = UNDISTURBED_PRICE
    shares = BASIC_SHARES + (OPTIONS if p > OPTION_PRICE else 0.0)
    shares += WARRANTS if p > WARRANT_PRICE else 0.0
    equity = p * shares
    return Price(
        "Undisturbed market value, 2023-12-15",
        "2023-12-15.yaml",
        equity + NET_DEBT - proceeds(p),
        "equity",
    )


PRICES = (
    undisturbed(),
    Price(
        "Dundee Precious Metals offer, 2023-12-18",
        "2023-12-18.yaml",
        287.0 + NET_DEBT - proceeds(1.553),
        "project",
    ),
    Price(
        "Shanjin offer, 2024-02-23", "2024-02-23.yaml", 368.0 + NET_DEBT - proceeds(1.90), "project"
    ),
)


def pv_annuity(rate: float, years: int) -> float:
    """Present value of 1 a year for ``years`` years, end-of-year."""
    t = np.arange(1, years + 1)
    return float(((1 + rate) ** -t).sum())


def odds_function(price: Price) -> tuple[Callable[[float], float], float, float]:
    """Return q(spread) at zero delay, the US$ price and the G&A share of it."""
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    dist = load_priors(ROOT / "data" / "priors.yaml").get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    risks = Risks(overrun=Overrun(dist, 0.914), build_rule=True)
    timing = Timing(years_to_start=YEARS_TO_START, max_wait=5)
    snap = load_snapshot(ROOT / "data" / "snapshots" / price.snapshot)
    fx, r = snap.value("usdcad"), snap.value("real_yield_10y")
    base = Market.market_consistent(snap.value("gold_spot"), r, 0.0, snap.value("realised_vol_10y"))
    usd = price.project_price_cad / fx
    financing = Financing(0.0, 0.1054) if price.claim == "equity" else Financing()
    ga = GA_PER_YEAR / fx if price.claim == "equity" else 0.0
    life = len(case.schedule.periods)
    ga_pass = ga * pv_annuity(r, YEARS_TO_START + life)
    ga_fail = ga * pv_annuity(r, YEARS_TO_START)

    def q(spread: float) -> float:
        m = replace(base, discount_rate=r + spread)
        f = equity_frontier(
            case, m, timing, risks, financing, 1.0, max_delay=0, n_paths=N, seed=SEED
        )
        denominator = f.points[0].value_if_passed - ga_pass + ga_fail
        return (usd + ga_fail) / denominator if denominator > 0 else float("inf")

    return q, usd, ga_pass


def main() -> None:
    """Print the tables."""
    grid = (0.0, 0.04, 0.08, 0.12, 0.15)
    for price in PRICES:
        q, usd, ga_pass = odds_function(price)
        snap = load_snapshot(ROOT / "data" / "snapshots" / price.snapshot)
        r = snap.value("real_yield_10y")
        print(
            f"\n{price.label}: C${price.project_price_cad:.1f}M = US${usd:.1f}M "
            f"against the {price.claim} claim; PV of G&A on built paths US${ga_pass:.1f}M"
        )
        print(" | ".join(f"{s:.0%}: {q(s):.2f}" if q(s) <= 1 else f"{s:.0%}: n/s" for s in grid))
        lo, hi = 0.0, 0.6
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if q(mid) < 1 else (lo, mid)
        print(f"Break-even spread: {0.5 * (lo + hi):.1%}")
        for name, rate in (
            ("DFS 5%", 0.05),
            ("CIM FS 8.9%", 0.089),
            ("Eight Capital 10.5%", 0.105),
            ("Eight Capital 13.5%", 0.135),
            ("Lopatnikov-Rumyantsev 16%", 0.16),
        ):
            v = q(rate - r)
            print(
                f"  {name}: spread {rate - r:.1%}, odds {v:.2f}"
                if v <= 1
                else f"  {name}: spread {rate - r:.1%}, no solution"
            )


if __name__ == "__main__":
    main()

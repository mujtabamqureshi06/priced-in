"""What Orla Mining's offer for Gold Standard Ventures implies for South Railroad (#81).

Two prices on the 2022 feasibility study (cases/south_railroad_fs2022.yaml), both with
balance-sheet items from Gold Standard's interim statements at March 31, 2022 (the
latest published before the offer):

- Orla's offer (announced June 13, 2022, priced on the June 10 close), compared with
  the project claim, since the acquirer funds construction (ADR 0031);
- the undisturbed market value on June 10, 2022, compared with the equity claim with
  dilution (ADR 0030), less corporate G&A (ADR 0033).

Gold Standard's other assets (Lewis, the rest of the Railroad-Pinion land package)
are given no value, so the odds read here are an upper bound for South Railroad alone.
Each price is shown as zero-delay implied odds against a real spread on net project
cash flows, with the break-even spread (ADR 0032).

Usage: uv run python scripts/gsv_takeover.py
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from pricedin.engine import Financing, Market, Overrun, Risks, Timing, simulate
from pricedin.inputs import Case, load_case
from pricedin.inversion import equity_frontier
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 20_000, 1
PRIOR = "timing.years_to_start.south_railroad_fs2022"
SNAPSHOT = "2022-06-10.yaml"

# Gold Standard interim statements, March 31, 2022 (C$ million): cash less lease
# liabilities. No borrowings. The Orion silver stream deposit (deferred revenue) is not
# debt: the stream is already in the study's silver revenue. Reclamation bonds and the
# reclamation provision are left out as tied to the project.
NET_DEBT = 0.115559 + 0.248211 - 17.491368
BASIC_SHARES = 358.735368  # millions, March 31, 2022 (also the circular's June 30 count)
RSUS = 4.245580  # millions; vest and receive the consideration under the arrangement
ITM_OPTIONS, ITM_STRIKE = 4.833410, 0.57  # granted Q1 2022; all other options are out
GA_PER_YEAR = 2.280039 * 4  # Q1 2022 operating and administrative expenses, annualised
OFFER_PRICE = 0.655  # C$ per share, implied by 0.1193 Orla + C$0.0001 at the June 10 close
UNDISTURBED_PRICE = OFFER_PRICE / 1.35  # stated 35% premium to the June 10 close


@dataclass(frozen=True)
class Price:
    """One observed price and how it maps to a claim."""

    label: str
    project_price_cad: float
    claim: str  # "project" or "equity"


def claim_price(share_price: float) -> float:
    """Equity value on a diluted basis plus net debt (C$ million)."""
    shares = BASIC_SHARES + RSUS
    intrinsic = ITM_OPTIONS * max(share_price - ITM_STRIKE, 0.0)
    return share_price * shares + intrinsic + NET_DEBT


PRICES = (
    Price("Orla offer, priced on the 2022-06-10 close", claim_price(OFFER_PRICE), "project"),
    Price("Undisturbed market value, 2022-06-10", claim_price(UNDISTURBED_PRICE), "equity"),
)


def pv_annuity(rate: float, years: int) -> float:
    """Present value of 1 a year for ``years`` years, end-of-year."""
    t = np.arange(1, years + 1)
    return float(((1 + rate) ** -t).sum())


def base_years() -> int:
    """Years to the study's Year -1 from the timing prior (ADR 0043)."""
    prior = load_priors(ROOT / "data" / "priors.yaml").get(PRIOR).distribution
    return int(prior.value)  # type: ignore[union-attr]


def setup(years_to_start: int) -> tuple[Case, Market, Timing, Risks, float]:
    """Case, market, timing and risks on the snapshot; returns the US$/C$ rate too."""
    case = load_case(ROOT / "cases" / "south_railroad_fs2022.yaml")
    dist = load_priors(ROOT / "data" / "priors.yaml").get("capex.overrun.fs").distribution
    assert isinstance(dist, ShiftedLognormal)
    risks = Risks(overrun=Overrun(dist, 0.914), build_rule=True)
    timing = Timing(years_to_start=years_to_start, max_wait=5)
    snap = load_snapshot(ROOT / "data" / "snapshots" / SNAPSHOT)
    market = Market.market_consistent(
        snap.value("gold_spot"), snap.value("real_yield_10y"), 0.0, snap.value("realised_vol_10y")
    )
    return case, market, timing, risks, snap.value("usdcad")


def odds_function(
    price: Price, years_to_start: int
) -> tuple[Callable[[float], float], float, float]:
    """Return q(spread) at zero added delay, the US$ price and the G&A share of it."""
    case, base, timing, risks, fx = setup(years_to_start)
    r = base.discount_rate
    usd = price.project_price_cad / fx * 1000.0  # case money is US$ thousands
    financing = Financing(0.0, 0.1054) if price.claim == "equity" else Financing()
    ga = GA_PER_YEAR / fx * 1000.0 if price.claim == "equity" else 0.0
    life = len(case.schedule.periods)
    ga_pass = ga * pv_annuity(r, years_to_start + life)
    ga_fail = ga * pv_annuity(r, years_to_start)

    def q(spread: float) -> float:
        m = replace(base, discount_rate=r + spread)
        f = equity_frontier(
            case, m, timing, risks, financing, 1.0, max_delay=0, n_paths=N, seed=SEED
        )
        denominator = f.points[0].value_if_passed - ga_pass + ga_fail
        return (usd + ga_fail) / denominator if denominator > 0 else float("inf")

    return q, usd, ga_pass


def break_even(q: Callable[[float], float]) -> float:
    """Smallest spread at which the price implies certain passage (q = 1)."""
    lo, hi = 0.0, 0.6
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if q(mid) < 1 else (lo, mid)
    return 0.5 * (lo + hi)


def main() -> None:
    """Print the tables."""
    base = base_years()
    for years in (base, 1):
        label = "timing prior" if years == base else "company schedule"
        case, market, timing, risks, fx = setup(years)
        certain = replace(risks, stage_odds=1.0)
        res = simulate(case, market, timing, certain, n_paths=N, seed=SEED)
        v, se = res.estimate(res.project_value)
        print(
            f"\n## {years} years to Year -1 ({label})\nProject value if it passes every gate, "
            f"at the real rate {market.discount_rate:.2%}: "
            f"US${v / 1000:,.1f}M (se {se / 1000:.1f}); "
            f"gold US${market.gold_spot:,.2f}, US$1 = C${fx:.4f}"
        )
        grid = (0.0, 0.04, 0.08, 0.12, 0.15)
        for price in PRICES:
            q, usd, ga_pass = odds_function(price, years)
            r = market.discount_rate
            print(
                f"\n{price.label}: C${price.project_price_cad:.1f}M = US${usd / 1000:.1f}M "
                f"against the {price.claim} claim; PV of G&A on built paths "
                f"US${ga_pass / 1000:.1f}M"
            )
            print(
                " | ".join(f"{s:.0%}: {q(s):.2f}" if q(s) <= 1 else f"{s:.0%}: n/s" for s in grid)
            )
            print(f"Break-even spread: {break_even(q):.1%}")
            for name, rate in (("FS 5%", 0.05), ("FS 10%", 0.10)):
                value = q(rate - r)
                print(
                    f"  {name}: spread {rate - r:.1%}, odds {value:.2f}"
                    if value <= 1
                    else f"  {name}: spread {rate - r:.1%}, no solution"
                )


if __name__ == "__main__":
    main()

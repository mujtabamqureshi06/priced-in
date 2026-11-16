"""What the Osino prices imply for Twin Hills (ADRs 0031 to 0033).

Three prices, all with balance-sheet items from Osino's interim statements at
September 30, 2023 (the latest published before each date):

- the undisturbed market value on December 15, 2023, compared with the equity claim
  with dilution (ADR 0030), less corporate G&A (ADR 0033);
- Dundee Precious Metals' offer (December 18, 2023) and Shanjin's (February 23, 2024),
  compared with the project claim, since the acquirer funds construction (ADR 0031).

Each is shown as zero-delay implied odds against a real spread on net project cash
flows, with the break-even spread (ADR 0032). Third-party reference rates are read the
way their sources applied them: gold flat in real terms at the source's deck, or at
spot where none is stated, discounted at the rate (ADR 0045).

Usage: uv run python scripts/osino_prices.py
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from pricedin import defaults
from pricedin.engine import Financing, Market, Risks, simulate
from pricedin.inputs import load_case
from pricedin.inversion import equity_frontier, project_frontier
from pricedin.priors import load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 200_000, 1  # published tables (standard errors shown)
PRIORS = load_priors(ROOT / "data" / "priors.yaml")
TIMING = defaults.timing(PRIORS, "osino_twin_hills")
# Osino interim statements, Sept 30, 2023 (C$ million): cash, Nebari credit facility,
# leases, other financial liabilities (deferred consideration and leases).
NET_DEBT = 19.676 + 0.084 + 2.668 - 8.339
OPTIONS, OPTION_PRICE = 9.431, 1.02  # millions, C$ weighted average
WARRANTS, WARRANT_PRICE = 9.252, 1.28
BASIC_SHARES = 159.514
GA_PER_YEAR = 5.449 / 0.75  # nine-month corporate G&A, annualised (C$ million)
UNDISTURBED_PRICE = 1.553 / 1.372  # implied by DPM's stated 37.2% premium to the close
DFS_DECK = 1750.0  # US$/oz, Twin Hills DFS base case
EIGHT_CAPITAL_DECK = 1850.0  # US$/oz, Eight Capital fairness opinion (circular)
CIM_FS = 0.089  # CIM stage-based real rate for a feasibility-stage project


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


@dataclass(frozen=True)
class Reading:
    """Implied odds for one price, in either convention."""

    price: Price
    usd: float
    spot: float
    real_rate: float
    ga_pass: float

    def _odds(self, market: Market, ga_rate: float) -> tuple[float, float]:
        case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
        risks = Risks(overrun=defaults.overrun(PRIORS, case.study.stage), build_rule=True)
        equity = self.price.claim == "equity"
        financing = defaults.equity_financing(PRIORS) if equity else Financing()
        fx = load_snapshot(ROOT / "data" / "snapshots" / self.price.snapshot).value("usdcad")
        ga = GA_PER_YEAR / fx if equity else 0.0
        life = len(case.schedule.periods)
        ga_pass = ga * pv_annuity(ga_rate, TIMING.years_to_start + life)
        ga_fail = ga * pv_annuity(ga_rate, TIMING.years_to_start)
        if equity:
            f = equity_frontier(
                case, market, TIMING, risks, financing, 1.0, max_delay=0, n_paths=N, seed=SEED
            )
        else:
            f = project_frontier(
                case, market, TIMING, risks, 1.0, max_delay=0, n_paths=N, seed=SEED
            )
        p = f.points[0]
        denominator = p.value_if_passed - ga_pass + ga_fail
        q = (self.usd + ga_fail) / denominator if denominator > 0 else float("inf")
        return q, q * p.gate_odds_se / p.gate_odds

    def market_consistent(self, spread: float) -> tuple[float, float]:
        """Odds (and std. error) at a real spread over the risk-free rate."""
        snap = load_snapshot(ROOT / "data" / "snapshots" / self.price.snapshot)
        base = Market.from_snapshot(snap, convenience_yield=0.0)
        return self._odds(replace(base, discount_rate=self.real_rate + spread), self.real_rate)

    def convention(self, gold: float, rate: float) -> tuple[float, float]:
        """Odds with gold flat at ``gold`` and everything discounted at ``rate`` (ADR 0045)."""
        return self._odds(Market.flat(gold, rate), rate)


def reading(price: Price) -> Reading:
    """Set up the reading of one price."""
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / price.snapshot)
    fx, r = snap.value("usdcad"), snap.value("real_yield_10y")
    ga = GA_PER_YEAR / fx if price.claim == "equity" else 0.0
    ga_pass = ga * pv_annuity(r, TIMING.years_to_start + len(case.schedule.periods))
    return Reading(price, price.project_price_cad / fx, snap.value("gold_spot"), r, ga_pass)


def _fmt(q: float, se: float) -> str:
    return f"{q:.2f} ({se:.3f})" if q <= 1 else "no solution"


def main() -> None:
    """Print the tables."""
    grid = (0.0, 0.04, 0.08, 0.12, 0.15)
    for price in PRICES:
        rd = reading(price)
        print(
            f"\n{price.label}: C${price.project_price_cad:.1f}M = US${rd.usd:.1f}M "
            f"against the {price.claim} claim; PV of G&A on built paths US${rd.ga_pass:.1f}M"
        )
        print(
            "Market-consistent: "
            + " | ".join(f"{s:.0%}: {_fmt(*rd.market_consistent(s))}" for s in grid)
        )
        lo, hi = 0.0, 0.6
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if rd.market_consistent(mid)[0] < 1 else (lo, mid)
        print(f"Break-even spread: {0.5 * (lo + hi):.1%}")
        print("Reference rates, gold flat in real terms (ADR 0045):")
        for name, rate, gold, label in (
            ("DFS 5%", 0.05, DFS_DECK, "DFS deck"),
            ("Eight Capital 10.5%", 0.105, EIGHT_CAPITAL_DECK, "its deck"),
            ("Eight Capital 13.5%", 0.135, EIGHT_CAPITAL_DECK, "its deck"),
            ("Eight Capital 10.5%", 0.105, rd.spot, "spot"),
            ("Eight Capital 13.5%", 0.135, rd.spot, "spot"),
            ("Lopatnikov-Rumyantsev 16%", 0.16, rd.spot, "spot"),
        ):
            print(f"  {name}, gold at {label} US${gold:,.0f}: {_fmt(*rd.convention(gold, rate))}")
        case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
        risks = Risks(overrun=defaults.overrun(PRIORS, case.study.stage), build_rule=True)
        res = simulate(case, Market.flat(rd.spot, CIM_FS), TIMING, risks, n_paths=N, seed=SEED)
        v, se = res.estimate(res.project_value)
        print(
            f"  CIM FS-stage 8.9% (already includes development risk; value only, no odds): "
            f"US${v:,.1f}M (se {se:.1f}) at spot, against a price of US${rd.usd:,.1f}M"
        )


if __name__ == "__main__":
    main()

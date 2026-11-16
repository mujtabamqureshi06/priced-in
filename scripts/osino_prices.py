"""What the Osino prices imply for Twin Hills (ADRs 0031 to 0033).

Four prices, each with balance-sheet items from the last Osino statements published
before its date:

- the developer's market value around the DFS (July 13, 2023): the July 2023 trading
  range, March 31, 2023 statements, equity claim with dilution less corporate G&A;
- the undisturbed market value on December 15, 2023, September 30, 2023 statements,
  same claim;
- Dundee Precious Metals' offer (December 18, 2023) and Shanjin's (February 23, 2024),
  compared with the project claim, since the acquirer funds construction (ADR 0031).

Dilutive securities are counted series by series by the treasury method: a series
counts, and its exercise proceeds reduce net debt, when the share price is above its
strike. Restricted and deferred share units always count and bring no proceeds.

Each price is shown as zero-delay implied odds against a real spread on net project
cash flows, with the break-even spread (ADR 0032). Third-party reference rates are read
the way their sources applied them: gold flat in real terms at the source's deck, or at
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
DFS_DECK = 1750.0  # US$/oz, Twin Hills DFS base case
EIGHT_CAPITAL_DECK = 1850.0  # US$/oz, Eight Capital fairness opinion (circular)
CIM_FS = 0.089  # CIM stage-based real rate for a feasibility-stage project


@dataclass(frozen=True)
class BalanceSheet:
    """Osino's capital structure from one set of statements (C$ million, millions)."""

    label: str
    net_debt: float
    shares: float
    share_units: float  # RSUs and DSUs: always dilutive, no proceeds
    series: tuple[tuple[float, float], ...]  # (count, C$ strike) for options and warrants
    ga_per_year: float

    def diluted_shares(self, share_price: float) -> float:
        """Shares, share units and in-the-money option and warrant series."""
        itm = sum(n for n, k in self.series if share_price > k)
        return self.shares + self.share_units + itm

    def proceeds(self, share_price: float) -> float:
        """Exercise proceeds of the in-the-money series."""
        return sum(n * k for n, k in self.series if share_price > k)


# Interim statements at March 31, 2023 (published May 2023), with the subsequent events
# they disclose: 38,636 broker warrants exercised at C$1.10 on April 17, 2023, and the
# Nebari second tranche drawn in May 2023 (US$5M less a US$50,000 fee, so net debt rises
# by the fee only; its 1,233,737 warrants are at C$1.45). Net debt: Nebari facility
# 5.978 and accrued interest 0.288, leases 0.112, other financial liabilities 0.125,
# less cash 8.822 and the warrant proceeds 0.042, plus the fee. G&A: corporate G&A of
# C$1.725M for the quarter (MD&A, results of operations), annualised.
MARCH_2023 = BalanceSheet(
    label="March 31, 2023",
    net_debt=5.978 + 0.288 + 0.112 + 0.125 - 8.822 - 0.042 + 0.066,
    shares=158.202 + 0.039,
    share_units=2.675,
    series=((10.710, 0.94), (4.773, 1.35), (0.534, 1.10), (2.062, 0.88), (1.234, 1.45)),
    ga_per_year=1.725 * 4,
)
# Interim statements at September 30, 2023: cash 8.339, Nebari facility 19.676, leases
# 0.084, other financial liabilities 2.668; 2.912M RSUs and 0.111M DSUs; options at their
# C$1.02 weighted average; warrants by series (Note 8). G&A: C$5.449M for nine months
# (MD&A), annualised.
SEPTEMBER_2023 = BalanceSheet(
    label="September 30, 2023",
    net_debt=19.676 + 0.084 + 2.668 - 8.339,
    shares=159.514,
    share_units=2.912 + 0.111,
    series=((9.431, 1.02), (4.773, 1.35), (2.062, 0.88), (1.234, 1.46), (1.184, 1.53)),
    ga_per_year=5.449 / 0.75,
)
# Cash spent between March 31 and May 29, 2023, implied by the Q1 MD&A: about C$10.9M
# of cash at May 29 after drawing the second tranche (about C$6.7M), against C$8.8M at
# March 31. Approximate; used as a sensitivity only.
BURN_TO_MAY_2023 = 8.822 + 6.7 - 10.9


@dataclass(frozen=True)
class Price:
    """One observed price and how it maps to a claim."""

    label: str
    snapshot: str
    project_price_cad: float
    claim: str  # "project" or "equity"
    sheet: BalanceSheet


def market_value(label: str, snapshot: str, share_price: float, sheet: BalanceSheet) -> Price:
    """Developer market value: diluted equity plus net debt less exercise proceeds."""
    equity = share_price * sheet.diluted_shares(share_price)
    return Price(
        label, snapshot, equity + sheet.net_debt - sheet.proceeds(share_price), "equity", sheet
    )


def offer(
    label: str, snapshot: str, equity: float, share_price: float, sheet: BalanceSheet
) -> Price:
    """Takeover price: stated diluted equity plus net debt less exercise proceeds."""
    return Price(
        label, snapshot, equity + sheet.net_debt - sheet.proceeds(share_price), "project", sheet
    )


UNDISTURBED_PRICE = 1.553 / 1.372  # implied by DPM's stated 37.2% premium to the close
JULY_LOW, JULY_HIGH = 1.07, 1.20  # July 2023 TSXV range (March 25, 2024 circular, p. 97)

PRICES = (
    market_value("Market value at the DFS, July 2023 low", "2023-07-13.yaml", JULY_LOW, MARCH_2023),
    market_value(
        "Market value at the DFS, July 2023 high", "2023-07-13.yaml", JULY_HIGH, MARCH_2023
    ),
    market_value(
        "Undisturbed market value, 2023-12-15", "2023-12-15.yaml", UNDISTURBED_PRICE, SEPTEMBER_2023
    ),
    offer(
        "Dundee Precious Metals offer, 2023-12-18", "2023-12-18.yaml", 287.0, 1.553, SEPTEMBER_2023
    ),
    offer("Shanjin offer, 2024-02-23", "2024-02-23.yaml", 368.0, 1.90, SEPTEMBER_2023),
)
SENSITIVITIES = tuple(
    market_value(
        f"Sensitivity: July 2023 {name}, net debt after cash spent to May 29, 2023",
        "2023-07-13.yaml",
        price,
        replace(MARCH_2023, net_debt=MARCH_2023.net_debt + BURN_TO_MAY_2023),
    )
    for name, price in (("low", JULY_LOW), ("high", JULY_HIGH))
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
        ga = self.price.sheet.ga_per_year / fx if equity else 0.0
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
    ga = price.sheet.ga_per_year / fx if price.claim == "equity" else 0.0
    ga_pass = ga * pv_annuity(r, TIMING.years_to_start + len(case.schedule.periods))
    return Reading(price, price.project_price_cad / fx, snap.value("gold_spot"), r, ga_pass)


def _fmt(q: float, se: float) -> str:
    return f"{q:.2f} ({se:.3f})" if q <= 1 else "no solution"


def main() -> None:
    """Print the tables."""
    grid = (0.0, 0.04, 0.08, 0.12, 0.15)
    for price in PRICES + SENSITIVITIES:
        rd = reading(price)
        print(
            f"\n{price.label} ({price.sheet.label} statements): "
            f"C${price.project_price_cad:.1f}M = US${rd.usd:.1f}M "
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

"""Royalty cases on multi-metal schedules (WP 2.6, ADRs 0035 and 0036).

A royalty case values one royalty on a project whose construction decision has been made,
from the study's own annual table of revenue by metal. It is used where the full project
model (``pricedin.inputs`` and ``pricedin.engine``) does not apply: more than one priced
metal, a currency other than US$, or a study that publishes pre-tax figures only.

**Money.** The study table is in the operator's currency. Revenue for metal ``m`` in
period ``t`` is payable metal times the deck price in US$, converted at the deck exchange
rate. Multiplying back by that rate gives US$ revenue exactly, so a royalty valued in US$
needs no exchange-rate path:

    US$ revenue_m,t = revenue_m,t x fx_t x P_m,t / deck_m,t

Treatment and refining charges are set in US$ per tonne of concentrate and per ounce, so
they are converted the same way and held at the study schedule (they depend on volumes,
not prices). The net smelter return is US$ revenue of the covered metals less these
deductions.

**Value.** With the construction decision made, every path that reaches production pays
the royalty, so its value is linear in each metal price. Under market-consistent dynamics
(ADR 0012) the expected price at year t is ``spot x (1 + r)^t x e^(-y t)``; discounting at
``(1 + r + s)^t`` gives the closed form below, which a correlated Monte Carlo reproduces
(tested). Volatility and correlation do not change the value.

**Inversion.** Failing paths pay nothing (no advance royalties), so the implied odds of
reaching production on the schedule are ``price / V(d)`` for each added delay d.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Annotated

import numpy as np
import yaml
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pricedin.inputs import TOTAL_TOLERANCE, Column, Document, Quantity, SourceRef
from pricedin.inversion import Frontier, FrontierPoint
from pricedin.price_models import CorrelatedGBM

FloatArray = NDArray[np.float64]
NonEmpty = Annotated[str, Field(min_length=1)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RoyaltyStudy(_Strict):
    """The study the schedule comes from."""

    stage: NonEmpty
    document: NonEmpty
    effective_date: date
    still_applies: SourceRef | None = None
    npv_pre_tax: Quantity
    discount_rate: Quantity
    discounting_note: NonEmpty
    payable_metal: dict[str, Quantity] = {}
    inferred_share: Quantity | None = None


class Deck(_Strict):
    """The study's price deck by period, in US$, and its exchange rate."""

    basis: NonEmpty
    source: SourceRef
    units: dict[str, NonEmpty]
    prices: dict[str, tuple[float, ...]]
    usd_per_local: tuple[float, ...]
    treatment_charge: Quantity | None = None
    refining_charge: Quantity | None = None


class Status(_Strict):
    """Construction status at the valuation date."""

    construction_decision: bool
    financed: bool
    first_concentrate: NonEmpty
    source: SourceRef


class RoyaltySchedule(_Strict):
    """The study's annual table. Costs are positive numbers."""

    money_units: NonEmpty
    first_production_period: NonEmpty
    periods: tuple[NonEmpty, ...]
    columns: dict[str, Column]


class RoyaltyTerms(_Strict):
    """The royalty and the price paid for it."""

    holder: NonEmpty
    kind: Annotated[str, Field(pattern=r"^(NSR|GRR)$")]
    rate: Quantity
    coverage_fraction: Quantity
    price: Quantity
    metals: tuple[NonEmpty, ...]
    deductions: tuple[NonEmpty, ...] = ()
    notes: str = ""


class RoyaltyCase(_Strict):
    """One royalty, on one project, as of one valuation date."""

    id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    name: NonEmpty
    operator: NonEmpty
    jurisdiction: NonEmpty
    as_of: date
    documents: tuple[Document, ...]
    study: RoyaltyStudy
    deck: Deck
    status: Status
    schedule: RoyaltySchedule
    royalty: RoyaltyTerms

    @model_validator(mode="after")
    def _consistent(self) -> RoyaltyCase:
        docs = {d.id for d in self.documents}
        late = [d.id for d in self.documents if d.date > self.as_of]
        if late:
            raise ValueError(f"documents dated after {self.as_of} (ADR 0007): {late}")
        refs = [
            self.study.npv_pre_tax.source,
            self.study.discount_rate.source,
            self.deck.source,
            self.status.source,
            self.royalty.rate.source,
            self.royalty.coverage_fraction.source,
            self.royalty.price.source,
            *(c.source for c in self.schedule.columns.values()),
            *(q.source for q in self.study.payable_metal.values()),
        ]
        if self.study.still_applies is not None:
            refs.append(self.study.still_applies)
        unknown = sorted({r.document for r in refs} - docs)
        if unknown or self.study.document not in docs:
            raise ValueError(f"sources refer to unknown documents: {unknown}")
        n = len(self.schedule.periods)
        if self.schedule.first_production_period not in self.schedule.periods:
            raise ValueError("first_production_period is not a schedule period")
        series = {"usd_per_local": self.deck.usd_per_local, **self.deck.prices}
        for name, values in series.items():
            if len(values) != n:
                raise ValueError(f"deck '{name}' has {len(values)} values for {n} periods")
            if min(values) <= 0:
                raise ValueError(f"deck '{name}' must be positive")
        for name, col in self.schedule.columns.items():
            if len(col.values) != n:
                raise ValueError(f"column '{name}' has {len(col.values)} values for {n} periods")
            allowed = max(TOTAL_TOLERANCE, 0.5 * n) * col.resolution
            if col.total is not None and abs(sum(col.values) - col.total) > allowed:
                raise ValueError(f"column '{name}' does not add to its reported total")
        for metal in self.royalty.metals:
            if f"{metal}_revenue" not in self.schedule.columns or metal not in self.deck.prices:
                raise ValueError(f"metal '{metal}' needs a revenue column and a deck price")
        missing = set(self.royalty.deductions) - self.schedule.columns.keys()
        if missing:
            raise ValueError(f"deductions name unknown columns: {sorted(missing)}")
        return self

    def column(self, name: str) -> FloatArray:
        """One schedule row as an array."""
        return np.asarray(self.schedule.columns[name].values, dtype=np.float64)

    @property
    def first_production_index(self) -> int:
        """Index of the first production period in the schedule."""
        return self.schedule.periods.index(self.schedule.first_production_period)


def load_royalty_case(path: Path) -> RoyaltyCase:
    """Load and validate a royalty case file."""
    return RoyaltyCase.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class MetalsMarket:
    """Market-consistent inputs for several metals (ADR 0012).

    Attributes:
        spots: price of each metal at the valuation date, US$ per unit as in the deck.
        real_rate: real risk-free rate (fraction per year, annual compounding).
        convenience_yields: continuously compounded convenience yield of each metal.

    """

    spots: Mapping[str, float]
    real_rate: float
    convenience_yields: Mapping[str, float]

    def expected_price(self, metal: str, years: FloatArray) -> FloatArray:
        """Return the expected price under the pricing measure: spot x (1 + r)^t x e^(-y t)."""
        y = self.convenience_yields[metal]
        growth: FloatArray = (1.0 + self.real_rate) ** years * np.exp(-y * years)
        return self.spots[metal] * growth

    def drift(self, metal: str) -> float:
        """Continuously compounded drift: ln(1 + r) - y."""
        return float(np.log1p(self.real_rate)) - self.convenience_yields[metal]


def usd_nsr(
    case: RoyaltyCase,
    prices: Mapping[str, FloatArray],
    *,
    metals: Sequence[str] | None = None,
    deductions: Sequence[str] | None = None,
) -> FloatArray:
    """Net smelter return in US$ millions by period, for given US$ metal prices.

    Args:
        case: the royalty case.
        prices: price per metal, each broadcastable to ``(..., n_periods)``.
        metals: metals whose revenue counts; default the royalty's own.
        deductions: cost columns deducted; default the royalty's own.

    """
    metals = case.royalty.metals if metals is None else metals
    deductions = case.royalty.deductions if deductions is None else deductions
    fx = np.asarray(case.deck.usd_per_local, dtype=np.float64)
    total: FloatArray = np.zeros(len(case.schedule.periods))
    for metal in metals:
        deck = np.asarray(case.deck.prices[metal], dtype=np.float64)
        total = total + case.column(f"{metal}_revenue") * fx * np.asarray(prices[metal]) / deck
    for name in deductions:
        total = total - case.column(name) * fx
    return total


def payment_years(
    case: RoyaltyCase, years_to_first_production: int, added_delay: int
) -> FloatArray:
    """Years from the valuation date at which each period's royalty is paid (end of year)."""
    shift = years_to_first_production + added_delay - case.first_production_index
    return np.arange(len(case.schedule.periods), dtype=np.float64) + shift


def royalty_value(
    case: RoyaltyCase,
    market: MetalsMarket,
    *,
    years_to_first_production: int,
    spread: float,
    added_delay: int = 0,
    metals: Sequence[str] | None = None,
    deductions: Sequence[str] | None = None,
) -> float:
    """Value of the royalty in US$ millions if production follows the schedule (closed form).

    Periods before production carry no revenue, so their payment year does not matter.
    """
    years = payment_years(case, years_to_first_production, added_delay)
    used = case.royalty.metals if metals is None else metals
    expected = {m: market.expected_price(m, np.maximum(years, 0.0)) for m in used}
    nsr = usd_nsr(case, expected, metals=used, deductions=deductions)
    share = case.royalty.rate.value * case.royalty.coverage_fraction.value
    paid = years >= 0
    return float(np.sum(share * nsr[paid] / (1.0 + market.real_rate + spread) ** years[paid]))


def simulated_royalty_value(
    case: RoyaltyCase,
    market: MetalsMarket,
    volatilities: Mapping[str, float],
    correlation: Sequence[Sequence[float]],
    *,
    years_to_first_production: int,
    spread: float,
    n_paths: int = 20_000,
    seed: int = 0,
) -> tuple[float, float]:
    """Monte Carlo value and standard error with correlated GBM prices.

    A check on the closed form: the two agree within Monte Carlo error whatever the
    volatilities and correlation.
    """
    metals = case.royalty.metals
    years = payment_years(case, years_to_first_production, 0)
    horizon = int(np.max(years))
    model = CorrelatedGBM(
        spots=tuple(market.spots[m] for m in metals),
        drifts=tuple(market.drift(m) for m in metals),
        volatilities=tuple(volatilities[m] for m in metals),
        correlation=tuple(tuple(row) for row in correlation),
    )
    paths = model.simulate(horizon, n_paths, np.random.default_rng(seed))
    paid = years >= 0
    cols = years[paid].astype(int)
    prices = {}
    for i, m in enumerate(metals):
        full = np.ones((n_paths, len(years)))
        full[:, paid] = paths[i][:, cols]
        prices[m] = full
    nsr = usd_nsr(case, prices)
    share = case.royalty.rate.value * case.royalty.coverage_fraction.value
    discount = (1.0 + market.real_rate + spread) ** -years[paid]
    values = share * nsr[:, paid] @ discount
    return float(values.mean()), float(values.std(ddof=1) / np.sqrt(n_paths))


def odds_frontier(
    case: RoyaltyCase,
    market: MetalsMarket,
    *,
    years_to_first_production: int,
    spread: float,
    max_delay: int = 5,
    price: float | None = None,
    metals: Sequence[str] | None = None,
    deductions: Sequence[str] | None = None,
) -> Frontier:
    """Implied odds of reaching production for each added delay: price / V(d)."""
    p = case.royalty.price.value if price is None else price
    points = []
    for d in range(max_delay + 1):
        v = royalty_value(
            case,
            market,
            years_to_first_production=years_to_first_production,
            spread=spread,
            added_delay=d,
            metals=metals,
            deductions=deductions,
        )
        q = p / v if v > 0 else float("inf")
        points.append(
            FrontierPoint(
                added_delay=d,
                gate_odds=q,
                gate_odds_se=0.0,
                build_probability=q,
                value_if_passed=v,
                value_if_failed=0.0,
            )
        )
    return Frontier(price=p, points=tuple(points))


def break_even_spread(
    case: RoyaltyCase,
    market: MetalsMarket,
    *,
    years_to_first_production: int,
    price: float | None = None,
    lo: float = 0.0,
    hi: float = 0.5,
    metals: Sequence[str] | None = None,
    deductions: Sequence[str] | None = None,
) -> float | None:
    """Spread at which the price equals the certain, on-schedule value (ADR 0028).

    Returns None if the price is outside the values at ``lo`` and ``hi`` (for example,
    above the value even at a zero spread).
    """
    p = case.royalty.price.value if price is None else price

    def gap(s: float) -> float:
        v = royalty_value(
            case,
            market,
            years_to_first_production=years_to_first_production,
            spread=s,
            metals=metals,
            deductions=deductions,
        )
        return v - p

    g_lo, g_hi = gap(lo), gap(hi)
    if g_lo * g_hi > 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        g_mid = gap(mid)
        if g_lo * g_mid <= 0:
            hi = mid
        else:
            lo, g_lo = mid, g_mid
        if hi - lo < 1e-7:
            break
    return 0.5 * (lo + hi)


def pre_tax_npv(case: RoyaltyCase, rate: float, *, mid_year: bool = True) -> float:
    """Study pre-tax NPV from the net cash-flow row, discounted from the first period.

    Used only to reconcile the transcription with the study's reported NPV, whose timing
    convention is not stated.
    """
    t = np.arange(len(case.schedule.periods), dtype=np.float64) + (0.5 if mid_year else 0.0)
    return float(case.column("net_cash_flow") @ (1.0 + rate) ** -t)

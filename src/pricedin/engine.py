"""Simulation engine: many futures of one case, and the value of each claim on them.

One run draws, for every path:

1. a gold price path (``pricedin.price_models.GBM``);
2. whether the project passes its remaining stage gates (one combined Bernoulli draw
   with the cumulative odds the caller supplies from ``data/priors.yaml``, ADR 0013);
3. a capital cost ratio (ADR 0015), applied to initial and expansion capital;
4. the build year, from the fixed build rule (#59): from the build-ready year the
   project is built in the first year its NPV at that year's gold price, at the study's
   capital estimate and discount rate, clears the hurdle; it never sees the overrun draw
   (ADR 0015). Paths that never clear it before the window closes are not built.

It then values, on the same paths:

- the **project**: after-tax cash flow in the case's money units, discounted at the
  valuation rate from the valuation date;
- a **royalty**, when one is given: rate x coverage x gold revenue, plus advance minimum
  royalties under the ADR 0021 rules, discounted at the valuation rate plus the buyer's
  spread (ADR 0014). Advances are paid at the end of each year before the first
  production year; on paths that fail a gate they stop at the build-ready year, and on
  paths the build rule never builds they stop when the window closes.

Every switch can be turned off. With all risks off, a flat study deck, the study's
discount rate and no delay, the project value equals the study NPV exactly; this is the
first step of the waterfall and is tested.

Simplifications, stated:

- Time is in whole years. The study's first schedule period falls ``years_to_start`` years
  after the valuation date when there is no delay. Cash flows are discounted on the
  study's own convention (``pricedin.project.period_times``); prices are sampled at the
  whole year of each period.
- A path that fails a stage gate fails at the build-ready year.
- The extra capital from an overrun carries no tax shield. This understates value
  slightly on overrun paths.
- Ramp-up (ADR 0019) is not yet applied; outputs label it "not modelled".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

import pricedin
from pricedin import lsm
from pricedin.inputs import Case
from pricedin.price_models import GBM
from pricedin.priors import ShiftedLognormal
from pricedin.project import period_times, schedule_cash_flows
from pricedin.snapshots import Snapshot

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class Market:
    """Price dynamics and the valuation rate for one valuation.

    Attributes:
        gold_spot: gold price at the valuation date, real US$/oz.
        drift: continuously compounded annual drift of the gold price. Market-consistent
            mode uses ln(1 + real rate) less the convenience yield (ADR 0012).
        volatility: annual volatility of log gold returns; 0 gives a deterministic path.
        discount_rate: annual rate used to discount project cash flows (real).

    """

    gold_spot: float
    drift: float
    volatility: float
    discount_rate: float

    def __post_init__(self) -> None:
        """Reject a non-positive price, negative volatility or a rate at or below -100%."""
        if not self.gold_spot > 0:
            raise ValueError(f"gold_spot must be positive, got {self.gold_spot}")
        if self.volatility < 0:
            raise ValueError(f"volatility must be non-negative, got {self.volatility}")
        if not self.discount_rate > -1.0:
            raise ValueError(f"discount_rate must be above -1, got {self.discount_rate}")

    @classmethod
    def flat(cls, price: float, rate: float) -> Market:
        """Convention valuation (ADR 0045): the metal flat in real terms at ``price``.

        This is how a stated real rate is applied by its source: a flat price deck, no
        volatility, cash flows discounted at that rate. Use it to read a price at a
        third-party reference rate. The spread curve and break-even spread stay in
        market-consistent mode. For a pure revenue claim with zero convenience yield
        the two agree when the market-consistent spread is ``rate * (1 + r)``.
        """
        return cls(gold_spot=price, drift=0.0, volatility=0.0, discount_rate=rate)

    @classmethod
    def market_consistent(
        cls, gold_spot: float, real_rate: float, convenience_yield: float, volatility: float
    ) -> Market:
        """Risk-neutral gold dynamics discounted at the real risk-free rate (ADR 0012)."""
        return cls(
            gold_spot=gold_spot,
            drift=float(np.log1p(real_rate)) - convenience_yield,
            volatility=volatility,
            discount_rate=real_rate,
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: Snapshot,
        *,
        convenience_yield: float,
        rate_key: str = "real_yield_10y",
        vol_key: str = "realised_vol_10y",
    ) -> Market:
        """Market-consistent inputs from a dated snapshot (ADR 0024 defaults)."""
        return cls.market_consistent(
            gold_spot=snapshot.value("gold_spot"),
            real_rate=snapshot.value(rate_key),
            convenience_yield=convenience_yield,
            volatility=snapshot.value(vol_key),
        )

    @classmethod
    def study_deck(cls, case: Case) -> Market:
        """Use the study's own flat price and discount rate (the reconciliation setting)."""
        return cls(
            gold_spot=case.study.price_deck["gold"].value,
            drift=0.0,
            volatility=0.0,
            discount_rate=case.study.discount_rate.value,
        )


@dataclass(frozen=True)
class Timing:
    """When the project can be built, in whole years after the valuation date.

    Attributes:
        years_to_start: years until the study's first schedule period with no delay.
        added_delay: further years of delay (the inversion's timing dimension).
        max_wait: years the build rule may defer construction after the build-ready year.
        failure_after_delay: if False (default, ADR 0025), a path that fails a stage
            gate fails at the base year (``years_to_start``), so added delay applies
            only to paths that pass. True is the named sensitivity "failure discovered
            at the delayed date".

    """

    years_to_start: int = 0
    added_delay: int = 0
    max_wait: int = 0
    failure_after_delay: bool = False

    def __post_init__(self) -> None:
        """Reject negative or fractional years."""
        for name in ("years_to_start", "added_delay", "max_wait"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | np.integer):
                raise ValueError(f"{name} must be a whole number of years, got {value!r}")
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")

    @property
    def build_ready(self) -> int:
        """First year in which construction can start."""
        return self.years_to_start + self.added_delay


@dataclass(frozen=True)
class Overrun:
    """Capital cost ratio: ``real_factor * (shift + lognormal)`` per path (ADR 0015)."""

    ratio: ShiftedLognormal
    real_factor: float


@dataclass(frozen=True)
class Risks:
    """Which risks are on, and their parameters.

    Attributes:
        stage_odds: probability of passing every remaining stage gate (1.0 = off).
        overrun: capital cost ratio distribution, or None for no overrun.
        build_rule: apply the price-dependent build decision (#59); if False, every
            path that passes its gates builds in the build-ready year.
        build_hurdle: NPV the project must reach, at the decision rate and the current
            gold price, for the rule to build (case money units).
        decision_rate: discount rate the build rule uses; None means the study's own
            rate (ADR 0023). Used by the fixed rule only.
        build_decision: "fixed" applies the hurdle rule above (ADR 0023); "lsm" builds
            when the market-consistent value of building now is at least the fitted
            value of waiting, by least-squares Monte Carlo (ADR 0038). Only used when
            ``build_rule`` is true.
        lsm_degree: polynomial degree of the LSM regression basis in the gold price.
        lsm_rate: real rate the LSM decision discounts at; None means the valuation
            rate. Setting it to the study's rate gives both rules the same decision rate
            (ADR 0038).
        holding_cost: real cost per year, in case money units, paid by the project at the
            end of each year that construction is deferred beyond ``years_to_start`` (ADR
            0049). Zero by default: no sourced figure exists. It lowers the project and
            equity claims, not the royalty or stream. The build decision does not include it.

    """

    stage_odds: float = 1.0
    overrun: Overrun | None = None
    build_rule: bool = False
    build_hurdle: float = 0.0
    decision_rate: float | None = None
    build_decision: Literal["fixed", "lsm"] = "fixed"
    lsm_degree: int = 3
    lsm_rate: float | None = None
    holding_cost: float = 0.0

    def __post_init__(self) -> None:
        """Reject odds outside [0, 1] and a negative holding cost."""
        if not 0.0 <= self.stage_odds <= 1.0:
            raise ValueError(f"stage_odds must be in [0, 1], got {self.stage_odds}")
        if self.holding_cost < 0.0:
            raise ValueError(f"holding_cost must be non-negative, got {self.holding_cost}")


@dataclass(frozen=True)
class RoyaltyClaim:
    """A royalty on gold revenue, with advance minimum royalties (ADR 0021).

    Attributes:
        rate: royalty rate as a fraction of revenue.
        coverage: fraction of the mine plan's gold the royalty covers (ADR 0016).
        amr_per_year: advance minimum royalty per year before production, a fixed nominal
            amount converted to the case's money units at the valuation-date exchange
            rate.
        amr_credited: whether paid advances are recovered from later royalty payments.
        spread: buyer's required spread over the valuation rate (ADR 0014).
        amr_inflation: annual inflation used to turn the fixed nominal advance into real
            terms (ADR 0021); 0 treats it as real. Credited advances are recovered as
            the same nominal total, so their real value falls with the recovery year.

    """

    rate: float
    coverage: float
    amr_per_year: float = 0.0
    amr_credited: bool = True
    spread: float = 0.0
    amr_inflation: float = 0.0

    def __post_init__(self) -> None:
        """Reject fractions outside [0, 1] and negative advances."""
        for name in ("rate", "coverage"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"royalty {name} must be a fraction in [0, 1], got {value}")
        if self.amr_per_year < 0:
            raise ValueError(f"amr_per_year must be non-negative, got {self.amr_per_year}")


@dataclass(frozen=True)
class StreamClaim:
    """A precious-metal stream on gold (#80).

    The holder receives ``share`` of payable gold and pays, per ounce, the lesser of
    the transfer price and the spot price, the standard ongoing-payment term. Each
    delivered ounce is therefore worth max(P - c, 0): the stream is a strip of call
    options on gold (Fuller 2023). The upfront deposit is the price being read and is
    not modelled as a cash flow.

    Attributes:
        share: fraction of payable gold delivered to the holder.
        transfer_price: ongoing payment per ounce at the valuation date, real US$/oz.
        transfer_escalation: real annual growth of the transfer price (0 if it is fixed
            in real terms; negative if it is fixed in nominal terms).
        spread: holder's required spread over the valuation rate (ADR 0014).

    """

    share: float
    transfer_price: float
    transfer_escalation: float = 0.0
    spread: float = 0.0

    def __post_init__(self) -> None:
        """Reject a share outside [0, 1] or a negative transfer price."""
        if not 0.0 <= self.share <= 1.0:
            raise ValueError(f"stream share must be a fraction in [0, 1], got {self.share}")
        if self.transfer_price < 0:
            raise ValueError(f"transfer_price must be non-negative, got {self.transfer_price}")


#: Case money units per (thousand ounces x US$/oz), i.e. per US$ thousand.
_PER_US_THOUSAND = {"US$ thousands": 1.0, "US$ millions": 1e-3}


def fixed_nominal_advance(
    amount: float, fx: float, nominal_rate: float, real_rate: float, money_scale: float
) -> tuple[float, float]:
    """Return engine inputs for a fixed nominal advance in a foreign currency (ADR 0024).

    A fixed nominal stream in currency C is worth its payments discounted at C's nominal
    rate and converted at spot (covered interest parity). The engine discounts advances
    at the real rate after deflating them, so the deflator that reproduces the nominal
    discount is ``(1 + nominal_rate) / (1 + real_rate) - 1``.

    Args:
        amount: advance per year in currency C (e.g. 120,000 C$).
        fx: units of C per US$ on the valuation date.
        nominal_rate: C's nominal government yield on the valuation date.
        real_rate: the valuation's real rate.
        money_scale: US$ per case money unit (1,000 for US$ thousands).

    Returns:
        ``(amr_per_year, amr_inflation)`` for ``RoyaltyClaim``.

    """
    return amount / fx / money_scale, (1.0 + nominal_rate) / (1.0 + real_rate) - 1.0


@dataclass(frozen=True)
class Financing:
    """How the operator funds initial capital, for the equity claim (#61, ADR 0030).

    Debt is raised at fair value, so it transfers no value. The equity-funded part of
    each year's initial capital (actual capital, overrun included, less the debt share
    of the study estimate) is raised at a discount ``issue_discount`` to fair value,
    which transfers ``E x d / (1 - d)`` to the new investors.

    Attributes:
        debt_fraction: share of the study's initial capital estimate funded by debt.
        issue_discount: discount of the equity issue price to fair value.

    """

    debt_fraction: float = 0.0
    issue_discount: float = 0.0

    def __post_init__(self) -> None:
        """Reject values outside their ranges."""
        if not 0.0 <= self.debt_fraction <= 1.0:
            raise ValueError("debt_fraction must be in [0, 1]")
        if not 0.0 <= self.issue_discount < 1.0:
            raise ValueError("issue_discount must be in [0, 1)")


@dataclass(frozen=True)
class Results:
    """Per-path outcomes and values. Values are present values at the valuation date."""

    project_value: FloatArray
    royalty_value: FloatArray | None
    advance_value: FloatArray | None
    equity_value: FloatArray | None
    passed_gates: BoolArray
    built: BoolArray
    build_year: IntArray
    seed: int
    n_paths: int
    stream_value: FloatArray | None = None
    version: str = field(default=pricedin.__version__)

    @property
    def window_expired_share(self) -> float:
        """Share of paths that pass every gate but are never built (ADR 0023)."""
        return float((self.passed_gates & ~self.built).mean())

    @property
    def advance_share(self) -> float | None:
        """Share of royalty value that comes from advance minimum royalties."""
        if self.royalty_value is None or self.advance_value is None:
            return None
        total = float(self.royalty_value.sum())
        return float(self.advance_value.sum()) / total if total else None

    @staticmethod
    def estimate(values: FloatArray) -> tuple[float, float]:
        """Mean and Monte Carlo standard error."""
        if values.size < 2:
            return float(values.mean()), 0.0
        return float(values.mean()), float(values.std(ddof=1) / np.sqrt(values.size))


def _discount(rate: float, years: FloatArray) -> FloatArray:
    factors: FloatArray = (1.0 + rate) ** -years
    return factors


def _decision_npv(case: Case, price: FloatArray, rate: float) -> FloatArray:
    """Project NPV at the decision rate with each path's price held flat."""
    n = len(case.schedule.periods)
    flat = np.repeat(price[:, None], n, axis=1)
    cf = schedule_cash_flows(case, flat)
    values: FloatArray = cf.after_tax @ _discount(rate, period_times(case))
    return values


def _build_value(case: Case, market: Market, price: FloatArray, rate: float) -> FloatArray:
    """Market-consistent value, at the build year, of building now at gold price ``price``.

    Expected prices from the build year follow the market drift; after-tax cash flows
    at study capital (the decision never sees the overrun draw, ADR 0015) are discounted
    at ``rate``. Using the expected price path ignores the convexity the tax
    floor adds; this is stated in ADR 0038.
    """
    n = len(case.schedule.periods)
    t = np.arange(n, dtype=np.float64)
    path = price[:, None] * np.exp(market.drift * t)[None, :]
    cf = schedule_cash_flows(case, path)
    values: FloatArray = cf.after_tax @ _discount(rate, period_times(case))
    return values


def mean_overrun_ratio(risks: Risks) -> float:
    """Return the expected capital cost ratio of the overrun prior, computed analytically.

    ``real_factor * (shift + exp(mu + sigma**2 / 2))``; 1.0 with no overrun. The build
    decision uses this mean, never a path's draw (ADR 0015 rule 3, ADR 0059).
    """
    if risks.overrun is None:
        return 1.0
    r = risks.overrun.ratio
    return float(risks.overrun.real_factor * (r.shift + np.exp(r.mu + 0.5 * r.sigma**2)))


def _gate_costs(case: Case, market: Market, risks: Risks, financing: Financing | None) -> float:
    """Return the expected overrun and dilution costs at the build year, at the market rate.

    Subtracted from ``_build_value`` to give the decision-time value C of building
    (ADR 0059): (mean ratio - 1) x PV of initial and expansion capital, plus, when the
    run includes a ``Financing``, d / (1 - d) x PV of the equity raise at the mean ratio.
    Both are present values at the build year on the study's own timing.
    """
    cols = case.schedule.columns
    initial = np.asarray(cols["initial_capex"].values, dtype=np.float64)
    capex = initial.copy()
    if "expansion_capex" in cols:
        capex = capex + np.asarray(cols["expansion_capex"].values, dtype=np.float64)
    m = mean_overrun_ratio(risks)
    disc = _discount(market.discount_rate, period_times(case))
    cost = (m - 1.0) * float(capex @ disc)
    if financing is not None:
        raised = np.maximum(m * initial - financing.debt_fraction * initial, 0.0)
        d = financing.issue_discount
        cost += float((raised * d / (1.0 - d)) @ disc)
    return cost


def _decision_value(
    case: Case,
    market: Market,
    price: FloatArray,
    rate: float,
    gate_cost: float,
) -> FloatArray:
    """Decision-time value C of building now at ``price``: build value less expected costs."""
    values: FloatArray = _build_value(case, market, price, rate) - gate_cost
    return values


def _lsm_build_years(
    case: Case,
    market: Market,
    timing: Timing,
    risks: Risks,
    prices: FloatArray,
    passes: BoolArray,
    rng: np.random.Generator,
    gate_cost: float = 0.0,
) -> IntArray:
    """Build year per path from a least-squares Monte Carlo rule (ADR 0038).

    The rule is fitted on independent paths, so a path's own future prices never
    inform its decision, then applied to the valuation paths. Decision dates run from
    the build-ready year to the end of the window; a path that never builds gets -1.
    """
    first, last = timing.build_ready, timing.build_ready + timing.max_wait
    start = max(first - 1, 0)

    def window(p: FloatArray) -> FloatArray:
        cols = p[:, start : last + 1]
        if first == 0:  # a dummy time-0 column so that the first decision is a step
            cols = np.concatenate([p[:, :1], cols], axis=1)
        return cols

    rate = market.discount_rate if risks.lsm_rate is None else risks.lsm_rate

    def payoff(k: int, state: FloatArray) -> FloatArray:
        return np.maximum(_decision_value(case, market, state, rate, gate_cost), 0.0)

    fit_paths = GBM(market.gold_spot, market.drift, market.volatility).simulate(
        last, prices.shape[0], rng
    )
    discount = 1.0 / (1.0 + rate)
    rule = lsm.fit_rule(window(fit_paths), payoff, discount, degree=risks.lsm_degree)
    _, step = lsm.apply_rule(rule, window(prices[:, : last + 1]), payoff, discount)
    build_year = np.where((step > 0) & passes, first - 1 + step, -1)
    return np.asarray(build_year, dtype=np.int64)


def simulate(
    case: Case,
    market: Market,
    timing: Timing,
    risks: Risks,
    *,
    royalty: RoyaltyClaim | None = None,
    stream: StreamClaim | None = None,
    financing: Financing | None = None,
    n_paths: int = 10_000,
    seed: int = 0,
) -> Results:
    """Run the engine on one case. See the module docstring for the steps."""
    t0 = case.schedule.periods.index(case.study.discounting.t0_column)
    if t0 != 0:
        raise ValueError("the study's t0 period must be the first schedule period")
    n_periods = len(case.schedule.periods)
    horizon = timing.build_ready + timing.max_wait + n_periods

    price_rng, gate_rng, overrun_rng, fit_rng = (
        np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(4)
    )
    prices = GBM(market.gold_spot, market.drift, market.volatility).simulate(
        horizon, n_paths, price_rng
    )

    decision_rate = (
        case.study.discount_rate.value if risks.decision_rate is None else risks.decision_rate
    )
    passes = gate_rng.random(n_paths) < risks.stage_odds
    build_year = np.full(n_paths, -1, dtype=np.int64)
    candidates = (
        range(timing.build_ready, timing.build_ready + timing.max_wait + 1)
        if risks.build_rule
        else range(timing.build_ready, timing.build_ready + 1)
    )
    # Decision-time gate (ADR 0059): with the build rule on, a path builds only if the
    # value of building now, net of the expected overrun and (for an equity run) the
    # expected dilution, is non-negative. Limited liability is applied here, once, at
    # the decision; it is not applied to realised outcomes.
    gate_cost = _gate_costs(case, market, risks, financing) if risks.build_rule else 0.0
    if risks.build_rule and risks.build_decision == "lsm":
        build_year = _lsm_build_years(
            case, market, timing, risks, prices, passes, fit_rng, gate_cost
        )
        candidates = range(0)
    for k in candidates:
        waiting = passes & (build_year < 0)
        if not waiting.any():
            break
        if risks.build_rule:
            ok = np.zeros(n_paths, dtype=bool)
            ok[waiting] = (
                _decision_npv(case, prices[waiting, k], decision_rate) >= risks.build_hurdle
            ) & (
                _decision_value(case, market, prices[waiting, k], market.discount_rate, gate_cost)
                >= 0.0
            )
        else:
            ok = waiting
        build_year[ok] = k
    built = build_year >= 0

    if risks.overrun is not None:
        lognormal = np.exp(
            overrun_rng.normal(risks.overrun.ratio.mu, risks.overrun.ratio.sigma, n_paths)
        )
        ratio = risks.overrun.real_factor * (risks.overrun.ratio.shift + lognormal)
    else:
        ratio = np.ones(n_paths)
    cols = case.schedule.columns
    capex = np.asarray(cols["initial_capex"].values, dtype=np.float64)
    if "expansion_capex" in cols:
        capex = capex + np.asarray(cols["expansion_capex"].values, dtype=np.float64)

    project_value = np.zeros(n_paths)
    equity_value = np.zeros(n_paths) if financing is not None else None
    initial = np.asarray(cols["initial_capex"].values, dtype=np.float64)
    royalty_value = np.zeros(n_paths) if royalty is not None else None
    stream_value = np.zeros(n_paths) if stream is not None else None
    advance_value = np.zeros(n_paths) if royalty is not None else None
    periods = np.arange(n_periods)
    times = period_times(case)
    # Holding cost (ADR 0049): paid at the end of each year of deferral beyond the base
    # year, until construction, the close of the build window, or a failed gate.
    fail_year = timing.build_ready if timing.failure_after_delay else timing.years_to_start
    hold_end = np.where(
        built, build_year, np.where(passes, timing.build_ready + timing.max_wait, fail_year)
    )
    holding = np.zeros(n_paths)
    if risks.holding_cost > 0.0:
        for end in np.unique(hold_end):
            n_hold = int(end) - timing.years_to_start
            if n_hold > 0:
                hold_years = np.arange(timing.years_to_start + 1, int(end) + 1, dtype=np.float64)
                pv = risks.holding_cost * float(_discount(market.discount_rate, hold_years).sum())
                holding[hold_end == end] = pv
    project_value -= holding
    if equity_value is not None:
        # Unbuilt paths: the equity claim bears the holding cost like the project
        # (ADR 0049); with no holding cost it is zero.
        equity_value -= case.operator_share * holding

    for b in np.unique(build_year[built]):
        idx = np.flatnonzero(build_year == b)
        path_prices = prices[np.ix_(idx, b + periods)]
        cf = schedule_cash_flows(case, path_prices)
        after_tax = cf.after_tax - (ratio[idx, None] - 1.0) * capex
        years = b + times
        project_value[idx] = after_tax @ _discount(market.discount_rate, years) - holding[idx]
        if financing is not None and equity_value is not None:
            raised = np.maximum(ratio[idx, None] * initial - financing.debt_fraction * initial, 0.0)
            d = financing.issue_discount
            transfer = (raised * d / (1.0 - d)) @ _discount(market.discount_rate, years)
            # No per-path floor (ADR 0059, superseding ADR 0047): holders commit at the
            # build decision, before the overrun and later prices are known, so a single
            # built path can carry negative equity. Limited liability is applied at the
            # decision by the gate above.
            equity_value[idx] = case.operator_share * (project_value[idx] - transfer)
        if stream is not None and stream_value is not None:
            stream_value[idx] = _stream_pv(case, stream, path_prices, years, market.discount_rate)
        if royalty is not None and royalty_value is not None and advance_value is not None:
            gold = np.asarray(cols["gold_revenue"].values, dtype=np.float64)
            gold_rev = gold * path_prices / case.study.price_deck["gold"].value
            payments = royalty.rate * royalty.coverage * gold_rev
            first_revenue = int(np.flatnonzero(gold > 0)[0])
            n_advances = max(0, int(b) + first_revenue - 1)
            royalty_value[idx] = _royalty_pv(
                payments, years, n_advances, royalty, market.discount_rate
            )
            advance_value[idx] = _advances_pv(n_advances, royalty, market.discount_rate)

    if royalty is not None and royalty_value is not None and advance_value is not None:
        unbuilt = ~built
        end = np.where(passes, timing.build_ready + timing.max_wait, fail_year)
        for n_adv in np.unique(end[unbuilt]):
            idx = np.flatnonzero(unbuilt & (end == n_adv))
            royalty_value[idx] = _advances_pv(int(n_adv), royalty, market.discount_rate)
            advance_value[idx] = royalty_value[idx]

    return Results(
        project_value=project_value,
        royalty_value=royalty_value,
        stream_value=stream_value,
        advance_value=advance_value,
        equity_value=equity_value,
        passed_gates=passes,
        built=built,
        build_year=build_year,
        seed=seed,
        n_paths=n_paths,
    )


def _stream_pv(
    case: Case, stream: StreamClaim, prices: FloatArray, years: FloatArray, rate: float
) -> FloatArray:
    """Present value of stream deliveries on built paths, in the case's money units."""
    units = case.schedule.money_units
    if units not in _PER_US_THOUSAND:
        raise ValueError(f"streams need a US$ case, got money units '{units}'")
    ounces = np.asarray(case.schedule.columns["payable_gold_koz"].values, dtype=np.float64)
    transfer = stream.transfer_price * (1.0 + stream.transfer_escalation) ** years
    margin = np.maximum(prices - transfer[None, :], 0.0)
    flows = stream.share * ounces[None, :] * margin * _PER_US_THOUSAND[units]
    pv: FloatArray = flows @ _discount(rate + stream.spread, years)
    return pv


def _advances_pv(n_advances: int, royalty: RoyaltyClaim, rate: float) -> float:
    """Present value of advance payments at the end of years 1..n_advances."""
    if n_advances <= 0 or royalty.amr_per_year == 0.0:
        return 0.0
    years = np.arange(1, n_advances + 1, dtype=np.float64)
    real = royalty.amr_per_year * _discount(royalty.amr_inflation, years)
    return float(real @ _discount(rate + royalty.spread, years))


def _royalty_pv(
    payments: FloatArray,
    years: FloatArray,
    n_advances: int,
    royalty: RoyaltyClaim,
    rate: float,
) -> FloatArray:
    """Present value of royalty payments plus advances, with optional crediting.

    Advances are paid at the end of years 1..n_advances (until production starts).
    If credited, their nominal total is recovered from the first royalty payments.
    """
    paid = payments.copy()
    if royalty.amr_credited and n_advances > 0:
        nominal_left = np.full(paid.shape[0], royalty.amr_per_year * n_advances)
        for t in range(paid.shape[1]):
            index = (1.0 + royalty.amr_inflation) ** years[t]
            take = np.minimum(nominal_left / index, paid[:, t])
            paid[:, t] -= take
            nominal_left -= take * index
    pv: FloatArray = paid @ _discount(rate + royalty.spread, years)
    return pv + _advances_pv(n_advances, royalty, rate)

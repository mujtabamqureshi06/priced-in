"""Phase 6 deal pricer: one royalty or stream deal's price range (protocol 8.2 to 8.4, 8.6).

This module turns a deal's study schedule and terms into a range of values, with no deal
price anywhere in it. It holds only methods; the inputs for real deals are transcribed
separately (``docs/phase6/protocol.md`` section 8.8, step 4) and nothing here reads them.

Steps, each a function below:

1. **Decision distribution (8.2).** A stage's Kaplan-Meier cumulative incidence F(t) of a
   construction decision, at 12, 24, 36 and 60 months after the study (ADR 0068), is read
   linearly between those points with F(0) = 0. Beyond 60 months F is extended at the
   constant hazard implied between 36 and 60 months. For a deal ``a`` months after its
   study, P(decision by t) = (F(t) - F(a)) / (1 - F(a)) for t in [a, a + 60]. The window
   is split into yearly probabilities; the remainder is "no decision in the window". A
   decision already made puts probability 1 at year 0.
2. **Value given the decision year (8.4, ``methodology.md`` section 8, ADR 0041).** Gold
   is risk-neutral geometric Brownian motion (``engine.Market.market_consistent``, zero
   convenience yield by default, ADR 0024). Cash flows are discounted at the real rate
   plus the drawn spread, compounded annually as in the engine. Decisions are drawn
   independently of gold (8.2), so the value is the probability-weighted sum, over
   decision years, of the value given that year. Royalties linear in price use
   E[P_t] = S exp(drift t); a stream paying the lesser of a fixed price and spot, and an
   NSR royalty with offsite costs per ounce, are strips of Black calls on the forward.
   Only path-dependent terms (a cap on cumulative payments, advances credited in money)
   use Monte Carlo, and then each draw's standard error must be under 1% of its value.
3. **Spread (8.3, ADR 0045).** A disclosed rate is made real, then turned into a spread
   by s = k(1 + r). The prior weights each company equally and splits a company's weight
   evenly across its rows; a row "x% to y%" contributes both ends.
4. **Draws (8.4).** 2,000 joint draws, each pairing a spread from the prior with one
   cluster-bootstrap replicate of the stage incidence (the deal's project left out).
   The range is the 10th to 90th percentile of the draw values; the centre is the median.
5. **Contingent amounts (8.6 sensitivity).** The expected present value of a payment
   triggered by a construction decision or first production within the window,
   discounted at the real risk-free rate from the trigger date.

Conventions, stated:

- Time is in years from the deal date. A decision in window year k (k = 1..5) is dated
  at the end of that year, t = k; a decision already made is dated t = 0. Production
  starts ``preproduction_years`` after the decision. The payment for production year j
  falls at decision + preproduction + (j - 1) + ``period_offset`` (1 = end of year).
- Advance minimum royalties (ADR 0021, ADR 0072) are paid at the end of each whole
  year from the deal date up to the start of production; with no decision in the
  window they stop when the window closes.
- Ounce quantities are in the schedule's unit (ounces or thousand ounces); money amounts
  (advances, caps, values) are in that unit times US$ per ounce.
- Terms the module does not implement raise ``NotImplementedError``; such a deal is "not
  priced" (8.4). It is never approximated.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.special import ndtr  # type: ignore[import-untyped]

from pricedin.engine import Market
from pricedin.stage_table import HORIZONS, cluster_bootstrap, cumulative_incidence

FloatArray = NDArray[np.float64]

#: Build window after the deal date, in years (protocol 8.2).
WINDOW_YEARS = 5
#: Months per year, for converting the table's horizons.
MONTHS_PER_YEAR = 12
#: Decision to first production when the study states none, in years (8.2; ADR 0063 item 2).
DEFAULT_PREPRODUCTION_YEARS = 1.0
#: Joint draws of spread and incidence per deal (8.4 step 2).
N_DRAWS = 2_000
#: Largest Monte Carlo standard error allowed, as a share of the value (8.4 step 3).
MAX_RELATIVE_SE = 0.01
#: Percentiles of the draw values reported: the 80% range and its centre (8.4 step 4).
PERCENTILES = (10.0, 50.0, 90.0)
#: Minimum spread set for an interval score: rates and companies (8.3).
MIN_RATES, MIN_COMPANIES = 8, 4
#: Default Monte Carlo paths for path-dependent terms; raised if the SE test fails.
DEFAULT_PATHS = 20_000

_LAST = float(HORIZONS[-1])  # 60 months
_HAZARD_FROM = float(HORIZONS[-2])  # 36 months


# --------------------------------------------------------------------------------------
# 1. Decision distribution (8.2)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Incidence:
    """Cumulative incidence of a construction decision at 12, 24, 36 and 60 months.

    Attributes:
        values: F at the horizons of ``stage_table.HORIZONS`` (months after the study),
            fractions in [0, 1], non-decreasing.

    """

    values: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        """Reject missing, out-of-range or decreasing values."""
        v = np.asarray(self.values, dtype=float)
        if v.shape != (len(HORIZONS),):
            raise ValueError(f"incidence needs {len(HORIZONS)} values, got {v.shape}")
        if np.isnan(v).any():
            raise ValueError(f"incidence has a missing value (no subject followed): {v}")
        if (v < 0).any() or (v > 1).any():
            raise ValueError(f"incidence values must be in [0, 1], got {v}")
        if (np.diff(v) < -1e-12).any():
            raise ValueError(f"incidence must be non-decreasing, got {v}")

    @classmethod
    def from_array(cls, values: Sequence[float] | FloatArray) -> Incidence:
        """Build from any sequence of four floats."""
        a, b, c, d = (float(x) for x in values)
        return cls((a, b, c, d))

    def monthly_hazard(self) -> float:
        """Constant hazard per month implied between 36 and 60 months (8.2).

        Returns ``inf`` when nothing survives to 60 months.
        """
        s36, s60 = 1.0 - self.values[2], 1.0 - self.values[3]
        if s60 <= 0.0:
            return float("inf")
        return float(np.log(s36 / s60) / (_LAST - _HAZARD_FROM))

    def cdf(self, months: float | Sequence[float] | FloatArray) -> FloatArray:
        """F(t) at ``months`` after the study.

        Linear between (0, 0) and the table's points; beyond 60 months the survival
        1 - F decays at the 36-to-60-month constant hazard (8.2).
        """
        t = np.atleast_1d(np.asarray(months, dtype=float))
        if (t < 0).any():
            raise ValueError(f"months must be non-negative, got {t}")
        knots = np.concatenate([[0.0], np.asarray(HORIZONS, dtype=float)])
        vals = np.concatenate([[0.0], np.asarray(self.values, dtype=float)])
        out = np.interp(t, knots, vals)
        beyond = t > _LAST
        if beyond.any():
            s60 = 1.0 - self.values[3]
            h = self.monthly_hazard()
            surv = 0.0 if not np.isfinite(h) else s60 * np.exp(-h * (t[beyond] - _LAST))
            out[beyond] = 1.0 - surv
        result: FloatArray = np.asarray(out, dtype=np.float64)
        return result


@dataclass(frozen=True)
class DecisionTiming:
    """Probabilities of a construction decision by year of the window after the deal.

    Attributes:
        probs: probability that the decision falls in year k, for k = 0..window_years.
            Year 0 is "decision already made" (probability 1 or 0); year k >= 1 is the
            k-th year after the deal date.
        needs_extension: whether the window reaches beyond 60 months after the study, so
            the constant-hazard extension is used (reported per 8.2).
        already_decided: whether a decision was already made at the deal date.

    """

    probs: FloatArray
    needs_extension: bool
    already_decided: bool

    @property
    def window_years(self) -> int:
        """Length of the window in years."""
        return int(self.probs.size - 1)

    @property
    def p_decision(self) -> float:
        """Probability of a decision within the window (at most 1)."""
        return float(self.probs.sum())

    @property
    def p_none(self) -> float:
        """Probability of no decision within the window."""
        return max(0.0, 1.0 - self.p_decision)

    def scenario_probs(self) -> FloatArray:
        """Probabilities over decision years 0..W followed by "no decision"."""
        out: FloatArray = np.append(self.probs, self.p_none)
        return out


def decision_timing(
    incidence: Incidence | None,
    age_months: float,
    *,
    already_decided: bool = False,
    window_years: int = WINDOW_YEARS,
) -> DecisionTiming:
    """Yearly decision probabilities over the window, conditional on the deal's age.

    Args:
        incidence: the stage's cumulative incidence; may be None only when
            ``already_decided``.
        age_months: months from the study date to the deal date (>= 0).
        already_decided: documents dated on or before the announcement show a
            construction decision on the covered ground; probability 1 at year 0.
        window_years: window length in years (5 in the primary run, 10 in a 8.7
            sensitivity).

    Returns:
        ``DecisionTiming`` with P(year k) = G(a + 12k) - G(a + 12(k - 1)), where
        G(t) = (F(t) - F(a)) / (1 - F(a)) (protocol 8.2).

    """
    if window_years < 1:
        raise ValueError(f"window_years must be at least 1, got {window_years}")
    if not age_months >= 0.0:
        raise ValueError(f"age_months must be non-negative, got {age_months}")
    extension = age_months + window_years * MONTHS_PER_YEAR > _LAST
    if already_decided:
        probs = np.zeros(window_years + 1)
        probs[0] = 1.0
        return DecisionTiming(probs, needs_extension=False, already_decided=True)
    if incidence is None:
        raise ValueError("incidence is required unless the decision was already made")
    edges = age_months + MONTHS_PER_YEAR * np.arange(window_years + 1, dtype=float)
    f = incidence.cdf(edges)
    if f[0] >= 1.0:
        raise ValueError(
            f"F({age_months:.1f} months) = 1: the stage table gives no undecided projects "
            "at this age, so the conditional window is undefined"
        )
    g = (f - f[0]) / (1.0 - f[0])
    probs = np.concatenate([[0.0], np.diff(g)])
    return DecisionTiming(np.asarray(probs, dtype=np.float64), extension, False)


def stage_incidence(time: FloatArray, event: NDArray[np.bool_]) -> Incidence:
    """Kaplan-Meier cumulative incidence at 12, 24, 36 and 60 months (Phase 5 table)."""
    return Incidence.from_array(cumulative_incidence(time, event, HORIZONS))


def leave_project_out(
    time: FloatArray,
    event: NDArray[np.bool_],
    cluster: Sequence[str],
    project: str | None,
) -> Incidence:
    """Stage incidence with every entry of ``project`` removed (8.2).

    ``cluster`` holds each entry's project; linked components carry their group's id,
    as in ``scripts/phase5_stage_table.py``, so they are removed with it. ``None`` removes
    nothing (the deal's project is not in the Phase 5 frame).
    """
    keep = _keep_mask(cluster, project, len(time))
    return stage_incidence(np.asarray(time)[keep], np.asarray(event)[keep])


def incidence_replicates(
    time: FloatArray,
    event: NDArray[np.bool_],
    cluster: Sequence[str],
    *,
    n_boot: int,
    seed: int,
    exclude_project: str | None = None,
) -> FloatArray:
    """Cluster-bootstrap replicates of the stage incidence over projects (8.4 step 2).

    Uses ``stage_table.cluster_bootstrap``, as the Phase 5 table does. The deal's own
    project is removed first. A replicate in which no entry is followed to a horizon has
    NaN at that horizon; ``price_range`` rejects such a replicate with an error.

    Returns:
        Array of shape ``(n_boot, 4)``: F at 12, 24, 36 and 60 months per replicate.

    """
    keep = _keep_mask(cluster, project=exclude_project, n=len(time))
    t = np.asarray(time, dtype=float)[keep]
    e = np.asarray(event, dtype=bool)[keep]
    keys = [c for c, k in zip(cluster, keep, strict=True) if k]
    if not keys:
        raise ValueError("no entries left after removing the deal's project")
    return cluster_bootstrap(
        keys, lambda idx: cumulative_incidence(t[idx], e[idx], HORIZONS), n_boot, seed
    )


def _keep_mask(cluster: Sequence[str], project: str | None, n: int) -> NDArray[np.bool_]:
    if len(cluster) != n:
        raise ValueError(f"cluster has {len(cluster)} entries, time has {n}")
    keys = np.asarray(cluster, dtype=object)
    mask: NDArray[np.bool_] = (
        np.ones(n, dtype=bool) if project is None else np.asarray(keys != project, dtype=bool)
    )
    return mask


# --------------------------------------------------------------------------------------
# 2. Terms and value given the decision year (8.4)
# --------------------------------------------------------------------------------------

BuyBack = Literal["none", "fair_market_value", "fixed_price"]


@dataclass(frozen=True)
class RateStep:
    """A royalty rate that applies once cumulative covered ounces reach a threshold.

    Attributes:
        threshold: cumulative covered production, in schedule ounce units, from the
            start of production, at which ``rate`` starts to apply.
        rate: royalty rate from the threshold on (0 caps the royalty in ounces).

    """

    threshold: float
    rate: float


@dataclass(frozen=True)
class DeliveryStep:
    """A stream delivery share that applies once cumulative ounces reach a threshold.

    Attributes:
        threshold: cumulative ounces (delivered or produced, per the stream's
            ``step_basis``) at which ``share`` starts to apply.
        share: fraction of covered payable gold delivered from the threshold on (0 caps
            deliveries).

    """

    threshold: float
    share: float


@dataclass(frozen=True)
class AdvanceMinimum:
    """Advance minimum royalty (ADR 0021; ADR 0072 item 3 for payments in ounces).

    Attributes:
        amount: payment per year before production; money units if ``unit`` is
            "money" (fixed in nominal terms, deflated by the royalty's ``inflation``),
            ounces of gold if "ounces" (valued at the expected gold price).
        unit: "money" or "ounces".
        credited: whether paid advances are recovered from later royalty payments. Money
            advances are recovered as the same nominal total from the first payments
            (path-dependent, Monte Carlo); ounce advances are recovered from the first
            royalty ounces (deterministic, closed form).
        max_years: number of yearly payments the terms allow, if they state one.
        max_total: total of advance payments the terms allow (in ``unit``), if stated;
            the last payment is reduced to stay within it.

    """

    amount: float
    unit: Literal["money", "ounces"] = "money"
    credited: bool = True
    max_years: int | None = None
    max_total: float | None = None


@dataclass(frozen=True)
class RoyaltyTerms:
    """Terms of a gold royalty for the Phase 6 pricer.

    Attributes:
        rate: royalty rate at the start of production, fraction of revenue.
        kind: "NSR" (net smelter return) or "GRR" (gross revenue).
        coverage: share of the study schedule the royalty covers (8.4 step 1).
        offsite_cost_per_oz: NSR deductions, real US$ per ounce. None for an NSR means
            gross revenue, flagged as an upper bound (8.4 step 1). Ignored for a GRR.
        steps: rate changes after cumulative covered ounces, in increasing threshold.
        cap: cap on cumulative payments to the holder (advances included), fixed in
            nominal money units; path-dependent, valued by Monte Carlo.
        advance: advance minimum royalty, if any.
        inflation: annual inflation turning fixed nominal amounts (advances, cap) into
            real terms; 0 treats them as real. Phase 6 passes the deal-date breakeven
            inflation from the snapshot (the country's own rate for a non-US$ amount where
            the snapshot has one, otherwise the US rate, flagged by the caller).
        buyback: "fair_market_value" is ignored (no effect on value); "fixed_price" is
            ignored with a flag, which overstates value slightly (8.4).
        other_terms: any further term, named. A non-empty tuple raises
            ``NotImplementedError``: the deal is not priced.
        step_basis: "covered" when the terms say thresholds count covered ounces;
            "unspecified" when the terms do not say which ounces count, so the deal is
            not priced (the transcriber does not choose).

    """

    rate: float
    kind: Literal["NSR", "GRR"] = "NSR"
    coverage: float = 1.0
    offsite_cost_per_oz: float | None = None
    steps: tuple[RateStep, ...] = ()
    cap: float | None = None
    advance: AdvanceMinimum | None = None
    inflation: float = 0.0
    buyback: BuyBack = "none"
    other_terms: tuple[str, ...] = ()
    step_basis: Literal["covered", "unspecified"] = "covered"

    def __post_init__(self) -> None:
        """Validate fractions, amounts and the order of steps."""
        _fraction("royalty rate", self.rate)
        _fraction("royalty coverage", self.coverage)
        if self.kind not in ("NSR", "GRR"):
            raise ValueError(f"royalty kind must be 'NSR' or 'GRR', got {self.kind!r}")
        if self.offsite_cost_per_oz is not None and self.offsite_cost_per_oz < 0:
            raise ValueError(f"offsite_cost_per_oz must be >= 0, got {self.offsite_cost_per_oz}")
        for s in self.steps:
            _fraction("step rate", s.rate)
        _check_thresholds([s.threshold for s in self.steps])
        if self.cap is not None and not self.cap > 0:
            raise ValueError(f"cap must be positive, got {self.cap}")
        if self.advance is not None and self.advance.amount < 0:
            raise ValueError(f"advance amount must be >= 0, got {self.advance.amount}")
        if self.advance is not None and self.advance.unit not in ("money", "ounces"):
            raise ValueError(f"advance unit must be 'money' or 'ounces', got {self.advance.unit}")
        if not self.inflation > -1.0:
            raise ValueError(f"inflation must be above -1, got {self.inflation}")
        _check_buyback(self.buyback)


@dataclass(frozen=True)
class StreamTerms:
    """Terms of a gold stream for the Phase 6 pricer (ADR 0041).

    Attributes:
        share: fraction of covered payable gold delivered at the start of production.
        payment: ongoing payment per delivered ounce:
            "lesser_of_fixed_and_spot" (min(c, P): a strip of calls, ADR 0041);
            "share_of_spot" (``spot_share`` x P); "fixed" (c regardless of spot).
        fixed_price: c at the deal date, US$/oz (nominal if ``inflation`` > 0).
        escalation: annual growth of the fixed price in the contract's terms.
        escalation_from: when escalation starts: "deal" (the deal date, as
            ``engine.StreamClaim``) or "production" (first production).
        inflation: annual inflation deflating a nominal fixed price; 0 treats it as real
            (a price fixed in nominal terms then needs ``inflation`` > 0).
        spot_share: holder's payment as a fraction of spot, for "share_of_spot".
        coverage: share of the study schedule the stream covers.
        steps: delivery-share changes after cumulative ounces, increasing threshold.
        step_basis: whether step thresholds count "delivered" or "produced" ounces.
        buyback: as for royalties.
        other_terms: any further term, named; non-empty raises ``NotImplementedError``.

    """

    share: float
    payment: Literal["lesser_of_fixed_and_spot", "share_of_spot", "fixed"]
    fixed_price: float = 0.0
    escalation: float = 0.0
    escalation_from: Literal["deal", "production"] = "deal"
    inflation: float = 0.0
    spot_share: float = 0.0
    coverage: float = 1.0
    steps: tuple[DeliveryStep, ...] = ()
    step_basis: Literal["delivered", "produced", "unspecified"] = "delivered"
    buyback: BuyBack = "none"
    other_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate fractions, prices and the order of steps."""
        _fraction("stream share", self.share)
        _fraction("stream coverage", self.coverage)
        _fraction("stream spot_share", self.spot_share)
        if self.payment not in ("lesser_of_fixed_and_spot", "share_of_spot", "fixed"):
            raise ValueError(f"unknown stream payment {self.payment!r}")
        if self.fixed_price < 0:
            raise ValueError(f"fixed_price must be >= 0, got {self.fixed_price}")
        if self.escalation_from not in ("deal", "production"):
            raise ValueError(
                f"escalation_from must be 'deal' or 'production', not {self.escalation_from}"
            )
        if self.step_basis not in ("delivered", "produced", "unspecified"):
            raise ValueError(
                "step_basis must be 'delivered', 'produced' or 'unspecified', "
                f"not {self.step_basis}"
            )
        if not self.inflation > -1.0 or not self.escalation > -1.0:
            raise ValueError("inflation and escalation must be above -1")
        for s in self.steps:
            _fraction("step share", s.share)
        _check_thresholds([s.threshold for s in self.steps])
        _check_buyback(self.buyback)


Claim = RoyaltyTerms | StreamTerms


def _fraction(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be a fraction in [0, 1], got {value}")


def _check_thresholds(thresholds: Sequence[float]) -> None:
    t = np.asarray(thresholds, dtype=float)
    if (t < 0).any() or (np.diff(t) <= 0).any():
        raise ValueError(f"step thresholds must be non-negative and increasing, got {t}")


def _check_buyback(buyback: str) -> None:
    if buyback not in ("none", "fair_market_value", "fixed_price"):
        raise ValueError(
            f"buyback must be 'none', 'fair_market_value' or 'fixed_price', not {buyback}"
        )


def check_implemented(claim: Claim) -> tuple[str, ...]:
    """Raise for terms the pricer does not implement; return the flags the terms carry.

    Raises:
        NotImplementedError: the claim has a term listed in ``other_terms``. The deal is
            "not priced" (protocol 8.4): it is counted and reported, never approximated.

    """
    if claim.other_terms:
        raise NotImplementedError(
            "not priced: term(s) not implemented in the Phase 6 pricer: "
            + "; ".join(claim.other_terms)
            + " (protocol 8.4: such a deal is counted and reported, never approximated)"
        )
    has_steps = bool(claim.steps)
    if claim.step_basis == "unspecified" and has_steps:
        raise NotImplementedError(
            "not priced: the terms do not say which ounces count toward a threshold"
        )
    flags: list[str] = []
    if claim.buyback == "fixed_price":
        flags.append("fixed-price buy-back ignored (overstates value slightly)")
    if claim.buyback == "fair_market_value":
        flags.append("buy-back at fair market value ignored (no effect on value)")
    if isinstance(claim, RoyaltyTerms):
        if claim.kind == "NSR" and claim.offsite_cost_per_oz is None:
            flags.append("NSR valued on gross revenue: no offsite costs stated (upper bound)")
    elif claim.payment in ("lesser_of_fixed_and_spot", "fixed") and claim.fixed_price > 0:
        flags.append("spread conversion approximate (fixed-price stream, protocol 8.3)")
    return tuple(flags)


def _stepped_weights(
    ounces: FloatArray, base: float, steps: Sequence[tuple[float, float]]
) -> FloatArray:
    """Integral of a step function of cumulative ounces over each year's production.

    ``steps`` are (threshold, level) pairs on cumulative ``ounces``; the level is
    ``base`` below the first threshold. A threshold crossed inside a year splits that
    year's ounces pro rata.
    """
    edges = np.concatenate([[0.0], np.cumsum(ounces)])
    bounds = np.array([0.0, *[t for t, _ in steps], np.inf])
    levels = np.array([base, *[lv for _, lv in steps]])
    out = np.zeros(ounces.size)
    for lo, hi, lv in zip(bounds[:-1], bounds[1:], levels, strict=True):
        overlap = np.clip(np.minimum(edges[1:], hi) - np.maximum(edges[:-1], lo), 0.0, None)
        out += lv * overlap
    return out


def _delivered_to_produced(base: float, steps: Sequence[DeliveryStep]) -> list[tuple[float, float]]:
    """Convert thresholds on cumulative delivered ounces to thresholds on produced ounces."""
    out: list[tuple[float, float]] = []
    produced, delivered, share = 0.0, 0.0, base
    for s in steps:
        if share <= 0.0:
            break  # deliveries have stopped; later thresholds are never reached
        produced += (s.threshold - delivered) / share
        delivered = s.threshold
        share = s.share
        out.append((produced, share))
    return out


def claim_ounces(claim: Claim, schedule: FloatArray) -> FloatArray:
    """Ounce weights per production year after coverage and step-downs.

    For a royalty, the rate-weighted covered ounces (royalty ounces); for a stream, the
    delivered ounces. Thresholds count covered production (royalty) or, for a stream,
    delivered or produced ounces as its ``step_basis`` states.
    """
    covered = np.asarray(schedule, dtype=float) * claim.coverage
    if (covered < 0).any():
        raise ValueError("schedule ounces must be non-negative")
    if isinstance(claim, RoyaltyTerms):
        return _stepped_weights(covered, claim.rate, [(s.threshold, s.rate) for s in claim.steps])
    steps: list[tuple[float, float]]
    if claim.step_basis == "produced":
        steps = [(s.threshold, s.share) for s in claim.steps]
    else:
        steps = _delivered_to_produced(claim.share, claim.steps)
    return _stepped_weights(covered, claim.share, steps)


def _black_call(forward: FloatArray, strike: FloatArray, vol: float, t: FloatArray) -> FloatArray:
    """E[max(P_t - K, 0)] for lognormal P_t with mean ``forward`` (Black 1976)."""
    forward = np.asarray(forward, dtype=float)
    strike = np.broadcast_to(np.asarray(strike, dtype=float), forward.shape)
    sd = vol * np.sqrt(np.broadcast_to(np.asarray(t, dtype=float), forward.shape))
    intrinsic = np.maximum(forward - strike, 0.0)
    out = intrinsic.copy()
    live = (sd > 0) & (strike > 0)
    if live.any():
        f, k, s = forward[live], strike[live], sd[live]
        d1 = (np.log(f / k) + 0.5 * s * s) / s
        out[live] = f * ndtr(d1) - k * ndtr(d1 - s)
    result: FloatArray = np.asarray(out, dtype=np.float64)
    return result


def _strike(claim: StreamTerms, t: FloatArray, production_start: float) -> FloatArray:
    """Real fixed price per ounce at times ``t``."""
    start = 0.0 if claim.escalation_from == "deal" else production_start
    esc = (1.0 + claim.escalation) ** np.maximum(t - start, 0.0)
    real: FloatArray = claim.fixed_price * esc / (1.0 + claim.inflation) ** t
    return real


@dataclass(frozen=True)
class CashFlowModel:
    """Expected real cash flows of a claim by decision scenario, on a common time grid.

    Scenarios are the decision years 0..W followed by "no decision in the window". A
    draw's value is sum over scenarios and times of p_scenario x mean x discount factor,
    which is exact because decisions are independent of gold (8.2).

    Attributes:
        times: payment times in years from the deal date, increasing.
        mean: expected real cash flow, shape ``(W + 2, len(times))``.
        cov: covariance of the per-path cash flows across all (scenario, time) cells, for
            the Monte Carlo standard error; None in closed form.
        n_paths: Monte Carlo paths (0 in closed form).
        real_rate: the market's real rate, the base of discounting.
        flags: labels the terms and inputs carry (8.2 to 8.4).

    """

    times: FloatArray
    mean: FloatArray
    cov: FloatArray | None
    n_paths: int
    real_rate: float
    flags: tuple[str, ...]

    def value(self, scenario_probs: FloatArray, spread: float) -> tuple[float, float]:
        """Value and Monte Carlo standard error at ``spread`` for scenario weights."""
        p = np.asarray(scenario_probs, dtype=float)
        if p.shape != (self.mean.shape[0],):
            raise ValueError(f"need {self.mean.shape[0]} scenario probabilities, got {p.shape}")
        rate = self.real_rate + spread
        if not rate > -1.0:
            raise ValueError(f"real rate plus spread must be above -1, got {rate}")
        disc = (1.0 + rate) ** -self.times
        w = (p[:, None] * disc[None, :]).ravel()
        value = float(w @ self.mean.ravel())
        if self.cov is None:
            return value, 0.0
        var = float(w @ self.cov @ w) / self.n_paths
        return value, float(np.sqrt(max(var, 0.0)))


def market_inputs(
    gold_spot: float, real_rate: float, volatility: float, convenience_yield: float = 0.0
) -> Market:
    """Market-consistent gold at the announcement date (ADR 0024: y = 0 by default)."""
    return Market.market_consistent(gold_spot, real_rate, convenience_yield, volatility)


def cash_flow_model(
    claim: Claim,
    schedule: Sequence[float] | FloatArray,
    market: Market,
    *,
    preproduction_years: float | None = None,
    window_years: int = WINDOW_YEARS,
    period_offset: float = 1.0,
    decision_point: float = 0.5,
    n_paths: int = DEFAULT_PATHS,
    seed: int = 0,
) -> CashFlowModel:
    """Build the expected cash flows of a royalty or stream by decision year (8.4).

    Args:
        claim: royalty or stream terms.
        schedule: the study's annual payable gold for the covered ground, by production
            year (schedule mode), before the coverage share.
        market: gold dynamics and real rate; use ``market_inputs`` (market-consistent)
            in the primary run. ``Market.flat(spot, 0.0)`` with the drawn rate k passed
            as the spread gives the 8.3 flat-deck sensitivity.
        preproduction_years: decision to first production from the study; None uses one
            year, flagged (8.2).
        window_years: build window in years.
        period_offset: where in each production year the payment falls (1 = end, the
            primary run, matching study convention; 0.5 is the mid-year sensitivity).
        decision_point: where in window year k >= 1 a decision is dated: at
            t = k - 1 + decision_point (0.5 = mid-year, the primary run; 1 = end of year,
            a sensitivity). A decision already made is dated at t = 0.
        n_paths: Monte Carlo paths, used only for path-dependent terms.
        seed: Monte Carlo seed (ADR 0011).

    Raises:
        NotImplementedError: a term the pricer does not implement (deal not priced).

    """
    flags = list(check_implemented(claim))
    if preproduction_years is None:
        preproduction_years = DEFAULT_PREPRODUCTION_YEARS
        flags.append("pre-production period not stated: one year assumed")
    if preproduction_years < 0:
        raise ValueError(f"preproduction_years must be >= 0, got {preproduction_years}")
    if not 0.0 < period_offset <= 1.0:
        raise ValueError(f"period_offset must be in (0, 1], got {period_offset}")
    if not 0.0 < decision_point <= 1.0:
        raise ValueError(f"decision_point must be in (0, 1], got {decision_point}")
    sched = np.asarray(schedule, dtype=float)
    if sched.ndim != 1 or sched.size == 0:
        raise ValueError("schedule must be a non-empty 1-d sequence of annual ounces")
    weights = claim_ounces(claim, sched)
    n_prod = sched.size

    k_years = np.arange(window_years + 1, dtype=float)
    decisions = np.where(k_years > 0, k_years - 1.0 + decision_point, 0.0)
    starts = decisions + preproduction_years
    prod_times = starts[:, None] + np.arange(n_prod)[None, :] + period_offset
    # Advances: end of each whole year up to production start; window close if undecided.
    adv_counts = [int(np.floor(s + 1e-9)) for s in starts] + [window_years]
    adv = claim.advance if isinstance(claim, RoyaltyTerms) else None
    if adv is not None and adv.max_years is not None:
        adv_counts = [min(c, adv.max_years) for c in adv_counts]
    if adv is not None and adv.max_total is not None and adv.amount > 0:
        full = int(np.ceil(adv.max_total / adv.amount - 1e-12))
        adv_counts = [min(c, full) for c in adv_counts]

    def adv_amounts(n: int) -> FloatArray:
        """Advance payments in years 1..n, the last cut to respect ``max_total``."""
        assert adv is not None
        out = np.full(n, adv.amount, dtype=float)
        if adv.max_total is not None and n > 0:
            out[-1] = min(adv.amount, adv.max_total - adv.amount * (n - 1))
        return out

    adv_times = np.arange(1, max(adv_counts) + 1, dtype=float) if adv is not None else np.zeros(0)
    times = np.unique(np.round(np.concatenate([prod_times.ravel(), adv_times]), 9))
    n_scen = window_years + 2

    def col(t: FloatArray) -> NDArray[np.intp]:
        return np.searchsorted(times, np.round(t, 9))

    path_dependent = isinstance(claim, RoyaltyTerms) and (
        claim.cap is not None or (adv is not None and adv.unit == "money" and adv.credited)
    )
    if not path_dependent:
        mean = np.zeros((n_scen, times.size))
        for k in range(n_scen):
            w = weights
            n_adv = adv_counts[k]
            if adv is not None and n_adv > 0:
                t_adv = np.arange(1, n_adv + 1, dtype=float)
                amounts = adv_amounts(n_adv)
                if adv.unit == "money":
                    mean[k, col(t_adv)] += amounts / (1.0 + claim.inflation) ** t_adv
                else:
                    forward = market.gold_spot * np.exp(market.drift * t_adv)
                    mean[k, col(t_adv)] += amounts * forward
                    if adv.credited:
                        w = _credit_ounces(w, float(amounts.sum()))
            if k == n_scen - 1:
                continue  # no decision in the window: advances only
            t = prod_times[k]
            mean[k, col(t)] += w * _per_ounce_mean(claim, market, t, starts[k])
        return CashFlowModel(times, mean, None, 0, market.discount_rate, tuple(flags))

    assert isinstance(claim, RoyaltyTerms)
    flags.append(f"Monte Carlo ({n_paths} paths) for path-dependent terms")
    prices = _gbm_at(market, times, n_paths, np.random.default_rng(seed))
    deflator = (1.0 + claim.inflation) ** times
    blocks = []
    for k in range(n_scen):
        nominal = np.zeros((n_paths, times.size))
        n_adv = adv_counts[k]
        credit = np.zeros(n_paths)
        if adv is not None and n_adv > 0:
            idx = col(np.arange(1, n_adv + 1, dtype=float))
            amounts = adv_amounts(n_adv)
            if adv.unit == "money":
                nominal[:, idx] += amounts
                if adv.credited:
                    credit += float(amounts.sum())
            else:
                nominal[:, idx] += amounts * prices[:, idx] * deflator[idx]
        w = weights
        if adv is not None and adv.unit == "ounces" and adv.credited and n_adv > 0:
            w = _credit_ounces(w, float(adv_amounts(n_adv).sum()))
        if k < n_scen - 1:
            idx = col(prod_times[k])
            nominal[:, idx] += w * _per_ounce_paths(claim, prices[:, idx]) * deflator[idx]
            first_royalty = int(idx[0])
            for j in range(first_royalty, times.size):  # credited money advances
                take = np.minimum(credit, nominal[:, j])
                nominal[:, j] -= take
                credit -= take
        if claim.cap is not None:
            paid = np.cumsum(nominal, axis=1)
            allowed = np.minimum(paid, claim.cap)
            nominal = np.diff(np.concatenate([np.zeros((n_paths, 1)), allowed], axis=1), axis=1)
        blocks.append(nominal / deflator)
    stacked = np.concatenate(blocks, axis=1)
    mean = stacked.mean(axis=0).reshape(n_scen, times.size)
    cov = np.atleast_2d(np.cov(stacked, rowvar=False))
    return CashFlowModel(times, mean, cov, n_paths, market.discount_rate, tuple(flags))


def _credit_ounces(weights: FloatArray, total: float) -> FloatArray:
    """Recover ``total`` advance ounces from the first royalty ounces."""
    out = weights.copy()
    left = total
    for j in range(out.size):
        take = min(left, out[j])
        out[j] -= take
        left -= take
    return out


def _per_ounce_mean(claim: Claim, market: Market, t: FloatArray, start: float) -> FloatArray:
    """Closed-form expected real value per claim ounce at times ``t``."""
    forward = market.gold_spot * np.exp(market.drift * t)
    if isinstance(claim, RoyaltyTerms):
        if claim.kind == "GRR" or claim.offsite_cost_per_oz is None:
            return forward
        cost = np.full(t.shape, claim.offsite_cost_per_oz)
        return _black_call(forward, cost, market.volatility, t)
    if claim.payment == "share_of_spot":
        result: FloatArray = (1.0 - claim.spot_share) * forward
        return result
    strike = _strike(claim, t, start)
    if claim.payment == "fixed":
        fixed: FloatArray = forward - strike
        return fixed
    return _black_call(forward, strike, market.volatility, t)


def _per_ounce_paths(claim: RoyaltyTerms, prices: FloatArray) -> FloatArray:
    """Real value per royalty ounce on simulated paths."""
    if claim.kind == "GRR" or claim.offsite_cost_per_oz is None:
        return prices
    net: FloatArray = np.maximum(prices - claim.offsite_cost_per_oz, 0.0)
    return net


def _gbm_at(
    market: Market, times: FloatArray, n_paths: int, rng: np.random.Generator
) -> FloatArray:
    """Exact GBM gold prices at increasing ``times`` (the engine's dynamics)."""
    dt = np.diff(np.concatenate([[0.0], times]))
    z = rng.standard_normal((n_paths, times.size))
    vol = market.volatility
    steps = (market.drift - 0.5 * vol * vol) * dt + vol * np.sqrt(dt) * z
    paths: FloatArray = market.gold_spot * np.exp(np.cumsum(steps, axis=1))
    return paths


# --------------------------------------------------------------------------------------
# 3. Spread (8.3, ADR 0045)
# --------------------------------------------------------------------------------------


def real_from_nominal(nominal: float, inflation: float) -> float:
    """Real rate from a nominal rate and an inflation rate: (1 + n) / (1 + i) - 1."""
    if not inflation > -1.0:
        raise ValueError(f"inflation must be above -1, got {inflation}")
    return (1.0 + nominal) / (1.0 + inflation) - 1.0


def spread_from_rate(rate: float, real_rate: float) -> float:
    """Spread over the real rate equivalent to a real rate k on a flat deck: k(1 + r).

    Exact for a revenue claim with zero convenience yield (ADR 0045).
    """
    return rate * (1.0 + real_rate)


@dataclass(frozen=True)
class SpreadRow:
    """One spread-set row after conversion: a company's spread, or a low-to-high range.

    Attributes:
        company: the disclosing company.
        low: spread at the low end, fraction per year.
        high: spread at the high end; equal to ``low`` for a single rate.

    """

    company: str
    low: float
    high: float

    def __post_init__(self) -> None:
        """Reject a range whose high end is below its low end."""
        if self.high < self.low:
            raise ValueError(f"{self.company}: high {self.high} below low {self.low}")


def spread_prior(rows: Sequence[SpreadRow]) -> tuple[FloatArray, FloatArray]:
    """Support points and weights of the empirical spread prior (8.3).

    Each company gets weight 1 / (number of companies), split evenly across its rows;
    a row with a range splits its weight evenly between its two ends.
    """
    if not rows:
        raise ValueError("the spread set is empty")
    companies = sorted({r.company for r in rows})
    per_company = {c: sum(1 for r in rows if r.company == c) for c in companies}
    values: list[float] = []
    weights: list[float] = []
    for r in rows:
        w = 1.0 / len(companies) / per_company[r.company]
        if r.high == r.low:
            values.append(r.low)
            weights.append(w)
        else:
            values += [r.low, r.high]
            weights += [w / 2.0, w / 2.0]
    return np.asarray(values, dtype=np.float64), np.asarray(weights, dtype=np.float64)


def meets_minimum(rows: Sequence[SpreadRow]) -> bool:
    """Whether the set has at least 8 rates from at least 4 companies (8.3).

    A range counts as two rates, since the protocol records it as both ends.
    """
    n_rates = sum(1 if r.high == r.low else 2 for r in rows)
    return n_rates >= MIN_RATES and len({r.company for r in rows}) >= MIN_COMPANIES


def sample_spreads(rows: Sequence[SpreadRow], n: int, rng: np.random.Generator) -> FloatArray:
    """Draw ``n`` spreads from the equal-weight-by-company prior."""
    values, weights = spread_prior(rows)
    draws: FloatArray = rng.choice(values, size=n, replace=True, p=weights / weights.sum())
    return draws


# --------------------------------------------------------------------------------------
# 4. Draw loop (8.4)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PriceRange:
    """A deal's range of engine values over joint draws (8.4 step 4).

    Attributes:
        values: value per draw.
        standard_errors: Monte Carlo standard error per draw (0 in closed form).
        spreads: spread per draw.
        n_paths: Monte Carlo paths per draw (0 in closed form).
        p10, p50, p90: 10th percentile, median and 90th percentile of ``values``.
        needs_extension: whether any draw's window used the extension beyond 60 months.
        flags: labels carried from the terms and inputs.

    """

    values: FloatArray
    standard_errors: FloatArray
    spreads: FloatArray
    n_paths: int
    p10: float
    p50: float
    p90: float
    needs_extension: bool
    flags: tuple[str, ...] = field(default=())

    @property
    def max_relative_se(self) -> float:
        """Largest per-draw standard error as a share of its value (reported, not a typical one)."""
        nz = self.values != 0.0
        if not nz.any():
            return 0.0
        return float(np.max(np.abs(self.standard_errors[nz] / self.values[nz])))


def price_range(
    model: CashFlowModel,
    spreads: FloatArray,
    *,
    replicates: FloatArray | None,
    age_months: float,
    already_decided: bool = False,
    window_years: int = WINDOW_YEARS,
) -> PriceRange:
    """Values over joint draws of spread and incidence replicate (8.4 steps 2 to 4).

    Draw i pairs ``spreads[i]`` with ``replicates[i]`` (from ``incidence_replicates``,
    the deal's project left out). When the decision was already made, the replicates are
    not used and may be None.

    Raises:
        ValueError: a replicate has a missing horizon, the arrays differ in length, or a
            Monte Carlo standard error is not under 1% of its value (raise ``n_paths``).

    """
    s = np.asarray(spreads, dtype=float)
    n = s.size
    if n == 0:
        raise ValueError("no draws")
    window = model.mean.shape[0] - 2
    if window != window_years:
        raise ValueError(f"model window is {window} years, asked for {window_years}")
    if not already_decided:
        if replicates is None or np.asarray(replicates).shape != (n, len(HORIZONS)):
            raise ValueError(f"need replicates of shape ({n}, {len(HORIZONS)})")
        if np.isnan(replicates).any():
            bad = int(np.isnan(replicates).any(axis=1).sum())
            raise ValueError(f"{bad} incidence replicate(s) have a missing horizon")
    values = np.zeros(n)
    ses = np.zeros(n)
    extension = False
    fixed = decision_timing(None, age_months, already_decided=True, window_years=window_years)
    for i in range(n):
        if already_decided:
            timing = fixed
        else:
            assert replicates is not None
            inc = Incidence.from_array(replicates[i])
            timing = decision_timing(inc, age_months, window_years=window_years)
            extension = extension or timing.needs_extension
        values[i], ses[i] = model.value(timing.scenario_probs(), float(s[i]))
    if model.cov is not None:
        too_noisy = (ses > 0) & (ses >= MAX_RELATIVE_SE * np.abs(values))
        if too_noisy.any():
            worst = float(np.max(ses[too_noisy] / np.maximum(np.abs(values[too_noisy]), 1e-300)))
            raise ValueError(
                f"Monte Carlo standard error is {worst:.2%} of value for "
                f"{int(too_noisy.sum())} draw(s), above {MAX_RELATIVE_SE:.0%}: "
                f"raise n_paths above {model.n_paths}"
            )
    p10, p50, p90 = (float(x) for x in np.percentile(values, PERCENTILES))
    flags = model.flags + (("window extended beyond 60 months",) if extension else ())
    return PriceRange(values, ses, s, model.n_paths, p10, p50, p90, extension, flags)


# --------------------------------------------------------------------------------------
# 5. Contingent amounts (8.6 sensitivity)
# --------------------------------------------------------------------------------------


def contingent_epv(
    amount: float,
    timing: DecisionTiming,
    *,
    trigger: Literal["decision", "first_production"],
    real_rate: float,
    preproduction_years: float | None = None,
    trigger_in_window: bool = True,
    decision_point: float = 0.5,
) -> float:
    """Return the expected present value of a contingent payment (8.6 sensitivity).

    The payment (real US$) is due at a construction decision, or at first production
    ``preproduction_years`` later (one year if None), and is discounted at the real
    risk-free rate from the trigger date. With ``trigger_in_window`` the trigger itself
    must fall inside the window (so a production trigger needs decision plus
    pre-production within it); otherwise any decision in the window counts. Decisions
    in window year k >= 1 are dated at k - 1 + ``decision_point`` (mid-year by default).
    """
    if trigger not in ("decision", "first_production"):
        raise ValueError(f"trigger must be 'decision' or 'first_production', got {trigger!r}")
    if not real_rate > -1.0:
        raise ValueError(f"real_rate must be above -1, got {real_rate}")
    lag = 0.0
    if trigger == "first_production":
        lag = DEFAULT_PREPRODUCTION_YEARS if preproduction_years is None else preproduction_years
    k_years = np.arange(timing.probs.size, dtype=float)
    t = np.where(k_years > 0, k_years - 1.0 + decision_point, 0.0) + lag
    p = timing.probs.copy()
    if trigger_in_window:
        p = np.where(t <= timing.window_years + 1e-9, p, 0.0)
    return float(amount * np.sum(p * (1.0 + real_rate) ** -t))

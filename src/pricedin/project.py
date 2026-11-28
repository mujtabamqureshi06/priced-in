"""Project cash flow in schedule mode.

Schedule mode starts from the study's own annual cash-flow table (``pricedin.inputs``)
and changes only what depends on the gold price. With the study's flat price deck the
result reproduces the study table exactly; this is the reconciliation the engine is
checked against.

How a different gold price changes each line (all in the case's money units, real):

- **Gold revenue** scales with the price: ``gold_revenue_t * P_t / P_deck``. The study
  table already embeds payable ounces, payability and refining terms, so scaling the
  study's own revenue line keeps them exactly.
- **Other revenue** (by-products, for example silver) stays at the study deck unless
  a ratio is supplied. Phase 1 models gold only (ADR 0006).
- **Revenue-linked costs** (royalties, levies, selling costs the case lists in
  ``schedule.revenue_linked``) scale with total revenue in the same period.
- **Tax** is the study's tax plus the marginal tax rate times the change in pre-tax
  profit. A period whose tax would turn negative pays zero and carries the shortfall
  forward as a credit against later tax, which approximates loss carry-forward. This
  ignores changes in depreciation timing and other fiscal detail. Its error is measured
  against the price sensitivity tables each study publishes (tests and
  ``docs/methodology.md``).

Capital, operating cost and working capital follow the study schedule. Capital cost
overrun (ADR 0015) and ramp-up (ADR 0017) are applied in the engine (`pricedin.engine`).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pricedin.inputs import MILLIONS_PER_UNIT, Case

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class CashFlows:
    """Project cash flows by path and period, in the case's money units.

    Every array has shape ``(n_paths, n_periods)``; periods follow
    ``case.schedule.periods``.
    """

    revenue: FloatArray
    revenue_linked_costs: FloatArray
    tax: FloatArray
    pre_tax: FloatArray
    after_tax: FloatArray


def _column(case: Case, name: str) -> FloatArray:
    return np.asarray(case.schedule.columns[name].values, dtype=np.float64)


def schedule_cash_flows(
    case: Case,
    gold_price: FloatArray,
    *,
    other_revenue_ratio: float = 1.0,
) -> CashFlows:
    """Recompute the study cash flows for given gold prices.

    Args:
        case: a schedule-mode case.
        gold_price: real gold price in US$/oz, shape ``(n_paths, n_periods)``, aligned
            with ``case.schedule.periods``.
        other_revenue_ratio: multiplier on non-gold revenue relative to the study deck.
            Leave at 1.0 in Phase 1; used to reproduce studies whose sensitivity tables
            move by-product prices with gold.

    Returns:
        The cash flows, with the same shape as ``gold_price``.

    """
    n_periods = len(case.schedule.periods)
    prices = np.asarray(gold_price, dtype=np.float64)
    if prices.ndim != 2 or prices.shape[1] != n_periods:
        raise ValueError(f"gold_price must have shape (n_paths, {n_periods}), got {prices.shape}")
    if np.any(prices <= 0):
        raise ValueError("gold prices must be positive")

    deck = case.study.price_deck["gold"].value
    cols = case.schedule.columns
    gold_study = _column(case, "gold_revenue")
    total_study = _column(case, "revenue") if "revenue" in cols else gold_study
    other_study = total_study - gold_study

    revenue = gold_study * (prices / deck) + other_study * other_revenue_ratio

    linked_study = np.zeros(n_periods)
    for name in case.schedule.revenue_linked:
        linked_study += _column(case, name)
    safe_total = np.where(total_study > 0, total_study, 1.0)
    scale = np.where(total_study > 0, revenue / safe_total, 1.0)
    linked = linked_study * scale

    delta_profit = (revenue - total_study) - (linked - linked_study)
    pre_tax = _column(case, "cash_flow_pre_tax") + delta_profit
    tax_rate = case.study.marginal_tax_rate.value
    study_tax = _column(case, "taxes")
    tax = _adjusted_tax(study_tax, tax_rate * delta_profit)
    # Built from the study's own after-tax line, so the study deck reproduces it exactly
    # even where the report's rounded rows differ by a unit.
    after_tax = _column(case, "cash_flow_after_tax") + delta_profit - (tax - study_tax)
    return CashFlows(
        revenue=revenue,
        revenue_linked_costs=linked,
        tax=tax,
        pre_tax=pre_tax,
        after_tax=after_tax,
    )


def _adjusted_tax(study_tax: FloatArray, change: FloatArray) -> FloatArray:
    """Study tax plus a change, with negative tax carried forward as a credit.

    A period whose adjusted tax would be negative pays zero and carries the shortfall
    forward, to reduce tax in later periods. This approximates loss carry-forward at a
    constant tax rate. Unused credit at the end of the schedule is lost.
    """
    tax = np.empty_like(change)
    credit = np.zeros(change.shape[0])
    for t in range(change.shape[1]):
        raw = study_tax[t] + change[:, t]
        credit += np.maximum(0.0, -raw)
        payable = np.maximum(0.0, raw)
        used = np.minimum(credit, payable)
        tax[:, t] = payable - used
        credit -= used
    return tax


def period_times(case: Case) -> FloatArray:
    """Years from the t0 column to each period's cash flow, on the study's convention.

    The period named by ``case.study.discounting.t0_column`` and the
    ``periods_at_t0 - 1`` periods after it are at ``t0_years``. Later periods are at
    whole years after the last of them (``end_of_year``) or half a year earlier
    (``mid_year``). Periods before t0 are at negative times, compounded forward.
    """
    d = case.study.discounting
    t0 = case.schedule.periods.index(d.t0_column)
    k = np.arange(len(case.schedule.periods), dtype=np.float64) - t0
    t = np.where(k >= d.periods_at_t0, k - (d.periods_at_t0 - 1), np.minimum(k, 0.0))
    if d.convention == "mid_year":
        t = np.where(k >= d.periods_at_t0, t - 0.5, t)
    out: FloatArray = t + d.t0_years
    return out


def usd_millions_per_unit(case: Case) -> float:
    """US$ millions per unit of the case's money, at the case's stated exchange rate."""
    scale = MILLIONS_PER_UNIT[case.schedule.money_units]
    fx = case.schedule.fx_usd_per_unit
    return scale * (1.0 if fx is None else fx.value)


def discount_factors(case: Case, rate: float) -> FloatArray:
    """Discount factors on the study's own timing (see ``period_times``).

    The period named by ``case.study.discounting.t0_column`` has factor 1.0.
    """
    factors: FloatArray = (1.0 + rate) ** -period_times(case)
    return factors


def npv(cash_flows: FloatArray, case: Case, rate: float) -> FloatArray:
    """Net present value of each path's cash flows at a flat annual rate."""
    values: FloatArray = cash_flows @ discount_factors(case, rate)
    return values

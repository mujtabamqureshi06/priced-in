"""Sum-of-parts adapter for a company with more than one asset (#75, ADR 0044).

The market value of a multi-asset company is split into parts. What is left after the
other parts are taken out is the price of the asset of interest. Each part that cannot
be valued to one number enters as a range, so the residual is a band, not a point:

    residual = enterprise value - producing assets - other projects - G&A credit

All money is in one currency (US$ million in the Orla case).

Producing assets are valued on their study's remaining after-tax cash flows, re-priced
at the expected gold price under the market-consistent drift. The re-pricing follows
schedule mode (`pricedin.project`): gold revenue scales with the price, revenue-linked
costs scale with revenue, and tax changes at a stated marginal rate. A producing mine
has no gate or build decision left, so the expected price path is enough; this ignores
the small convexity from the tax floor and any option to close early.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class ProducingAsset:
    """Remaining study cash flows of a producing mine.

    Attributes:
        times: years from the valuation date to each cash flow.
        gold_revenue: study gold revenue at the study deck, per period.
        after_tax: study after-tax cash flow, per period.
        deck: study gold price (US$/oz).
        linked_share: revenue-linked costs (royalties, duties) as a share of revenue.
        tax_rate: marginal tax rate on a change in pre-tax profit.

    """

    times: FloatArray
    gold_revenue: FloatArray
    after_tax: FloatArray
    deck: float
    linked_share: float
    tax_rate: float

    def __post_init__(self) -> None:
        """Check shapes and ranges."""
        n = self.times.shape
        if self.gold_revenue.shape != n or self.after_tax.shape != n:
            raise ValueError("times, gold_revenue and after_tax must have the same shape")
        if np.any(self.times < 0):
            raise ValueError("cash-flow times must be non-negative")
        if not (0.0 <= self.linked_share < 1.0 and 0.0 <= self.tax_rate < 1.0):
            raise ValueError("linked_share and tax_rate must be fractions below 1")
        if self.deck <= 0:
            raise ValueError("the study deck must be positive")


def producing_value(asset: ProducingAsset, spot: float, drift: float, rate: float) -> float:
    """Value of the remaining cash flows at the expected gold price, discounted at ``rate``.

    The expected price at time t is ``spot * exp(drift * t)``. A change in revenue moves
    after-tax cash flow by ``(1 - linked_share) * (1 - tax_rate)`` per dollar.
    """
    price = spot * np.exp(drift * asset.times)
    change = asset.gold_revenue * (price / asset.deck - 1.0)
    flows = asset.after_tax + change * (1.0 - asset.linked_share) * (1.0 - asset.tax_rate)
    return float(flows @ (1.0 + rate) ** -asset.times)


@dataclass(frozen=True)
class Part:
    """One item taken out of enterprise value, as a range (low <= high)."""

    label: str
    low: float
    high: float

    def __post_init__(self) -> None:
        """Reject an inverted range."""
        if self.low > self.high:
            raise ValueError(f"part '{self.label}': low {self.low} exceeds high {self.high}")


@dataclass(frozen=True)
class Band:
    """The residual price of the asset of interest."""

    low: float
    high: float
    enterprise_value: float
    parts: tuple[Part, ...]


def residual_band(enterprise_value: float, parts: Sequence[Part]) -> Band:
    """Enterprise value less every part. The low end takes each part at its high end."""
    low = enterprise_value - sum(p.high for p in parts)
    high = enterprise_value - sum(p.low for p in parts)
    return Band(low=low, high=high, enterprise_value=enterprise_value, parts=tuple(parts))


def treasury_shares(
    basic: float, instruments: Sequence[tuple[float, float]], price: float
) -> tuple[float, float]:
    """Diluted share count and exercise proceeds under the treasury method.

    ``instruments`` holds (count, strike) pairs in the share price's currency; only
    those in the money are counted. Returns (shares, proceeds).
    """
    shares, proceeds = basic, 0.0
    for count, strike in instruments:
        if price > strike:
            shares += count
            proceeds += count * strike
    return shares, proceeds

"""Gold volatility from a monthly average price series (ADR 0057).

The World Bank's monthly gold series (Pink Sheet) reports the average price of each
month. Returns between monthly averages understate the volatility of the price itself.
For a random walk observed through period averages, the variance of the change between
consecutive averages is (2n^2 + 1) / (3n^2) of the variance of the change over one
period, where n is the number of observations averaged; for daily prices in a month this
is about 2/3 (Working 1960). Annualising monthly returns and dividing the variance by
that ratio recovers the volatility of the price. ``tests/test_volatility.py`` checks the
ratio by simulation.

Each snapshot uses the trailing 10 years of months up to and including the snapshot's
month, so no price after the snapshot enters its volatility.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Mapping, Sequence

#: Variance of changes in period averages, as a share of the true one-period variance,
#: in the limit of many observations per period (Working 1960).
AVERAGING_VARIANCE_RATIO = 2.0 / 3.0


def averaging_variance_ratio(n: int) -> float:
    """Exact ratio for ``n`` equally spaced observations per period: (2n^2 + 1) / (3n^2)."""
    if n < 1:
        raise ValueError("n must be at least 1")
    return (2.0 * n * n + 1.0) / (3.0 * n * n)


def annualised_vol(monthly_averages: Sequence[float], *, correct_averaging: bool = True) -> float:
    """Annualised volatility of the price from a run of monthly average prices.

    Args:
        monthly_averages: consecutive monthly average prices, oldest first.
        correct_averaging: divide the variance by ``AVERAGING_VARIANCE_RATIO``.

    """
    if len(monthly_averages) < 3:
        raise ValueError("need at least three months")
    returns = [math.log(b / a) for a, b in itertools.pairwise(monthly_averages)]
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1) * 12.0
    if correct_averaging:
        var /= AVERAGING_VARIANCE_RATIO
    return math.sqrt(var)


def trailing_vol(
    series: Mapping[str, float], month: str, *, years: int = 10, correct_averaging: bool = True
) -> float:
    """Volatility from the ``years`` x 12 monthly returns ending in ``month`` ("YYYY-MM")."""
    keys = sorted(k for k in series if k <= month)
    window = keys[-(12 * years + 1) :]
    if len(window) < 12 * years + 1 or window[-1] != month:
        raise ValueError(f"not enough months up to {month}")
    return annualised_vol([series[k] for k in window], correct_averaging=correct_averaging)

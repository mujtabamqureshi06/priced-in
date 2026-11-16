"""Commodity price paths.

Phase 1 models gold with geometric Brownian motion (GBM). Schwartz (1997) could not fit
a one-factor mean-reverting model to gold, so a random walk in the log price is the
standard choice (ADR 0006).

Prices are in real terms (ADR 0007). Paths are sampled once a year, at the end of each
year, to match the annual cash-flow tables the engine reproduces. The price for year
``t`` is the simulated price at time ``t``; this is a documented simplification of an
annual average price.

Under the market-consistent valuation mode (ADR 0012) the drift is the real risk-free
rate less the convenience yield (for gold, close to the lease rate), so that the
discounted price is a martingale up to that yield. The caller supplies the drift; this
module does not choose it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class GBM:
    """Geometric Brownian motion for one commodity.

    Attributes:
        spot: price at time 0, in real currency units per unit of metal (e.g. US$/oz).
        drift: annual drift of the price, continuously compounded (fraction per year).
        volatility: annual volatility of log returns (fraction per year).

    """

    spot: float
    drift: float
    volatility: float

    def __post_init__(self) -> None:
        """Reject a non-positive spot or a negative volatility."""
        if not self.spot > 0:
            raise ValueError(f"spot must be positive, got {self.spot}")
        if self.volatility < 0:
            raise ValueError(f"volatility must be non-negative, got {self.volatility}")

    def simulate(
        self,
        n_years: int,
        n_paths: int,
        rng: np.random.Generator,
        *,
        antithetic: bool = False,
    ) -> FloatArray:
        """Simulate annual prices.

        Uses the exact solution of the GBM stochastic differential equation, so there is
        no discretisation error at the annual sampling points.

        Args:
            n_years: number of annual steps after time 0.
            n_paths: number of paths. Must be even when ``antithetic`` is true.
            rng: random generator (ADR 0011).
            antithetic: pair each normal draw with its negative to reduce variance.

        Returns:
            Array of shape ``(n_paths, n_years + 1)``; column 0 is the spot price.

        """
        if n_years < 0:
            raise ValueError(f"n_years must be non-negative, got {n_years}")
        if n_paths < 1:
            raise ValueError(f"n_paths must be at least 1, got {n_paths}")
        if antithetic and n_paths % 2:
            raise ValueError(f"n_paths must be even with antithetic draws, got {n_paths}")

        if antithetic:
            half = rng.standard_normal((n_paths // 2, n_years))
            z = np.concatenate([half, -half])
        else:
            z = rng.standard_normal((n_paths, n_years))

        step = (self.drift - 0.5 * self.volatility**2) + self.volatility * z
        log_paths = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(step, axis=1)], axis=1)
        return self.spot * np.exp(log_paths)


def flat_deck(price: float, n_years: int, n_paths: int = 1) -> FloatArray:
    """Return a deterministic flat price deck, as used in technical studies.

    This is the "risks off" price input used to reproduce a study NPV exactly.

    Returns:
        Array of shape ``(n_paths, n_years + 1)`` filled with ``price``.

    """
    if not price > 0:
        raise ValueError(f"price must be positive, got {price}")
    if n_years < 0 or n_paths < 1:
        raise ValueError("n_years must be non-negative and n_paths at least 1")
    return np.full((n_paths, n_years + 1), float(price))

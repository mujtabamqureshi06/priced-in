"""Commodity price paths.

Phase 1 models gold with geometric Brownian motion (GBM), a random walk in the log
price, as in Brennan and Schwartz (1985) (ADR 0006).

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
        paths: FloatArray = np.asarray(self.spot * np.exp(log_paths), dtype=np.float64)
        return paths


@dataclass(frozen=True)
class CorrelatedGBM:
    """Geometric Brownian motion for several commodities with correlated shocks (#72).

    Each price follows its own GBM; the annual normal shocks are correlated through the
    Cholesky factor of ``correlation``. With one commodity this is ``GBM``.

    Attributes:
        spots: price of each commodity at time 0.
        drifts: continuously compounded annual drift of each price.
        volatilities: annual volatility of each price's log returns.
        correlation: correlation matrix of the annual log-return shocks.

    """

    spots: tuple[float, ...]
    drifts: tuple[float, ...]
    volatilities: tuple[float, ...]
    correlation: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        """Check shapes, signs and that the correlation matrix is valid."""
        n = len(self.spots)
        if n == 0 or len(self.drifts) != n or len(self.volatilities) != n:
            raise ValueError("spots, drifts and volatilities must have the same, non-zero length")
        if any(s <= 0 for s in self.spots):
            raise ValueError("spots must be positive")
        if any(v < 0 for v in self.volatilities):
            raise ValueError("volatilities must be non-negative")
        corr = np.asarray(self.correlation, dtype=np.float64)
        if corr.shape != (n, n):
            raise ValueError(f"correlation must be {n} x {n}, got {corr.shape}")
        if not np.allclose(corr, corr.T) or not np.allclose(np.diag(corr), 1.0):
            raise ValueError("correlation must be symmetric with ones on the diagonal")
        if float(np.min(np.linalg.eigvalsh(corr))) < -1e-12:
            raise ValueError("correlation must be positive semi-definite")

    def simulate(self, n_years: int, n_paths: int, rng: np.random.Generator) -> FloatArray:
        """Simulate annual prices, exactly at each annual point.

        Returns:
            Array of shape ``(n_commodities, n_paths, n_years + 1)``; column 0 is spot.

        """
        if n_years < 0 or n_paths < 1:
            raise ValueError("n_years must be non-negative and n_paths at least 1")
        n = len(self.spots)
        corr = np.asarray(self.correlation, dtype=np.float64)
        # Eigen-decomposition rather than Cholesky so a singular matrix (perfect
        # correlation) is accepted.
        w, v = np.linalg.eigh(corr)
        factor = v * np.sqrt(np.clip(w, 0.0, None))
        z = np.einsum("ij,jpt->ipt", factor, rng.standard_normal((n, n_paths, n_years)))
        out = np.empty((n, n_paths, n_years + 1))
        for i in range(n):
            vol = self.volatilities[i]
            step = (self.drifts[i] - 0.5 * vol**2) + vol * z[i]
            log_paths = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(step, axis=1)], axis=1)
            out[i] = self.spots[i] * np.exp(log_paths)
        return out


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

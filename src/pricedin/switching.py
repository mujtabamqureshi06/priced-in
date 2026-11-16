"""A mine with options to close, reopen and abandon, by least-squares Monte Carlo (#76).

This module replicates the copper mine of Brennan and Schwartz (1985), "Evaluating
Natural Resource Investments", Journal of Business 58(2), 135-157, the standard test of
real-option methods for mines. It validates the least-squares Monte Carlo approach the
engine uses for its build decision (ADRs 0037, 0038) on a problem with a known answer.

The model, as specified by Maier (2021, Sect. 2.2) to reproduce Brennan and Schwartz:

- The copper price follows geometric Brownian motion under the pricing measure, with
  drift r - delta (interest rate less convenience yield).
- The mine is open (producing at rate q), closed (paying maintenance) or abandoned.
  Each period of length dt an open mine may operate, close or be abandoned; a closed
  mine may reopen (and produce that period), stay closed or be abandoned. Abandonment
  is free and final. A mine whose inventory is exhausted is worth nothing more.
- Operating cash flow per year: q (X - A) less royalty tau1 q X and income tax
  max(tau2 q (X (1 - tau1) - A), 0); no loss offset. Closing, reopening and
  maintenance costs are not taxed. Costs grow at the inflation rate pi.
- Cash flows are discounted at r + lambda1, the property tax on the mine's value acting
  as an extra discount rate. The mine is abandoned at the horizon if not before.

Inventory is a discrete state (remaining production periods), so the regression runs
once per date for every (mode, inventory) state together, on the same simulated prices.
The basis is a piecewise-linear spline in the log price; polynomial bases left a low
bias of 2% to 8% at low prices. Values follow Longstaff and Schwartz: the realised cash
flows under the fitted policy. The policy is fitted and valued on the same paths, so the
estimate carries in-sample (foresight) bias upward as well as suboptimality bias
downward; the bias is not one-sided.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import erf, log, sqrt

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class SwitchingMine:
    """Inputs for the mine, in US$, pounds and years (Maier 2021, Table 1)."""

    output_rate: float = 10e6
    inventory: float = 150e6
    average_cost: float = 0.50
    opening_cost: float = 200e3
    closing_cost: float = 200e3
    maintenance_cost: float = 500e3
    cost_inflation: float = 0.08
    convenience_yield: float = 0.01
    price_variance: float = 0.08
    interest_rate: float = 0.10
    royalty: float = 0.0
    income_tax: float = 0.50
    property_tax: float = 0.02


@dataclass(frozen=True)
class SwitchingValue:
    """Values of the mine, US$ millions, with Monte Carlo standard errors."""

    open_value: float
    closed_value: float
    open_se: float
    closed_se: float


def spline_basis(u: FloatArray, n_knots: int) -> FloatArray:
    """Piecewise-linear basis 1, u, (u - k_i)+ with knots at evenly spaced quantiles."""
    knots = np.quantile(u, np.linspace(0.05, 0.95, n_knots))
    columns = [np.ones_like(u), u, *(np.maximum(u - k, 0.0) for k in knots)]
    return np.column_stack(columns)


def price_paths(
    mine: SwitchingMine, spot: float, n_steps: int, dt: float, n_paths: int, seed: int
) -> FloatArray:
    """Antithetic GBM price paths at steps 0..n_steps, shape (n_paths, n_steps + 1)."""
    if n_paths % 2:
        raise ValueError("n_paths must be even (antithetic pairs)")
    rng = np.random.default_rng(seed)
    half = rng.standard_normal((n_paths // 2, n_steps))
    z = np.concatenate([half, -half])
    sigma = np.sqrt(mine.price_variance)
    drift = (mine.interest_rate - mine.convenience_yield - 0.5 * sigma**2) * dt
    log_x = np.log(spot) + np.cumsum(drift + sigma * np.sqrt(dt) * z, axis=1)
    paths: FloatArray = np.concatenate([np.full((n_paths, 1), spot), np.exp(log_x)], axis=1)
    return paths


def _operating_flow(mine: SwitchingMine, x: FloatArray, t: float, dt: float) -> FloatArray:
    """After-tax operating cash flow over one period at price x and time t."""
    q, a = mine.output_rate, mine.average_cost * np.exp(mine.cost_inflation * t)
    tax = mine.royalty * q * x + np.maximum(
        mine.income_tax * q * (x * (1.0 - mine.royalty) - a), 0.0
    )
    flow: FloatArray = (q * (x - a) - tax) * dt
    return flow


def _choose(
    est_a: FloatArray, est_b: FloatArray, real_a: FloatArray, real_b: FloatArray
) -> FloatArray:
    """Pick the better of two actions or abandonment (worth 0), by fitted value."""
    best = np.maximum(est_a, est_b)
    realised = np.where(est_a >= est_b, real_a, real_b)
    chosen: FloatArray = np.where(best > 0.0, realised, 0.0)
    return chosen


def value_switching_mine(
    mine: SwitchingMine,
    spot: float,
    *,
    n_paths: int = 40_000,
    seed: int = 1,
    dt: float = 0.2,
    horizon: float = 60.0,
    n_knots: int = 12,
) -> SwitchingValue:
    """Value the mine open and closed at a copper price, by least-squares Monte Carlo."""
    n_steps = round(horizon / dt)
    n_inv = round(mine.inventory / (mine.output_rate * dt))
    discount = np.exp(-(mine.interest_rate + mine.property_tax) * dt)
    x_all = price_paths(mine, spot, n_steps, dt, n_paths, seed)

    # value[mode, i, path]: mode 0 open, 1 closed; i periods of inventory left.
    value = np.zeros((2, n_inv + 1, n_paths))
    for j in range(n_steps - 1, -1, -1):
        t = j * dt
        x = x_all[:, j]
        growth = np.exp(mine.cost_inflation * t)
        maintain = mine.maintenance_cost * growth * dt
        close = mine.closing_cost * growth
        reopen = mine.opening_cost * growth
        produce = _operating_flow(mine, x, t, dt)

        realised = value * discount
        if j > 0:
            basis = spline_basis(np.log(x), n_knots)
            coef = np.linalg.lstsq(basis, realised.reshape(-1, n_paths).T, rcond=None)[0]
            fitted = (basis @ coef).T.reshape(realised.shape)
        else:  # every path starts at the same price: the regression is the mean
            fitted = np.broadcast_to(realised.mean(axis=2, keepdims=True), realised.shape)

        new = np.zeros_like(value)
        new[0, 1:] = _choose(
            produce + fitted[0, :-1],
            -maintain - close + fitted[1, 1:],
            produce + realised[0, :-1],
            -maintain - close + realised[1, 1:],
        )
        new[1, 1:] = _choose(
            produce - reopen + fitted[0, :-1],
            -maintain + fitted[1, 1:],
            produce - reopen + realised[0, :-1],
            -maintain + realised[1, 1:],
        )
        value = new

    open_paths, closed_paths = value[0, n_inv] / 1e6, value[1, n_inv] / 1e6
    root_n = np.sqrt(n_paths)
    return SwitchingValue(
        open_value=float(open_paths.mean()),
        closed_value=float(closed_paths.mean()),
        open_se=float(open_paths.std(ddof=1) / root_n),
        closed_se=float(closed_paths.std(ddof=1) / root_n),
    )


def fixed_output_value(mine: SwitchingMine, spot: float, *, dt: float = 0.2) -> float:
    """Exact value, US$ millions, of operating every period until the inventory is gone.

    Each period's expected after-tax flow is closed form: the income tax is a call on
    the price struck at the inflated cost (Black and Scholes 1973), with royalty zero.
    Used to check the simulation's payoffs and discounting.
    """
    if mine.royalty != 0.0:
        raise ValueError("the closed form assumes no royalty")

    def cdf(v: float) -> float:
        return 0.5 * (1.0 + erf(v / sqrt(2.0)))

    n_inv = round(mine.inventory / (mine.output_rate * dt))
    sigma = sqrt(mine.price_variance)
    total = 0.0
    for j in range(n_inv):
        t = j * dt
        forward = spot * np.exp((mine.interest_rate - mine.convenience_yield) * t)
        cost = mine.average_cost * np.exp(mine.cost_inflation * t)
        if t == 0.0:
            call = max(forward - cost, 0.0)
        else:
            s = sigma * sqrt(t)
            d1 = (log(forward / cost) + 0.5 * s * s) / s
            call = forward * cdf(d1) - cost * cdf(d1 - s)
        flow = mine.output_rate * ((forward - cost) - mine.income_tax * call) * dt
        total += flow * np.exp(-(mine.interest_rate + mine.property_tax) * t)
    return float(total / 1e6)

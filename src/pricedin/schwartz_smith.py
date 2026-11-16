"""Schwartz-Smith two-factor commodity price model with Kalman-filter calibration (WP 3.3).

Schwartz, E. S. and Smith, J. E. (2000), "Short-Term Variations and Long-Term Dynamics in
Commodity Prices", Management Science 46(7), 893-911.

The log spot price is the sum of a short-term deviation and a long-term level,
ln S_t = chi_t + xi_t, with

    d chi = -kappa chi dt + sigma_chi dz_chi           (mean-reverting)
    d xi  = mu_xi dt + sigma_xi dz_xi                  (Brownian motion with drift)
    dz_chi dz_xi = rho dt.

Under the pricing measure the drifts carry risk premia lambda_chi and lambda_xi, and
the log futures price for maturity T is (Schwartz and Smith 2000, eq. 9):

    ln F(t, T) = e^(-kappa T) chi_t + xi_t + A(T),
    A(T) = mu*_xi T - (1 - e^(-kappa T)) lambda_chi / kappa
           + 0.5 [(1 - e^(-2 kappa T)) sigma_chi^2 / (2 kappa) + sigma_xi^2 T
                  + 2 (1 - e^(-kappa T)) rho sigma_chi sigma_xi / kappa],

with mu*_xi = mu_xi - lambda_xi. The states are unobserved; a panel of log futures
prices observed with independent errors is filtered with the Kalman filter, and the
parameters maximise the likelihood from the prediction-error decomposition (the
paper's Section 3). Copper is the intended commodity (the build plan flags a structural
break after 2004); calibration to real futures waits for a free futures panel (ADR 0042).
"""

from __future__ import annotations

from dataclasses import astuple, dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize  # type: ignore[import-untyped]

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class SchwartzSmith:
    """Model parameters, annual units.

    Attributes:
        kappa: speed of mean reversion of the short-term factor.
        sigma_chi: volatility of the short-term factor.
        lambda_chi: risk premium on the short-term factor.
        mu_xi: real-world drift of the long-term factor.
        sigma_xi: volatility of the long-term factor.
        mu_xi_star: risk-neutral drift of the long-term factor (mu_xi - lambda_xi).
        rho: correlation of the two factors' shocks.

    """

    kappa: float
    sigma_chi: float
    lambda_chi: float
    mu_xi: float
    sigma_xi: float
    mu_xi_star: float
    rho: float

    def __post_init__(self) -> None:
        """Reject parameters outside their domain."""
        if self.kappa <= 0 or self.sigma_chi < 0 or self.sigma_xi < 0:
            raise ValueError("kappa must be positive and volatilities non-negative")
        if not -1.0 <= self.rho <= 1.0:
            raise ValueError("rho must lie in [-1, 1]")

    def a(self, maturity: FloatArray) -> FloatArray:
        """Deterministic part A(T) of the log futures price."""
        t = np.asarray(maturity, dtype=np.float64)
        k, sc, sx = self.kappa, self.sigma_chi, self.sigma_xi
        e1, e2 = 1.0 - np.exp(-k * t), 1.0 - np.exp(-2.0 * k * t)
        variance = e2 * sc**2 / (2.0 * k) + sx**2 * t + 2.0 * e1 * self.rho * sc * sx / k
        out: FloatArray = self.mu_xi_star * t - e1 * self.lambda_chi / k + 0.5 * variance
        return out

    def log_futures(self, chi: FloatArray, xi: FloatArray, maturity: FloatArray) -> FloatArray:
        """Log futures prices for states (chi, xi) and maturities (broadcast)."""
        t = np.asarray(maturity, dtype=np.float64)
        out: FloatArray = np.exp(-self.kappa * t) * chi + xi + self.a(t)
        return out

    def transition(self, dt: float) -> tuple[FloatArray, FloatArray, FloatArray]:
        """Real-world state transition x' = c + G x + w, w ~ N(0, W), over dt years."""
        k, sc, sx = self.kappa, self.sigma_chi, self.sigma_xi
        c = np.array([0.0, self.mu_xi * dt])
        g = np.diag([np.exp(-k * dt), 1.0])
        cov = (1.0 - np.exp(-k * dt)) * self.rho * sc * sx / k
        w = np.array([[(1.0 - np.exp(-2.0 * k * dt)) * sc**2 / (2.0 * k), cov], [cov, sx**2 * dt]])
        return c, g, w


def simulate_states(
    params: SchwartzSmith, chi0: float, xi0: float, n_steps: int, dt: float, seed: int
) -> FloatArray:
    """Real-world states at steps 0..n_steps, shape (n_steps + 1, 2), exact transition."""
    c, g, w = params.transition(dt)
    chol = np.linalg.cholesky(w + 1e-18 * np.eye(2))
    rng = np.random.default_rng(seed)
    x = np.empty((n_steps + 1, 2))
    x[0] = (chi0, xi0)
    for i in range(1, n_steps + 1):
        x[i] = c + g @ x[i - 1] + chol @ rng.standard_normal(2)
    return x


def kalman_log_likelihood(
    params: SchwartzSmith,
    log_prices: FloatArray,
    maturities: FloatArray,
    dt: float,
    measurement_sd: FloatArray,
) -> float:
    """Gaussian log-likelihood of a panel of log futures prices (rows are dates).

    ``maturities`` has the same shape as ``log_prices`` (time to maturity of each
    observed contract on each date). Measurement errors are independent with the given
    standard deviation for each column.
    """
    y = np.asarray(log_prices, dtype=np.float64)
    tau = np.asarray(maturities, dtype=np.float64)
    c, g, w = params.transition(dt)
    v = np.diag(np.asarray(measurement_sd, dtype=np.float64) ** 2)
    # Diffuse-ish start: chi at its long-run mean 0, xi at the first observed level.
    x = np.array([0.0, float(y[0, 0] - params.a(tau[0, 0]))])
    p = np.diag([params.sigma_chi**2 / (2.0 * params.kappa), 1.0])
    total = 0.0
    for i in range(y.shape[0]):
        if i > 0:
            x = c + g @ x
            p = g @ p @ g.T + w
        f = np.column_stack([np.exp(-params.kappa * tau[i]), np.ones(tau.shape[1])])
        pred = f @ x + params.a(tau[i])
        s = f @ p @ f.T + v
        err = y[i] - pred
        sign, logdet = np.linalg.slogdet(s)
        if sign <= 0:
            return -np.inf
        s_inv_err = np.linalg.solve(s, err)
        total += -0.5 * (len(err) * np.log(2.0 * np.pi) + logdet + err @ s_inv_err)
        gain = p @ f.T @ np.linalg.inv(s)
        x = x + gain @ err
        p = p - gain @ f @ p
    return float(total)


def _unpack(theta: FloatArray, n_obs: int) -> tuple[SchwartzSmith, FloatArray]:
    k, sc, lc, mx, sx, mxs, rho_raw = theta[:7]
    params = SchwartzSmith(
        kappa=float(np.exp(k)),
        sigma_chi=float(np.exp(sc)),
        lambda_chi=float(lc),
        mu_xi=float(mx),
        sigma_xi=float(np.exp(sx)),
        mu_xi_star=float(mxs),
        rho=float(np.tanh(rho_raw)),
    )
    return params, np.exp(theta[7 : 7 + n_obs])


def fit(
    log_prices: FloatArray,
    maturities: FloatArray,
    dt: float,
    start: SchwartzSmith,
    *,
    start_measurement_sd: float = 0.01,
    common_error: bool = False,
) -> tuple[SchwartzSmith, FloatArray, float]:
    """Maximum-likelihood parameters, measurement standard deviations and log-likelihood.

    With ``common_error`` every contract shares one measurement standard deviation,
    which halves the number of parameters.
    """
    n_cols = np.asarray(log_prices).shape[1]
    n_obs = 1 if common_error else n_cols
    theta0 = np.array(
        [
            np.log(start.kappa),
            np.log(start.sigma_chi),
            start.lambda_chi,
            start.mu_xi,
            np.log(start.sigma_xi),
            start.mu_xi_star,
            np.arctanh(start.rho),
            *([np.log(start_measurement_sd)] * n_obs),
        ]
    )

    def objective(theta: FloatArray) -> float:
        params, sd = _unpack(theta, n_obs)
        sd = np.broadcast_to(sd, (n_cols,))
        value = kalman_log_likelihood(params, log_prices, maturities, dt, sd)
        return -value if np.isfinite(value) else 1e12

    result = minimize(objective, theta0, method="L-BFGS-B")
    params, sd = _unpack(result.x, n_obs)
    return params, np.broadcast_to(sd, (n_cols,)).copy(), float(-result.fun)


def as_tuple(params: SchwartzSmith) -> tuple[float, ...]:
    """Parameters as a plain tuple, in field order."""
    return tuple(float(v) for v in astuple(params))

"""Tests for the Schwartz-Smith two-factor model and its Kalman filter (#77)."""

from __future__ import annotations

import numpy as np
import pytest

from pricedin.schwartz_smith import SchwartzSmith, fit, kalman_log_likelihood, simulate_states

TRUE = SchwartzSmith(
    kappa=1.2, sigma_chi=0.25, lambda_chi=0.05, mu_xi=0.01, sigma_xi=0.15, mu_xi_star=-0.01, rho=0.3
)
MATURITIES = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0])


def _panel(n: int, seed: int, noise: float = 0.004) -> tuple[np.ndarray, np.ndarray]:
    states = simulate_states(TRUE, 0.1, np.log(4.0), n, 1 / 52, seed=seed)
    tau = np.tile(MATURITIES, (n + 1, 1))
    rng = np.random.default_rng(seed + 1)
    y = TRUE.log_futures(states[:, :1], states[:, 1:], tau) + rng.normal(0.0, noise, tau.shape)
    return y, tau


def test_futures_converge_to_long_term_factor() -> None:
    """At long maturities the short-term factor's weight vanishes."""
    f0 = TRUE.log_futures(np.array(0.5), np.array(1.0), np.array(50.0))
    f1 = TRUE.log_futures(np.array(-0.5), np.array(1.0), np.array(50.0))
    assert f0 == pytest.approx(f1, abs=1e-12)


def test_zero_maturity_is_spot() -> None:
    assert TRUE.log_futures(np.array(0.3), np.array(1.2), np.array(0.0)) == pytest.approx(1.5)


def test_one_factor_limit() -> None:
    """With no short-term factor, futures grow at the risk-neutral drift plus half variance."""
    gbm = SchwartzSmith(1.0, 0.0, 0.0, 0.0, 0.2, 0.03, 0.0)
    t = np.array(2.0)
    assert gbm.a(t) == pytest.approx(0.03 * 2.0 + 0.5 * 0.04 * 2.0)


def test_likelihood_peaks_near_truth() -> None:
    y, tau = _panel(150, seed=3)
    sd = np.full(MATURITIES.size, 0.004)
    at_truth = kalman_log_likelihood(TRUE, y, tau, 1 / 52, sd)
    off = SchwartzSmith(2.0, 0.25, 0.05, 0.01, 0.15, -0.01, 0.3)
    assert at_truth > kalman_log_likelihood(off, y, tau, 1 / 52, sd)


def test_synthetic_recovery() -> None:
    """Five years of weekly six-contract curves recover the identified parameters."""
    y, tau = _panel(260, seed=11)
    start = SchwartzSmith(0.8, 0.3, 0.0, 0.0, 0.2, 0.0, 0.0)
    est, sd, _ = fit(y, tau, 1 / 52, start, common_error=True)
    assert est.kappa == pytest.approx(TRUE.kappa, rel=0.2)
    assert est.sigma_chi == pytest.approx(TRUE.sigma_chi, rel=0.1)
    assert est.sigma_xi == pytest.approx(TRUE.sigma_xi, rel=0.15)
    assert est.mu_xi_star == pytest.approx(TRUE.mu_xi_star, abs=0.005)
    assert est.rho == pytest.approx(TRUE.rho, abs=0.2)
    assert np.all(np.abs(sd - 0.004) < 0.0015)


def test_rejects_bad_parameters() -> None:
    with pytest.raises(ValueError, match="kappa"):
        SchwartzSmith(0.0, 0.2, 0.0, 0.0, 0.1, 0.0, 0.0)
    with pytest.raises(ValueError, match="rho"):
        SchwartzSmith(1.0, 0.2, 0.0, 0.0, 0.1, 0.0, 1.5)

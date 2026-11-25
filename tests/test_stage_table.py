"""Tests for the Phase 5 stage-table estimators."""

from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from pricedin.stage_table import (
    aalen_johansen,
    brier,
    cluster_bootstrap,
    cumulative_incidence,
    discounted_incidence,
    fine_gray,
    months_between,
    percentile_interval,
)


def test_months_between_one_year() -> None:
    assert months_between(date(2020, 1, 1), date(2021, 1, 1)) == pytest.approx(366 / (365.25 / 12))


def test_cumulative_incidence_no_censoring_is_a_proportion() -> None:
    time = np.array([5.0, 15.0, 30.0, 70.0, 70.0])
    event = np.array([True, True, True, False, False])
    ci = cumulative_incidence(time, event, (12, 24, 36, 60))
    assert ci == pytest.approx([0.2, 0.4, 0.6, 0.6])


def test_cumulative_incidence_with_censoring_matches_hand_km() -> None:
    # At t=10 one event among 4; censored at 20; at t=30 one event among 2.
    time = np.array([10.0, 20.0, 30.0, 50.0])
    event = np.array([True, False, True, False])
    ci = cumulative_incidence(time, event, (12, 36))
    s = (1 - 1 / 4) * (1 - 1 / 2)
    assert ci == pytest.approx([0.25, 1 - s])


def test_cumulative_incidence_beyond_follow_up_is_nan() -> None:
    ci = cumulative_incidence(np.array([5.0, 40.0]), np.array([True, False]), (36, 60))
    assert ci[0] == pytest.approx(0.5)
    assert np.isnan(ci[1])


def test_aalen_johansen_reduces_to_proportions_without_censoring() -> None:
    time = np.array([5.0, 8.0, 20.0, 70.0])
    cause = np.array([1, 2, 1, 0])
    c1, c2 = aalen_johansen(time, cause, (12, 24, 60))
    assert c1 == pytest.approx([0.25, 0.5, 0.5])
    assert c2 == pytest.approx([0.25, 0.25, 0.25])


def test_aalen_johansen_cause_one_alone_equals_km() -> None:
    time = np.array([10.0, 20.0, 30.0, 50.0])
    cause = np.array([1, 0, 1, 0])
    c1, c2 = aalen_johansen(time, cause, (12, 36))
    km = cumulative_incidence(time, cause == 1, (12, 36))
    assert c1 == pytest.approx(km)
    assert c2 == pytest.approx([0.0, 0.0])


def test_brier() -> None:
    assert brier(np.array([1.0, 0.0]), np.array([0.5, 0.5])) == pytest.approx(0.25)


def test_cluster_bootstrap_keeps_clusters_together() -> None:
    clusters = ["a", "a", "b"]
    sizes = cluster_bootstrap(clusters, lambda idx: np.array([float(idx.size)]), 200, 1)
    # Each replicate draws two clusters: sizes are 2+2, 2+1 or 1+1.
    assert set(np.unique(sizes)) <= {2.0, 3.0, 4.0}


def test_percentile_interval_ignores_nan() -> None:
    lo, hi = percentile_interval(np.array([[0.0], [1.0], [np.nan], [2.0]]), 0.5)
    assert lo[0] == pytest.approx(0.5)
    assert hi[0] == pytest.approx(1.5)


def test_fine_gray_recovers_a_clear_effect() -> None:
    rng = np.random.default_rng(0)
    n = 400
    group = rng.integers(0, 2, n)
    rate = np.where(group == 1, 0.06, 0.02)
    t1 = rng.exponential(1 / rate)
    t2 = rng.exponential(1 / 0.01, n)
    cens = np.full(n, 60.0)
    time = np.minimum(np.minimum(t1, t2), cens)
    cause = np.where(time == t1, 1, np.where(time == t2, 2, 0))
    beta = fine_gray(time, cause, cens, group[:, None].astype(float))
    assert beta[0] > 0.6


def test_fine_gray_without_competing_events_is_cox() -> None:
    time = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    cause = np.array([1, 1, 1, 1, 1, 0])
    x = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0]])
    beta = fine_gray(time, cause, np.full(6, 6.0), x)
    assert np.isfinite(beta[0])


def test_discounted_incidence_at_zero_rate_matches_cumulative_incidence() -> None:
    time = np.array([5.0, 15.0, 20.0, 30.0, 40.0, 70.0, 70.0])
    event = np.array([True, True, False, True, False, False, False])
    for h in (12, 24, 36, 60):
        expected = cumulative_incidence(time, event, (h,))[0]
        assert discounted_incidence(time, event, 0.0, h) == pytest.approx(expected)


def test_discounted_incidence_hand_case() -> None:
    # No censoring: events at 12 and 24 months among four subjects.
    time = np.array([12.0, 24.0, 60.0, 60.0])
    event = np.array([True, True, False, False])
    got = discounted_incidence(time, event, 0.05, 36)
    assert got == pytest.approx(0.25 / 1.05 + 0.25 / 1.05**2)


def test_discounted_incidence_beyond_follow_up_is_nan() -> None:
    time = np.array([10.0, 20.0])
    event = np.array([True, False])
    assert np.isnan(discounted_incidence(time, event, 0.05, 36))

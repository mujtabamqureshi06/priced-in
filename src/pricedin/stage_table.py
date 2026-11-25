"""Probability and timing of a construction decision by study stage (Phase 5).

Estimators for the stage-to-build table in ``docs/phase5/protocol.md``:

* cumulative incidence of one event with administrative censoring (Kaplan-Meier,
  reported as one minus the survival function);
* cumulative incidence of two competing events (Aalen-Johansen);
* a Fine and Gray subdistribution hazard model for a categorical covariate, for the
  case where every subject's potential censoring time is known (all censoring is at the
  data cut-off), so subjects with the competing event stay in the risk set until that
  time with weight one;
* the 36-month Brier score and a cluster bootstrap over projects;
* the expected discount factor to the event within a horizon, which turns a stage curve
  into a NAV multiple (protocol section 8).

Times are in months. Every function takes plain numpy arrays so that the tests can
check them against hand-worked cases.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize  # type: ignore[import-untyped]

DAYS_PER_MONTH = 365.25 / 12
HORIZONS = (12, 24, 36, 60)

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


def months_between(start: date, end: date) -> float:
    """Elapsed time from ``start`` to ``end`` in months of 365.25 / 12 days."""
    return (end - start).days / DAYS_PER_MONTH


def cumulative_incidence(
    time: FloatArray, event: NDArray[np.bool_], horizons: Sequence[float] = HORIZONS
) -> FloatArray:
    """One minus the Kaplan-Meier survival function at each horizon.

    ``time`` is the event time for subjects with ``event`` true and the censoring time
    otherwise. Events at time zero count as events. Ties: events before censoring.
    """
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=bool)
    if time.size == 0:
        return np.full(len(horizons), np.nan)
    order = np.lexsort((~event, time))
    t, e = time[order], event[order]
    n = t.size
    surv = 1.0
    times: list[float] = []
    values: list[float] = []
    i = 0
    while i < n:
        j = i
        while j < n and t[j] == t[i]:
            j += 1
        d = int(e[i:j].sum())
        at_risk = n - i
        if d:
            surv *= 1.0 - d / at_risk
            times.append(float(t[i]))
            values.append(1.0 - surv)
        i = j
    out = np.zeros(len(horizons))
    for k, h in enumerate(horizons):
        if h > float(np.max(t)):
            out[k] = np.nan  # no subject observed to the horizon
            continue
        idx = int(np.searchsorted(np.array(times), h, side="right")) - 1
        out[k] = values[idx] if idx >= 0 else 0.0
    return out


def discounted_incidence(
    time: FloatArray, event: NDArray[np.bool_], rate: float, horizon: float
) -> float:
    """Return the expected discount factor to the event within ``horizon`` months.

    Each Kaplan-Meier increment of the cumulative incidence is discounted at the annual
    ``rate`` from its own time: ``sum_j dF(t_j) (1 + rate)^(-t_j / 12)`` over event times
    ``t_j <= horizon``. With ``rate = 0`` it equals ``cumulative_incidence`` at the
    horizon. Returns NaN if no subject is observed to the horizon.
    """
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=bool)
    if time.size == 0 or horizon > float(np.max(time)):
        return float("nan")
    order = np.lexsort((~event, time))
    t, e = time[order], event[order]
    n = t.size
    surv, total, i = 1.0, 0.0, 0
    while i < n and t[i] <= horizon:
        j = i
        while j < n and t[j] == t[i]:
            j += 1
        dead = int(e[i:j].sum())
        if dead:
            new = surv * (1.0 - dead / (n - i))
            total += (surv - new) * (1.0 + rate) ** (-t[i] / 12.0)
            surv = new
        i = j
    return total


def aalen_johansen(
    time: FloatArray, cause: IntArray, horizons: Sequence[float] = HORIZONS
) -> tuple[FloatArray, FloatArray]:
    """Cumulative incidence of causes 1 and 2 with competing risks.

    ``cause`` is 0 for censored, 1 or 2 for the first event observed.
    """
    time = np.asarray(time, dtype=float)
    cause = np.asarray(cause, dtype=int)
    if time.size == 0:
        nan = np.full(len(horizons), np.nan)
        return nan, nan.copy()
    order = np.lexsort((cause == 0, time))
    t, c = time[order], cause[order]
    n = t.size
    surv = 1.0
    cif1 = cif2 = 0.0
    grid: list[float] = []
    v1: list[float] = []
    v2: list[float] = []
    i = 0
    while i < n:
        j = i
        while j < n and t[j] == t[i]:
            j += 1
        at_risk = n - i
        d1 = int((c[i:j] == 1).sum())
        d2 = int((c[i:j] == 2).sum())
        if d1 or d2:
            cif1 += surv * d1 / at_risk
            cif2 += surv * d2 / at_risk
            surv *= 1.0 - (d1 + d2) / at_risk
            grid.append(float(t[i]))
            v1.append(cif1)
            v2.append(cif2)
        i = j
    g = np.array(grid)
    o1 = np.zeros(len(horizons))
    o2 = np.zeros(len(horizons))
    for k, h in enumerate(horizons):
        if h > float(np.max(t)):
            o1[k] = o2[k] = np.nan
            continue
        idx = int(np.searchsorted(g, h, side="right")) - 1
        if idx >= 0:
            o1[k], o2[k] = v1[idx], v2[idx]
    return o1, o2


def brier(outcome: FloatArray, forecast: FloatArray) -> float:
    """Mean squared difference between a 0/1 outcome and a probability forecast."""
    outcome = np.asarray(outcome, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    return float(np.mean((outcome - forecast) ** 2))


def cluster_bootstrap(
    clusters: Sequence[str],
    statistic: Callable[[IntArray], FloatArray],
    n_boot: int,
    seed: int,
) -> FloatArray:
    """Resample clusters with replacement and return ``statistic`` for each replicate.

    ``statistic`` receives the row indices of the resampled data (a row appears once
    for each time its cluster is drawn) and returns a 1-d array.
    """
    rng = np.random.default_rng(seed)
    keys = np.asarray(clusters)
    uniq, inverse = np.unique(keys, return_inverse=True)
    rows_of = [np.flatnonzero(inverse == k) for k in range(uniq.size)]
    out = []
    for _ in range(n_boot):
        draw = rng.integers(0, uniq.size, uniq.size)
        idx = np.concatenate([rows_of[k] for k in draw]) if draw.size else np.array([], int)
        out.append(statistic(idx.astype(np.int64)))
    return np.asarray(out, dtype=float)


def percentile_interval(draws: FloatArray, level: float = 0.95) -> tuple[FloatArray, FloatArray]:
    """Equal-tailed percentile interval of bootstrap draws along axis 0, ignoring NaN."""
    a = (1.0 - level) / 2.0
    return (
        np.nanquantile(draws, a, axis=0),
        np.nanquantile(draws, 1.0 - a, axis=0),
    )


def _cox_negloglik(
    beta: FloatArray, time: FloatArray, event: NDArray[np.bool_], x: FloatArray
) -> float:
    """Negative Breslow partial log-likelihood."""
    eta = x @ beta
    ll = 0.0
    for t in np.unique(time[event]):
        dead = event & (time == t)
        risk = time >= t
        ll += float(eta[dead].sum()) - int(dead.sum()) * float(np.log(np.exp(eta[risk]).sum()))
    return -ll


def fine_gray(
    time: FloatArray,
    cause: IntArray,
    censor_time: FloatArray,
    x: FloatArray,
) -> FloatArray:
    """Fine and Gray subdistribution log hazard ratios for cause 1.

    Valid when every subject's potential censoring time ``censor_time`` is known, as
    with censoring only at a fixed data cut-off. Subjects with cause 2 then stay in the
    risk set until their censoring time with weight one (Fine and Gray 1999, section 3).
    """
    time = np.asarray(time, dtype=float)
    cause = np.asarray(cause, dtype=int)
    t_star = np.where(cause == 2, np.asarray(censor_time, dtype=float), time)
    ev = cause == 1
    x = np.asarray(x, dtype=float)
    res = minimize(
        _cox_negloglik,
        np.zeros(x.shape[1]),
        args=(t_star, ev, x),
        method="BFGS",
    )
    return np.asarray(res.x, dtype=float)

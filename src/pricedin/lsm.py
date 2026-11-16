"""Least-squares Monte Carlo for optimal stopping (WP 3.2).

Longstaff and Schwartz (2001), "Valuing American Options by Simulation: A Simple
Least-Squares Approach", Review of Financial Studies 14(1), 113-147.

On simulated paths of a state variable, the holder of an option to stop (exercise an
option, or build a mine) compares at each date the value of stopping now with the value
of waiting. The value of waiting is not known on a path, so it is estimated by
regressing the realised, discounted cash flow from continuing on functions of the
current state, using only paths where stopping now pays something (the in-the-money
paths, as in the paper). Working backwards from the last date gives a stopping rule;
the option value is the average discounted cash flow under that rule.

Two properties the tests check:

- With one exercise date the method reduces to the European value.
- The estimate is low-biased: the rule is suboptimal on any finite sample, so the
  value converges to the true American value from below as paths and basis grow.
  (Using the same paths to fit and to value adds a small upward bias in the other
  direction; ``out_of_sample`` re-values on fresh paths to remove it.)

This module is generic: it knows nothing about mines. ``pricedin.engine`` will use it
for the build decision (ADR 0037).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

#: Payoff of stopping at step ``k`` given the state on every path, shape ``(n_paths,)``.
Payoff = Callable[[int, FloatArray], FloatArray]


@dataclass(frozen=True)
class StoppingRule:
    """Regression coefficients by step: stop when payoff >= fitted continuation.

    ``coefficients[k]`` is None where no regression was run (the last step, or too few
    in-the-money paths). Before the last step the rule then waits; at the last step it
    stops whenever the payoff is positive.
    """

    coefficients: tuple[FloatArray | None, ...]
    degree: int
    scale: float

    def continuation(self, k: int, state: FloatArray) -> FloatArray:
        """Fitted value of continuing at step ``k``; infinite where no fit exists."""
        coef = self.coefficients[k]
        if coef is None:
            return np.full_like(state, np.inf)
        fitted: FloatArray = _basis(state / self.scale, self.degree) @ coef
        return fitted


@dataclass(frozen=True)
class LSMResult:
    """Value of the option to stop and where each path stopped.

    Attributes:
        value: average discounted cash flow under the fitted rule.
        standard_error: Monte Carlo standard error of ``value``.
        stop_step: step at which each path stopped; -1 if it never stopped.
        rule: the fitted stopping rule, reusable on other paths.

    """

    value: float
    standard_error: float
    stop_step: IntArray
    rule: StoppingRule


def _basis(x: FloatArray, degree: int) -> FloatArray:
    """Monomials 1, x, ..., x^degree of a scaled state."""
    return np.vander(x, degree + 1, increasing=True)


def fit_rule(
    paths: FloatArray,
    payoff: Payoff,
    discount: float,
    *,
    degree: int = 3,
    scale: float | None = None,
    min_in_the_money: int | None = None,
) -> StoppingRule:
    """Fit the stopping rule by backward induction (Longstaff and Schwartz 2001).

    Args:
        paths: state on each path at steps 0..n, shape ``(n_paths, n_steps + 1)``.
            Stopping is allowed at steps 1..n.
        payoff: value of stopping at step k for every path (non-negative).
        discount: discount factor for one step.
        degree: degree of the polynomial basis in the scaled state.
        scale: divisor applied to the state before the basis (numerical conditioning);
            default the mean of the time-0 state.
        min_in_the_money: fewest in-the-money paths needed to regress at a step;
            default ``10 * (degree + 1)``.

    """
    n_paths, n_cols = paths.shape
    n_steps = n_cols - 1
    if n_steps < 1:
        raise ValueError("paths need at least one step after time 0")
    if not 0.0 < discount <= 1.0:
        raise ValueError(f"discount must be in (0, 1], got {discount}")
    scale = float(np.mean(paths[:, 0])) if scale is None else scale
    needed = 10 * (degree + 1) if min_in_the_money is None else min_in_the_money

    coefficients: list[FloatArray | None] = [None] * (n_steps + 1)
    cash = np.asarray(payoff(n_steps, paths[:, n_steps]), dtype=np.float64)
    for k in range(n_steps - 1, 0, -1):
        cash = cash * discount  # value at step k of the cash flow already chosen
        now = np.asarray(payoff(k, paths[:, k]), dtype=np.float64)
        itm = now > 0
        if itm.sum() < needed:
            continue
        x = _basis(paths[itm, k] / scale, degree)
        coef, *_ = np.linalg.lstsq(x, cash[itm], rcond=None)
        coefficients[k] = coef
        stop = np.zeros(n_paths, dtype=bool)
        stop[itm] = now[itm] >= x @ coef
        cash = np.where(stop, now, cash)
    return StoppingRule(coefficients=tuple(coefficients), degree=degree, scale=scale)


def apply_rule(
    rule: StoppingRule, paths: FloatArray, payoff: Payoff, discount: float
) -> tuple[FloatArray, IntArray]:
    """Discounted cash flow at time 0 and stop step on each path, under a rule.

    A path stops at the first step where the payoff is positive and at least the
    fitted continuation value; at the last step it stops if the payoff is positive.
    """
    n_paths, n_cols = paths.shape
    n_steps = n_cols - 1
    value = np.zeros(n_paths)
    stop_step = np.full(n_paths, -1, dtype=np.int64)
    alive = np.ones(n_paths, dtype=bool)
    for k in range(1, n_steps + 1):
        if not alive.any():
            break
        now = np.asarray(payoff(k, paths[:, k]), dtype=np.float64)
        if k == n_steps:
            stop = alive & (now > 0)
        else:
            stop = alive & (now > 0) & (now >= rule.continuation(k, paths[:, k]))
        value[stop] = now[stop] * discount**k
        stop_step[stop] = k
        alive &= ~stop
    return value, stop_step


def value_option(
    paths: FloatArray,
    payoff: Payoff,
    discount: float,
    *,
    degree: int = 3,
    scale: float | None = None,
    out_of_sample: FloatArray | None = None,
    immediate: float | None = None,
) -> LSMResult:
    """Fit the rule on ``paths`` and value it, on fresh paths when given.

    Args:
        paths: fitting paths, shape ``(n_paths, n_steps + 1)``.
        payoff: value of stopping at each step.
        discount: one-step discount factor.
        degree: polynomial degree of the basis.
        scale: state scale for the basis.
        out_of_sample: independent paths to value the fitted rule on; removes the
            in-sample bias at the cost of a second simulation.
        immediate: value of stopping at time 0, if allowed; the result is the larger of
            this and the continuation value.

    """
    rule = fit_rule(paths, payoff, discount, degree=degree, scale=scale)
    valuation_paths = paths if out_of_sample is None else out_of_sample
    cash, stop_step = apply_rule(rule, valuation_paths, payoff, discount)
    value = float(cash.mean())
    se = float(cash.std(ddof=1) / np.sqrt(cash.size)) if cash.size > 1 else 0.0
    if immediate is not None and immediate > value:
        return LSMResult(immediate, 0.0, np.zeros(cash.size, dtype=np.int64), rule)
    return LSMResult(value, se, stop_step, rule)

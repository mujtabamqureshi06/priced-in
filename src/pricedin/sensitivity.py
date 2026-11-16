"""Sensitivities, build-year distribution and a plain-English readout (#63).

The tornado changes one input at a time from a base set of parameters and records the
output each time. The readout is filled from fixed templates and computed numbers only;
there is no free-text generation, so every number in it can be traced to a result.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from pricedin.engine import Market, Results, Risks, Timing, simulate
from pricedin.inputs import Case
from pricedin.report import Step

Params = Mapping[str, Any]


@dataclass(frozen=True)
class Bar:
    """One tornado bar: the output at the low and high alternative of one input."""

    name: str
    low_label: str
    high_label: str
    low: float
    high: float
    base: float

    @property
    def swing(self) -> float:
        """Width of the bar."""
        return abs(self.high - self.low)


def tornado(
    evaluate: Callable[[Params], float],
    base: Params,
    alternatives: Mapping[str, tuple[tuple[str, Any], tuple[str, Any]]],
) -> tuple[Bar, ...]:
    """Bars sorted by swing, widest first.

    Args:
        evaluate: maps a full parameter set to the output (for example a mean value).
        base: the base parameter set.
        alternatives: for each parameter name, a (label, value) pair for its low and
            high alternative.

    """
    base_value = evaluate(base)
    bars = []
    for name, ((lo_label, lo), (hi_label, hi)) in alternatives.items():
        if name not in base:
            raise KeyError(f"'{name}' is not a base parameter")
        low = evaluate({**base, name: lo})
        high = evaluate({**base, name: hi})
        bars.append(Bar(name, lo_label, hi_label, low, high, base_value))
    return tuple(sorted(bars, key=lambda b: b.swing, reverse=True))


def build_year_distribution(results: Results) -> dict[str, float]:
    """Share of paths by build year (years after the valuation date), and never built."""
    n = results.n_paths
    out: dict[str, float] = {}
    built_years = results.build_year[results.built]
    for year in np.unique(built_years):
        out[f"year {int(year)}"] = float((built_years == year).sum() / n)
    out["never built"] = float((~results.built).sum() / n)
    return out


def project_readout(case_name: str, units: str, steps: tuple[Step, ...]) -> str:
    """Two-sentence readout of a waterfall, from a fixed template."""
    study, final = steps[0].value, steps[-1].value
    largest = max(steps[1:], key=lambda s: abs(s.change))
    direction = "lowers" if largest.change < 0 else "raises"
    return (
        f"For {case_name}, the engine values the project at {final:,.0f} {units} "
        f"against the study's {study:,.0f} {units} "
        f"({(final - study) / study:+.0%}). "
        f"The largest single step is {largest.label.lower()}, which {direction} value "
        f"by {abs(largest.change):,.0f} {units}."
    )


@dataclass(frozen=True)
class DelayThreshold:
    """Where one year of delay stops adding project value (ADR 0046).

    Attributes:
        gain: change in project value from one added year of delay, at zero convenience
            yield and no spread.
        convenience_yield: yield at which that change is zero, with no spread; None if
            it is not found below the search limit.
        spread: real spread at which that change is zero, with zero convenience yield;
            None if not found below the search limit.

    """

    gain: float
    convenience_yield: float | None
    spread: float | None


def delay_threshold(
    case: Case,
    spot: float,
    real_rate: float,
    volatility: float,
    timing: Timing,
    risks: Risks,
    *,
    n_paths: int = 50_000,
    seed: int = 1,
    max_yield: float = 0.05,
    max_spread: float = 0.3,
) -> DelayThreshold:
    """Find the convenience yield, and separately the spread, at which delay stops paying.

    With zero convenience yield, expected gold grows at the real rate while costs are
    fixed in real terms, so deferring construction raises project value. Every gate is
    passed; the given overrun and build rule apply. Common random numbers keep the
    comparison of delayed and on-time values smooth.
    """
    passed = replace(risks, stage_odds=1.0)
    later_timing = replace(timing, added_delay=timing.added_delay + 1)

    def gain(y: float, spread: float) -> float:
        drift = float(np.log1p(real_rate)) - y
        market = Market(spot, drift, volatility, real_rate + spread)
        now = simulate(case, market, timing, passed, n_paths=n_paths, seed=seed)
        later = simulate(case, market, later_timing, passed, n_paths=n_paths, seed=seed)
        return float(later.project_value.mean() - now.project_value.mean())

    def root(f: Callable[[float], float], hi: float) -> float | None:
        lo = 0.0
        if f(lo) <= 0 or f(hi) > 0:
            return None
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return 0.5 * (lo + hi)

    return DelayThreshold(
        gain=gain(0.0, 0.0),
        convenience_yield=root(lambda y: gain(y, 0.0), max_yield),
        spread=root(lambda s: gain(0.0, s), max_spread),
    )


def delay_text(d: DelayThreshold) -> str:
    """Describe a delay threshold in plain sentences."""
    if d.gain <= 0:
        return (
            f"One year of delay changes project value by {d.gain:+,.1f} at zero convenience "
            "yield and no spread, so delay does not add value here."
        )
    y = "not reached below 5%" if d.convenience_yield is None else f"{d.convenience_yield:.2%}"
    s = "not reached below 30%" if d.spread is None else f"{d.spread:.2%}"
    return (
        f"One year of delay changes project value by {d.gain:+,.1f} at zero convenience yield "
        f"and no spread. Delay stops adding value at a convenience yield of {y} (no spread), "
        f"or at a real spread of {s} (zero convenience yield)."
    )

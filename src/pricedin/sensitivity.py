"""Sensitivities, build-year distribution and a plain-English readout (WP 1.10).

The tornado changes one input at a time from a base set of parameters and records the
output each time. The readout is filled from fixed templates and computed numbers only;
there is no free-text generation, so every number in it can be traced to a result.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from pricedin.engine import Results
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

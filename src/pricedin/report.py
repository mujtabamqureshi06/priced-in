"""Waterfall: from the study NPV to the engine's value, one named step at a time (WP 1.9).

Risks are switched on one at a time in a fixed order, all on the same random paths:

0. Study NPV (after tax, as published).
1. Discounting at the valuation rate, study deck held flat.
2. Market prices: the gold spot on the valuation date with its market-consistent drift,
   no volatility.
3. Base timing: construction starts ``years_to_start`` years after the valuation date.
4. Capital cost overrun (ADR 0015).
5. Ramp-up: not modelled in the public cases (ADR 0029); reported as zero with that label.
6. Stage failure (ADR 0013).
7. Price uncertainty and the build decision (WP 1.6).

Step sizes depend on the order. The steps sum exactly to the difference between the
final value and the study NPV, because each value is the previous one plus its step.

``shapley_waterfall`` removes the order dependence for the four risk steps (WP 3.5).
Steps 1 and 2 set the valuation basis and stay in sequence. Each risk's step is then its
Shapley value: its average marginal effect over every order in which the four risks
can be switched on (Shapley 1953). That takes 16 runs on the same paths. The Shapley
steps also sum exactly to the total, and a risk whose effect does not depend on the
others gets the same step in either method.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, replace

import numpy as np
from numpy.typing import NDArray

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import Case

FloatArray = NDArray[np.float64]

#: The four risk steps attributed by Shapley value, in the sequential order.
RISK_FACTORS: tuple[str, ...] = (
    "Base timing",
    "Capital cost overrun",
    "Stage failure",
    "Price uncertainty and build decision",
)


@dataclass(frozen=True)
class Step:
    """One bar of the waterfall."""

    label: str
    value: float
    change: float
    standard_error: float
    note: str = ""


def project_waterfall(
    case: Case,
    market: Market,
    timing: Timing,
    risks: Risks,
    *,
    n_paths: int = 10_000,
    seed: int = 0,
) -> tuple[Step, ...]:
    """Waterfall of the project claim, in the case's money units."""
    deck = Market.study_deck(case)
    flat_at_rate = replace(deck, discount_rate=market.discount_rate)
    market_no_vol = replace(market, volatility=0.0)
    base_timing = Timing()
    start = replace(timing, max_wait=0, added_delay=0)
    no_risk = Risks()

    stages: list[tuple[str, Market, Timing, Risks, str]] = [
        ("Discounting at the valuation rate", flat_at_rate, base_timing, no_risk, ""),
        ("Market gold prices", market_no_vol, base_timing, no_risk, ""),
        ("Base timing", market_no_vol, start, no_risk, ""),
        (
            "Capital cost overrun",
            market_no_vol,
            start,
            replace(no_risk, overrun=risks.overrun),
            "",
        ),
        (
            "Ramp-up",
            market_no_vol,
            start,
            replace(no_risk, overrun=risks.overrun),
            "not modelled (ADR 0029)",
        ),
        (
            "Stage failure",
            market_no_vol,
            start,
            replace(no_risk, overrun=risks.overrun, stage_odds=risks.stage_odds),
            "",
        ),
        ("Price uncertainty and build decision", market, timing, risks, ""),
    ]

    study = case.study.npv_after_tax.value
    steps = [Step("Study NPV", study, 0.0, 0.0, "as published")]
    previous = study
    for label, m, t, r, note in stages:
        res = simulate(case, m, t, r, n_paths=n_paths, seed=seed)
        value, se = res.estimate(res.project_value)
        steps.append(Step(label, value, value - previous, se, note))
        previous = value
    return tuple(steps)


def _configuration(
    market: Market, timing: Timing, risks: Risks, on: frozenset[str]
) -> tuple[Market, Timing, Risks]:
    """Engine inputs with only the named risk factors switched on."""
    price = "Price uncertainty and build decision" in on
    years = timing.years_to_start if "Base timing" in on else 0
    return (
        market if price else replace(market, volatility=0.0),
        Timing(years_to_start=years, max_wait=timing.max_wait if price else 0),
        Risks(
            stage_odds=risks.stage_odds if "Stage failure" in on else 1.0,
            overrun=risks.overrun if "Capital cost overrun" in on else None,
            build_rule=risks.build_rule if price else False,
            build_hurdle=risks.build_hurdle,
            decision_rate=risks.decision_rate,
            build_decision=risks.build_decision,
            lsm_degree=risks.lsm_degree,
            lsm_rate=risks.lsm_rate,
        ),
    )


def shapley_waterfall(
    case: Case,
    market: Market,
    timing: Timing,
    risks: Risks,
    *,
    n_paths: int = 10_000,
    seed: int = 0,
) -> tuple[Step, ...]:
    """Waterfall with order-independent risk steps (Shapley values), WP 3.5.

    The first three bars match ``project_waterfall``. Each risk bar is the Shapley
    value of that risk; ramp-up stays a labelled zero (ADR 0029). Standard errors come
    from the per-path Shapley combination, valid because every run uses the same paths.
    """
    sequential = project_waterfall(case, market, timing, risks, n_paths=n_paths, seed=seed)
    head = sequential[:3]
    n = len(RISK_FACTORS)
    values: dict[frozenset[str], FloatArray] = {}
    for size in range(n + 1):
        for combo in itertools.combinations(RISK_FACTORS, size):
            on = frozenset(combo)
            m, t, r = _configuration(market, timing, risks, on)
            values[on] = simulate(case, m, t, r, n_paths=n_paths, seed=seed).project_value

    steps = list(head)
    previous = head[-1].value
    for factor in RISK_FACTORS:
        others = [f for f in RISK_FACTORS if f != factor]
        contribution = np.zeros(n_paths)
        for size in range(n):
            weight = math.factorial(size) * math.factorial(n - size - 1) / math.factorial(n)
            for combo in itertools.combinations(others, size):
                without = frozenset(combo)
                contribution += weight * (values[without | {factor}] - values[without])
        change = float(contribution.mean())
        se = float(contribution.std(ddof=1) / np.sqrt(n_paths)) if n_paths > 1 else 0.0
        previous += change
        steps.append(Step(factor, previous, change, se, "Shapley value"))
        if factor == "Capital cost overrun":
            steps.append(Step("Ramp-up", previous, 0.0, 0.0, "not modelled (ADR 0029)"))
    return tuple(steps)

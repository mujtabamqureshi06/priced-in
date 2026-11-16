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

Step sizes depend on the order; this is a known limitation (WP 1.9), and an
order-independent attribution is planned for Phase 3. The steps sum exactly to the
difference between the final value and the study NPV, because each value is the
previous one plus its step.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import Case


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

"""Inversion: from a royalty price to the odds-timing frontier (WP 2.5).

One price cannot identify both the odds that the project is built and how late it is
built. For each added delay ``d`` (whole years on top of base timing), this module finds
the stage-gate odds ``q(d)`` at which the engine's royalty value equals the price. The
set of pairs ``(d, q(d))`` is the frontier (ADR 0023).

The royalty value is exactly linear in the gate odds, because the gate draw is
independent of the gold price and the overrun:

    value(q, d) = q * V_pass(d) + (1 - q) * V_fail(d)

where ``V_pass`` is the value on paths that pass every gate (built when the build rule
allows, with advances paid until production or until the window closes) and ``V_fail``
is the value of the advances paid until the build-ready year on paths that fail. So

    q(d) = (price - V_fail(d)) / (V_pass(d) - V_fail(d))

needs no root-finding. Both terms are computed on the same price paths (common random
numbers), so the frontier is smooth in ``d``.

A path that fails a stage gate fails at the base build-ready year, whatever the added
delay; the delay applies only to paths that pass, so the axis reads "years late, for a
project that is built" (ADR 0025). If failing projects in fact linger and keep paying
advances, this understates their value and slightly overstates implied odds.

Two numbers summarise the frontier without a timing prior (ADR 0023):

- the zero-delay odds ``q(0)``: the lowest build odds consistent with the price if the
  project keeps to the schedule assumed at the valuation date;
- the certain-build delay: the added delay at which ``q`` reaches 1, interpolated
  linearly between whole years. Beyond it, the price is consistent with certain
  construction only that late or later.

Neither is "the market's odds".
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, replace
from typing import Literal

import numpy as np

from pricedin.engine import Market, Risks, RoyaltyClaim, Timing, simulate
from pricedin.inputs import Case


@dataclass(frozen=True)
class FrontierPoint:
    """Implied gate odds at one added delay.

    Attributes:
        added_delay: whole years added to base timing.
        gate_odds: implied probability of passing every stage gate. Values outside
            [0, 1] mean no odds reproduce the price at this delay.
        gate_odds_se: Monte Carlo standard error of ``gate_odds``.
        build_probability: implied probability the project is ever built: gate odds
            times the share of passing paths the build rule builds.
        value_if_passed: royalty value on paths that pass every gate (case money units).
        value_if_failed: royalty value on paths that fail a gate (advances only).

    """

    added_delay: int
    gate_odds: float
    gate_odds_se: float
    build_probability: float
    value_if_passed: float
    value_if_failed: float
    step_se: float = 0.0

    @property
    def solvable(self) -> bool:
        """Whether some odds in [0, 1] reproduce the price at this delay.

        Above 1 means the price is above the certain-build value at this delay; report
        it as "no solution", never as a probability (ADR 0025).
        """
        return 0.0 <= self.gate_odds <= 1.0


@dataclass(frozen=True)
class Frontier:
    """The odds-timing frontier for one price."""

    price: float
    points: tuple[FrontierPoint, ...]

    @property
    def zero_delay_odds(self) -> float:
        """Implied gate odds with no added delay."""
        return self.points[0].gate_odds

    @property
    def shape(self) -> Literal["rising", "flat", "not monotone"]:
        """Shape of the frontier, allowing for Monte Carlo noise (ADR 0025).

        Each step from one delay to the next is tested against two standard errors of
        that step, computed on the same paths. Any significant fall gives "not
        monotone"; no significant step at all gives "flat" (reported as "flat within
        Monte Carlo error"); otherwise "rising".
        """
        tiny = 1e-9  # floating-point noise when there is no Monte Carlo noise at all
        steps = [(b.gate_odds - a.gate_odds, b.step_se) for a, b in itertools.pairwise(self.points)]
        if any(d < -2.0 * se - tiny for d, se in steps):
            return "not monotone"
        if all(abs(d) <= 2.0 * se + tiny for d, se in steps):
            return "flat"
        return "rising"

    @property
    def certain_build_delay(self) -> float | None:
        """Added delay at which implied odds reach 1, interpolated between whole years.

        Returns 0.0 if the odds are already at or above 1 with no delay, and None if
        they stay below 1 over the whole frontier.
        """
        pts = self.points
        if pts[0].gate_odds >= 1.0:
            return 0.0
        for a, b in itertools.pairwise(pts):
            if b.gate_odds >= 1.0:
                share = (1.0 - a.gate_odds) / (b.gate_odds - a.gate_odds)
                return a.added_delay + share * (b.added_delay - a.added_delay)
        return None


def royalty_frontier(
    case: Case,
    market: Market,
    timing: Timing,
    risks: Risks,
    royalty: RoyaltyClaim,
    price: float,
    *,
    max_delay: int = 15,
    n_paths: int = 10_000,
    seed: int = 0,
) -> Frontier:
    """Implied gate odds for each added delay from 0 to ``max_delay`` years.

    ``risks.stage_odds`` is ignored: it is what the inversion solves for. ``timing``
    gives base timing; its ``added_delay`` is replaced at each step. ``price`` is in the
    case's money units.
    """
    points: list[FrontierPoint] = []
    previous: tuple[np.ndarray, float] | None = None
    for d in range(max_delay + 1):
        t = replace(timing, added_delay=d)
        passed = simulate(
            case,
            market,
            t,
            replace(risks, stage_odds=1.0),
            royalty=royalty,
            n_paths=n_paths,
            seed=seed,
        )
        failed = simulate(
            case,
            market,
            t,
            replace(risks, stage_odds=0.0),
            royalty=royalty,
            n_paths=1,
            seed=seed,
        )
        assert passed.royalty_value is not None and failed.royalty_value is not None
        v_pass, se_pass = passed.estimate(passed.royalty_value)
        v_fail = float(failed.royalty_value[0])
        gap = v_pass - v_fail
        q = (price - v_fail) / gap
        # Delta method: dq/dV_pass = -q / gap. The step's standard error uses the
        # per-path difference, so noise common to both delays cancels.
        weighted = (-q / gap) * passed.royalty_value
        step_se = 0.0
        if previous is not None:
            diff = weighted - previous[0]
            step_se = float(diff.std(ddof=1) / np.sqrt(diff.size)) if diff.size > 1 else 0.0
        previous = (weighted, q)
        points.append(
            FrontierPoint(
                added_delay=d,
                gate_odds=q,
                gate_odds_se=abs(q) * se_pass / abs(gap),
                build_probability=q * float(passed.built.mean()),
                value_if_passed=v_pass,
                value_if_failed=v_fail,
                step_se=step_se,
            )
        )
    return Frontier(price=price, points=tuple(points))

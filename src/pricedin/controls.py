"""Producing-royalty controls: the buyer's spread implied by a royalty price (ADR 0014).

A control is a royalty on a producing mine with a disclosed price and a mine plan that
was public before the deal (ADR 0026). Its royalty cash flows are valued exactly as the
engine values the target in market-consistent mode (ADR 0024): the expected gold price
in year t is spot x (1 + r)^t x e^(-y t), discounted at (1 + r + s)^t. The implied spread
s is the one that makes this value equal the price. The analyst-mode cross-check is the
single real rate that equates the flat-spot cash flows to the price.

Payments fall at the end of each year after the deal date, as in the engine.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Annotated

import numpy as np
import yaml
from pydantic import BaseModel, ConfigDict, Field

NonEmpty = Annotated[str, Field(min_length=1)]


class Sourced(BaseModel):
    """A number with its source."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    value: float
    units: NonEmpty
    source: NonEmpty


class Control(BaseModel):
    """One producing-royalty control."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    name: NonEmpty
    buyer: NonEmpty
    seller: NonEmpty
    operator: NonEmpty
    deal_date: date
    royalty_rate: Sourced
    price: Sourced
    price_sensitivities: dict[str, Sourced] = {}
    share_of_price_in_shares: float = 0.0
    mine_plan_tier: Annotated[int, Field(ge=1, le=2)]
    payable_gold_oz: tuple[float, ...]
    schedule_basis: NonEmpty
    schedule_sensitivities: dict[str, tuple[float, ...]] = {}
    gold_spot: Sourced
    real_rate: Sourced
    notes: str = ""


def load_control(path: Path) -> Control:
    """Load and validate a control YAML file."""
    return Control.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def royalty_value(
    rate: float,
    ounces: tuple[float, ...] | np.ndarray,
    spot: float,
    real_rate: float,
    convenience_yield: float,
    spread: float,
) -> float:
    """Market-consistent value of a gold royalty on a fixed schedule."""
    oz = np.asarray(ounces, dtype=np.float64)
    t = np.arange(1, oz.size + 1, dtype=np.float64)
    growth = (1.0 + real_rate) ** t * np.exp(-convenience_yield * t)
    return float((rate * oz * spot * growth / (1.0 + real_rate + spread) ** t).sum())


def _solve(f: Callable[[float], float], lo: float, hi: float) -> float:
    """Bisection for a decreasing function with a sign change on [lo, hi]."""
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        raise ValueError("no root in the bracket: the price is outside the attainable range")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if f_mid == 0 or hi - lo < 1e-12:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return 0.5 * (lo + hi)


def implied_spread(
    price: float,
    rate: float,
    ounces: tuple[float, ...] | np.ndarray,
    spot: float,
    real_rate: float,
    convenience_yield: float = 0.0,
) -> float:
    """Real spread over the real risk-free rate at which value equals price."""

    def gap(s: float) -> float:
        return royalty_value(rate, ounces, spot, real_rate, convenience_yield, s) - price

    return _solve(gap, -real_rate - 0.5 + 1e-9, 2.0)


def analyst_rate(
    price: float, rate: float, ounces: tuple[float, ...] | np.ndarray, spot: float
) -> float:
    """Single real discount rate equating flat-spot royalty cash flows to the price."""
    oz = np.asarray(ounces, dtype=np.float64)
    t = np.arange(1, oz.size + 1, dtype=np.float64)

    def flat_gap(x: float) -> float:
        return float((rate * oz * spot / (1.0 + x) ** t).sum()) - price

    return _solve(flat_gap, -0.5, 2.0)


def schedule_from_reserves(recoverable_oz: float, annual_oz: float) -> tuple[float, ...]:
    """Tier 2 schedule (ADR 0026): run recoverable reserves at a fixed annual rate."""
    if recoverable_oz <= 0 or annual_oz <= 0:
        raise ValueError("reserves and rate must be positive")
    full = int(recoverable_oz // annual_oz)
    rest = recoverable_oz - full * annual_oz
    return tuple([annual_oz] * full + ([rest] if rest > 1e-9 else []))

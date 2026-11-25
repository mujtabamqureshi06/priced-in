"""Synthetic tests of the Phase 6 scoring helpers (no deal data)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase6_score as sc


def test_interval_score_inside_is_width() -> None:
    assert sc.interval_score(10.0, 20.0, 15.0) == pytest.approx(math.log(2.0))


def test_interval_score_penalises_misses() -> None:
    # Below by a factor e: width ln 2 plus (2 / 0.2) * 1.
    assert sc.interval_score(10.0, 20.0, 10.0 / math.e) == pytest.approx(math.log(2) + 10.0)
    assert sc.interval_score(10.0, 20.0, 20.0 * math.e) == pytest.approx(math.log(2) + 10.0)


def test_centred_range_has_the_width() -> None:
    lo, hi = sc.centred(100.0, 1.0)
    assert math.log(hi / lo) == pytest.approx(1.0)
    assert math.sqrt(lo * hi) == pytest.approx(100.0)


def test_clopper_pearson_known_values() -> None:
    lo, hi = sc.clopper_pearson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.3085, abs=1e-4)
    lo, hi = sc.clopper_pearson(10, 10)
    assert lo == pytest.approx(0.6915, abs=1e-4) and hi == 1.0


def test_implied_spread_interpolates_and_bounds() -> None:
    s, v = [0.0, 0.1], [200.0, 100.0]
    assert sc.implied_spread(s, v, 200.0) == pytest.approx(0.0)
    assert sc.implied_spread(s, v, math.sqrt(200 * 100)) == pytest.approx(0.05)
    assert sc.implied_spread(s, v, 300.0) is None

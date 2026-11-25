"""Synthetic tests of the Phase 6 freeze script's helpers (no deal data)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase6_freeze as fz

from pricedin import deal_pricer as dp


def test_stage_of() -> None:
    assert fz.stage_of("DFS") == "FS"
    assert fz.stage_of("pfs") == "PFS"
    with pytest.raises(ValueError):
        fz.stage_of("scoping")


def test_stated_inflation() -> None:
    assert fz.stated_inflation("2% (stated in FY2017 comparative)") == pytest.approx(0.02)
    assert fz.stated_inflation("") is None
    assert fz.stated_inflation("not stated") is None


def _royalty_input(**kw: object) -> dict[str, object]:
    d: dict[str, object] = {
        "instrument": "royalty",
        "covered_share": 0.7,
        "offsite_cost_per_oz": 5.0,
        "royalty": {
            "rate": 0.02,
            "kind": "NSR",
            "steps": [],
            "step_basis": "unspecified",
            "cap": 1_000_000,
            "advance": None,
            "buyback": "none",
        },
    }
    d.update(kw)
    return d


def test_claim_from_royalty_input() -> None:
    c = fz.claim_from_input(_royalty_input(), inflation=0.02)
    assert isinstance(c, dp.RoyaltyTerms)
    assert (c.rate, c.coverage, c.offsite_cost_per_oz, c.cap) == (0.02, 0.7, 5.0, 1_000_000.0)
    assert c.inflation == 0.02  # a nominal cap is deflated at the breakeven rate
    assert c.step_basis == "covered"  # no steps, so the basis does not matter
    no_cap = _royalty_input()
    no_cap["royalty"] = {**no_cap["royalty"], "cap": None}  # type: ignore[dict-item]
    assert fz.claim_from_input(no_cap, inflation=0.02).inflation == 0.0


def test_claim_from_stream_input() -> None:
    d = {
        "instrument": "stream",
        "covered_share": 1.0,
        "stream": {
            "share": 0.1,
            "payment": "share_of_spot",
            "fixed_price": None,
            "escalation": None,
            "escalation_from": None,
            "spot_share": 0.2,
            "steps": [{"threshold": 1000, "share": 0.05}],
            "step_basis": "delivered",
            "buyback": "none",
        },
    }
    c = fz.claim_from_input(d, inflation=0.02)
    assert isinstance(c, dp.StreamTerms)
    assert (c.share, c.spot_share, c.fixed_price, c.inflation) == (0.1, 0.2, 0.0, 0.0)
    assert c.steps == (dp.DeliveryStep(1000.0, 0.05),)


def test_benchmark_hand_case() -> None:
    # 1% gross royalty, 100 oz in year 1, deck 1,000, rate 5%, no pre-production:
    # one payment of 1,000 at t = 1, worth 1,000 / 1.05.
    c = dp.RoyaltyTerms(rate=0.01, kind="GRR")
    assert fz.benchmark(c, [100.0], 1000.0, 0.05, 0.0) == pytest.approx(1000 / 1.05)
    # One year of pre-production pushes it to t = 2.
    assert fz.benchmark(c, [100.0], 1000.0, 0.05, 1.0) == pytest.approx(1000 / 1.05**2)

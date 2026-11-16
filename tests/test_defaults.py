"""Engine settings read from the priors registry by id."""

from pathlib import Path

import pytest

from pricedin import defaults
from pricedin.priors import load_priors

ROOT = Path(__file__).resolve().parents[1]
PRIORS = load_priors(ROOT / "data" / "priors.yaml")


def test_stage_odds_follow_the_registry() -> None:
    fs = defaults.fixed_value(PRIORS, "stage.fs_to_build")
    pfs = defaults.fixed_value(PRIORS, "stage.pfs_to_fs")
    assert defaults.stage_odds(PRIORS, "FS") == fs
    assert defaults.stage_odds(PRIORS, "PFS") == pytest.approx(pfs * fs)


def test_pea_stage_has_no_default() -> None:
    with pytest.raises(ValueError, match="user assumption"):
        defaults.stage_odds(PRIORS, "PEA")


def test_overrun_and_financing_come_from_their_priors() -> None:
    o = defaults.overrun(PRIORS, "FS")
    assert o.real_factor == defaults.fixed_value(PRIORS, "capex.inflation_adjustment")
    f = defaults.equity_financing(PRIORS)
    assert f.issue_discount == defaults.fixed_value(PRIORS, "equity.issue_discount")


def test_timing_uses_the_case_prior_and_build_window() -> None:
    t = defaults.timing(PRIORS, "south_railroad_fs2022")
    assert t.years_to_start == defaults.fixed_value(
        PRIORS, "timing.years_to_start.south_railroad_fs2022"
    )
    assert t.max_wait == defaults.fixed_value(PRIORS, "build.window_years")


def test_a_distribution_is_not_a_fixed_value() -> None:
    with pytest.raises(ValueError, match="not a fixed value"):
        defaults.fixed_value(PRIORS, "capex.overrun.fs")

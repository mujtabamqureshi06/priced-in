"""Engine settings read from the priors registry by id (ADRs 0013, 0015, 0030).

Scripts and the app call these instead of retyping registry values, so a change to
`data/priors.yaml` reaches every result.
"""

from __future__ import annotations

from pricedin.engine import Financing, Overrun, Timing
from pricedin.inputs import StudyStage
from pricedin.priors import Fixed, PriorsRegistry, ShiftedLognormal


def fixed_value(registry: PriorsRegistry, prior_id: str) -> float:
    """Return the value of a fixed prior; raise if the prior is a distribution."""
    dist = registry.get(prior_id).distribution
    if not isinstance(dist, Fixed):
        raise ValueError(f"prior '{prior_id}' is not a fixed value")
    return dist.value


def stage_odds(registry: PriorsRegistry, stage: StudyStage | str) -> float:
    """Return the odds of reaching a construction decision from a study stage (ADR 0013).

    FS uses the FS-to-build prior; PFS multiplies in the PFS-to-FS prior. There is no
    default for PEA or earlier: the caller must supply its own value and label it as a
    user assumption.
    """
    stage = StudyStage(stage)
    fs = fixed_value(registry, "stage.fs_to_build")
    if stage == StudyStage.FS:
        return fs
    if stage == StudyStage.PFS:
        return fixed_value(registry, "stage.pfs_to_fs") * fs
    raise ValueError(
        f"no default stage odds for a {stage.value}-stage case; "
        "supply a value and label it as a user assumption"
    )


def overrun(registry: PriorsRegistry, stage: StudyStage | str) -> Overrun:
    """Return the capital overrun for the study stage, in real terms (ADR 0015)."""
    stage = StudyStage(stage)
    if stage not in (StudyStage.FS, StudyStage.PFS):
        raise ValueError(f"no overrun prior for a {stage.value}-stage case")
    dist = registry.get(f"capex.overrun.{stage.value.lower()}").distribution
    if not isinstance(dist, ShiftedLognormal):
        raise ValueError("the overrun prior must be a shifted lognormal")
    return Overrun(dist, fixed_value(registry, "capex.inflation_adjustment"))


def equity_financing(registry: PriorsRegistry) -> Financing:
    """Return the debt share and equity issue discount for the equity claim (ADR 0030)."""
    return Financing(
        fixed_value(registry, "equity.debt_fraction"),
        fixed_value(registry, "equity.issue_discount"),
    )


def timing(registry: PriorsRegistry, case_id: str) -> Timing:
    """Return base timing: years to start from the case prior, build window from the registry."""
    return Timing(
        years_to_start=int(fixed_value(registry, f"timing.years_to_start.{case_id}")),
        max_wait=int(fixed_value(registry, "build.window_years")),
    )

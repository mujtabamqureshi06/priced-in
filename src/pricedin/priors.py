"""Priors registry: every calibration assumption, with its source and verification status.

The registry lives in ``data/priors.yaml``. Each entry is validated on load. An entry
without a source, a location or units is rejected, so no assumption can enter the
engine as an unsourced number. Code refers to priors by ``id`` only.

Status codes follow ``docs/sources.md``:

- ``V``: verified against the primary document.
- ``V-abs``: verified from the abstract or citation only.
- ``S``: seen only in a secondary summary.
- ``P``: practitioner or industry source, not peer-reviewed.

Entries with status ``S`` must carry a flag. A flagged prior can be used, but every
output that depends on it must show the flag text (ADR 0013).
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

NonEmpty = Annotated[str, Field(min_length=1)]


class Status(StrEnum):
    """Verification status of a prior's source."""

    VERIFIED = "V"
    VERIFIED_ABSTRACT = "V-abs"
    SECONDARY = "S"
    PRACTITIONER = "P"


class Fixed(BaseModel):
    """A single value with no uncertainty."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["fixed"]
    value: float


class Uniform(BaseModel):
    """Uniform distribution on [low, high]."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["uniform"]
    low: float
    high: float

    @model_validator(mode="after")
    def _ordered(self) -> Uniform:
        if not self.low < self.high:
            raise ValueError(f"uniform requires low < high, got low={self.low}, high={self.high}")
        return self


class Triangular(BaseModel):
    """Triangular distribution with lower bound, mode and upper bound."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["triangular"]
    low: float
    mode: float
    high: float

    @model_validator(mode="after")
    def _ordered(self) -> Triangular:
        if not (self.low <= self.mode <= self.high and self.low < self.high):
            raise ValueError(
                "triangular requires low <= mode <= high and low < high, "
                f"got low={self.low}, mode={self.mode}, high={self.high}"
            )
        return self


class ShiftedLognormal(BaseModel):
    """Lognormal variable plus a shift: X = shift + exp(N(mu, sigma)).

    Bertisen and Davis (2008) recommend this form for capital cost outcomes.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["shifted_lognormal"]
    mu: float
    sigma: Annotated[float, Field(gt=0)]
    shift: float = 0.0


Distribution = Annotated[
    Fixed | Uniform | Triangular | ShiftedLognormal, Field(discriminator="kind")
]


class AppliesTo(BaseModel):
    """Scope of a prior. ``None`` means the prior is not restricted on that dimension."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stage: str | None = None
    commodity: str | None = None
    jurisdiction: str | None = None


class Alternative(BaseModel):
    """A named value used only in sensitivity analysis, never as the default.

    ``status`` is ``None`` when the value is a stated judgment rather than a sourced
    figure; ``source`` must then read "judgment".
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    label: NonEmpty
    value: float
    source: NonEmpty
    status: Status | None = None

    @model_validator(mode="after")
    def _judgment_or_sourced(self) -> Alternative:
        if self.status is None and self.source != "judgment":
            raise ValueError(
                f"alternative '{self.label}' has no status, so its source must be 'judgment'"
            )
        return self


class Prior(BaseModel):
    """One registry entry.

    ``flag`` holds the caveat text that every output using this prior must show.
    An empty flag means the prior carries no caveat.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Annotated[str, Field(pattern=r"^[a-z0-9_.]+$")]
    description: NonEmpty
    distribution: Distribution
    units: NonEmpty
    applies_to: AppliesTo = AppliesTo()
    source: NonEmpty
    location: NonEmpty
    status: Status
    flag: str = ""
    sensitivity: tuple[Alternative, ...] = ()
    decision: str = ""
    notes: str = ""

    @property
    def flagged(self) -> bool:
        """Whether outputs using this prior must show a caveat."""
        return bool(self.flag)

    @model_validator(mode="after")
    def _secondary_must_be_flagged(self) -> Prior:
        if self.status is Status.SECONDARY and not self.flagged:
            raise ValueError(f"prior '{self.id}' has status S and must set a flag")
        return self


class PriorsRegistry(BaseModel):
    """All priors, keyed by id."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    priors: dict[str, Prior]

    def get(self, prior_id: str) -> Prior:
        """Return the prior with this id, or raise KeyError naming the missing id."""
        try:
            return self.priors[prior_id]
        except KeyError:
            raise KeyError(f"no prior with id '{prior_id}' in the registry") from None

    def flagged(self) -> list[Prior]:
        """Return every prior marked as flagged, in id order."""
        return [p for _, p in sorted(self.priors.items()) if p.flagged]


def load_priors(path: Path) -> PriorsRegistry:
    """Load and validate a priors file.

    The file holds a top-level ``priors`` list. Duplicate ids are rejected.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("priors"), list):
        raise ValueError(f"{path}: expected a top-level 'priors' list")
    entries = [Prior.model_validate(item) for item in raw["priors"]]
    by_id: dict[str, Prior] = {}
    for entry in entries:
        if entry.id in by_id:
            raise ValueError(f"{path}: duplicate prior id '{entry.id}'")
        by_id[entry.id] = entry
    return PriorsRegistry(priors=by_id)

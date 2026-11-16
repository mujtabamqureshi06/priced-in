"""Market snapshots: dated market observations for one valuation date (ADR 0007).

Each observation carries its value, units, source, series identifier, the date it was
observed and its verification status. Observations dated after the snapshot date are
rejected, so a valuation cannot use information that did not exist yet.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pricedin.priors import Status

NonEmpty = Annotated[str, Field(min_length=1)]


class Observation(BaseModel):
    """One market number with its provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    value: float
    units: NonEmpty
    observed: date
    source: NonEmpty
    series: NonEmpty
    status: Status
    notes: str = ""


class Snapshot(BaseModel):
    """All market observations for one valuation date."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    as_of: date
    observations: dict[str, Observation]

    @model_validator(mode="after")
    def _no_look_ahead(self) -> Snapshot:
        late = sorted(k for k, o in self.observations.items() if o.observed > self.as_of)
        if late:
            raise ValueError(f"observations dated after {self.as_of}: {', '.join(late)}")
        return self

    def value(self, key: str) -> float:
        """Return an observation's value; raise KeyError naming the snapshot if absent."""
        if key not in self.observations:
            raise KeyError(f"snapshot {self.as_of} has no observation '{key}'")
        return self.observations[key].value


def load_snapshot(path: Path) -> Snapshot:
    """Load and validate a snapshot YAML file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Snapshot.model_validate(raw)

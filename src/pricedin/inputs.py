"""Case input template: the numbers taken from a technical report, each traceable to a page.

A case file records one project as of one valuation date (ADR 0007). Every number
carries a reference to a document listed in the case and a location in it (page or
table), so a reader can check each value against the source.

Two input modes are planned. This module implements **schedule mode**: the report's
own annual cash-flow table is entered row by row, so the engine can reproduce the
study NPV exactly with every risk switched off. Build-up mode (tonnes, grade and
costs) comes later.

Money is entered in the units the report uses, stated in the column name (for example
``_usd_k`` for thousands of US dollars), to avoid conversion errors at entry.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

NonEmpty = Annotated[str, Field(min_length=1)]
Fraction = Annotated[float, Field(ge=0.0, le=1.0)]

#: Columns every schedule-mode case must provide.
REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {
        "payable_gold_koz",
        "initial_capex_usd_k",
        "cash_flow_pre_tax_usd_k",
        "cash_flow_after_tax_usd_k",
    }
)

#: Tolerance when checking a column against the report's own total (report units).
#: Reports round each cell, so totals can differ from the sum by a few units.
TOTAL_TOLERANCE = 2.0


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class StudyStage(StrEnum):
    """Stage of the project at the valuation date."""

    PEA = "PEA"
    PFS = "PFS"
    FS = "FS"
    CONSTRUCTION = "construction"
    PRODUCING = "producing"


class Document(_Strict):
    """A public document the case draws on. Never stored in the repository (ADR 0003)."""

    id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    title: NonEmpty
    issuer: NonEmpty
    date: date
    url: NonEmpty


class SourceRef(_Strict):
    """Where a value comes from: a document id from the case and a location in it."""

    document: NonEmpty
    location: NonEmpty


class Quantity(_Strict):
    """A single sourced number."""

    value: float
    units: NonEmpty
    source: SourceRef


class Discounting(_Strict):
    """How the study discounts its cash-flow table.

    ``t0_column`` is the schedule column discounted with exponent zero; later columns
    are discounted at whole-year steps (end-of-year convention). This is checked by
    reproducing the study NPV from the table.
    """

    t0_column: NonEmpty
    convention: Annotated[str, Field(pattern=r"^end_of_year$")] = "end_of_year"
    source: SourceRef


class Study(_Strict):
    """The technical study the case is valued on."""

    stage: StudyStage
    document: NonEmpty
    effective_date: date
    price_deck: dict[str, Quantity]
    discount_rate: Quantity
    npv_pre_tax_usd_k: Quantity
    npv_after_tax_usd_k: Quantity
    irr_after_tax: Quantity
    discounting: Discounting
    tax_summary: NonEmpty


class Column(_Strict):
    """One row of the report's cash-flow table: a value per period, plus the report's total."""

    values: tuple[float, ...]
    total: float | None = None
    source: SourceRef


class Schedule(_Strict):
    """The report's annual table, transcribed. Periods are the report's own labels."""

    periods: tuple[NonEmpty, ...]
    columns: dict[str, Column]

    @model_validator(mode="after")
    def _consistent(self) -> Schedule:
        missing = REQUIRED_COLUMNS - self.columns.keys()
        if missing:
            raise ValueError(f"schedule is missing required columns: {sorted(missing)}")
        n = len(self.periods)
        for name, col in self.columns.items():
            if len(col.values) != n:
                raise ValueError(
                    f"column '{name}' has {len(col.values)} values but there are {n} periods"
                )
            if col.total is not None and abs(sum(col.values) - col.total) > TOTAL_TOLERANCE:
                raise ValueError(
                    f"column '{name}' sums to {sum(col.values):,.1f} but the report total is "
                    f"{col.total:,.1f}; check the transcription"
                )
        return self


class Royalty(_Strict):
    """A royalty on the project, as disclosed."""

    holder: NonEmpty
    kind: Annotated[str, Field(pattern=r"^(NSR|GRR|NPI|stream)$")]
    rate: Quantity
    coverage_fraction: Quantity
    advance_minimum_per_year: Quantity | None = None
    advance_minimum_credited: bool | None = None
    notes: str = ""

    @model_validator(mode="after")
    def _fractions(self) -> Royalty:
        for label, q in (("rate", self.rate), ("coverage_fraction", self.coverage_fraction)):
            if not 0.0 <= q.value <= 1.0:
                raise ValueError(f"royalty {label} must be a fraction in [0, 1], got {q.value}")
        return self


class Status(_Strict):
    """Permitting, financing and construction status at the valuation date."""

    permitted: bool
    financed: bool
    construction_decision: bool
    source: SourceRef


class Case(_Strict):
    """One project, as of one valuation date."""

    id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    name: NonEmpty
    operator: NonEmpty
    jurisdiction: NonEmpty
    commodity: NonEmpty
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    as_of: date
    operator_share: Fraction
    documents: tuple[Document, ...]
    study: Study
    status: Status
    schedule: Schedule
    royalties: tuple[Royalty, ...] = ()
    notes: str = ""

    @model_validator(mode="after")
    def _references_and_dates(self) -> Case:
        docs = {d.id: d for d in self.documents}
        if len(docs) != len(self.documents):
            raise ValueError("document ids must be unique")
        for ref in self._all_refs():
            if ref.document not in docs:
                raise ValueError(f"source refers to unknown document '{ref.document}'")
        if self.study.document not in docs:
            raise ValueError(f"study refers to unknown document '{self.study.document}'")
        late = [d.id for d in self.documents if d.date > self.as_of]
        if late:
            raise ValueError(
                f"documents dated after the valuation date {self.as_of} are not allowed "
                f"(no look-ahead, ADR 0007): {late}"
            )
        if self.study.discounting.t0_column not in self.schedule.periods:
            raise ValueError(
                f"discounting t0_column '{self.study.discounting.t0_column}' is not a period"
            )
        return self

    def _all_refs(self) -> list[SourceRef]:
        refs = [
            self.status.source,
            self.study.discount_rate.source,
            self.study.npv_pre_tax_usd_k.source,
            self.study.npv_after_tax_usd_k.source,
            self.study.irr_after_tax.source,
            self.study.discounting.source,
            *(q.source for q in self.study.price_deck.values()),
            *(c.source for c in self.schedule.columns.values()),
        ]
        for r in self.royalties:
            refs += [r.rate.source, r.coverage_fraction.source]
            if r.advance_minimum_per_year is not None:
                refs.append(r.advance_minimum_per_year.source)
        return refs


def load_case(path: Path) -> Case:
    """Load and validate a case file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Case.model_validate(raw)

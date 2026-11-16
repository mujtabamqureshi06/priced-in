"""The royalty transaction dataset (#73): ``data/transactions.csv``.

One row per disclosed deal. Only deals with a public economic study at the deal date are
modelled (scope ``modelled`` or ``planned``); producing-royalty controls have scope
``control``; everything else is kept for completeness with scope ``listed`` and a reason.
Sellers are described by type only (for example "private family"), never by name.
"""

from __future__ import annotations

import csv
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

NonEmpty = Annotated[str, Field(min_length=1)]


class Scope(StrEnum):
    """How a deal is used."""

    MODELLED = "modelled"
    PLANNED = "planned"
    CONTROL = "control"
    LISTED = "listed"


class Transaction(BaseModel):
    """One royalty deal, as disclosed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    announced: date | None
    completed: date | None
    buyer: NonEmpty
    seller: NonEmpty
    asset: NonEmpty
    operator_at_deal: NonEmpty
    jurisdiction: NonEmpty
    commodities: tuple[NonEmpty, ...]
    royalty_type: Annotated[str, Field(pattern=r"^(NSR|GVR|GRR|NPI|stream|mixed)$")]
    rate: Annotated[float, Field(gt=0, le=1)] | None
    coverage: NonEmpty
    price: Annotated[float, Field(gt=0)]
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    price_usd: Annotated[float, Field(gt=0)]
    payment: NonEmpty
    fees: NonEmpty
    stage_at_deal: NonEmpty
    study: NonEmpty
    study_date: date | None
    scope: Scope
    scope_note: NonEmpty
    sources: tuple[NonEmpty, ...]
    verification: Annotated[str, Field(pattern=r"^(V|P|U)$")]

    @field_validator("announced", "completed", "study_date", "rate", mode="before")
    @classmethod
    def _blank_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("commodities", mode="before")
    @classmethod
    def _split_commodities(cls, value: object) -> object:
        return tuple(v.strip() for v in value.split(";")) if isinstance(value, str) else value

    @field_validator("sources", mode="before")
    @classmethod
    def _split_sources(cls, value: object) -> object:
        return tuple(v.strip() for v in value.split("|")) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _consistent(self) -> Transaction:
        if self.announced is None and self.completed is None:
            raise ValueError(f"{self.deal_id}: needs an announcement or completion date")
        if self.announced and self.completed and self.completed < self.announced:
            raise ValueError(f"{self.deal_id}: completed before it was announced")
        deal_date = self.announced or self.completed
        if self.study_date and deal_date and self.study_date > deal_date:
            raise ValueError(f"{self.deal_id}: study dated after the deal (look-ahead)")
        if self.currency == "USD" and self.price != self.price_usd:
            raise ValueError(f"{self.deal_id}: a US$ price must equal price_usd")
        if self.scope in (Scope.MODELLED, Scope.PLANNED):
            if self.study == "none" or self.study_date is None:
                raise ValueError(f"{self.deal_id}: a modelled deal needs a dated public study")
            if self.rate is None or self.royalty_type == "mixed":
                raise ValueError(f"{self.deal_id}: a modelled deal needs a single royalty rate")
        return self

    @property
    def deal_date(self) -> date:
        """The announcement date, or the completion date when no announcement is listed."""
        chosen = self.announced or self.completed
        assert chosen is not None  # guaranteed by the validator
        return chosen


def load_transactions(path: Path) -> list[Transaction]:
    """Load and validate the transaction dataset; deal ids must be unique."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [Transaction.model_validate(row) for row in csv.DictReader(handle)]
    ids = [r.deal_id for r in rows]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate deal ids: {duplicates}")
    return rows

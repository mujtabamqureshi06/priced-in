"""Tests for the royalty transaction dataset (WP 2.7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from pricedin.transactions import Scope, Transaction, load_transactions

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "transactions.csv"


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "deal_id": "example",
        "announced": "2021-06-07",
        "completed": "",
        "buyer": "Buyer",
        "seller": "private seller",
        "asset": "Asset",
        "operator_at_deal": "Operator",
        "jurisdiction": "Nevada",
        "commodities": "gold",
        "royalty_type": "NSR",
        "rate": "0.01",
        "coverage": "all",
        "price": "1000000",
        "currency": "USD",
        "price_usd": "1000000",
        "payment": "cash",
        "fees": "none",
        "stage_at_deal": "PFS",
        "study": "PFS",
        "study_date": "2020-01-01",
        "scope": "modelled",
        "scope_note": "case file",
        "sources": "https://example.org/a | https://example.org/b",
        "verification": "V",
    }
    row.update(overrides)
    return row


def test_repository_dataset_loads() -> None:
    deals = load_transactions(DATASET)
    ids = {d.deal_id for d in deals}
    assert {"vox_south_railroad_2021", "vox_sorby_hills_2026", "vox_white_dam_2026"} <= ids
    assert all(d.sources for d in deals)


def test_every_case_file_named_in_the_dataset_exists() -> None:
    for deal in load_transactions(DATASET):
        for part in deal.scope_note.split(";"):
            token = part.strip().split(" ")[0]
            if token.endswith(".yaml"):
                assert (ROOT / token).exists(), token


def test_only_deals_with_a_dated_study_are_modelled() -> None:
    for deal in load_transactions(DATASET):
        if deal.scope in (Scope.MODELLED, Scope.PLANNED):
            assert deal.study_date is not None
            assert deal.study_date <= deal.deal_date


def test_parsing_splits_lists_and_blanks() -> None:
    deal = Transaction.model_validate(_row(commodities="gold;silver"))
    assert deal.commodities == ("gold", "silver")
    assert deal.sources == ("https://example.org/a", "https://example.org/b")
    assert deal.completed is None


def test_rejects_a_study_published_after_the_deal() -> None:
    with pytest.raises(ValueError, match="look-ahead"):
        Transaction.model_validate(_row(study_date="2022-01-01"))


def test_rejects_a_modelled_deal_without_a_study() -> None:
    with pytest.raises(ValueError, match="dated public study"):
        Transaction.model_validate(_row(study="none", study_date=""))


def test_rejects_inconsistent_usd_price() -> None:
    with pytest.raises(ValueError, match="price_usd"):
        Transaction.model_validate(_row(price_usd="999"))


def test_rejects_duplicate_ids(tmp_path: Path) -> None:
    lines = DATASET.read_text(encoding="utf-8").splitlines()
    path = tmp_path / "dup.csv"
    path.write_text("\n".join([*lines, lines[1]]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_transactions(path)

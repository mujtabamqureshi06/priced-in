from pathlib import Path

import pytest
import yaml

from pricedin.snapshots import Snapshot, load_snapshot

SNAPSHOTS = Path(__file__).resolve().parents[1] / "data" / "snapshots"


@pytest.mark.parametrize("name", ["2021-06-07", "2023-07-13"])
def test_snapshots_load_and_cover_the_inputs(name: str) -> None:
    snap = load_snapshot(SNAPSHOTS / f"{name}.yaml")
    assert snap.as_of.isoformat() == name
    for key in ("gold_spot", "real_yield_10y", "breakeven_10y", "gvz", "realised_vol_10y"):
        assert snap.value(key) == snap.observations[key].value
    assert 1000 < snap.value("gold_spot") < 3000
    assert -0.05 < snap.value("real_yield_10y") < 0.05


def test_south_railroad_snapshot_has_fx() -> None:
    snap = load_snapshot(SNAPSHOTS / "2021-06-07.yaml")
    assert snap.value("usdcad") == pytest.approx(1.2062)


def test_observation_after_as_of_rejected() -> None:
    raw = yaml.safe_load((SNAPSHOTS / "2021-06-07.yaml").read_text(encoding="utf-8"))
    raw["observations"]["gold_spot"]["observed"] = "2021-06-08"
    with pytest.raises(ValueError, match="after 2021-06-07"):
        Snapshot.model_validate(raw)


def test_missing_observation_names_the_snapshot() -> None:
    snap = load_snapshot(SNAPSHOTS / "2023-07-13.yaml")
    with pytest.raises(KeyError, match="2023-07-13"):
        snap.value("usdcad")


@pytest.mark.parametrize("name", ["2023-12-15", "2023-12-18", "2024-02-23"])
def test_osino_deal_snapshots(name: str) -> None:
    snap = load_snapshot(SNAPSHOTS / f"{name}.yaml")
    for key in ("gold_spot", "real_yield_10y", "usdcad", "realised_vol_10y"):
        assert snap.value(key) > 0

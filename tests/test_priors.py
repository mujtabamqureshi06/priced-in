from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from pricedin.priors import Prior, Status, load_priors


def _entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "capex.overrun.fs",
        "description": "Capital cost outcome as a multiple of the FS estimate",
        "distribution": {"kind": "shifted_lognormal", "mu": 0.0, "sigma": 0.3, "shift": 0.0},
        "units": "multiple of FS initial capex",
        "source": "Bertisen and Davis (2008)",
        "location": "The Engineering Economist 53(2):118-139",
        "status": "V-abs",
    }
    base.update(overrides)
    return base


def _write(tmp_path: Path, entries: list[dict[str, Any]]) -> Path:
    path = tmp_path / "priors.yaml"
    path.write_text(yaml.safe_dump({"priors": entries}), encoding="utf-8")
    return path


def test_loads_valid_entry(tmp_path: Path) -> None:
    registry = load_priors(_write(tmp_path, [_entry()]))
    prior = registry.get("capex.overrun.fs")
    assert prior.status is Status.VERIFIED_ABSTRACT
    assert prior.distribution.kind == "shifted_lognormal"


@pytest.mark.parametrize("missing", ["source", "units", "location", "status"])
def test_rejects_entry_missing_required_field(missing: str) -> None:
    entry = _entry()
    del entry[missing]
    with pytest.raises(ValidationError, match=missing):
        Prior.model_validate(entry)


@pytest.mark.parametrize("field", ["source", "units", "location"])
def test_rejects_empty_required_text(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        Prior.model_validate(_entry(**{field: ""}))


def test_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError, match="status"):
        Prior.model_validate(_entry(status="verified"))


def test_secondary_source_must_be_flagged() -> None:
    with pytest.raises(ValidationError, match="must set a flag"):
        Prior.model_validate(_entry(status="S"))
    assert Prior.model_validate(_entry(status="S", flag="secondary source only")).flagged


def test_rejects_duplicate_ids(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="duplicate prior id"):
        load_priors(_write(tmp_path, [_entry(), _entry()]))


def test_rejects_file_without_priors_list(tmp_path: Path) -> None:
    path = tmp_path / "priors.yaml"
    path.write_text("other: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="top-level 'priors' list"):
        load_priors(path)


def test_unknown_id_error_names_the_id(tmp_path: Path) -> None:
    registry = load_priors(_write(tmp_path, [_entry()]))
    with pytest.raises(KeyError, match=r"stage\.fs_to_build"):
        registry.get("stage.fs_to_build")


@pytest.mark.parametrize(
    "dist",
    [
        {"kind": "uniform", "low": 0.9, "high": 0.3},
        {"kind": "triangular", "low": 0.3, "mode": 0.99, "high": 0.95},
        {"kind": "shifted_lognormal", "mu": 0.0, "sigma": 0.0},
        {"kind": "beta", "a": 1.0, "b": 1.0},
    ],
)
def test_rejects_invalid_distributions(dist: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Prior.model_validate(_entry(distribution=dist))


def test_flagged_lists_only_flagged_priors(tmp_path: Path) -> None:
    entries = [
        _entry(),
        _entry(id="stage.fs_to_build", status="S", flag="secondary source only"),
    ]
    registry = load_priors(_write(tmp_path, entries))
    assert [p.id for p in registry.flagged()] == ["stage.fs_to_build"]


def test_alternative_without_status_must_be_judgment() -> None:
    bad = {"label": "stress low", "value": 0.5, "source": "AMC"}
    with pytest.raises(ValidationError, match="judgment"):
        Prior.model_validate(_entry(sensitivity=[bad]))
    good = {"label": "stress low", "value": 0.5, "source": "judgment"}
    assert Prior.model_validate(_entry(sensitivity=[good])).sensitivity[0].value == 0.5


def test_repository_registry_is_valid() -> None:
    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    fs = registry.get("stage.fs_to_build")
    assert fs.distribution.kind == "fixed"
    assert {a.value for a in fs.sensitivity} == {0.75, 0.5, 0.95}
    assert all(p.flagged for p in registry.priors.values() if p.id.startswith("stage."))

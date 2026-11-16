import re
import tomllib
from pathlib import Path

import pricedin

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_version_matches_pyproject() -> None:
    declared = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    assert pricedin.__version__ == declared


def test_version_is_semantic() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", pricedin.__version__)

"""Extract gold projects from Resources and Energy Major Projects data files (ADR 0051).

The Australian Government's annual Resources and Energy Major Projects (REMP) reports
are the Phase 4 candidate list (protocol section 8). Each edition ships an Excel data
file with one sheet per commodity. This script reads the "Gold" sheet of every edition
given, maps columns by their header names (the layout changes between editions), and
writes one row per project per edition to ``data/phase4/remp_gold.csv``.

The data files are not stored in this repository. Download them from
https://www.industry.gov.au/remp (each edition's "data" spreadsheet), then run:

    uv run --with openpyxl python scripts/phase4_candidates.py FILE [FILE ...]

Source: Department of Industry, Science and Resources, Office of the Chief Economist,
Resources and Energy Major Projects, licensed under CC BY 4.0.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import openpyxl  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "phase4" / "remp_gold.csv"
FIELDS = ("edition", "project", "company", "state", "type", "status", "capacity", "unit", "cost")
HEADERS = {
    "project": "project",
    "company": "company",
    "state": "state",
    "type": "type",
    "status": "status",
    "capacity": "annual estimated new capacity",
    "unit": "capacity unit",
    "cost": "cost estimate",
}


def _clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip() if value is not None else ""


def read_edition(path: Path) -> list[dict[str, str]]:
    """Gold rows from one edition's data file, keyed by ``FIELDS``."""
    match = re.search(r"(20\d\d)", path.name)
    if match is None:
        raise ValueError(f"cannot read the edition year from '{path.name}'")
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Gold"]
    rows = [tuple(r) for r in sheet.iter_rows(values_only=True)]
    start = next(i for i, r in enumerate(rows) if r and _clean(r[0]).lower() == "project")
    header = [_clean(h).lower() for h in rows[start]]
    col = {}
    for field, name in HEADERS.items():
        hits = [i for i, h in enumerate(header) if h.startswith(name)]
        if not hits:
            raise ValueError(f"{path.name}: no '{name}' column in the Gold sheet")
        col[field] = hits[0]
    out = []
    for r in rows[start + 1 :]:
        project = _clean(r[col["project"]]) if r else ""
        if not project or project.lower().startswith("notes"):
            continue
        row = {field: _clean(r[i]) for field, i in col.items()}
        row["edition"] = match.group(1)
        out.append(row)
    return out


def main(paths: list[str]) -> None:
    """Write the combined list, sorted by edition and project."""
    rows = [row for p in paths for row in read_edition(Path(p))]
    rows.sort(key=lambda r: (r["edition"], r["project"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    editions = sorted({r["edition"] for r in rows})
    print(f"{len(rows)} rows from editions {', '.join(editions)} -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])

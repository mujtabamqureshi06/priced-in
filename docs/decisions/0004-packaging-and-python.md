# 0004. Packaging tool and Python version

- Status: accepted
- Date: 2026-11-15

## Context

WP 0.1 asks for a packaging tool to be chosen by ADR (uv or poetry) and a pinned Python version.

## Options

1. Poetry with its own build backend.
2. uv for environments and locking, with hatchling as the build backend.

## Decision

Option 2. **uv** with **hatchling**. `requires-python = ">=3.11"`. Develop on 3.12 (pinned in `.python-version`). CI runs on 3.11 and 3.12. Tooling: ruff (lint and format), mypy in strict mode, pytest with coverage, pre-commit.

## Consequences

`uv.lock` is committed and CI installs with `uv sync --locked`, so every environment resolves the same versions. Python 3.11 is the floor, which allows `tomllib` and modern typing syntax.

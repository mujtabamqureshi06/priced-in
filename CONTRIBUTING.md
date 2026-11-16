# Contributing

These conventions apply to every change, whoever makes it.

## Workflow

- `main` is always releasable. It is protected and CI must pass before a merge.
- One work order, one branch, one pull request. Branch prefixes: `feat/`, `fix/`, `docs/`, `test/`, `chore/`, `research/`.
- Conventional commit messages (`feat: add GBM price model`, `docs: record ADR 0012`). No messages like "update".
- Squash merge. Tags per release (`v0.1.0`).
- Code, tests and documentation change in the same pull request.

## Code

- Python 3.11 or later. Package under `src/pricedin/`.
- Type hints everywhere; `mypy --strict` passes.
- `ruff check` and `ruff format` pass. Line length 100.
- Docstrings on public functions state units and cite the source of any method.
- No magic numbers. Every assumption comes from the case inputs or from `data/priors.yaml`, referenced by `id`.
- Randomness uses `numpy.random.Generator` with an explicit seed (ADR 0011). No global random state.
- Vectorise over simulation paths with NumPy.
- Every model component has a known-answer test.
- Inputs that fail validation raise errors that name the field and the allowed range.

## Data

- Every row in a data file has a source and a location (page, table or URL).
- Raw and processed data are kept apart. A script regenerates every processed file.
- Third-party documents (technical reports, papers, filings) are never committed. Store links, page references and download scripts.
- Nothing private is committed (ADR 0010). The `private/` and `sources/` folders are ignored by git.

## Writing

- Plain, precise English with Canadian spelling (ADR 0005).
- Short sentences. No emojis, no em dashes, no hype words.
- Units and a source on every number.
- Results on real companies' deals state what the price implies. They never say a buyer overpaid or a seller was wrong.

## Decisions

Significant decisions are recorded as short ADRs in `docs/decisions/` (ADR 0001). Each states the context, the options, the decision, the consequences and who decided.

## Definition of done

- [ ] Tests, lint and type check pass in CI.
- [ ] Docs updated in the same pull request.
- [ ] Every number traceable to inputs or `data/priors.yaml` with a source.
- [ ] No confidential material and no third-party documents.
- [ ] Reviewed, and explainable by the owner.

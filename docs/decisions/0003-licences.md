# 0003. Licences

- Status: accepted
- Date: 2026-11-15

## Context

The code, the compiled transaction dataset and the third-party documents the data come from have different owners and need different treatment.

## Options

- Code: MIT, Apache-2.0, GPL-3.0.
- Compiled dataset: CC BY 4.0, CC0, no licence.

## Decision

- Code: **MIT**.
- Our compiled dataset (for example `data/transactions.csv`): **CC BY 4.0**, released only after each source's terms of use are checked.
- Third-party documents (technical reports, papers, filings, press releases): **never redistributed**. The repository stores links, page and table references, and download scripts.

## Consequences

Anyone can reuse the code with attribution. Each data row must carry a source and a licence note. A `.gitignore` rule blocks PDFs and office files from being committed by accident.

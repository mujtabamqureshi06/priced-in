# 0010. Confidentiality and test-case policy

- Status: accepted
- Date: 2026-11-15

## Decision

- The engine is built and tested only on public information: published technical studies, disclosed royalty deals and public takeovers.
- A final private test (Phase 6) uses cases held outside this repository. Work on them happens only in the git-ignored `private/` folder. Results are never public by default.
- No private material, private contact or item on the local denylist appears in code, data, documents, commit messages, issues or posts.
- Third-party documents are never committed (ADR 0003). The `sources/` folder for downloaded documents is git-ignored.
- The repository was made public only after a confidentiality check of its full history.

## Consequences

A confidentiality audit (#89) searches the repository and its full history before any public release.

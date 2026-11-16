# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-11-15
- Decided by: owner (project instructions)

## Context

The project will be reviewed by industry readers and must be explainable by its owner in an interview. Choices made early (discounting, conventions, scope) need a durable record of why they were made and by whom. Three parties can decide: the owner, the Independent Decision Maker acting as the owner's proxy, and the Mastermind for routine choices.

## Options

1. Keep decisions in chat history.
2. Keep a decision log in one file.
3. One short Architecture Decision Record (ADR) per decision, numbered, in `docs/decisions/`.

## Decision

Option 3. Each ADR has: status, date, decided by, context, options, decision, consequences. "Decided by" is one of: owner; Independent Decision Maker (owner's proxy); Mastermind (routine). A decision is changed by a new ADR that supersedes the old one; old ADRs are not edited except to mark them superseded.

## Consequences

Every significant choice can be traced. Reviewers can see which choices were judgment calls and who made them.

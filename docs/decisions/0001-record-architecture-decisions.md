# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-11-15

## Context

The project will be reviewed by industry readers. Choices made early (discounting, conventions, scope) need a durable record of why they were made.

## Options

1. Keep decisions in chat history.
2. Keep a decision log in one file.
3. One short Architecture Decision Record (ADR) per decision, numbered, in `docs/decisions/`.

## Decision

Option 3. Each ADR has: status, date, context, options where there were real alternatives, decision and consequences. A decision is changed by a new ADR that supersedes the old one. Old ADRs are not edited except to mark them superseded, or for editorial changes that leave the decision unchanged; those are noted in the changelog.

## Consequences

Every significant choice can be traced, and reviewers can see which choices were judgment calls.

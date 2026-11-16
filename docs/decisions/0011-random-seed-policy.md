# 0011. Random seed policy

- Status: accepted
- Date: 2026-11-15
- Decided by: Mastermind (routine)

## Context

Monte Carlo results must be reproducible so that reviewers can regenerate every published number.

## Decision

- All randomness uses `numpy.random.Generator` with the PCG64 bit generator. No calls to the legacy `numpy.random` global functions.
- Every public function that draws random numbers takes an explicit `seed` or `Generator` argument.
- Independent random streams (price, stage gates, overrun, delay, ramp-up) are derived from one root seed with `numpy.random.SeedSequence.spawn`, so adding a new driver does not change the draws of existing ones.
- Every results object records the root seed, the number of paths and the package version.
- Headline values are reported with their Monte Carlo standard error.

## Consequences

Same seed, same version, same inputs gives identical results. Tests can assert exact values.

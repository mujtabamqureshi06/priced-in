# ADR 0074: Schedule discounting offsets and Canadian-dollar tables

- Status: accepted
- Date: 2026-11-28
- Amends: the case schema (`pricedin.inputs`, `cases/_template.yaml`)

## Context

The Phase 7 builder validation needs study cash-flow tables that the schema could not hold exactly:

- Some studies discount their first column a full year or half a year, so no column sits at exponent zero.
- Some place several pre-production years at the valuation date and then discount mid-year from the first production year.
- Some report money in Canadian dollars, while the schema accepted only US$ units.

Forcing these tables into the old conventions moved their NPVs by 1.5% to 9%, which is larger than the transcription check allows and would be read as builder error.

## Decision

1. `study.discounting` gains two optional fields:
   - `t0_years`, the exponent of the t0 column, from 0 to 1, default 0;
   - `periods_at_t0`, the number of leading columns placed at t0, default 1.

   Later columns count on from the last of those, at whole years (`end_of_year`) or half a year earlier (`mid_year`). The defaults give the old timing exactly.
2. `schedule.money_units` also accepts `C$ thousands` and `C$ millions`. A C$ table must record `schedule.fx_usd_per_unit`: the study's own exchange rate if it states one, otherwise the valuation-date rate. This is the same order as the Phase 6 rule for non-US$ offsite costs. `pricedin.project.usd_millions_per_unit` gives the factor to US$ millions. Comparisons convert both sides at the same rate.
3. The engine still values a case in its own money units. Streams still require a US$ case.

## Consequences

Tables are entered as printed, with the convention that reproduces the study's NPV. Existing cases are unchanged. These are conventions for holding tables, not a change to the builder.

# ADR 0073: Phase 6 part 2, price range, width measure and scoring rule

- Status: accepted
- Date: 2026-11-25
- Amends: ADR 0070

## Context

Phase 6 part 1 found 22 usable deals (`docs/phase6/count.md`), so the phase is a case series (ADR 0063). ADR 0063 item 5 requires three things to be fixed before any deal is priced: the source of the spread range, a width measure, and a scoring rule that penalises width. ADR 0070 item 6 requires them to be fixed by someone who has not looked at the price amounts. Part 1 also left open how contingent amounts enter the price.

The engine also needs build odds and timing for each deal. One price cannot identify both (ADR 0023), and in Phase 6 the price is what is being predicted, so neither can be read from it.

## Decision

`docs/phase6/protocol.md` section 8, fixed without access to any deal price:

1. **Build odds and timing.** From the Phase 5 primary table (ADR 0068), by study stage.
   - The window is 5 years from the deal date, conditioned on the time since the study. The table is extended beyond 60 months at the 36-to-60-month hazard.
   - Each deal's own project is left out of the table used to price it. A decision already made sets the probability to 1.
   - The table replaces the engine's stage gates and gold-driven build rule for Phase 6 pricing only. Decisions are independent of the gold path, a stated assumption that lowers values somewhat.
2. **Spread range.** The empirical distribution of discount rates disclosed for producing gold royalty and stream interests by the 23 searched companies in 2012 to 2025 statements.
   - Rates are converted to real and pre-tax where the statements allow, then to spreads by s = k(1 + r) (ADR 0045). Each company is weighted equally.
   - At least 8 rates from 4 companies, otherwise an illustrative grid with no score.
   - Development-asset rates, the producing-royalty control, and a flat-deck valuation of fixed-payment streams are sensitivities.
3. **Range.** The 10th to 90th percentiles of engine values over 2,000 joint draws of spread and a Phase 5 bootstrap replicate: an 80% range.
   - Each value is an expected value, with Monte Carlo standard error under 1% of value.
4. **Width.** W = ln(upper / lower).
5. **Scoring.** The interval score of Gneiting and Raftery (2007) on log prices at alpha = 0.2, with coverage (Clopper-Pearson), misses by side and implied spreads.
   - The headline comparison with the study-convention and analyst-mode benchmarks is the median absolute log error of central values.
   - Interval scores are compared against the benchmarks centred in ranges of the engine's width.
6. **Price.** The unconditional consideration is primary. Contingent amounts with triggers the engine models are a sensitivity, so no model output enters the quantity being predicted. The resulting downward push on prices is stated in advance.
7. **Publication.** Aggregates only. Nothing over fewer than 5 deals is published, including any with-and-without reading or sensitivity where the changed group or the rest has fewer than 5.
8. **Order of work.** The rules, the spread set, the engine terms and the price-free inputs are fixed first. A freeze commit then records the hashes of the Phase 5 table, the spread set, the inputs, the engine commit and the output. Prices are joined only after that, and only once the Phase 5 table is final.

## Consequences

- The work packages that follow are: the spread-set compilation, the stream and royalty terms not yet in the engine, and input transcription with a seeded second transcription of 6 deals.
- Phase 6 scoring waits for the Phase 5 table to be final. No Phase 6 aggregate is published before the Phase 5 results.
- With 22 deals, any coverage from 14 to 21 is consistent with a calibrated 80% range (probability 0.97). The write-up says the series can reveal gross miscalibration but cannot confirm that the engine prices royalties well.
- The project's claim stays "what prices imply". Results never describe a party as having overpaid or underpaid.

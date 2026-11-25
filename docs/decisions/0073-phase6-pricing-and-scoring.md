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

## Amendment, 2026-11-25: pricer conventions

Fixed without access to any deal price, after the pricer was written. Where the whole-year engine forces a convention, the choice removes an artefact of the method and keeps any convention shared with the study benchmark (B1). Each known bias is stated with its direction.

1. **Decision dating.** A build decision in window year k is dated mid-year, t = k - 0.5. End of year is a sensitivity.
2. **Payment timing.** Payments are dated at the end of each year in the primary run, the same convention studies use. Royalties are paid monthly or quarterly, so this understates value by about half a year of discounting. A mid-year payment sensitivity is reported.
3. **Advance royalties.** A shorter duration or a total set by the terms limits the advances; the window end is only the outer limit. Creditable advances are recovered from later payments and add no value of their own. Stopping at the window end understates value where advances run longer.
4. **Caps.** All payments, advances included, count toward a cap. A nominal cap is deflated at the deal-date breakeven inflation rate from the snapshot. A cap in another currency uses that country's breakeven rate where the snapshot has one, otherwise the US rate, flagged.
5. **Step thresholds.** If the terms do not say which ounces count toward a threshold, the deal is not priced for that reason. The transcriber does not choose.
6. **Offsite costs.** Real and constant, with the NSR base floored at zero each year.
7. **Fixed-price streams.** A lesser-of price is a strip of calls; a pure fixed price is P - c and may be negative. Escalation follows the terms. The flat-deck sensitivity for fixed-payment streams still applies.
8. **Contingent production triggers.** Modelled only for the contingent sensitivity (item 6 of the decision).
9. **Incomplete bootstrap replicates.** A replicate without a 60-month value raises an error. It is never dropped silently; if one occurs it is reported and the freeze waits.
10. **Terms not implemented.**
    - A sliding scale or value threshold tied to the gold price on a usable deal is a coding error under rule 4 and goes back to resolution.
    - For other terms, the usable deals were counted before transcription. That count is a coding fact, not a price: 0 carry a debt-linked step, 0 a completion test and 0 an advance on a stream. 1 carries a minimum cash-flow guarantee.
    - A term carried by 2 or more usable deals is implemented and unit-tested before the freeze if the documents specify it fully. Otherwise the deal is not priced. On these counts, none needs new code, and the deal with the guarantee is not priced unless the guarantee proves to have no effect on value. The count of deals not priced is reported with reasons.
11. **Monte Carlo.** 20,000 paths and seed 0 for each draw. The same seed across draws gives common random numbers, which reduces noise in differences between draws. The largest per-draw standard error across all draws is reported. A draw above 1% of its value raises the path count for that deal before the freeze.

## Amendment, 2026-11-25: converting disclosed rates by deck shape (protocol 8.3)

Fixed without access to any deal price, before the freeze. Protocol 8.3 said how to convert a rate stated as nominal, but not one whose basis is not stated, which is 14 of the 24 rows in the primary set.

For a revenue claim on a flat deck the label does not change the value: a flat nominal price at a nominal rate gives the same value as a flat real price at a real rate. So the conversion goes by the deck the rate was applied to (ADR 0045: apply a rate as its source did). Step 1 of the 8.3 conversion now reads, per row:

- a flat deck, or a deck flat in the long term: no conversion, whatever the label (22 rows);
- an escalating deck with a stated inflation assumption: deflated at that rate (1 row);
- a deck not stated: treated as flat, flagged, in the primary run, and deflated at the 10-year US breakeven rate at the fiscal year end as a sensitivity (1 row).

If the unstated rates were in fact applied to escalating decks, the primary run overstates spreads and understates values. The minimum of 8 rates from 4 companies still holds: 24 rows from 7 companies. Empress Royalty's 16.5% applies to one producing stream, so it stays in the primary set.

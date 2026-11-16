# 0043. Gold Standard Ventures takeover case

- Status: accepted
- Date: 2026-11-16

## Context

Orla Mining's offer for Gold Standard Ventures (announced June 13, 2022) is the second public takeover read through the takeover adapter (#81, ADR 0042). It prices South Railroad a year after the Vox royalty (ADR 0028) and on a newer study, the February 2022 feasibility study (FS). Three questions came up while building the case:

- the FS discounts on a mid-year convention, which the schedule-mode engine did not support;
- the statutory tax rates do not reproduce the FS's own gold-price sensitivity;
- the timing prior, since the company's schedule and the 2021 rule (ADR 0023) differ by three years.

## Decision

1. **Mid-year discounting.** `Discounting.convention` accepts `mid_year`: the t0 column stays at zero and the column k periods later is discounted k - 0.5 years (`project.period_times`). With Year -1 at zero, this reproduces all four NPVs in FS Table 22-7 (before and after tax, 5% and 10%) to within US$1 thousand. The engine shifts these times by whole years for delay; prices are still sampled at the whole year of each period.
2. **Marginal tax rate fitted to the study.** The case uses 0.195, fitted to the FS sensitivity (Table 22-6). It reproduces the after-tax NPV at US$1,400, 1,500, 1,800 and 1,899 to within US$0.6 million. The statutory derivation (excise, net proceeds tax, 21% federal tax) gives 0.258 and misses the table by up to 9%. The model probably includes deductions the text does not describe, such as percentage depletion; this is an inference, not stated in the FS. A fitted rate uses only the study's own published numbers, so it adds no look-ahead. The 2020 PFS case keeps its statutory rate.
3. **Timing prior.** Base: 4 years from June 10, 2022 to the FS Year -1 (`timing.years_to_start.south_railroad_fs2022`). This applies the ADR 0023 rule: the Notice of Intent had not been published (Gold Standard expected it in Q1 2022), so the clock starts at the BLM median of 3.79 years from Notice of Intent to Record of Decision. The company schedule (construction from Q2 2023, so 1 year) is the sensitivity. Both are reported.
4. **Price to claim.** As for Osino (ADRs 0031 and 0033):
   - Orla's offer goes against the project claim, since the acquirer funds construction.
   - The undisturbed June 10 value goes against the equity claim with dilution, less corporate G&A.
   - Balance-sheet items come from the March 31, 2022 interim statements, the latest published before the offer: cash less lease liabilities.
   - Options: only the Q1 2022 grant at C$0.57 is in the money, and it enters at intrinsic value.
   - The Orion silver stream deposit is not debt, since the FS silver revenue is already net of the stream.
   - Gold Standard's other ground (Lewis, North Railroad) is valued at zero, so the implied odds are an upper bound for South Railroad alone.

## Consequences

- The offer is read in `scripts/gsv_takeover.py` and `docs/cases/gold_standard_takeover.md`.
- The mid-year option is available to any later case whose study uses it. Each case must still show that it reproduces the study NPV.
- Fitting the tax rate is allowed where the study publishes a sensitivity table and the statutory derivation fails it. The case file must state both rates.

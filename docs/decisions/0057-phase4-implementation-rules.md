# 0057. Phase 4: implementation rules for the implied odds

- Status: accepted
- Date: 2026-11-19
- Amends: the Phase 4 protocol (sections 3 and 5), ADR 0024 (volatility for the panel) and `docs/phase4/tax_method.md` (section 3)

## Context

Before any implied odds were computed for any panel project, building the inputs raised questions the protocol does not settle: some studies' NPV and IRR cannot both be matched by the two-parameter study builder; the verified daily gold series starts in 2012, too late for a 10-year volatility at the early snapshots; studies and share prices are in different currencies; Capital IQ restates historical prices and share counts for later share consolidations; the tax table had no rate for Guyana before 2017; and the panel had no rule for when construction starts, for the overrun prior at PEA and scoping stage, or for part-owned projects.

These rules were fixed on 2026-11-19. No implied odds, test statistics or comparisons with outcomes had been computed.

## Decision

1. **Calibration tolerance.** The IRR tolerance is half a unit of the last digit the study states (0.5 points for a whole-number IRR, 0.05 points for one decimal): a rule about the precision a study reports, not about fit (`parametric.irr_tolerance`). The NPV tolerance stays at 0.1% of initial capital.
2. **Shape not matched.** If no schedule within the tilt bounds matches both figures, the entry stays in the panel with the closest schedule that still matches the NPV, flagged "cash-flow shape not matched", with its IRR miss recorded (`calibrate(..., allow_shape_miss=True)`). An entry is excluded only if its NPV cannot be matched. Every result is also reported without the flagged entries, and the flags are reported by outcome and exchange. Excluding them outright could bias the panel, since front-loaded studies (starter pits, ramp-ups) may differ in how often they are built. A third profile parameter was rejected as a change to the method after outcomes were labelled.
3. **Volatility.** Trailing 10-year volatility at each snapshot from the World Bank's monthly gold series (Pink Sheet), using months up to the snapshot's month only. Returns between monthly averages understate the volatility of the price: for a random walk the variance of changes in averages is about two thirds of the true variance (Working 1960, Econometrica 28(4), 916-918; derived and tested by simulation in `pricedin.volatility` and `tests/test_volatility.py`). The variance is divided by 2/3. After that correction the monthly figure is 1.2 points below the daily figure for 2012-2021 (13.5% against 14.7%); this is disclosed.
4. **Currency.** Each study is calibrated in its own currency, at the exchange rate it states where its figures mix currencies. Each project is valued at the snapshot's exchange rate, and the equity price is converted at the same rate. Valuing everything in US dollars at each study's rate is reported as a check.
5. **Capital IQ restatement.** Capital IQ Pro restates historical prices and share counts for later consolidations, by the same factor, so its market capitalisation is unaffected. The equity value is Capital IQ's market capitalisation; the as-traded price is that value divided by the basic shares the company reported at the same date. Any snapshot where that price differs by more than 10% from a price the company stated is resolved from company documents. Options and warrants are counted series by series as the protocol (section 3) and ADR 0048 specify.
6. **Guyana.** Added to `data/phase4/tax_regimes.csv` by the committed method: 30% for non-commercial companies from 2012 to 2016 (Corporation Tax Act as amended, in force from the year of assessment 2012).
7. **Construction start.** One year after the snapshot for every project, so "on schedule" has one meaning across the panel. Each study's own stated start, where its release gives one, is a check. This departs from the case files, which follow company guidance (ADR 0023): whether a release states a timeline may itself be related to the outcome.
8. **Overrun prior for PEA and scoping entries.** The PFS prior (the FS-stage distribution), labelled "FS-stage distribution applied to a PEA or scoping estimate; likely understates". The widened PFS sensitivity is the check. Stage-probability defaults do not enter the primary predictor, which is the price divided by the value if the project passes its gates.
9. **Ownership and other assets.** The equity price is compared with the owner's attributable share of the project value; government free-carried interests reduce that share. Other assets are valued at zero and flagged; the number of such companies is reported, and results are also shown without companies holding another project with a published resource estimate at the snapshot.

## Consequences

- The panel keeps every project whose study NPV can be matched.
- The volatility uses no information after any snapshot.
- Results carry two new robustness checks: without shape-flagged entries, and with each study's own construction timing.

## Amendment (2026-11-19): panel inputs completed

Fixed after every primary-panel study input was complete and before any implied odds were compared with outcomes.

10. **Shape flags.** With every input complete, 14 of the 85 primary entries are flagged "cash-flow shape not matched", above the eight at which this rule was to be revisited. The rule stands. The flagged entries are 9 TSXV, 4 TSX and 1 ASX; by outcome, none of the 16 construction decisions, 1 of the 11 takeovers and 13 of the 58 entries with no event. The check without flagged entries is reported beside every result. The rule is revisited if that check moves the AUC by more than 0.05.
11. **Re-read of the three largest misses.** The entry documents of the three entries with the largest IRR misses at the time (Buckreef, Namdini, Castelo de Sonhos) were re-read against the base-case convention and the single-currency rule.
    - Buckreef (PEA, 25 April 2012): the release gives one case at US$1,600/oz, in US dollars. A restatement filed in August 2012 at a regulator's request used US$1,500/oz as its base; as with other regulator-prompted restatements, it is not a new entry study. Its sensitivity table gives a post-tax IRR of 54% at US$1,600/oz against the release's 48%, at the same NPV; the release figure is kept. The study describes a modular plant, which a single initial capital figure cannot represent.
    - Namdini (scoping study, 5 February 2018): three throughput options; the release designates none as preferred and presents the 7.0 Mtpa option "for indicative purposes". That option is used, in US dollars. Its higher-grade starter pit front-loads production.
    - Castelo de Sonhos (PEA, 16 November 2018): one base case, in US dollars, with Brazilian costs converted at a stated R$3.8 per US$. Production averages about 160,000 oz a year for the first four years against 120,000 oz over the 9.1-year life.
    In each case the inputs stand and the flag stays; the misses come from front-loaded or phased schedules, not from a reading error.
12. **Schedule shorter than the builder allows.** The builder needs at least two production years. Julius (BFS stage 1, 18 January 2017) has 1.25 years. Its schedule is compressed to two production years with total ounces unchanged (51.2 koz a year over 1.25 years becomes 32 koz a year over 2 years), flagged "schedule compressed to the builder's minimum".
13. **Annual production.** Annual production is the life-of-mine total divided by the production years, not a steady-state or early-years rate. Where a document gives only tonnes, grade and recovery, production is derived from them and flagged.
14. **Inputs completed from the entry documents.**

| Entry | Input | Value | Source |
|---|---|---|---|
| Eagle Mountain | production | 21.1 koz a year (168,700 oz over 8 years) | Goldsource Mines, PEA release, 31 July 2014 |
| Granada (primary) | gold price | US$1,260/oz at C$1.11 per US$ | Gold Bullion Development, PFS release, 6 May 2014 |
| Hammerdown | initial capital | C$54.2M, derived: C$67.8M total less sustaining (C$5.5M and C$7.1M) and closure (C$1.0M); flagged | Maritime Resources, PFS release, 2 March 2017, Table 4 |
| Laiva | gold price | US$1,300/oz | PEA technical report, 3 July 2018, section 22.2.1, p. 22-1 |
| Mirado South Zone | production | 23.6 koz a year, derived from 996,000 t at 2.33 g/t and 95% recovery over 3 years; flagged | Orefinders Resources, PEA release, 15 January 2018 |
| Valentine Lake | initial capital, life, production | US$380M; 10.2 years; 185.9 koz a year (1,896,300 oz) | Marathon Gold, release of 30 October 2018, May 2018 column |
| Qala Shallows | gold price, life, production | US$1,750/oz; 16 production years, derived from a 17-year life that starts with construction; 41.4 koz a year (663,000 oz); flagged | West Wits Mining, DFS release, 2 September 2021 |

The gold price for Mirado South Zone is US$1,300/oz with figures in Canadian dollars at US$0.76 per C$, as its release states.

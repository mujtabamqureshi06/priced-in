# Phase 4 results: does the market price of a gold developer anticipate a construction decision?

Status: complete. Rules are in `protocol.md`, `labelling.md`, `tax_method.md` and ADRs 0051 to 0062. Market data are from S&P Capital IQ. Only derived results are shown here; the raw data are not redistributed.

## 1. Summary

At each project's entry study, we divided the developer's market value by what the engine says the project would be worth if built on schedule. This is the price-to-built-value ratio (ADR 0061).

On 80 ASX, TSX and TSXV gold developers, with 16 construction decisions within 36 months, the ratio ranked later builds somewhat above the rest. The AUC was 0.624, with a 95% interval of 0.468 to 0.770. The interval includes 0.5. At this panel size, the smallest AUC the test can reliably tell from 0.5 is about 0.73, so the result is inconclusive, not negative.

The ratio did no better than two measures an analyst already has: P/NAV (0.668) and the study stage (0.715). Once stage is known, it adds nothing detectable.

None of the checks fixed in advance changes this reading. A quarterly hazard model and a competing-risks model, which treats takeovers as the other outcome, agree with it.

The result does not show that markets misprice developers. It does not show that discounted cash flow is wrong. It is not a trading signal.

## 2. How the evidence was produced

- **Order of events.** The analysis rules were fixed before predictor values were compared with outcomes. Several rules were fixed after the outcomes had been labelled; each is dated in its decision record.
- **Run timing.**
  - The predictor files were written at 04:29 and 10:30 ET on 19 November 2026.
  - The freeze record (#131) merged at 10:35:15 ET.
  - The primary output file was last written at 10:35:21 ET, six seconds later. File times show only the last write, so an earlier comparison run between 10:18 and 10:35 ET cannot be excluded from file evidence alone.
- **Engine.** Every figure in sections 3 to 6 uses the engine as frozen at commit b5e3eb8. Section 9 explains the later correction.
- **Bootstrap.** Confidence intervals are 95% intervals from 10,000 resamples of projects, seed 20261119.
- **Event.** A construction decision within 36 months of the entry study. A takeover without a decision is a non-event (protocol section 4).

## 3. Primary result

| Predictor | n | Events | AUC [95% CI] | Brier |
|---|---|---|---|---|
| Price-to-built-value ratio, 0% spread (primary) | 80 | 16 | 0.624 [0.468, 0.770] | 0.216 |
| 5% spread | 80 | 16 | 0.646 [0.490, 0.789] | 0.231 |
| 10% spread | 80 | 16 | 0.654 [0.496, 0.794] | 0.272 |
| Break-even spread | 80 | 16 | 0.635 [0.477, 0.779] | |
| P/NAV | 78 | 16 | 0.668 [0.501, 0.819] | |
| Study stage (FS > PFS > PEA) | 80 | 16 | 0.715 [0.572, 0.848] | |

- **Brier scores.** The base rate gives a Brier score of 0.160. The ratios do worse than the base rate as probability levels, which is expected: they are used only to rank projects (protocol section 6).
- **Paired differences.** Ratio minus P/NAV is -0.038 [-0.109, 0.019]. Ratio minus stage is -0.091 [-0.269, 0.086]. Neither is significant.
- **Logit (exploratory).** The log ratio alone has a coefficient of 0.24 (p 0.30). With stage added, the ratio's coefficient falls to 0.03 (p 0.91), and stage's is 1.15 (p 0.003).
- **Why stage wins almost mechanically.** The ratio has no time horizon, while the event does (36 months). Build rates also differ by stage in the panel: about 10% from a PEA or scoping study, 31% from a PFS and 50% from a FS.
- **Medians.** The median ratio at 0% spread was 0.22 for projects later built and 0.13 for the rest.

## 4. Checks fixed in advance

| Check | n | Events | AUC [95% CI] |
|---|---|---|---|
| No cash adjustment after the last report | 80 | 16 | 0.625 [0.465, 0.775] |
| Cash adjustment by estimate for every entry | 80 | 16 | 0.620 [0.454, 0.768] |
| Without share increases above 10% | 69 | 14 | 0.630 [0.468, 0.774] |
| Documented subset, undiluted | 15 | 3 | 0.639 [0.231, 0.929] |
| Documented subset, diluted | 15 | 3 | 0.639 [0.240, 0.929] |
| Without "cash-flow shape not matched" entries | 67 | 16 | 0.619 [0.459, 0.771] |
| Without Davyhurst | 79 | 15 | 0.608 [0.448, 0.762] |
| Without Windfall Lake (offer outstanding at entry) | 79 | 16 | 0.621 [0.464, 0.766] |
| Without presumed or flagged ownership | 73 | 15 | 0.677 [0.529, 0.809] |
| Keeping Laiva as a construction decision | 81 | 17 | 0.596 [0.439, 0.746] |
| ASX only | 11 | 3 | 0.542 (interval uninformative) |
| TSX and TSXV only | 69 | 13 | 0.646 [0.493, 0.786] |
| Widened overrun prior for PEA, scoping and PFS | 80 | 16 | 0.623 [0.467, 0.769] |
| Takeovers excluded | 70 | 16 | 0.635 [0.471, 0.783] |
| Construction start at the study's own schedule | 80 | 16 | 0.623 [0.467, 0.769] |
| Check panel, with tax-modelled pre-tax entries | 83 | 16 | 0.633 [0.470, 0.785] |
| Without companies holding another resource-stage project (separate projects only) | 66 | 13 | 0.668 [0.498, 0.818] |
| As above, also counting deposits on the same property outside the study | 55 | 11 | 0.640 [0.459, 0.811] |

**Revisit triggers.** None fired:
- shape flags moved the AUC by 0.005 (trigger 0.05);
- diluted against undiluted differed by 0.000 (trigger 0.05);
- removing the share increases moved it by 0.006 (trigger 0.05);
- the widened overrun prior moved it by 0.001;
- the study-timing check moved it by 0.001 (trigger 0.03).

**Study timing.** The definition was fixed after the primary result was known. Construction starts at the study's stated first production less its stated pre-production period. Where the study gives no date, the default of one year stays and the entry is flagged. Nine entries changed.

**Other assets.**
- Holdings were taken from company documents dated on or before each entry. These were mostly the "about the company" paragraph of the study release; a few were an MD&A.
- Holdings could not be established for 14 entries. They are kept in the main row.
- Restricting to entries confirmed to hold no separate other project gives 0.715 [0.564, 0.848] (n 52, 12 events). On the same subset, P/NAV gives 0.704 and stage 0.731. The ratio may rank better where the company is a single-project developer, but stage still ranks as well or better. The intervals are wide.

**Check panel.**
- Fourteen check-panel entries opened at studies reporting pre-tax figures only. Their after-tax values are modelled with the committed tax method.
- Three could not be priced: two have no Capital IQ market value (Kobada, Tampia) and one reports in a currency the market inputs do not cover (Amulsar, 2012).
- One entry, Mankarga 5, was found to report after-tax figures in a later company document that restates its study. It is valued on those figures.

## 5. Takeovers as a competing outcome

| Model | n | Events | Estimate [95% CI] |
|---|---|---|---|
| Fine and Gray, log ratio, takeover as a competing event | 80 | 16 | subdistribution hazard ratio per doubling 1.15 [0.86, 1.55] |
| Takeover or construction as the event (exploratory) | 80 | 26 | AUC 0.602 [0.463, 0.739] |
| Takeover alone as the event (exploratory) | 80 | 10 | AUC 0.523 [0.303, 0.743] |

## 6. Quarterly hazard (secondary, ADR 0060)

- **Data and model.** 838 project-quarters from 80 projects, with 16 decisions. The model is complementary log-log with a Firth penalty and stage as a factor. Intervals come from a project-cluster bootstrap (2,000 resamples, seed 20261120).
- **Code and run.** The script was committed before its first run, and the run was logged at 2026-11-19 17:55:55 UTC.

| Model | Rows | Events | Log-ratio coefficient [95% CI] | Hazard ratio per doubling |
|---|---|---|---|---|
| Primary | 838 | 16 | +0.216 [-0.117, +0.698] | 1.16 |
| Ratio from two quarter-ends earlier | 680 | 14 | -0.124 [-0.476, +0.384] | 0.92 |
| Without floored ratios | 820 | 16 | +0.199 [-0.159, +0.694] | 1.15 |
| High- and medium-confidence labels | 773 | 11 | +0.202 [-0.191, +0.836] | 1.15 |
| Ratio at 10% spread | 838 | 16 | +0.260 [-0.093, +0.741] | 1.20 |
| Without the two quarters before each change of control | 819 | 16 | +0.236 [-0.078, +0.691] | 1.18 |

A higher ratio at a quarter-end goes with a slightly higher hazard of a decision in the next quarter, but every interval includes zero. When the ratio is lagged six months, the sign reverses. Whatever association exists may come from prices moving shortly before decisions are announced. No prediction at entry is claimed.

## 7. Calibration by quintile (0% spread ratio, clipped to [0, 1])

| Quintile | n | Mean ratio | Observed build rate |
|---|---|---|---|
| 1 (lowest) | 16 | 0.027 | 0.125 |
| 2 | 16 | 0.073 | 0.062 |
| 3 | 16 | 0.148 | 0.188 |
| 4 | 16 | 0.253 | 0.375 |
| 5 (highest) | 16 | 0.657 | 0.250 |

The highest quintile builds less often than the fourth, and its ratios are far above its build rate. The top of the ranking holds prices that are high relative to value for reasons other than the odds of a build.

## 8. Labels

**Second coding.** 38 rows were recoded: a random 20% (seed 20261120), plus every row resting on press reports only or marked low confidence. Outcomes agreed on 37 of 38, and on 20 of 20 in the random sample. The labelling note calls the recode blind. However, the recoding sessions had access to the repository in which the first labels were stored, so blindness cannot be shown. The agreement is reported as a consistency check, not an independent recode.

**Label confidence (exploratory, proposed after the result).** Of the 16 construction decisions, 2 are high-confidence labels, 9 medium and 5 low. On the 73 projects with high- or medium-confidence labels (11 events), the AUCs are: ratio 0.764, P/NAV 0.833, stage 0.740. All three rank better on the firmer labels, and the ratio still ranks below P/NAV. These figures are exploratory and are not a headline.

## 9. Engine correction after the result (ADR 0059)

**What changed.** The frozen engine floored equity at zero on each simulated path, which overstated the equity claim. On 19 November 2026 the floor was replaced: shareholders' limited liability is now applied at the build decision. Two things follow:
- A path builds only if building is worth something after the expected overrun and dilution.
- The equity on a built path is not floored.

**Effect on this result.** The primary result stands as computed with the frozen engine. Values for this panel under the corrected engine (commit 2df6022) would be an exploratory secondary, because the outcomes are already known.

**Published figures.** Every published case figure has been regenerated with the corrected engine:
- the case notes for Osino, Gold Standard Ventures and Orla;
- the backtest table;
- the website's illustrative example, which did not change.

## 10. The study builder

Each entry's annual schedule is rebuilt from the study's headline figures by `pricedin.parametric`. The builder was checked against annual cash-flow tables transcribed from the studies themselves. Each table was hashed before any comparison. Values are computed at each entry's market inputs on the study's own discounting convention.

**Coverage.**
- The validation set is a random 17 (seed 20261119) plus 3 shape-flagged entries (seed 52052).
- 12 tables were comparable.
- Six studies publish no annual table, and one report could not be obtained.
- The validated set leans toward NI 43-101 reports.

**Thresholds.**
- Median absolute error at most 10%.
- 90th percentile at most 25%.
- Spearman correlation of built against transcribed ratios at least 0.95.

All three are measured at 0% spread. They were set after the errors on four tables were known.

| Engine | Spread | Median abs error | 90th percentile | Max | Spearman | Median, as % of capital | 90th percentile, as % of capital |
|---|---|---|---|---|---|---|---|
| Frozen (b5e3eb8) | 0% | 5.7% | 8.2% | 26.9% | 0.993 | 13.1% | 26.7% |
| Frozen (b5e3eb8) | 10% | 5.5% | 11.3% | 11.9% | 1.000 | 3.6% | 8.1% |
| Corrected (2df6022) | 0% | 5.2% | 40.4% | 76.6% | 0.965 | 8.6% | 20.1% |
| Corrected (2df6022) | 10% | 11.8% | 126.9% | 161.4% | 0.993 | 6.3% | 13.2% |

**Reading.**
- On the frozen engine, which produced the result above, the builder passes.
- On the corrected engine it fails the 90th-percentile threshold. The misses come from projects close to break-even: Brewery Creek, with an NPV of US$23 million on US$85 million of capital, and Livengood, with a negative NPV.
- A percentage error is badly behaved when value-if-built is near zero, so the error is also shown as a share of initial capital.
- Any later use of the builder with the corrected engine must reduce the error on marginal projects. The reduction must be tested on tables not used here, and the error must be reported by project margin.

**Note added 2026-11-28.** Re-tested on rebuilt entry snapshots and re-transcribed tables (`docs/phase7/builder_validation.md`): Brewery Creek +7.6%, Livengood +31.3% (a project whose value is almost all option value; 0.01 times capital). Engine 2df6022 and the current engine give the same errors on these tables, so the earlier misses were not caused by engine changes. They could not be reproduced, and their cause is unknown because the original comparison script and transcriptions were lost.

## 11. A second sample, shelved

A stock sample of developers at 31 March 2022 was fixed in ADR 0062 and screened before any outcome or price was examined. It gave:
- 35 entrants, 186 exclusions and 12 unresolved;
- about 9 expected construction decisions at the first sample's stage rates.

ADR 0062 makes the sample confirmatory only with at least 100 projects and 25 expected events. That threshold cannot be reached: even if every unresolved candidate entered, the counts would be 47 projects and 15 expected events. The sample was therefore stopped as a test of the ratio. No predictor was computed for it, and no outcome was labelled. Its screening record is kept.

## 12. Screen recall

- **ASX.** The screen's recall was audited before outcomes, against the Australian Government's major-projects gold lists (protocol section 8). The gap in recall between built and unbuilt projects was below the 20-point threshold in all three variants (8 to 16 points).
- **Misses.** Of the five missed companies, three had an in-window study:
  - Calidus (Warrawoona): added by name, later labelled a construction decision.
  - Explaurum (Tampia): a check-panel entry, later taken over.
  - Kin Mining (Cardinia): never reached committed status in the lists to 2021.

  The other two published their first studies after 2021.
- **TSX and TSXV.** Recall is unmeasured; no independent project-level list was found.

## 13. What this shows and what it does not

The market price of a gold developer, read through the engine, contains some information about whether the project will be built. On this panel it contains no more than the study stage and P/NAV already carry.

The reasons the test could not settle the question are stated above:
- the panel size;
- the absence of a time horizon in the ratio;
- the number of construction decisions.

The ratio remains useful as a reading of a price under stated assumptions. It is reported beside P/NAV, not instead of it.

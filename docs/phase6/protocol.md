# Phase 6 protocol: royalty and stream pricer, part 1 (counting)

Status: part 1 fixed 2026-11-25, before any deal was counted (ADR 0070); part 2 (section 8) fixed after the count and before any deal is priced (ADR 0073). Part 2 (spread range, width measure and scoring rule) is fixed after counting and before any deal is priced (ADR 0063).

## 1. Question

Given a gold project's public economic study and a royalty's or stream's terms, what range of prices does the engine give, and how often does the disclosed deal price fall inside it? Part 1 only decides which deals can be used and counts them.

## 2. Usable deal

A deal is usable if it meets rules 1 to 5 on its announcement date. Rules 6 and 7 record the deal's type and flag it; they exclude nothing. Each rule is judged from documents dated on or before that date, except rule 1, which may use the buyer's later financial statements to confirm the price.

1. **Price.** The consideration is disclosed in money or in listed shares. Shares are valued at the last close before the announcement. Contingent or deferred amounts are recorded separately, each with its trigger. The deal is usable if the unconditional part is at least 75% of the stated total; the price used is the unconditional part, with the total as a check. Part 2 decides whether contingent amounts whose triggers the engine models are valued. Finder's and advisory fees are recorded and not added.
2. **Pre-production gold project.** No commercial production on the ground the royalty or stream covers at the announcement date (trial mining and bulk sampling do not count as production; Phase 5 protocol, section 5.1). A past producer is usable only if a restart study meeting rule 3 exists, flagged. Gold is at least 80% of revenue in the study used, by the Phase 5 gold-share rule (Phase 5 protocol, section 2.6).
3. **Study.** A public PEA, PFS or FS with after-tax NPV and IRR, dated on or before the announcement (a study released the same day counts), whose mine plan includes the ground the royalty or stream covers. The latest such study is used. Its age at the announcement is recorded, and studies more than 3 years old are flagged. A study that covers only part of the royalty ground is usable only if a document states the share covered; such deals are flagged, and every result is also reported without them.
4. **Standard terms.** One of:
   - a net smelter return or gross revenue royalty at a fixed rate, with any step-down, cap, threshold, buy-back or advance minimum royalty fully specified;
   - a gold stream with a fixed delivery percentage (step-downs fully specified) and an ongoing payment that is a fixed price per ounce, a fixed share of spot, the lesser of the two, or a fixed price with a specified escalation.

   Completion tests are allowed if fully specified, flagged.

   Net profit interests, sliding-scale royalties tied to the gold price, and streams with delivery tied to cash flow are not standard. Instruments that combine a royalty or stream with debt or equity in one price are usable only if the price of the royalty or stream part is disclosed.
5. **One asset per price.** The price applies to one royalty or stream on one project. Portfolio deals are usable only if the price split by asset is disclosed.
6. **Transaction type recorded, not filtered.** Both a royalty or stream created by the operator to fund the project and a purchase of an existing royalty from a third party count. The type is recorded, and every result is reported for both types together and for each separately.
7. **Related parties flagged.** A deal between related parties (common control, a shared controlling holder, or a buyer holding more than 10% of the seller or operator) is flagged, and every result is also reported without such deals.

A usable deal also needs the engine's market inputs (gold price, real rate, volatility) for its announcement date.

## 3. Window and sources

- **Window.** Announcements from 1 January 2010 to 31 October 2026. The count from 1 January 2012 is reported as a sensitivity.
- **Buyers searched.** Every listed royalty or streaming company with gold royalties or streams at any time in the window, found from the buyers' own annual reports, plus operators' announcements of royalties or streams they sold. The search list is recorded in `data/phase6/search_log.csv` before the first deal is coded. A buyer found later is added with the date and the reason, and searched the same way. Every company on the list is searched in full: annual information forms or annual reports, financial-statement notes on acquisitions, and news releases.
- **Recall limit.** Purchases by private funds and unlisted buyers are found only where the seller or operator disclosed them. The write-up states this.
- **Documents.** Company news releases, financial statements, technical reports and regulatory filings (SEDAR+, EDGAR, ASX, LSE RNS). Press reports and aggregators are used only to find a deal, not to code it. No third-party document is committed; rows hold links and page references.

## 4. Coding

- **Two passes.** A first coder records every gold royalty or stream deal found in the window, with each of the seven rules marked yes, no or unclear and the document behind each mark. A second coder, without the first coder's marks, codes a random 30% of deals drawn with a seed recorded before the draw, plus every deal marked unclear.
- **Prices are not compared with anything.** Coders record whether a price is disclosed and its amount. No study value, implied rate or model output is computed in part 1.
- **Disagreements** are settled under the written rules, with the reason recorded per deal. Agreement is reported for each rule.
- **Deals already seen.** The deals already in `data/transactions.csv` are recoded under these rules like any other deal, without reference to earlier rulings on them. Every deal the project has already priced or examined (South Railroad, Sorby Hills, White Dam and the others in that file) is flagged "seen", and every Phase 6 result is reported with and without them.

## 5. Count and consequence (ADR 0063)

- 25 or more usable deals: the pricer is tested on all of them under part 2.
- 15 to 24: the phase is a case series, with every deal reported in aggregate and no test statistic presented as confirmatory.
- Fewer than 15: Phase 6 merges into Phase 7, and the deals become worked examples in the study-entry tool.

The count is recorded in `docs/phase6/count.md` and committed before part 2 is written. It holds counts only: no price amounts and no ratios of prices to anything. Part 2 is written without first looking at the price amounts.

## 6. Publication

Per-deal results are private; only aggregates are published (owner, 2026-11-19). The list of usable deals and their sources can be published if the owner decides, because it contains public information only. Results on real deals state what the price implies, never that a party overpaid or underpaid.

## 7. Coding interpretations (ADR 0071 and ADR 0072, fixed after the first-pass count)

These were decided after the first-pass count (23 usable, 20 unclear, against the threshold of 25) and before second coding. `count.md` reports the usable count under each interpretation and its alternative, and says so if the test or case-series outcome turns on one of them.

1. **Unlisted or unvalued securities.** Warrants or units in the consideration are unconditional but unvalued. A value stated in a filing or the financial statements is used, flagged "issuer-valued", with a check price without them. Otherwise they are taken at notional value (number times exercise price), an upper bound, and the deal passes rule 1 only if cash and listed shares are at least 75% of that total. If they are not, or the notional value is unknown, the deal is not usable. The project never values warrants itself.
2. **Buy-back at fair market value.** Standard, flagged, and every result is also reported without such deals. If "fair value" is defined by a formula, the formula must be fully specified.
3. **Fixed-ounce deliveries.** Not standard. A hybrid with a fixed-ounce part is standard only if the fixed part is a minimum shown to be below study production in every year (a floor), flagged. The number of deals excluded under this point is reported.
4. **When a study counts.** From the first public date of its after-tax NPV and IRR, usually the results news release, as in Phase 5. The effective date never counts. If the filed report's figures differ from the release, the release figures are used, flagged.
5. **Gold share on other bases.** Shares use study prices only. A share on head-grade or contained metal settles a deal only outside 70% to 90%: below 70% fails rule 2; 90% or above passes, flagged. Between them the deal stays unclear until a revenue table or payable figures are found. Deals still unclear after second coding are not usable, and are counted.
6. **Instrument gold share, debt-linked steps, ounce payments (ADR 0072).** Rule 2's 80% applies to the instrument as well as the project. A debt-linked step in a stream's delivery is standard if fully specified, flagged. Pre-production payments in ounces are an advance minimum royalty only if credited against later royalties or a stated minimum with a specified limit.

## 8. Part 2: price range, width measure and scoring rule (ADR 0073)

Fixed 2026-11-25, after the count (`docs/phase6/count.md`) and before any deal is priced. Written and decided without access to any deal price, price amount, price summary or ratio of price to anything.

### 8.1 Purpose

Part 1 found 22 usable deals, so Phase 6 is a case series (ADR 0063): every deal is priced and reported in aggregate, and no statistic is presented as confirmatory. This section fixes, before pricing:

1. how the engine turns a deal's study and terms into a price range (the build odds and timing it uses, and the source of the spread);
2. a width measure for that range;
3. a scoring rule that penalises width as well as misses;
4. the comparisons, sensitivities, publication limits and wording of the results;
5. the order of work that keeps prices away from everything above until the ranges are frozen.

It also settles the point part 1 left open: how contingent amounts enter the price (section 2, rule 1; here 8.6).

### 8.2 Build odds and timing

One price cannot identify both build odds and timing (ADR 0023), and here the price is the thing being predicted, so neither is read from it. Both come from the Phase 5 primary table: the cumulative incidence F(t) of a construction decision by any owner, by study stage, at 12, 24, 36 and 60 months after the study (ADR 0068).

- **Yearly probabilities.** F is read linearly between the table's points. Beyond 60 months, F is extended at the constant hazard implied between 36 and 60 months.
- **Window.** The build window is 5 years from the deal date. For a deal a months after its study, the probability of a decision by t is (F(t) - F(a)) / (1 - F(a)), for t from a to a + 60 months. The number of deals whose window needs the extension beyond 60 months is reported.
- **Decision already made.** If documents dated on or before the announcement show a construction decision on the covered ground, the decision probability is 1.
- **Decision to first production.** The study's stated pre-production period; if none is stated, one year, flagged (as ADR 0063 item 2).
- **Leave-one-project-out.** If a deal's project is in the Phase 5 frame, its own entries are removed from the table used to price it.
- **What it replaces.** For Phase 6 pricing, the incidence replaces the engine's stage gates and its gold-driven build rule. Using both would count development risk twice, and stacking the build rule on rates that already reflect realised gold prices would count gold twice. This is a Phase 6 pricing method only; it changes no engine default.
- **Independence.** Decisions are drawn independently of the simulated gold path. In practice more projects are built when gold is high, so this assumption lowers royalty and stream values somewhat. The write-up states the direction.
- **Past producers with a restart study** use the stage of the restart study, flagged.
- **Table version.** The table is identified by its commit hash, recorded before pricing. Prices are not joined until the Phase 5 table is final (8.8 step 6). If the table changes before then, the ranges are recomputed on the final table; no price has been joined, so this is not a deviation. No Phase 6 aggregate is published before the Phase 5 results are.

Why this source: it is the only build-rate source in the project measured on a price-free frame; it covers PEA, PFS and FS (ADR 0013 has no PEA default, and 4 of the 22 deals rest on a PEA); and it gives timing as well as odds, so no judgment timing prior is needed.

Limits stated in the write-up:

- **Look-ahead.** The table uses outcomes to March 2026, after most deal dates. Leaving the project out removes a deal's own outcome, not the information in other projects' later outcomes.
- **Frame.** Phase 5 covers projects held by companies with no producing mine. A deal whose operator had a producing mine at the announcement is flagged.

### 8.3 The spread range

The spread is the buyer's real required return over the real risk-free rate, on top of the risks the engine simulates (ADR 0008, ADR 0014, `methodology.md` section 7). With odds and timing fixed by 8.2, it is the main remaining input, and its source is independent of the deal prices.

**Source.** Discount rates that royalty and streaming companies disclose for their own gold royalty and stream interests:

- **Who.** The 23 companies on the Phase 6 search list (`data/phase6/search_log.csv`), and no others.
- **Where.** Audited annual financial statements and the MD&A filed with them, in impairment-test or fair-value notes, fiscal years 2012 to 2025.
- **What is recorded.** Each rate; whether real or nominal, pre-tax or post-tax; the asset class it applies to (producing, development, or both); the gold price deck stated with it; the statement date; and the page. One row per company, year and asset class. A range "x% to y%" is recorded as both ends.
- **Conversion.**
  1. Nominal to real with the inflation assumption stated in the same note; if none is stated, with the 10-year US breakeven inflation rate (FRED T10YIE) at the fiscal year end, flagged.
  2. Post-tax to pre-tax only with a pre-tax equivalent disclosed by the same company; otherwise the post-tax rate is used, flagged (it understates the pre-tax rate).
  3. Rate k to spread s = k(1 + r), with r the real rate at the statement date (ADR 0045).
- **Primary set.** Rates for producing assets. The engine already applies development risk through 8.2, so rates that include a development premium would count it twice (ADR 0045 item 3).
- **The prior.** The empirical distribution of the primary set. Each company is weighted equally and its weight is split evenly across its rows, so a company that discloses every year does not outweigh one that disclosed once.
- **Minimum.** At least 8 rates from at least 4 companies. If fewer qualify, no interval score is computed: each deal is shown on a fixed grid of spreads (0%, 2%, 4%, 6%, 8%, 10%, 15%), marked illustrative, with its break-even spread (ADR 0026 item 4).
- **Compilation.** The compiler records only rows the rules above select and logs each judgment. A compiler may see acquisition prices in the same statements; none is recorded. The set and its hash are committed before pricing.

**Fixed-payment streams.** For royalties and for streams that pay a fixed share of spot, s = k(1 + r) is exact (ADR 0045). For a stream that pays a fixed price per ounce it is approximate, because that payment behaves like a fixed cost. Primary values for such streams are labelled "spread conversion approximate", and a sensitivity values them the ADR 0045 way: a flat deck at spot on the deal date, discounted at the drawn k.

The write-up describes the range as "the discount rates royalty companies use in their own statements", not as the market's required return. These are accounting inputs for producing assets, often on flat decks.

### 8.4 How a deal's range is built

For each deal:

1. **Inputs.** The study's annual payable gold for the covered ground (schedule mode), at the coverage share the documents state; the royalty rate or stream terms; for a net smelter return royalty, the study's offsite costs per ounce (none stated: gross revenue, flagged as an upper bound); and market inputs from the snapshot at the announcement date (ADR 0024: real rate, trailing 10-year volatility, zero convenience yield, spot gold, exchange rates). Operating and capital costs do not enter a royalty or stream value once 8.2 replaces the build rule, so the study-entry builder error found in Phase 4 does not reach these values.
2. **Draws.** 2,000 joint draws, each pairing a spread drawn from the 8.3 prior with one Phase 5 bootstrap replicate (rebuilt leaving the deal's project out). Each draw gives one engine value: an expected value in market-consistent mode at that spread and incidence. The range is a range over uncertain inputs, not a distribution of NPVs discounted at a risk-adjusted rate (Davis 1995; ADR 0012).
3. **Simulation error.** Each draw's value states its path count and Monte Carlo standard error. The standard error must be under 1% of the value; otherwise the path count is raised before the freeze. Royalty values that are linear in price are computed in closed form.
4. **Range.** The 10th and 90th percentiles of the 2,000 values: an 80% range under the stated priors. The central value is the median.
5. **Price.** The unconditional consideration in US$ at the announcement date (part 1 rule 1: shares at the last close before the announcement; foreign currency converted at that day's rate from a named central bank or FRED series, recorded). Contingent amounts follow 8.6.

Royalty value follows `methodology.md` section 8 at the drawn spread; stream value follows ADR 0041 (a strip of calls). Terms the engine does not yet model (step-downs, caps, thresholds, debt-linked steps, completion tests, advance minimum royalties as defined in ADR 0072) are implemented and unit-tested on synthetic cases before the freeze. A buy-back at fair market value has no effect on value and is ignored. A buy-back at a fixed price is ignored in the primary run, which overstates value slightly, flagged. A deal with a term that cannot be implemented before the freeze is "not priced": it is counted and reported, never approximated after prices are seen.

### 8.5 Width measure and scoring rule

Deal sizes vary widely, so everything is measured on the log of the price.

**Width.** W = ln(u / l), with l and u the 10th and 90th percentile values. A width of 0.69 means the upper end is twice the lower. Reported as the median and interquartile range across deals.

**Scoring rule.** The interval score (Gneiting and Raftery 2007, *Journal of the American Statistical Association* 102(477), 359-378; the formula is checked against the authors' technical report, University of Washington Department of Statistics Technical Report 463, 2004, section 5.2, equation 19, which states it in an equivalent positively oriented, rescaled form). On log prices, with y = ln(price), l and u the log ends of the 80% range, and alpha = 0.2:

S = (u - l) + (2 / alpha)(l - y) 1{y < l} + (2 / alpha)(y - u) 1{y > u}

Lower is better. The first term is the width; the others charge a miss by its distance outside the range, 10 times over at alpha = 0.2. The score is proper for a central 80% interval: in expectation it is best to report one's true 10th and 90th percentiles, so neither a wide nor a narrow range is rewarded for its own sake. Alpha follows from the range's nominal level (8.4 step 4); it is not a free choice.

**Coverage.** The number of prices inside their ranges, with a Clopper-Pearson 95% interval (Clopper and Pearson 1934, *Biometrika* 26(4), 404-413), beside the nominal 80%. Misses are counted by side.

**Implied spread.** For each deal, the spread at which the engine value at the Phase 5 central incidence equals the price (the break-even spread, `methodology.md` section 7), shown as a distribution against the 8.3 prior. If no spread from 0% to 50% solves, the deal is reported as "above the value at a zero spread" or "below the value at 50%".

### 8.6 Contingent amounts

**Primary: the unconditional price only.** The quantity being predicted contains no model output. Weighting contingent payments by the Phase 5 probability would put the same probability on both sides of the comparison and link price and range mechanically.

**Direction, stated in advance.** Leaving out contingent amounts understates what the buyer pays, so it pushes prices toward the low side of the range. Part 1 limits contingent amounts to 25% of the stated total, so the effect is bounded.

**Sensitivity.** Contingent payments whose trigger the engine models (a construction decision or first production on the covered ground) are added at expected present value: the payment times the probability of the trigger within the window (8.2), discounted at the real risk-free rate from the trigger date. Payments with other triggers are listed and not valued. The number of deals with model-triggered contingent amounts, and the largest such share of a price, are reported, subject to 8.7.

### 8.7 Comparisons, sensitivities and reporting

**Benchmarks**, each priced on the same inputs with no deal price used:

- **B1, study convention.** The royalty or stream valued at the study's own gold deck and discount rate on the study schedule, with no other risk.
- **B2, analyst mode.** The study deck with the CIM stage-based real rate (12.6% PEA, 11.1% PFS, 8.9% FS; Smith 2013 via Lopatnikov and Rumyantsev 2025; `calibration.md` section 7).

**Location is the headline comparison**: the median absolute log error of the engine's central value against B1 and B2.

**Matched-width benchmarks, B1-W and B2-W.** Each benchmark value is centred in a range of the same log width W as the engine's range for that deal. The engine's interval score is compared with theirs, which compares location at equal width. B1 and B2 scored as zero-width points may be shown; the text then states that a zero-width forecast is penalised by construction, so the engine's advantage over them on that score is not a finding.

**Primary results** (aggregate only):

1. coverage k of 22, its Clopper-Pearson interval, misses by side;
2. median width W and its interquartile range;
3. median absolute log error: engine, B1, B2;
4. mean interval score: engine, B1-W, B2-W, with the mean per-deal difference and a bootstrap 95% interval over deals (descriptive, not a test);
5. the distribution of implied spreads against the 8.3 prior;
6. the number not priced, with reasons.

**Reported with and without**, subject to the publication limit below: past producers with a restart study; partial coverage; study more than 3 years old; buy-back at fair market value; not completed; warrants at notional value; related parties; operator with a producing mine at the announcement; Phase 5 project overlap. Also by transaction type and by study stage.

**Sensitivities**, each beside the primary, none replacing it:

- development-asset rates added to the spread set;
- the producing-royalty control (Wharf, `calibration.md` section 8) and any control that qualifies under ADRs 0014 and 0026 before pricing, added to the set;
- post-tax-only rows removed from the set, if 8 rates from 4 companies remain;
- equal weight per company-year in the prior;
- fixed-payment streams valued on a flat deck (8.3);
- the window anchored at the study date instead of the deal date;
- a 10-year window, with the 36-to-60-month hazard extended;
- the Phase 5 linked table in place of the primary table;
- contingent amounts added (8.6);
- 1% convenience yield (ADR 0024);
- alpha = 0.1 and 0.5 with the matching 90% and 50% ranges.

**Publication limit.** Per-deal results are private (section 6). An aggregate over fewer than 5 deals is not published. A with-and-without reading, a split, or a sensitivity is published only if both the group it changes and the rest each hold at least 5 deals; otherwise subtraction would reveal single results, and it is held privately with the per-deal results. On the count, this holds back gross revenue royalties (2), streams (3) and PEA-based deals (4) as separate groups, and every flag covering fewer than 5 deals.

**Wording.** "In a series of 22 disclosed gold royalty and stream deals, k prices fell inside the engine's 80% range." Never "the engine predicts deal prices", that a buyer overpaid or underpaid, or that the market misprices royalties. A price above the range is "consistent with a lower required return, earlier construction, or value outside the study mine plan than the engine assumes"; a price below it, the reverse.

**Known biases, stated in advance.**

- The engine values only the study mine plan (ADR 0014 criterion 6). Value beyond reserves, which buyers often pay for, pushes prices above the range.
- Decisions independent of gold lower values somewhat (8.2).
- Leaving out contingent amounts pushes prices down (8.6).
- The spread set is accounting rates for producing assets on flat decks (8.3).
- The Phase 5 frame differs from the deal sample (8.2).

None is corrected after prices are seen.

### 8.8 Order of work and blinding

1. **Fix this section** with ADR 0073.
2. **Spread set** (8.3) compiled and committed with its hash.
3. **Engine terms** (8.4) implemented with synthetic tests and merged.
4. **Inputs** transcribed for each deal from the study and the deal terms into `data/phase6/inputs/`, with no price fields. Transcription rules are mechanical, and each judgment is logged with its rule. A second person transcribes 6 deals drawn with a recorded seed, without the first transcription; the two are compared on input values, never on engine output.
5. **Freeze.** The pricing script runs on the frozen inputs and writes the ranges, central values, benchmark values and each deal's value-against-spread curve. The freeze commit records the hashes of the Phase 5 table, the spread set, the inputs, the engine commit and the output file, before any price is joined.
6. **Score**, only once the Phase 5 table is final. A separate script joins the private price file and computes 8.5 to 8.7. Per-deal output stays private; the repository receives only the aggregates 8.7 allows.

Nothing in steps 1 to 5 reads a price. People who have seen prices may do steps 2 to 4, which record facts under written rules and compute nothing, but nobody runs the engine on a deal before step 5. Any change to steps 1 to 5 after a price is joined is reported as a deviation, with results shown both ways.

### 8.9 What Phase 6 cannot show

With 22 deals and nominal coverage of 80%, a perfectly calibrated range would put between 14 and 21 prices inside with probability 0.97 (binomial, n = 22, p = 0.8: P(k <= 13) = 0.020, P(k >= 22) = 0.007). Any coverage in that band is consistent with a well-calibrated range. The series can show a gross miscalibration of the range, or that the engine's central value is no closer to prices than the study convention. It cannot confirm that the engine prices royalties well, and the write-up says so.

### 8.10 Pricer conventions (ADR 0073 amendment)

The conventions the pricer needs beyond 8.2 to 8.6 are fixed in the amendment to ADR 0073: mid-year decision dating, end-of-year payments with a mid-year sensitivity, limits and crediting of advances, deflation of nominal caps at breakeven inflation, unpriced deals where a threshold's ounce basis is not stated, and how terms not yet implemented are handled. The largest per-draw Monte Carlo standard error is reported.

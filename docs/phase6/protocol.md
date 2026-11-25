# Phase 6 protocol: royalty and stream pricer, part 1 (counting)

Status: fixed 2026-11-25, before any deal is counted (ADR 0070). Part 2 (spread range, width measure and scoring rule) is fixed after counting and before any deal is priced (ADR 0063).

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

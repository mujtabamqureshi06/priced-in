# Phase 4 tax method

- Status: written before the validation in section 4 was run. The commit that adds this file is the record of that order.
- Decision record: ADR 0054.

Some studies in the panel report only pre-tax NPV and IRR. For those, the study builder (`pricedin.parametric`) is calibrated to the pre-tax figures and the after-tax schedule is modelled with the method below. Studies that report after-tax figures are calibrated to them directly; the same regime table supplies their tax rate, which the builder needs for the depreciation shield.

## 1. Rate

One combined statutory marginal rate per project, taken from `data/phase4/tax_regimes.csv` for the project's jurisdiction and the period containing the entry study's date.

- It combines national corporate income tax, sub-national corporate income tax (Canadian provinces and territories, US states) and profit-based mining taxes (for example Quebec mining duties, the Ontario mining tax, the Nevada net proceeds of minerals tax).
- Where one tax is deductible against another, the combination follows the formula in the table's `formula` column.
- Progressive mining taxes use the marginal rate for a profitable mid-size gold mine; the range is in the table's notes.
- Revenue-based royalties and government carried interests are excluded. They are not income taxes, and a study's pre-tax cash flow already deducts royalties.
- Each row has a source, a location and a status: `verified` (government, legislation, or a large accounting firm's tax guide), `secondary` (another published source) or `unsourced`. Results that depend on a secondary rate say so.

## 2. Base

The builder's existing schedule: tax at the combined rate on revenue less operating cost less straight-line depreciation of initial capital over the mine life, never below zero in a year. Loss carry-forwards, tax holidays and investment allowances are not modelled. Where a study discloses one (for example Mali's tax holiday at Kobada, or tax losses at Laiva and Davyhurst), the case carries a flag.

## 3. Gaps

Three jurisdiction periods have no sourced rate: Ecuador in 2012, Guyana in 2012 to 2016 and Sudan in 2012 to 2015. No pre-tax-only study in the panel falls in them. If one later does, that project is reported only in the results that use reported after-tax figures.

## 4. Validation

- **Set:** every panel study whose release reports pre-tax and after-tax NPV and IRR at the same discount rate and base case (the both-basis check of 79 releases, `reports_both = yes`).
- **Test:** calibrate the builder to the pre-tax NPV and IRR with the rate from section 1, then compare the modelled after-tax NPV with the study's reported after-tax NPV.
- **Statistics:** median absolute error and median signed error as a share of reported after-tax NPV, overall and by country, and the number of studies the builder could not calibrate.
- **Rule:** if the median absolute error exceeds 10%, the primary test uses only projects with reported after-tax figures and the tax-modelled projects move to a check (ADR 0054).
- **Construction period:** where a study does not state one, the default from section 5.

## 5. Construction-period default

The builder needs a whole number of pre-production years. Where a study states a construction or pre-production period, it is rounded to the nearest whole year, with a minimum of one. Where it does not, the default comes from the 38 inclusions that do state one, split at the panel's median initial capital (US$125 million, with Canadian and Australian dollars converted at 0.80 and 0.75 US$ for the split only):

| Initial capital | Studies stating a period | Median period | Default |
|---|---|---|---|
| US$125 million or less | 21 | 1.0 years | 1 year |
| Above US$125 million | 17 | 2.0 years | 2 years |

Every result is also run with the other value, and the effect on project value is reported.

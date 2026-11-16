# 0050. LBMA cross-check of the gold spot snapshots

- Status: accepted
- Date: 2026-11-16
- Amends: ADR 0024 (item 4 and its revisit trigger)

## Context

ADR 0024 takes gold spot from a vendor daily series (status P) and requires a cross-check against the LBMA Gold Price PM for each date. A difference above 0.5% was to reopen the decision (#93).

LBMA's own site blocks automated access, so the PM fixes were read from a dealer's republished daily table (SD Bullion; status P). Four of seven dates differ by more than 0.5%:

| Date | Vendor | LBMA PM | Difference |
|---|---|---|---|
| 2021-06-07 | 1,898.50 | 1,888.40 | +0.53% |
| 2022-06-10 | 1,871.22 | 1,830.00 | +2.25% |
| 2022-08-12 | 1,801.60 | 1,792.10 | +0.53% |
| 2023-07-13 | 1,960.61 | 1,958.05 | +0.13% |
| 2023-12-15 | 2,019.82 | 2,032.30 | -0.61% |
| 2023-12-18 | 2,025.60 | 2,023.95 | +0.08% |
| 2024-02-23 | 2,035.79 | 2,027.45 | +0.41% |

The LBMA PM is set at 3 pm London, 10 am New York. The share prices this project reads are closing prices at 4 pm New York, so the timing of the gold price matters.

## Timing test

A gold price at 4 pm New York is implied by the SPDR Gold Trust: GLD's closing price divided by its gold per share. Gold per share is anchored at 0.093158 oz (29,531.0 thousand oz over 317.0 million shares at December 31, 2022, SPDR Gold Trust Form 10-Q). It is carried to each date at the trust's 0.40% annual sponsor fee. GLD closes are from Yahoo Finance (status P).

| Date | GLD close | Implied gold, 4 pm New York | Vendor vs implied | LBMA PM vs implied |
|---|---|---|---|---|
| 2021-06-07 | 177.87 | 1,897.4 | +0.06% | -0.47% |
| 2022-06-10 | 174.54 | 1,869.4 | +0.10% | -2.11% |
| 2022-08-12 | 167.87 | 1,799.2 | +0.13% | -0.40% |
| 2023-12-15 | 187.00 | 2,015.0 | +0.24% | +0.86% |

The vendor series tracks the 4 pm price within 0.24% on every date with a gap. The LBMA PM is 0.40% to 2.11% away. With the March 31, 2023 anchor instead, the vendor is within 0.30% and the LBMA PM 0.33% to 2.05% away. June 10, 2022 was a US CPI release day, and gold rallied after the London fix.

## Decision

1. The vendor closing price stays the gold spot for every snapshot: one source throughout, synchronous with the closing share prices.
2. Each snapshot records the LBMA PM beside it (`gold_lbma_pm`, status P) as the cross-check.
3. Revised trigger: a gap above 0.5% needs an explanation backed by timing evidence, with its effect disclosed. It reopens this decision only if the explanation fails, or if the gap moves a headline break-even by more than 1 point.
4. Gold Standard (June 10, 2022) is shown at the LBMA PM as a named sensitivity. Its break-evens move 0.8 to 1.7 points. Elsewhere the LBMA PM moves break-evens by 0.2 points or less and odds at spot by 0.02 or less.

## Consequences

- No headline number changes. The Gold Standard note shows the sensitivity table.
- The LBMA values stay P until they are confirmed on LBMA's own site.

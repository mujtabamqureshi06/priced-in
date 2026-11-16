# Calibration

Every prior the engine uses lives in `data/priors.yaml` (#51) with its value, units, source, location and status. This document explains each group of priors and its limits. Sections are completed as the priors are entered.

## 1. Stage transitions

No cohort-based source has been found that tracks projects from a study stage to a build decision ([sources.md](sources.md), section 2). ADR 0013 sets the defaults:

| Prior | Value | Sensitivity values | Source | Flag |
|---|---|---|---|---|
| `stage.pfs_to_fs` | 0.82 | 0.50 and 0.95 (judgment) | Sykes and Trench (2014), via Lopatnikov and Rumyantsev (2025), Table 1 | Count ratio, not a conversion rate |
| `stage.fs_to_build` | 0.88 | 0.75 (AMC, practitioner); 0.50 and 0.95 (judgment) | Same | Count ratio, not a conversion rate; understates odds for permitted or financed cases |

**Why a count ratio is not a conversion rate.** Sykes and Trench counted how many copper projects sat at each stage on one date: 92 at PFS, 75 at FS, 66 producing or constructing. Dividing one count by the next gives 0.82 and 0.88. But projects stay in some stages much longer than others. Mines stay "producing" for many years, so they pile up in that box and push the ratio up; projects that stall at FS pile up there and push it down. The ratio mixes how long projects sit in each stage with how many move on, so its bias has no known direction. That is why the value is flagged and why the case write-ups show results at both 0.88 and 0.75.

The values are fixed in the simulation, not drawn at random: the expected value is close to linear in them, so drawing them would hide the assumption without changing the answer much. There is no default for PEA or earlier stages: `pricedin.defaults.stage_odds` raises an error for a PEA-stage case, so the caller must supply a value and label it as a user assumption.

## 2. Stage durations and lead times

Stage gates carry probability only; they add no duration (ADR 0023). Base timing is set per case from an independent sourced duration where one exists, otherwise from company guidance published by the valuation date: South Railroad 4 years (BLM median of 3.79 years from Notice of Intent to Record of Decision, CEQ 2020; sensitivities 3 and 5), Osino 1 year (DFS Section 25; sensitivities 0 and 2). There is no timing prior: the frontier carries delay, and S&P and MinEx discovery-to-production lead times are not used because they do not measure delay against a company's own schedule. The build window is 5 years (10 as a sensitivity), a judgment (ADR 0023).

## 3. Capital cost overrun

`capex.overrun.fs` follows Bertisen and Davis (2008). Each simulated path draws one capital cost ratio: 0.91 plus a lognormal draw with mean 0.35 and standard deviation 0.42. The ratio compares as-built cost in nominal dollars with the feasibility estimate in real dollars, so the engine multiplies it by `capex.inflation_adjustment` (0.914, the authors' own inflation assumption) to stay in real terms (ADR 0007). The result is a real overrun of 15.2% on average (0.914 x 1.26), with a long right tail.

Why a shifted lognormal: the smallest observed ratio was 0.93, so costs rarely come in far under budget, while a few projects cost twice the estimate. A lognormal shifted to start near 0.91 captures both features.

Limits, carried in the flag: the sample is 63 projects that were financed and built, with bankable-feasibility estimates. It says nothing about PFS-stage estimates, which are less precise, and projects that were never built are missing.

PFS cases (`capex.overrun.pfs`, ADR 0015) use the same distribution with a flag saying it probably understates PFS cost risk. Each PFS write-up also shows a sensitivity in which the lognormal part keeps its mean of 0.35 but its standard deviation widens from 0.42 to 0.70 (a judgment based on conventional accuracy bands of about ±25% at PFS and ±15% at FS).

## 4. Ramp-up

McNulty (1998) curves, digitised from the original Figure 1 (`data/ramp_up_mcnulty_1998.csv`), weighted by McNulty's own Table 2 counts for the plant class (ADR 0019). Both public cases fall in the hydrometallurgical oxide class (6 of 7 plants Series 1, 1 of 7 Series 2); the all-plant counts (23/5/6/7 of 41) are the named sensitivity. The curves replace a study's own ramp-up years rather than adding to them. Weights are counts from a small, pre-1998 sample and are labelled as such, not presented as precise probabilities.

## 5. Gold price volatility and the risk-free curve

Market inputs come only from the dated snapshots in `data/snapshots/` (ADR 0024): the 10-year TIPS yield as the flat real rate (FRED DFII10), trailing 10-year realised gold volatility from the daily series (GVZ on the date as a sensitivity), a zero gold convenience yield (flagged; 1% sensitivity; not checked against futures, ADR 0027), and the Government of Canada 10-year yield with spot USD/CAD for C$ payments. The full TIPS curve is a Phase 3 refinement.

## 6. Dilution and financing

Equity is raised at a 10.54% discount to fair value (Carpentier and Suret 2009, mean of 3,476 Canadian private placements, 1993 to 2003; median 9.09% and 15% as sensitivities), with all-equity funding as the headline: the upper bound on dilution (ADR 0030). Debt shares of 30% and 60% are judgment sensitivities. Underwriting fees are not modelled.

## 7. Analyst-mode discount rates

The CIM Mineral Economics survey (Smith 2013, as reported in Lopatnikov and Rumyantsev 2025) gives real gold rates of 12.6% (scoping), 11.1% (PFS), 8.9% (FS) and 5.7% (producing). They are used as cross-checks only: the FS rate as a stricter build-rule hurdle (ADR 0023), and the producing rate labelled "producing-mine valuation convention; not royalty-specific" (ADR 0028).

## 8. Buyer's required return (ADR 0008)

A constant real spread over the real risk-free rate, calibrated on purchases of royalties on producing mines (ADR 0014, amended by 0026 and 0028). One control qualifies so far: Metalla's 2020 purchase of a 1.0% gross value royalty on Coeur's Wharf mine (Tier 2 schedule from disclosed reserves and guidance; 81% paid in shares), which implies about 15.8% on reserve-only flows, a lower bound. The convention reference is Osisko Gold Royalties' audited 2020 post-tax real discount rate of 3.5% for its producing Canadian NSR royalties (4.76% pre-tax equivalent). The two put South Railroad on opposite sides of the feasible region, so the spread is not fixed: results are shown across spreads with the break-even marked, until a second qualifying control agrees within tolerance.

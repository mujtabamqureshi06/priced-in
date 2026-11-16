# Calibration

Every prior the engine uses lives in `data/priors.yaml` (WP 0.4) with its value, units, source, location and status. This document explains each group of priors and its limits. Sections are completed as the priors are entered.

## 1. Stage transitions

No cohort-based source has been found that tracks projects from a study stage to a build decision ([sources.md](sources.md), section 2). ADR 0013 sets the defaults:

| Prior | Value | Sensitivity values | Source | Flag |
|---|---|---|---|---|
| `stage.pfs_to_fs` | 0.82 | 0.50 and 0.95 (judgment) | Sykes and Trench (2014), via Lopatnikov and Rumyantsev (2025), Table 1 | Count ratio, not a conversion rate |
| `stage.fs_to_build` | 0.88 | 0.75 (AMC, practitioner); 0.50 and 0.95 (judgment) | Same | Count ratio, not a conversion rate; understates odds for permitted or financed cases |

**Why a count ratio is not a conversion rate.** Sykes and Trench counted how many copper projects sat at each stage on one date: 92 at PFS, 75 at FS, 66 producing or constructing. Dividing one count by the next gives 0.82 and 0.88. But projects stay in some stages much longer than others. Mines stay "producing" for many years, so they pile up in that box and push the ratio up; projects that stall at FS pile up there and push it down. The ratio mixes how long projects sit in each stage with how many move on, so its bias has no known direction. That is why the value is flagged and why the case write-ups show results at both 0.88 and 0.75.

The values are fixed in the simulation, not drawn at random: the expected value is close to linear in them, so drawing them would hide the assumption without changing the answer much. There is no default for PEA or earlier stages; the engine refuses to run a PEA-stage case unless the user supplies a value, which is then labelled as a user assumption.

## 2. Stage durations and lead times

## 3. Capital cost overrun

`capex.overrun.fs` follows Bertisen and Davis (2008). Each simulated path draws one capital cost ratio: 0.91 plus a lognormal draw with mean 0.35 and standard deviation 0.42. The ratio compares as-built cost in nominal dollars with the feasibility estimate in real dollars, so the engine multiplies it by `capex.inflation_adjustment` (0.914, the authors' own inflation assumption) to stay in real terms (ADR 0007). The result is a real overrun of about 14% on average, with a long right tail.

Why a shifted lognormal: the smallest observed ratio was 0.93, so costs rarely come in far under budget, while a few projects cost twice the estimate. A lognormal shifted to start near 0.91 captures both features.

Limits, carried in the flag: the sample is 63 projects that were financed and built, with bankable-feasibility estimates. It says nothing about PFS-stage estimates, which are less precise, and projects that were never built are missing.

PFS cases (`capex.overrun.pfs`, ADR 0015) use the same distribution with a flag saying it probably understates PFS cost risk. Each PFS write-up also shows a sensitivity in which the lognormal part keeps its mean of 0.35 but its standard deviation widens from 0.42 to 0.70 (a judgment based on conventional accuracy bands of about ±25% at PFS and ±15% at FS).

## 4. Ramp-up

Not modelled for heap-leach cases such as South Railroad: the study's own ramp-up profile is used and the waterfall labels the step "not modelled; study ramp-up profile used" (ADR 0017). Milled cases will use McNulty (1998) curves once the original paper is in hand; the curves replace the study's ramp-up years rather than adding to them.

## 5. Gold price volatility and the risk-free curve

## 6. Dilution and financing

## 7. Analyst-mode discount rates

## 8. Buyer's required return (ADR 0008)

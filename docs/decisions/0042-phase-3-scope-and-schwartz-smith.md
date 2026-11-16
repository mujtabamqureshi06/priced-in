# 0042. Rest of Phase 3: Orla, Schwartz-Smith, and the v1.0 exit

- Status: accepted
- Date: 2026-11-16

## Context

The Phase 3 exit was: least-squares Monte Carlo validated, multi-asset outputs shown as bands, v1.0.0 tagged. The phase also lists copper and uranium.

- **Copper (#77):** the Schwartz-Smith two-factor model calibrated to futures by the Kalman filter.
- **Uranium (#78):** a term price and a consensus deck.

No free historical panel of copper futures curves is available. One site keeps two years of expired contracts; another is not reachable. A calibration on real futures is therefore not feasible now.

## Decision

1. **Multi-asset test company (#75):** Orla Mining, after it closed the Gold Standard Ventures acquisition in August 2022.
   - The band for South Railroad is enterprise value less three items: Camino Rojo (producing, valued by the engine from its feasibility study), Cerro Quema (a band from its pre-feasibility study, risked) and net cash.
   - Exploration ground is valued at zero, flagged.
   - Each asset uses the latest public plan before the valuation date.
2. **A new takeover case:** Orla's acquisition of Gold Standard Ventures. It uses the same 2022 feasibility study through the takeover adapter. South Railroad is then read through a royalty (2021), a takeover (2022) and a sum-of-parts band.
3. **Copper:** `pricedin.schwartz_smith` implements the model (Schwartz and Smith 2000), its futures formula, the exact state transition and the Kalman-filter likelihood with maximum-likelihood fitting.
   - It is tested by synthetic recovery.
   - Schwartz and Smith estimated their model on oil, so their parameters are not used for copper.
   - Any copper illustration uses verified copper-specific parameters, or synthetic data only.
4. **v1.0 exit, amended:** least-squares Monte Carlo validated (ADRs 0037, 0040); multi-asset outputs shown as bands (Orla); Schwartz-Smith with synthetic recovery. Calibration to real copper futures and the uranium price model move to after v1.0.
5. **Benchmark status:** the Brennan and Schwartz (1985) values were checked against the original article and moved from status S to V (ADR 0040).

## Synthetic recovery

Five years of weekly curves of six contracts (maturities 0.25 to 5 years), simulated from known parameters with 0.4% measurement noise, recover:
- the mean-reversion speed within 20%;
- both volatilities within 10% to 15%;
- the risk-neutral long-term drift within 0.5 percentage points;
- the correlation within 0.2.

The real-world drifts and the short-term risk premium are weakly identified, as Schwartz and Smith note, and are not tested.

## Consequences

The v1.0 release can close on methods validated against known answers and one multi-asset band. Commodity calibration to real futures becomes later work, waiting on a data source.

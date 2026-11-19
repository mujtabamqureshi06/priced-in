# 0059. Limited liability applied at the build decision, not on each path

- Status: accepted
- Date: 2026-11-19
- Supersedes: ADR 0047
- Amends: ADR 0030 (equity claim), ADR 0015 rule 3 (a second test at the decision), ADR 0038 (the least-squares rule's payoff)

## Context

ADR 0047 floored the equity claim at zero on every simulated path: equity = share x max(project - transfer, 0), evaluated after the path's gold prices and capital overrun were known. That floors realised outcomes with hindsight. Shareholders commit when construction is decided, before the overrun and later prices are known; once the money is raised and spent, a bad outcome is theirs. The floor gave them a put option they do not hold, and made the equity claim worth more than the project it is a share of.

E[max(X, 0)] is at least max(E[X], 0). On Osino and South Railroad, at a 1% real rate and 15% volatility, with the default overrun prior and financing, the floored claim was 4.7% to 7.4% above the unfloored claim at spot equal to the study price, and 25% to 70% above it at 0.7 to 0.8 times the study price (100,000 paths). At 0.8 times, Osino's floored equity (351.9) exceeded its project value (300.4).

## Decision

1. **Decision-time test.** With the build rule on, a path builds in year b only if the flat-price rule passes (ADR 0023) and the value of building now, C, is not negative:
   C = value of building at year b's gold price on the expected price path, at the run's discount rate (`engine._build_value`)
   - (mean overrun ratio - 1) x PV of initial and expansion capital
   - d / (1 - d) x PV of the equity raise at the mean ratio, only when the run includes a `Financing`.
   Present values are at the build year on the study's own timing. The mean overrun ratio is computed from the prior, real factor x (shift + exp(mu + sigma^2 / 2)), never from a path's draw (`engine.mean_overrun_ratio`), consistent with ADR 0015 rule 3: the board knows the overrun distribution, not the outcome.
2. **One decision per run.** The same build year applies to every claim valued in the run (project, equity, royalty, stream), so all claims stay on the same paths. The dilution term enters only for an equity run: an acquirer funds construction without a discounted raise, which is why takeover prices are read against the project claim (ADR 0031).
3. **No per-path floor.** On built paths, equity = operator share x (project - PV of the transfer). A single path can carry negative equity; only expectations are reported. On unbuilt paths equity is the operator's share of minus the holding cost (ADR 0049), zero when there is none.
4. **Least-squares rule.** The same C replaces `_build_value` in the least-squares payoff, so the secondary build mode sees the same costs (ADR 0038).
5. **Unchanged.** With the build rule off (the reconciliation setting), every path that passes its gates builds, as before. Contractual advance royalty payments (ADR 0021) and the holding cost (ADR 0049) remain on unbuilt paths.

## Consequences

- Tests: equity never exceeds share x project on any path, for two cases at spot 0.5 to 2 times the study price; royalty less advances is zero and project value is zero on unbuilt paths; the gate's mean overrun matches the analytic formula, and a heavy issue discount stops building that the project-only run would do.
- On the cases tested, the decision-time test did not change which paths build (the flat-price rule bound first); the change in equity comes from removing the floor.
- Published equity figures fall. The Osino, Gold Standard and other case notes that cite equity are re-run; the CHANGELOG gives old value, new value and reason.
- Phase 4: the frozen sample-1 primary result is unchanged. Sample-1 values under this rule are an exploratory secondary, computed after outcomes were known. This change and its tests are merged, and the engine commit recorded, before any value in the next sample is computed.

## Revisit if

A case needs a parent guarantee or another payoff that makes negative equity impossible, or the acceptance tests fail on a case for a reason other than Monte Carlo error.

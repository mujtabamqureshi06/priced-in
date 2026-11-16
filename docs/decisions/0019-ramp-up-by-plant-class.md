# 0019. Ramp-up by McNulty plant class, including heap leach (supersedes 0017)

- Status: accepted
- Date: 2026-11-16
- Decided by: Independent Decision Maker (owner's proxy), decision record DR-006
- Applied with: ADR 0029 (fallback: not modelled in either public case)
- Supersedes: ADR 0017, which rested on a wrong premise (that McNulty's curves came only from mills and chemical plants)

## Context

McNulty (1998), Table 2 (p. 53), classifies its 41 plants by type and series. Hydrometallurgical oxide plants (agitated leaching and heap or dump leaching of gold or copper oxide ores) were 6 Series 1 and 1 Series 2. Heap leach is in the sample. The curves measure percent of annualised design capacity (production rate), not leach kinetics.

## Decision

1. Every case, heap leach or mill, uses McNulty's curves (`data/ramp_up_mcnulty_1998.csv`) weighted by McNulty's own Table 2 counts for its plant class.
2. **South Railroad** (hydrometallurgical oxide class: 6/7 Series 1, 1/7 Series 2). The curves replace the study's ramp-up; they do not add to it. The study's steady-state stacking rate (8,236 kt a year, PFS Table 22-7) is 100% of design. Year 1 stacked tonnes are the drawn curve's Year 1 average times that rate, replacing the study's 7,618 kt. Tonnes not stacked in Year 1 are deferred to the end of the mine life, recovered on the study's own recovery profile. The study's leach kinetics are unchanged. The step is reported with whatever sign it has. If throughput cannot be cleanly separated from kinetics in the schedule-mode table, the step reverts to "not modelled; study ramp-up profile used", with the reason recorded.
3. **Named sensitivity:** the all-plant weights (23/5/6/7 of 41). Outputs label the weights "McNulty (1998) Table 2 counts, 7 plants, plants built before 1998" (or 41 plants for the all-plant set) and never present them as precise probabilities.
4. **Osino's class (Mastermind, routine):** hydrometallurgical oxide plants. McNulty's Table 1 places agitated leaching of gold ores in that class. The Twin Hills flowsheet is conventional crushing, milling, gravity, pre-oxidation and carbon-in-leach (DFS Section 1 summary and Section 17.2.9); flotation was tested but is not in the flowsheet, and there is no autoclave or bio-oxidation step. McNulty's sulfide class covers biologically assisted sulfide heap leaching, ambient agitated leaching of sulfides and autoclaving. The fit is not exact: Twin Hills treats mostly fresh ore (55.9 of 64.5 Mt, DFS Table 22.3.2) with an atmospheric pre-oxidation step, so the mapping is recorded as a judgment. The same 6/7 and 1/7 weights apply, with the all-plant weights as the sensitivity. The DFS expects nameplate within three months (Section 22.2), faster than McNulty's Series 1 average (87% at six months), so the step is likely negative for Osino.

## Consequences

The waterfall's ramp-up step is modelled for both public cases. Revisit if throughput cannot be separated (item 2) or a larger heap-leach ramp-up sample is found.

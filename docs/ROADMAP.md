# Roadmap

Phases close on exit criteria, not dates. The full work-package detail lives in the project build plan; this file is the summary kept in the repository. Sequencing follows ADR 0009: Phase 0, then the Phase 1 core on two public cases, then one royalty inversion on South Railroad, before app polish.

| Phase | Goal | Closes when | Status |
|---|---|---|---|
| 0. Foundation | Repository, tooling, verified sources, priors registry, input template, founding ADRs | CI green; every prior verified or flagged; templates for Osino and South Railroad traceable to report pages; owner can explain the design | In progress |
| 1. Forward engine | Simulate a gold project; value project, equity and royalty from the same paths; waterfall; app | Engine reproduces each study NPV with risks off; waterfall reconciles step by step; owner walk-through passes; v0.1.0 | Not started |
| 2. Price adapters and inversion | Implied odds and timing from royalty, developer and takeover prices; public deal back-test | Synthetic recovery passes; controls behave sensibly or deviations explained; v0.2.0 | Not started (South Railroad inversion pulled forward) |
| 3. Depth | Multi-asset adapter, Longstaff-Schwartz build decision, copper, uranium, streams | LSM validated against QuantLib and Brennan-Schwartz (1985); v1.0.0 | Not started |
| 4. Evidence | Do implied odds predict builds? | Panel reproducible; results stated without overclaiming | Not started |
| 5. Launch | Public polish, confidentiality audit, outreach | Every public number traceable; nothing private public | Not started |
| 6. Final private test | Run on private cases outside this repository | Comparison done privately | Not started |

## Phase 0 work packages

| WP | Content | Status |
|---|---|---|
| 0.1 | Repository and tooling | Done locally; awaiting GitHub repository |
| 0.2 | Project documents | Done |
| 0.3 | Source verification (`docs/sources.md`) | Case facts done; calibration sources partly done |
| 0.4 | Priors registry (`data/priors.yaml`, loader) | Not started |
| 0.5 | Input template and hand-filled cases | Not started; needs the DFS and PFS documents |
| 0.6 | Founding ADRs | Done (0001 to 0012) |

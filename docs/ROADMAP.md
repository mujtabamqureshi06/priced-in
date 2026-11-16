# Roadmap

Phases close on exit criteria, not dates. The full work-package detail lives in the project build plan; this file is the summary kept in the repository. Sequencing follows ADR 0009: Phase 0, then the Phase 1 core on two public cases, then one royalty inversion on South Railroad, before app polish.

| Phase | Goal | Closes when | Status |
|---|---|---|---|
| 0. Foundation | Repository, tooling, verified sources, priors registry, input template, founding ADRs | CI green; every prior verified or flagged; templates for Osino and South Railroad traceable to report pages; owner can explain the design | Criteria met; owner walk-through pending |
| 1. Forward engine | Simulate a gold project; value project, equity and royalty from the same paths; waterfall; app | Engine reproduces each study NPV with risks off; waterfall reconciles step by step; owner walk-through passes; v0.1.0 | Released as v0.1.0; app live at priced-in.streamlit.app; ramp-up not modelled in the public cases (ADR 0029); owner walk-through to confirm |
| 2. Price adapters and inversion | Implied odds and timing from royalty, developer and takeover prices; public deal back-test | Synthetic recovery passes; controls behave sensibly or deviations explained; v0.2.0 | Criteria met; released as v0.2.0. Royalty, developer and takeover adapters; South Railroad, Osino and Sorby Hills; transaction dataset; multi-metal royalties; back-test write-up approved (ADRs 0028 to 0036) |
| 3. Depth | Multi-asset adapter, Longstaff-Schwartz build decision, copper, uranium, streams | LSM validated against QuantLib and Brennan-Schwartz (1985); v1.0.0 | Not started |
| 4. Evidence | Do implied odds predict builds? | Panel reproducible; results stated without overclaiming | Not started |
| 5. Launch | Public polish, confidentiality audit, outreach | Every public number traceable; nothing private public | Not started |
| 6. Final private test | Run on private cases outside this repository | Comparison done privately | Not started |

## Phase 0 work packages

| WP | Content | Status |
|---|---|---|
| 0.1 | Repository and tooling | Done (branch protection not available from this session) |
| 0.2 | Project documents | Done |
| 0.3 | Source verification (`docs/sources.md`) | Case facts done; Bertisen and Davis read in full; others in progress |
| 0.4 | Priors registry (`data/priors.yaml`, loader) | In progress: loader, stage priors, FS overrun |
| 0.5 | Input template and hand-filled cases | Done: South Railroad (exact) and Osino (within cell rounding) |
| 0.6 | Founding ADRs | Done (0001 to 0012) |

## Phase 1 work packages

| WP | Content | Status |
|---|---|---|
| 1.1 | Simulation core and runner | Done (`engine.simulate`, seeds, standard errors) |
| 1.2 | Gold price model | Done |
| 1.3 | Project cash flow | Done (schedule mode, ADR 0018) |
| 1.4 | Stage gates and delays | Done (ADRs 0013, 0022, 0023, 0025) |
| 1.5 | Overrun and ramp-up | Overrun done (ADR 0015); ramp-up not modelled in the public cases (ADR 0029) |
| 1.6 | Build decision | Done (fixed rule, ADR 0023) |
| 1.7 | Discounting | Done (ADRs 0012, 0024) |
| 1.8 | Claims | Done: project, royalty with advances, equity with dilution (ADRs 0021, 0030) |
| 1.9 | Waterfall | Done |
| 1.10 | Sensitivities and readout | Done |
| 1.11 | Public cases | Done: `docs/cases/` |
| 1.12 | App | Built (`app/streamlit_app.py`); deployment needs the owner's Streamlit account |
| 1.13 | Documentation and release | Done: v0.1.0 |

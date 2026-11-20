# Roadmap

Phases close on exit criteria, not dates. This file summarises the plan; each item is a GitHub issue. Sequencing follows ADR 0009: Phase 0, then the Phase 1 core on two public cases, then one royalty inversion on South Railroad, before app polish.

| Phase | Goal | Closes when | Status |
|---|---|---|---|
| 0. Foundation | Repository, tooling, verified sources, priors registry, input template, founding ADRs | CI green; every prior verified or flagged; templates for Osino and South Railroad traceable to report pages; design reviewed | Done |
| 1. Forward engine | Simulate a gold project; value project, equity and royalty from the same paths; waterfall; app | Engine reproduces each study NPV with risks off; waterfall reconciles step by step; design review passes; v0.1.0 | Released as v0.1.0; app live at priced-in.streamlit.app; ramp-up not modelled in the public cases (ADR 0029) |
| 2. Price adapters and inversion | Implied odds and timing from royalty, developer and takeover prices; public deal back-test | Synthetic recovery passes; controls behave sensibly or deviations explained; v0.2.0 | Criteria met; released as v0.2.0. Royalty, developer and takeover adapters; South Railroad, Osino and Sorby Hills; transaction dataset; multi-metal royalties; back-test write-up approved (ADRs 0028 to 0036) |
| 3. Depth | Multi-asset adapter, Longstaff-Schwartz build decision, copper model, streams | LSM validated against QuantLib and Brennan-Schwartz (1985); multi-asset bands (Orla); Schwartz-Smith synthetic recovery; v1.0.0 (ADR 0042) | Criteria met; released as v1.0.0. LSM build rule, Brennan-Schwartz replication, Shapley waterfall, streams, Schwartz-Smith, Orla sum of parts, Gold Standard takeover; Review 1 corrections (ADRs 0037 to 0050) |
| 4. Evidence | Does the price-to-built-value ratio anticipate construction decisions? | Panel reproducible; results stated without overclaiming | Criteria met (`docs/phase4/results.md`): inconclusive at 80 projects, no better than P/NAV or study stage; second sample shelved (ADR 0063) |
| 5. Stage-to-build table | Probability and timing of a construction decision, and of a takeover, by study stage | Calibration on a time split, with pass marks fixed before the run | Not started |
| 6. Royalty and stream pricer | Price royalties and streams on pre-production projects; test on disclosed deals | Model and scoring rules fixed before any deal is priced; results reported in aggregate | Not started |
| 7. Study-entry tool | A study's headline figures in; risked value, peer position and a royalty or stream range out | Builder error bands by project margin, validated on new tables | Not started |
| 8. Design | App and public visuals | Specification implemented | Not started |
| 9. Launch | Public polish, confidentiality audit, documentation | Every public number traceable; nothing private public | Not started |

## Phase 0

| Issue | Content | Status |
|---|---|---|
| #48 | Repository and tooling | Done |
| #49 | Project documents | Done |
| #50 | Source verification (`docs/sources.md`) | Open: case facts and the main method sources verified; remaining items listed in the sources register |
| #51 | Priors registry (`data/priors.yaml`, loader) | Done |
| #52 | Input template and hand-filled cases | Done: South Railroad (exact) and Osino (within cell rounding) |
| #53 | Founding decision records | Done (ADRs 0001 to 0012) |

## Phase 1

| Issue | Content | Status |
|---|---|---|
| #54 | Simulation core and runner | Done |
| #55 | Gold price model | Done |
| #56 | Project cash flow | Done (ADR 0018) |
| #57 | Stage gates and delays | Done |
| #58 | Capital overrun and ramp-up | Overrun done; ramp-up not modelled in the public cases (ADR 0029) |
| #59 | Build decision | Done (ADR 0023) |
| #60 | Discounting | Done (ADRs 0012, 0024) |
| #61 | Claims | Done (ADRs 0021, 0030) |
| #62 | Waterfall | Done |
| #63 | Sensitivities and readout | Done |
| #64 | Public cases | Done |
| #65 | App | Done: https://priced-in.streamlit.app/ |
| #66 | Documentation and release | Done: v0.1.0 |

## Phase 2

| Issue | Content | Status |
|---|---|---|
| #67 | Adapter interface | Done (ADR 0031) |
| #68 | Royalty adapter | Done |
| #69 | Single-asset developer adapter | Done; Osino July 2023 value added in #90 (ADR 0048) |
| #70 | Takeover adapter | Done |
| #71 | Inversion and odds-timing frontier | Done |
| #72 | Multi-commodity revenue | Done (ADR 0036) |
| #73 | Royalty transaction dataset | Done (ADR 0034) |
| #74 | Back-test and write-up | Done: v0.2.0 |

## Phase 3

| Issue | Content | Status |
|---|---|---|
| #75 | Multi-asset sum-of-parts adapter (Orla Mining) | Done (ADR 0044) |
| #76 | Optimal build decision by least-squares Monte Carlo | Done (ADRs 0037, 0038, 0040) |
| #77 | Copper price model | Done with synthetic recovery; real-futures calibration in #91 |
| #78 | Uranium price model | Moved to after v1.0 (ADR 0042) |
| #79 | Order-independent waterfall | Done (ADR 0039) |
| #80 | Streams | Done (ADR 0041) |
| #81 | Gold Standard Ventures takeover case | Done (ADR 0043) |

Later phases are tracked by the `phase-4` and `phase-5` labels on the issue tracker.

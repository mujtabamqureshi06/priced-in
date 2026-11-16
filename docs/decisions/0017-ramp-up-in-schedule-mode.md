# 0017. Ramp-up risk in schedule mode

- Status: superseded by ADR 0019 (premise was wrong: heap leach is in McNulty's sample)
- Date: 2026-11-16
- Changes: build plan WP 1.5

## Context

The build plan calls for McNulty ramp-up series 1 to 4 with weights. McNulty (1998), Mining Engineering 50(10):50-55, built the curves from 41 metallurgical and chemical plants; the curve values are in figures in a paywalled paper and the series weights are not published as probabilities. A schedule-mode study already contains its own ramp-up profile, and South Railroad is a heap leach, where early recovery reflects leach kinetics rather than plant ramp-up.

## Decision

1. **Heap-leach cases (including South Railroad):** ramp-up risk is not modelled. The waterfall shows the step as "not modelled; study ramp-up profile used", never as zero.
2. **Milled cases (Osino, a CIL plant):** McNulty curves once the original paper is in hand. Use McNulty's own classification of his 41 projects by series if the paper reports it; otherwise Series 1 about 0.5 (MacKinnon, Mackey and McNulty 2026, once verified) and Series 2 to 4 sharing the rest equally, labelled as judgment.
3. **The curves replace the study's own ramp-up years; they do not add to them.** The work package names which study years are replaced.
4. **Curve values only from the original paper,** digitised; never from secondary reproductions.
5. **Osino does not wait for the paper.** Without it, Osino uses the study profile with the same "not modelled" label.

## Consequences

WP 1.5 is split: capital cost overrun now; ramp-up for milled cases when the paper is available. The paper is to be obtained through a library.

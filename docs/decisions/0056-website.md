# 0056. Website: a static page built from the engine

- Status: accepted
- Date: 2026-11-19

## Context

The project needs a public page that explains what an implied build odds figure is to a reader with basic finance and no mining background, and lets them change assumptions and watch the answer move. The Streamlit app runs the engine live but is slow to load and is a tool, not an explanation. A published number must never be typed by hand or computed in a browser, because then it could drift from the engine.

## Decision

1. **A static site on GitHub Pages**, built by `site/build.py` and published by `.github/workflows/pages.yml` on every change to the engine, the priors or the site. The Streamlit app stays as the live tool.
2. **Every figure comes from one export.** `scripts/export_site_example.py` runs the engine on an illustrative mine (200,000 paths, seed 1) and writes every number the page shows, including the implied odds for all 120 control states. The page builder formats and draws; the page's script looks values up and draws. Neither computes a published number. A test parses the built page and checks each figure against the export, and the deploy job runs it on the page it publishes.
3. **The example mine is labelled as made up**, its inputs are listed on the page, and no real deal or outcome appears on the home page.
4. **Rounding.** The value if built is shown to the whole US$ million, and the odds are price over that shown value, rounded half up to a whole percent, so the division on the page checks. The simulation error on the value (at most about US$1M) is larger than the effect of this rounding. When the price is above the value, no odds are shown.
5. **Fixed wording**: "implied odds of a build on schedule"; "simulated outcomes"; "Gold prices used for valuation, not a forecast". The page never says "fair", "probability" or "the market's odds".
6. **No third-party requests.** The Inter font is served from the site (SIL Open Font License, `site/assets/fonts/OFL.txt`).
7. **Pages that do not exist yet are not linked.** Real deals and How to read this site point to this repository until their pages exist.

Decided by the owner (hosting and publishing) and recorded here with the design rules applied.

## Consequences

- The page loads without the engine and works on a phone.
- Changing the engine or a prior changes the published page on the next push to main, with no manual step.
- The illustrative mine is not evidence about any real project; the real cases remain in `docs/cases/`.

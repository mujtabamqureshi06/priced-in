# 0052. Phase 4 sources: Capital IQ and the candidate frame

- Status: accepted
- Date: 2026-11-17
- Amends: ADR 0051

## Context

ADR 0051 needs a complete candidate list, and a price source that covers delisted companies. The government's major-projects data files exist for 2017 to 2021 only. They give about 16 ASX single-project gold developers at the feasibility stage, below the protocol's 30-project floor. Market Index's terms rule it out. The project's owner has S&P Capital IQ through the University of Toronto's academic licence. That licence permits publishing derived results that cannot be used to reconstruct the data. S&P's terms prohibit automated access to authenticated content, including access by AI agents.

## Decision

1. **Prices and shares outstanding:** Capital IQ, exported by the licensed user, by hand or with S&P's Excel plug-in. There is no browser automation. Raw data is never committed. The paper credits S&P and states that full reproduction needs a Capital IQ licence.
2. **Candidate list:** a screen of S&P's mining property database, if the licence includes it. The screen covers gold, scoping/PFS/FS reached 2012 to 2021, and ASX/TSX/TSXV owners, with inactive properties included. Its criteria and run date are recorded, and the list is frozen before outcomes are examined. Stage dates are checked on a sample, so they are known to have been recorded at the time. TSX and TSXV names may then enter the core panel.
3. **Fallback:** the government frame (2015 and 2017 to 2021), ASX only, as a pilot case series. No significance test is claimed.
4. At least 20% of construction-decision dates are verified against company announcements.

## Consequences

- Revisit if the screen yields fewer than 30 projects after exclusions, or if its stage dates prove to have been filled in later.

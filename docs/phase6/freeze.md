# Phase 6 freeze record (protocol 8.8 step 5)

The pricing script ran on the frozen, price-free inputs before any deal price was joined. This file records what was frozen. The inputs, the per-deal outputs and the manifests stay private (protocol section 6); only their SHA-256 hashes are published here, so any later change to them is detectable.

- Run: 2026-11-25T20:16:43+00:00 UTC, from commit `68c92dd541b47d8107ffdd867f92be065a121ac9` (`scripts/phase6_freeze.py`, engine `src/pricedin/deal_pricer.py`).
- Seeds: spreads and Monte Carlo paths 20261126; incidence replicates 20261121, the Phase 5 seed. 2,000 joint draws per deal; every deal uses the same spread draws (common random numbers).
- Primary run: spread-set rates whose deck is not stated are treated as flat (ADR 0073 amendment). Sensitivity: those rates deflated at the fiscal year-end breakeven.

## Public inputs

| File | SHA-256 |
|---|---|
| `data/phase6/spread_set.csv` | `b839d2f4f08a37c94a42ebc57de2cecf0dba71eea163f264d8e4aece0c1565d5` |
| `data/phase5/labels.csv` | `cd0c9aad055aed490ab5ef50d4552e85716e430dbd1ae8b0b75a0b640d841185` |
| `data/phase5/frame_entries.csv` | `1e4bd06a76e2cc79194ca75ab92612e4cc281a3a8618d2f2de2095bbca1c41ca` |
| `data/phase5/components.csv` | `5164432d9b3eb2a8d3a291e1eb152cac8b9bce930f00d687d8c4cd705e47c9d8` |

## Private files

| File | SHA-256 |
|---|---|
| Manifest, primary run (hashes of every input file, snapshot, deck and rate file, and the outputs) | `aef3bbcf2de961a009ce56d748f330c3be7668a1fe30673d233a10c1d6c24274` |
| Manifest, sensitivity run | `b67c5a57ce2aebe8368b2f5e973b4dfcde1a14b503c23834cff0c334b02fcb5f` |
| Ranges, primary run | `a49102f95ab726494b9905e3ac4f543383e6c949fcd6fd9660259541f1017698` |
| Ranges, sensitivity run | `77e7381e2413b55854eda64fc29ba403d1327a9a41ed0516962755421964161c` |
| Value-against-spread curves (the same in both runs) | `dbbcccd7eacec7e38ea75bc53c637c6ea32a005f8db10c75d5a35cc36e92d26a` |
| Study decks and rates (B1, B2) | `83d5e8a675c3f0cea2bbd288dde0ae48dd6ee3f5a8b07c34c5d1b1923ec14386` |
| Fiscal year-end real and breakeven rates | `81600e45368fb90a73983781819dc85357f124858896dd129cd1e245fbb41a69` |

## What happens next

Prices are joined (step 6) only once the Phase 5 table is final. If the Phase 5 walk-through changes a label or the table, the freeze is run again before any price is joined, and this record is replaced; that is not a deviation, since no price has been seen. Any change after prices are joined is reported as a deviation, with results shown both ways.

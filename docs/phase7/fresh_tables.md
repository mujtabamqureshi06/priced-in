# Phase 7 builder validation: fresh tables, hash record

Recorded 2026-11-26, before the builder fix is designed and before any builder or engine run on these files. The transcriptions themselves are private working files; only their SHA-256 hashes are recorded here so the later comparison can be checked against them.

Draw: the Phase 5 strict-frame entries less the 13 projects of the Phase 4 builder validation (229 entries), ordered by `numpy.random.default_rng(20261128).permutation`, taken from position 31 in order. A project is skipped if it was drawn earlier, if its table or headline has already been through the builder or engine (the Phase 4 panel, the Phase 6 deals, the priced cases), or if its entry study has no public annual cash-flow table with an after-tax NPV and IRR. 44 eligible entries were screened to keep 10. Three tables from positions 1 to 30 were run through the current builder before this record and are treated as in-sample only.

| File | SHA-256 |
|---|---|
| 33_yaramoko.yaml | `6343f27bb46daf7736edb7816b33c83e6cfcc36cd25e234c31cb6773d7ac6823` |
| 42_lindero.yaml | `2c402e9823e08f45771cbe4cb5720f4e9e91cda61e55210232242af76fdd5b87` |
| 43_mirado.yaml | `8c7d33b885d9aff001fba61144654d280ba4005d4e1329f6e686f2f1aa2e74b5` |
| 47_west_cache.yaml | `9fd3947dd59e5d614a74167ebfef08d72bb98e43ad2c13c19ec9d0503e7957be` |
| 52_condor_north.yaml | `777555f65c87d3b3df04fada83c4a2d78a6927ff174efdfcb550b8b0af29f63c` |
| 62_cerro_quema.yaml | `8970e2688d6c685bd5c871fddcf0d16cd9f5b5b30796705e5a29e40264072c0f` |
| 81_tres_cruces.yaml | `9b8a82a4ec103180f059cc84afec05adc270778e909a2f93e15f430fb22ec873` |
| 101_loma_larga.yaml | `ffefbe5baf52cf2ad9ecabaa87b13495d6b59e22186477f195201f62848c9ff1` |
| 106_val_d_or_east.yaml | `1970cf9748407b9096cd65b26350eeb23d9d5f37449df0660357077e2d497f9d` |
| 107_garrison.yaml | `dd45e88e72ee6fa8c8746d0a500f67eca198229003669078788d514a90759b98` |

The screening rules and the eligibility list were hashed before any table was opened:

| File | SHA-256 |
|---|---|
| RULES.md | `2890978384894bb09e4fc4df3c6ff931676ae6533c96da56e408e46287c66e98` |
| eligibility.csv | `18e7c3efb470138b16fd48a93dcdb3d0268e902f62b5fd509a034de961a3e71c` |

## Second hash set, 2026-11-28

Seven tables need the discounting offset (`study.discounting.t0_years`) or the C$ fields (`schedule.money_units` and `schedule.fx_usd_per_unit`, ADR 0074) to reproduce their study NPV. A copy of each was made that changes only those fields; a field-level comparison with the first file shows no other change, and each copy reproduces its study's after-tax NPV within 0.6%. Exchange rates are the studies' own stated rates (0.75 or 0.76 US$ per C$). These copies were hashed before any builder or engine run and are the files used in the test; the first set above stays the record of the original transcriptions.

| File | SHA-256 |
|---|---|
| 33_yaramoko_v2.yaml | `39c971c8180d588b5e42e2aaaeb0977aafb8176d77d77dfba79073b015aa470f` |
| 42_lindero_v2.yaml | `9b194f6fd50db9b6a592d2758f1eae08a0429e25a0ec69f8aaa2318e79cf1159` |
| 43_mirado_v2.yaml | `c9c423ffd56abc41fb54d5c9ec29f8357f3f4502323ffac5892905e178422b06` |
| 47_west_cache_v2.yaml | `f55ddeb4542ca3cf2bf7f180c0757fc5f885496493128dad178776401b43e27b` |
| 101_loma_larga_v2.yaml | `f8473a632a0461302867ea8e0ca3d23f04424da03899789249a0fe0122f34d1e` |
| 106_val_d_or_east_v2.yaml | `87b3c905264c7acd506babd8a24cb35f62cfc15ee588ac8c92c5bd67f79f6c3f` |
| 107_garrison_v2.yaml | `84e4e51dfd491e008a6460117782cc8288bf49c27bb235f26e58a4faea69a0f6` |

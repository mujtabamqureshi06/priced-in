# Ramp-up curves: McNulty (1998)

`ramp_up_mcnulty_1998.csv` holds the average ramp-up curves for the four series in McNulty, T. (1998), "Developing innovative technology", Mining Engineering 50(10):50-55, Figure 1 ("Rate of achievement of annualized design", p. 52).

- **How the values were obtained.** Digitised by eye from the plotted markers at 6, 12, 18, 24, 30 and 36 months, on a 300 dpi scan of the original paper (ADR 0017: original paper only, never secondary reproductions). Reading accuracy is about ±2 percentage points. The paper itself notes that estimates were made at 6, 12, 18 and 36 months after commissioning (p. 51).
- **What the series mean.** Series 1 to 4 represent, in declining order, the average percent of design operating rate at a given time (Table 2 note, p. 53). Series 1 projects used mature technology with thorough pilot testing; Series 4 had incomplete pilot testing, prototype equipment or misunderstood process chemistry (pp. 51-52).
- **Classification of the 41 plants** (Table 2, p. 53): Series 1: 23; Series 2: 5; Series 3: 6; Series 4: 7. By plant type: sulfide flotation 11/0/2/0; inorganic chemicals 3/1/1/2; copper and nickel smelters 2/2/1/1; hydrometallurgical sulfide 1/1/2/4; hydrometallurgical oxide (agitated leaching, heap or dump leaching of gold or copper oxide ores) 6/1/0/0.
- **Use.** Weights in `data/priors.yaml` (`rampup.weight.series1` to `series4`). The curves replace a study's own ramp-up years; they do not add to them (ADR 0017).

The paper is not stored in this repository (ADR 0003).

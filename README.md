# Creation Imbalance

A hypothesis-testing computational-physics project asking:

> Could a dark-matter/dark-sector component have existed in a pre-Big-Bang
> state, survived a transition that produced our observable universe, and
> subsequently influenced the matter-antimatter asymmetry?

**This is a hypothesis test, not an attempt to prove the hypothesis.** The
code is built so that it is equally capable of showing the mechanism fails,
works only under unrealistic parameters, or works broadly -- and it reports
whichever of those is actually true. See [`docs/results.md`](docs/results.md)
for the outcome of running it.

## Three-way labeling discipline

Every physics claim in this codebase and its documentation is tagged as one
of:

- **ESTABLISHED PHYSICS** -- textbook cosmology/particle physics (the
  Friedmann equation, Sakharov's conditions, the radiation energy density
  relation, the measured baryon-to-photon ratio, etc.).
- **SPECULATIVE ASSUMPTION** -- a modeling choice specific to the
  hypothesis under test (a pre-Big-Bang dark sector, a particular
  transition mechanism, a specific baryon-number-violating channel). None
  of these are claimed to be true; they are what is being tested.
- **NUMERICAL APPROXIMATION** -- a simplification made for
  tractability (constant g_star, a power-law expansion history instead of
  a full Friedmann solve, model units instead of physical GeV units, a
  single representative mass per species).

See [`docs/model_description.md`](docs/model_description.md) for the full
breakdown.

## Quickstart

```bash
pip install -r requirements.txt
python main.py          # runs all 12 experiments + sweeps + heatmaps + fine-tuning scan
pytest tests/ -q        # runs the test suite (conservation checks, Sakharov-switch checks, etc.)
```

`main.py` writes:

- `results/data/*.csv` -- every time series and every parameter-sweep table
- `results/plots/*.png` -- every required time-series and sweep plot
- `results/heatmaps/*.png` -- the two required 2D parameter heatmaps
- `docs/results.md` -- auto-generated summary tables + the eight
  automatically-answered conclusion questions

Nothing in `docs/results.md` is hand-edited after the fact -- it is
regenerated verbatim by `main.py` from whatever the code actually produces.

## Project structure

```
src/
  cosmology/       expansion models (simplified power-law + swappable Friedmann), constants
  dark_sector/      pre-Big-Bang dark-sector representations (3 conceptual modes)
  visible_sector/   matter/antimatter bookkeeping, eta definition
  reactions/        annihilation + dark<->visible interaction rate laws
  baryogenesis/     Sakharov-condition switches, asymmetry diagnostics
  transition/       PreBigBangState -> Transition -> HotEarlyUniverseState
  simulation/        Model A (baseline) / Model B (pre-BB) builders, ODE integration, experiment orchestration
  analysis/         conservation checks, Model A/B comparison, fine-tuning scan, conclusions
  visualization/    time-series plots, sweep plots, heatmaps
tests/              pytest suite
configs/            reference YAML parameter sets (see configs/README.md)
docs/               model description, equations, assumptions, limitations, observational constraints, results
results/            generated data/plots/heatmaps (produced by main.py, not hand-authored)
```

## Two models, always run side by side

- **Model A (baseline/control):** starts directly in the hot early
  universe. Dark matter is present as a free initial condition but has no
  pre-Big-Bang history and, by default, no coupling to the visible sector
  -- the standard cosmology assumption.
- **Model B (the hypothesis under test):** a `PreBigBangState` passes
  through a configurable `Transition` into a `HotEarlyUniverseState`, which
  then evolves under the *same* reaction network as Model A. The only
  differences between what Model A and Model B predict come from whichever
  parameters you change -- nothing is hard-coded to make Model B win.

## Key documents

- [`docs/model_description.md`](docs/model_description.md) -- what is modeled and why, established vs. speculative vs. approximated
- [`docs/equations.md`](docs/equations.md) -- the full ODE system and every reaction rate law
- [`docs/pre_big_bang_assumptions.md`](docs/pre_big_bang_assumptions.md) -- exactly what is and isn't assumed about the pre-Big-Bang state
- [`docs/physics_limitations.md`](docs/physics_limitations.md) -- known approximations and where the model would need to be extended to be a real cosmological calculation
- [`docs/observational_constraints.md`](docs/observational_constraints.md) -- what real observations could in principle falsify a mechanism like this
- [`docs/results.md`](docs/results.md) -- auto-generated results and conclusions

# Configs

Reference YAML parameter sets, loadable via
`src.simulation.config_loader.load_model_a_config` /
`load_model_b_config`. Keys map 1:1 to the keyword arguments of
`build_model_a()` / `build_model_b()` in `src/simulation/model_a.py` /
`model_b.py` -- see those files for the full parameter list and defaults.

- `model_a_baseline.yaml` -- the standard-cosmology control (Experiment 1).
- `model_b_equal_coupling.yaml` -- R=1 control (Experiment 3): equal
  coupling to matter and antimatter, demonstrating that this alone does
  not produce an asymmetry.
- `model_b_R4.yaml` -- the headline "differs from baseline" run (Experiment
  4 / the Sakharov-ablation baseline in Experiments 9-12).

`src/simulation/run_experiments.py`, which drives `main.py`, does not read
these files directly (it constructs configs inline so the full sweep/
ablation/gallery structure is visible in one place) -- these YAML files are
provided as a convenient, reproducible starting point for anyone who wants
to load a single named configuration interactively, e.g.:

```python
from src.simulation.config_loader import load_model_b_config
from src.simulation.runner import run_simulation

cfg = load_model_b_config("configs/model_b_R4.yaml")
result = run_simulation(cfg)
print(result.df.tail())
```

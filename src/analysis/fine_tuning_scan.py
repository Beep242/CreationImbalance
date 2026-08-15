"""
Monte Carlo fine-tuning scan.

"Does the mechanism require extreme fine-tuning?" is answered empirically
here rather than asserted: sample the Model-B parameters that matter
(coupling ratio R, dark-sector survival fraction, transition energy scale,
overall coupling magnitude) from broad, physically-agnostic priors, run
Model B for each sample, and report what fraction of the prior volume
produces a non-negligible, persistent asymmetry versus how much of that
volume produces nothing interesting (eta ~ 0) or a saturated extreme
(|eta| ~ 1, complete one-sided annihilation).

If only a tiny sliver of the sampled volume produces an interesting
result, that is evidence of fine-tuning. If a broad swath does, that is
evidence the mechanism is generic given its assumptions. Either outcome is
reported as-is.

Reproducibility: uses cosmology.constants.DEFAULT_RANDOM_SEED.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..baryogenesis.asymmetry import classify_outcome
from ..cosmology.constants import DEFAULT_RANDOM_SEED
from ..simulation.model_b import build_model_b
from ..simulation.runner import run_simulation


@dataclass
class FineTuningPriors:
    log10_R_range: tuple = (-2.0, 2.0)  # R = sigma_DM_matter / sigma_DM_antimatter
    log10_base_coupling_range: tuple = (-3.0, -0.5)  # geometric-mean coupling magnitude
    survival_fraction_range: tuple = (0.0, 1.0)
    log10_transition_energy_range: tuple = (-1.0, 1.0)


def run_fine_tuning_scan(
    n_samples: int = 500,
    priors: FineTuningPriors | None = None,
    seed: int = DEFAULT_RANDOM_SEED,
    t1: float = 50.0,
    n_eval: int = 150,
) -> pd.DataFrame:
    priors = priors or FineTuningPriors()
    rng = np.random.default_rng(seed)

    log10_R = rng.uniform(*priors.log10_R_range, size=n_samples)
    log10_base = rng.uniform(*priors.log10_base_coupling_range, size=n_samples)
    survival = rng.uniform(*priors.survival_fraction_range, size=n_samples)
    log10_Etrans = rng.uniform(*priors.log10_transition_energy_range, size=n_samples)

    rows = []
    for i in range(n_samples):
        R = 10.0 ** log10_R[i]
        base = 10.0 ** log10_base[i]
        sigma_m = base * (R ** 0.5)
        sigma_a = base / (R ** 0.5)

        cfg = build_model_b(
            coupling_to_matter=sigma_m,
            coupling_to_antimatter=sigma_a,
            dark_sector_survival_fraction=float(survival[i]),
            transition_energy_scale=10.0 ** log10_Etrans[i],
            t1=t1,
            n_eval=n_eval,
        )
        res = run_simulation(cfg)
        eta_final = float(res.df["eta"].iloc[-1])
        outcome = classify_outcome(
            eta_final,
            float(res.df["N_matter"].iloc[-1]),
            float(res.df["N_antimatter"].iloc[-1]),
        )
        rows.append({
            "sample": i, "R": R, "base_coupling": base,
            "survival_fraction": float(survival[i]),
            "transition_energy_scale": 10.0 ** log10_Etrans[i],
            "eta_final": eta_final, "outcome": outcome,
            "solver_success": res.success,
        })

    return pd.DataFrame(rows)


def summarize_fine_tuning(df: pd.DataFrame, interesting_threshold: float = 0.01) -> dict:
    n = len(df)
    interesting = (df["eta_final"].abs() > interesting_threshold) & (df["eta_final"].abs() < 0.999)
    negligible = df["eta_final"].abs() <= interesting_threshold
    saturated = df["eta_final"].abs() >= 0.999
    return {
        "n_samples": n,
        "fraction_negligible_asymmetry": float(negligible.mean()),
        "fraction_interesting_intermediate_asymmetry": float(interesting.mean()),
        "fraction_saturated_extreme_asymmetry": float(saturated.mean()),
        "eta_final_median_abs": float(df["eta_final"].abs().median()),
        "eta_final_max_abs": float(df["eta_final"].abs().max()),
    }

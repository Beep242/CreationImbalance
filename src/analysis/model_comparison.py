"""
Direct Model A vs Model B comparison.

Answers, from simulation output alone (no hand-tuning), the specific
questions the project's spec requires: does the pre-Big-Bang model produce
different predictions, does it naturally generate an asymmetry, does that
asymmetry survive annihilation, does dark matter survive the transition,
and which parameters are actually load-bearing.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..baryogenesis.asymmetry import asymmetry_persists, classify_outcome


@dataclass
class ModelComparisonResult:
    eta_final_a: float
    eta_final_b: float
    outcome_a: str
    outcome_b: str
    dark_survival_fraction_b: float
    dark_survives_b: bool
    asymmetry_persists_b: bool
    differs_from_baseline: bool
    delta_eta: float

    def summary(self) -> str:
        return (
            f"Model A final eta = {self.eta_final_a:.6g} ({self.outcome_a}); "
            f"Model B final eta = {self.eta_final_b:.6g} ({self.outcome_b}); "
            f"delta_eta = {self.delta_eta:.6g}; "
            f"Model B differs from baseline: {self.differs_from_baseline}; "
            f"dark-sector survival fraction (B): {self.dark_survival_fraction_b:.4g} "
            f"(survives: {self.dark_survives_b}); "
            f"asymmetry persists to end of run (B): {self.asymmetry_persists_b}"
        )


def compare_models(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    N_dark0_b: float,
    difference_threshold: float = 1e-3,
    survival_threshold: float = 1e-3,
) -> ModelComparisonResult:
    eta_final_a = float(df_a["eta"].iloc[-1])
    eta_final_b = float(df_b["eta"].iloc[-1])

    outcome_a = classify_outcome(
        eta_final_a, float(df_a["N_matter"].iloc[-1]), float(df_a["N_antimatter"].iloc[-1])
    )
    outcome_b = classify_outcome(
        eta_final_b, float(df_b["N_matter"].iloc[-1]), float(df_b["N_antimatter"].iloc[-1])
    )

    dark_final_b = float(df_b["N_dark"].iloc[-1])
    dark_survival_fraction_b = dark_final_b / N_dark0_b if N_dark0_b > 0 else 0.0
    dark_survives_b = dark_survival_fraction_b > survival_threshold

    persists_b = asymmetry_persists(df_b["eta"].to_numpy())

    delta_eta = eta_final_b - eta_final_a
    differs = abs(delta_eta) > difference_threshold

    return ModelComparisonResult(
        eta_final_a=eta_final_a,
        eta_final_b=eta_final_b,
        outcome_a=outcome_a,
        outcome_b=outcome_b,
        dark_survival_fraction_b=dark_survival_fraction_b,
        dark_survives_b=dark_survives_b,
        asymmetry_persists_b=persists_b,
        differs_from_baseline=differs,
        delta_eta=delta_eta,
    )

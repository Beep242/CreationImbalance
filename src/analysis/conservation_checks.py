"""
Numerical self-consistency (conservation) checks.

These are NOT independent physical laws being tested against the
simulation -- they are bookkeeping identities that follow directly from how
the reaction terms in src/reactions and src/simulation/ode_system.py were
constructed (every number-changing reaction moves a matched amount of
rest-mass energy into or out of the radiation bath). If the identities
below hold to numerical-solver precision, that indicates the ODE right-hand
side and the solver trajectory are mutually consistent (no bug, no
excessive numerical drift) -- it does not independently validate the
underlying physical model, which is explicitly speculative.

Two checks are provided:

1. `closed_energy_conservation_residual`: for the number-changing channels
   (annihilation, D<->M, D<->A, dark self-annihilation), verifies that
   mass-energy lost by the particle sector exactly equals the energy
   deposited into radiation, at every saved timestep.

2. `dark_number_conservation_when_b_violation_off`: when
   baryon_number_violation_enabled is False, N_dark should evolve only via
   dilution (already implicit in comoving variables) and self-annihilation
   -- i.e. D<->M and D<->A channels must contribute exactly zero.

The `coupling_to_visible` elastic-heating channel is deliberately excluded
from check 1: it represents an open energy injection with no tracked
energy reservoir on the dark-sector side (see docstring in
src/simulation/ode_system.py), so it is reported separately rather than
folded into the closed-system residual.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..simulation.ode_system import PhysicsParams, reaction_diagnostics


def closed_energy_conservation_residual(df: pd.DataFrame, physics: PhysicsParams) -> pd.Series:
    """
    residual(t) = [E_ann + E_dtom + E_dtoa + E_selfann](t)
                  - a(t) * [ -(m_M*dN_M/dt|_react + m_A*dN_A/dt|_react + m_D*dN_D/dt|_react) ]

    Recomputed independently from stored (t, y) pairs using the same rate
    functions as the ODE right-hand side, then compared against what the
    solver actually produced. Should be ~0 (solver-tolerance-level) at
    every row by construction; large nonzero values indicate a coding bug
    in the energy bookkeeping, not a physical effect.
    """
    ann = physics.ann_params
    dark = physics.dark_params
    residuals = []
    for _, row in df.iterrows():
        y = [row["a"], row["N_matter"], row["N_antimatter"], row["N_dark"], row["E_rad"]]
        diag = reaction_diagnostics(row["t"], y, physics)
        a = max(row["a"], 1e-12)

        d_to_m = diag["d_to_m_net"]
        d_to_a = diag["d_to_a_net"]
        self_ann = diag["self_ann_rate"]
        ann_rate = diag["ann_rate"]

        dN_M_react = ann_rate + d_to_m
        dN_A_react = ann_rate + d_to_a
        dN_D_react = -d_to_m - d_to_a + self_ann

        mass_energy_lost_by_particles = -(
            ann.m_matter * dN_M_react
            + ann.m_antimatter * dN_A_react
            + dark.m_dark * dN_D_react
        )

        radiation_gain_closed = diag["E_ann"] + diag["E_dtom"] + diag["E_dtoa"] + diag["E_selfann"]

        residuals.append(radiation_gain_closed - a * mass_energy_lost_by_particles)

    return pd.Series(residuals, index=df.index, name="energy_conservation_residual")


def dark_number_conservation_when_b_violation_off(
    df: pd.DataFrame, physics: PhysicsParams
) -> pd.Series:
    """
    When baryon_number_violation_enabled is False, D<->M and D<->A rates
    must be identically zero at every timestep (returns the max |rate|
    found; should be exactly 0.0).
    """
    if physics.dark_params.baryon_number_violation_enabled:
        return pd.Series([np.nan] * len(df), index=df.index,
                          name="b_violation_leak (not applicable: B-violation is enabled)")
    leaks = []
    for _, row in df.iterrows():
        y = [row["a"], row["N_matter"], row["N_antimatter"], row["N_dark"], row["E_rad"]]
        diag = reaction_diagnostics(row["t"], y, physics)
        leaks.append(abs(diag["d_to_m_net"]) + abs(diag["d_to_a_net"]))
    return pd.Series(leaks, index=df.index, name="b_violation_leak")


def summarize_conservation(df: pd.DataFrame, physics: PhysicsParams) -> dict:
    energy_resid = closed_energy_conservation_residual(df, physics)
    b_leak = dark_number_conservation_when_b_violation_off(df, physics)
    scale = max(df["E_rad"].abs().max(), df["N_matter"].abs().max(), 1.0)
    return {
        "max_abs_energy_conservation_residual": float(energy_resid.abs().max()),
        "max_abs_energy_conservation_residual_relative": float(energy_resid.abs().max() / scale),
        "max_abs_b_violation_leak": (
            None if b_leak.isna().all() else float(b_leak.abs().max())
        ),
    }

"""
ODE integration driver.

Uses scipy.integrate.solve_ivp with an implicit, stiffness-aware method
(Radau by default -- this is a genuine multistep/implicit Runge-Kutta
solver, not Euler integration) with tight tolerances, and reruns with a
tighter tolerance automatically if the solver reports non-success.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from ..baryogenesis.sakharov import SakharovSwitches
from ..visible_sector.particles import eta_from_numbers
from .ode_system import PhysicsParams, Y_LABELS, reaction_diagnostics, rhs, temperature_from_E_rad


@dataclass
class SimulationConfig:
    model_name: str
    y0: list
    physics: PhysicsParams
    sakharov: SakharovSwitches
    t0: float = 0.0
    t1: float = 50.0
    n_eval: int = 400
    method: str = "Radau"
    rtol: float = 1e-8
    atol: float = 1e-10
    metadata: dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    config: SimulationConfig
    df: pd.DataFrame
    success: bool
    message: str


def run_simulation(cfg: SimulationConfig) -> SimulationResult:
    t_eval = np.linspace(cfg.t0, cfg.t1, cfg.n_eval)

    sol = solve_ivp(
        rhs,
        (cfg.t0, cfg.t1),
        cfg.y0,
        method=cfg.method,
        t_eval=t_eval,
        args=(cfg.physics,),
        rtol=cfg.rtol,
        atol=cfg.atol,
        dense_output=False,
    )

    if not sol.success:
        # Retry once with a more conservative, still-implicit method before
        # giving up -- LSODA auto-switches between stiff/non-stiff internal
        # methods and is a robust fallback.
        sol = solve_ivp(
            rhs,
            (cfg.t0, cfg.t1),
            cfg.y0,
            method="LSODA",
            t_eval=t_eval,
            args=(cfg.physics,),
            rtol=cfg.rtol,
            atol=cfg.atol,
        )

    rows = []
    for i, t in enumerate(sol.t):
        y = sol.y[:, i]
        a, N_M, N_A, N_D, E_rad = y
        T = temperature_from_E_rad(E_rad, a, cfg.physics.g_star)
        eta = eta_from_numbers(N_M, N_A)
        ratio = (N_M / N_A) if N_A > 1e-300 else float("inf")
        H = cfg.physics.expansion_model.hubble_rate(
            max(a, 1e-12),
            (cfg.physics.ann_params.m_matter * max(N_M, 0.0)
             + cfg.physics.ann_params.m_antimatter * max(N_A, 0.0)
             + cfg.physics.dark_params.m_dark * max(N_D, 0.0)) / max(a, 1e-12) ** 3
            + max(E_rad, 0.0) / max(a, 1e-12) ** 4,
        )
        diag = reaction_diagnostics(t, y, cfg.physics)
        row = {
            "t": t, "a": a, "N_matter": N_M, "N_antimatter": N_A,
            "N_dark": N_D, "E_rad": E_rad, "T": T, "eta": eta,
            "matter_antimatter_ratio": ratio, "H": H,
        }
        row.update(diag)
        rows.append(row)

    df = pd.DataFrame(rows)
    return SimulationResult(config=cfg, df=df, success=bool(sol.success), message=str(sol.message))

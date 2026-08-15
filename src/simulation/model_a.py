"""
Model A -- standard baseline / control.

The simulation begins directly in the hot early-universe phase. Dark
matter is present as an initial condition (a free parameter, N_dark0) with
NO pre-Big-Bang history and, by default, NO coupling to the visible
sector -- i.e. the standard assumption that dark matter is collisionless
and does not interconvert with baryons/antibaryons. The visible sector
starts exactly matter/antimatter symmetric.

Because this model contains no baryon-number-violating channel, no C/CP
violation, and no built-in departure-from-equilibrium asymmetry source, it
should -- and, if the code is correct, will -- fail to generate any
persistent matter/antimatter asymmetry from a symmetric start. Left alone,
symmetric matter and antimatter simply annihilate down toward whatever
small relic is set by Hubble freeze-out of the annihilation reaction
itself (the textbook "why is there anything left at all" problem that
motivates Sakharov's conditions in the first place). This is the expected,
correct behavior of the control, not a bug.
"""

from __future__ import annotations

from ..baryogenesis.sakharov import SakharovSwitches
from ..cosmology.expansion import ExpansionModel, SimplifiedExpansion
from ..reactions.annihilation import AnnihilationParams
from ..reactions.dark_interactions import DarkInteractionParams
from .ode_system import PhysicsParams
from .runner import SimulationConfig


def build_model_a(
    *,
    N_matter0: float = 50.0,
    N_antimatter0: float = 50.0,
    N_dark0: float = 50.0,
    sigma_ann: float = 0.02,
    sigma_DD: float = 0.0,
    expansion_model: ExpansionModel | None = None,
    t1: float = 50.0,
    n_eval: int = 400,
    seed_asymmetry: float = 0.0,
    metadata: dict | None = None,
) -> SimulationConfig:
    expansion_model = expansion_model or SimplifiedExpansion(H0=1.0, a0=1.0, power=2.0)

    ann_params = AnnihilationParams(sigma_ann=sigma_ann, m_matter=1.0, m_antimatter=1.0)
    dark_params = DarkInteractionParams(
        sigma_DM_matter=0.0,
        sigma_DM_antimatter=0.0,
        equilibrium_factor=0.0,
        coupling_to_visible=0.0,
        sigma_DD=sigma_DD,
        m_dark=1.0,
        m_matter=1.0,
        m_antimatter=1.0,
        baryon_number_violation_enabled=False,
    )
    physics = PhysicsParams(
        expansion_model=expansion_model,
        ann_params=ann_params,
        dark_params=dark_params,
        transition_duration=0.0,
        g_star=10.0,
    )
    sakharov = SakharovSwitches(
        baryon_number_violation_enabled=False,
        cp_violation_enabled=False,
        thermal_equilibrium=False,
    )

    N_m0 = N_matter0 * (1.0 + seed_asymmetry)
    N_a0 = N_antimatter0 * (1.0 - seed_asymmetry)
    y0 = [1.0, N_m0, N_a0, N_dark0, 1e-6]

    meta = {
        "model": "A",
        "description": "Standard baseline: no pre-Big-Bang dark-sector history, "
        "no dark-visible coupling.",
    }
    if metadata:
        meta.update(metadata)

    return SimulationConfig(
        model_name="Model A (baseline)",
        y0=y0,
        physics=physics,
        sakharov=sakharov,
        t0=0.0,
        t1=t1,
        n_eval=n_eval,
        metadata=meta,
    )

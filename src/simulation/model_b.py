"""
Model B -- pre-Big-Bang dark-sector model.

Builds a PreBigBangState, passes it through a configurable Transition, and
uses the resulting HotEarlyUniverseState as the initial condition for the
same Phase-2 ODE machinery used by Model A. This is the experimental
model: whether it behaves differently from Model A, and under which
parameter choices, is exactly the question the rest of the project
answers -- nothing here pre-decides that outcome.
"""

from __future__ import annotations

from ..baryogenesis.sakharov import SakharovSwitches, build_effective_dark_interaction_params
from ..cosmology.expansion import ExpansionModel, SimplifiedExpansion
from ..dark_sector.dark_sector import DarkSectorMode, PreBigBangState
from ..reactions.annihilation import AnnihilationParams
from ..transition.transition import TransitionConfig, TransitionType, run_transition
from .ode_system import PhysicsParams
from .runner import SimulationConfig


def build_model_b(
    *,
    pre_transition_density: float = 100.0,
    pre_transition_temperature: float | None = None,
    transition_type: TransitionType = TransitionType.GENERIC,
    transition_energy_scale: float = 1.0,
    transition_duration: float = 0.5,
    dark_sector_survival_fraction: float = 1.0,
    entropy_production: float = 1.0,
    visible_sector_seed_number: float = 100.0,
    coupling_to_matter: float = 0.05,
    coupling_to_antimatter: float = 0.05,
    coupling_to_visible: float = 0.0,
    sigma_ann: float = 0.02,
    sigma_DD: float = 0.001,
    baryon_number_violation_enabled: bool = True,
    cp_violation_enabled: bool = True,
    thermal_equilibrium: bool = False,
    expansion_power: float = 2.0,
    expansion_model: ExpansionModel | None = None,
    t1: float = 50.0,
    n_eval: int = 400,
    metadata: dict | None = None,
) -> SimulationConfig:
    pre = PreBigBangState(
        mode=DarkSectorMode.PARTICLE_POPULATION,
        density_pre=pre_transition_density,
        temperature_pre=pre_transition_temperature,
        label=transition_type.value,
    )

    transition_cfg = TransitionConfig(
        transition_type=transition_type,
        transition_energy_scale=transition_energy_scale,
        transition_duration=transition_duration,
        dark_sector_survival_fraction=dark_sector_survival_fraction,
        entropy_production=entropy_production,
        visible_sector_seed_number=visible_sector_seed_number,
        coupling_to_matter=coupling_to_matter,
        coupling_to_antimatter=coupling_to_antimatter,
        expansion_power_during_transition=expansion_power,
    )

    hot_state = run_transition(pre, transition_cfg)

    switches = SakharovSwitches(
        baryon_number_violation_enabled=baryon_number_violation_enabled,
        cp_violation_enabled=cp_violation_enabled,
        thermal_equilibrium=thermal_equilibrium,
    )

    dark_params = build_effective_dark_interaction_params(
        sigma_DM_matter=coupling_to_matter,
        sigma_DM_antimatter=coupling_to_antimatter,
        switches=switches,
        coupling_to_visible=coupling_to_visible,
        sigma_DD=sigma_DD,
        m_dark=1.0,
        m_matter=1.0,
        m_antimatter=1.0,
    )

    ann_params = AnnihilationParams(sigma_ann=sigma_ann, m_matter=1.0, m_antimatter=1.0)

    expansion_model = expansion_model or SimplifiedExpansion(
        H0=1.0, a0=hot_state.a0, power=expansion_power
    )

    physics = PhysicsParams(
        expansion_model=expansion_model,
        ann_params=ann_params,
        dark_params=dark_params,
        transition_duration=hot_state.transition_duration,
        g_star=10.0,
    )

    y0 = [hot_state.a0, hot_state.N_matter0, hot_state.N_antimatter0,
          hot_state.N_dark0, hot_state.E_rad0]

    meta = {
        "model": "B",
        "description": "Pre-Big-Bang dark sector through a configurable transition.",
        "pre_big_bang_state": pre.describe(),
        "transition_provenance": hot_state.provenance,
        "sakharov": switches.summary(),
        "configured_R": (coupling_to_matter / coupling_to_antimatter
                          if coupling_to_antimatter != 0 else float("inf")),
    }
    if metadata:
        meta.update(metadata)

    return SimulationConfig(
        model_name="Model B (pre-Big-Bang dark sector)",
        y0=y0,
        physics=physics,
        sakharov=switches,
        t0=0.0,
        t1=t1,
        n_eval=n_eval,
        metadata=meta,
    )

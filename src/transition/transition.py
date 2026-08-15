"""
The pre-Big-Bang -> hot-early-universe transition.

    PreBigBangState  --[Transition]-->  HotEarlyUniverseState

SPECULATIVE ASSUMPTION (the entire module): this represents a hypothetical
transition out of a pre-Big-Bang dark-sector state. Five conceptual
interpretations are offered via `TransitionType` purely as labels/framing
-- they do not change the underlying mathematics, which is a single
configurable parameterization common to all of them. This is intentional:
the project is agnostic about *which* real mechanism (if any) such a
transition would be, and instead asks what generic consequences follow
from *any* mechanism describable by these parameters.

IMPORTANT DESIGN COMMITMENT: the transition sets *initial conditions* for
the post-transition reaction network (dark-sector population, temperature,
and -- symmetrically, always -- the matter/antimatter populations). It does
NOT itself inject a matter/antimatter asymmetry by fiat. Per the project's
scientific requirement ("do not artificially force eta to become
positive"), the visible sector always starts symmetric
(N_matter0 == N_antimatter0) coming out of the transition. Any asymmetry
seen later must originate from the post-transition reaction network in
src/reactions/dark_interactions.py as gated by
src/baryogenesis/sakharov.py. This keeps the transition module honest: it
can influence *how much room* the reaction network has to generate an
asymmetry (via N_dark0, T0, and the reaction switch-on timescale), but it
cannot manufacture the asymmetry directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..cosmology.constants import DEFAULT_G_STAR, PI
from ..dark_sector.dark_sector import DarkSectorMode, PreBigBangState


class TransitionType(Enum):
    PHASE_TRANSITION = "phase_transition"
    BOUNCE = "bounce"
    REHEATING_LIKE = "reheating_like"
    VACUUM_TRANSITION = "vacuum_transition"
    GENERIC = "generic_initial_condition_transition"


@dataclass
class TransitionConfig:
    transition_type: TransitionType = TransitionType.GENERIC
    transition_energy_scale: float = 1.0
    transition_duration: float = 0.1
    dark_sector_survival_fraction: float = 1.0  # in [0, 1]
    entropy_production: float = 1.0  # multiplicative boost to radiation entropy dumped
    visible_sector_seed_number: float = 100.0  # total N_matter0 + N_antimatter0
    coupling_to_matter: float = 1.0  # -> sigma_DM_matter, post-transition
    coupling_to_antimatter: float = 1.0  # -> sigma_DM_antimatter, post-transition
    expansion_power_during_transition: float = 2.0  # passed through to expansion model
    a_start: float = 1.0
    g_star: float = DEFAULT_G_STAR


@dataclass
class HotEarlyUniverseState:
    """Initial condition for the Phase-2 ODE integration, plus provenance."""

    a0: float
    N_matter0: float
    N_antimatter0: float
    N_dark0: float
    E_rad0: float
    T0: float
    transition_duration: float
    coupling_to_matter: float
    coupling_to_antimatter: float
    expansion_power: float
    provenance: dict = field(default_factory=dict)

    def describe(self) -> str:
        return (
            f"HotEarlyUniverseState: a0={self.a0:.4g} "
            f"N_M0={self.N_matter0:.4g} N_A0={self.N_antimatter0:.4g} "
            f"N_D0={self.N_dark0:.4g} T0={self.T0:.4g} "
            f"(survived fraction={self.provenance.get('dark_sector_survival_fraction')}, "
            f"transition={self.provenance.get('transition_type')})"
        )


def run_transition(pre: PreBigBangState, cfg: TransitionConfig) -> HotEarlyUniverseState:
    """
    Deterministically map a PreBigBangState through a TransitionConfig into
    a HotEarlyUniverseState. No randomness, no hidden asymmetry injection.
    """
    if pre.mode != DarkSectorMode.PARTICLE_POPULATION:
        raise ValueError(
            "run_transition currently implements the PARTICLE_POPULATION "
            "pathway only (needed for the discrete B-violating channel in "
            "reactions.dark_interactions). FIELD_BACKGROUND and "
            "GENERIC_ENERGY_DENSITY dark-sector modes are demonstrated "
            "separately in dark_sector.dark_sector and are not wired into "
            "the full reaction network."
        )

    survival = min(max(cfg.dark_sector_survival_fraction, 0.0), 1.0)
    N_dark0 = pre.density_pre * survival

    # Radiation energy dumped by the transition itself, set by the
    # transition energy scale and an entropy-production multiplier.
    # rho_rad = (pi^2/30) g_star T^4  =>  E_rad0 (comoving, a0=cfg.a_start) follows.
    T0 = cfg.transition_energy_scale * cfg.entropy_production**0.25
    rho_rad0 = (PI**2 / 30.0) * cfg.g_star * T0**4
    E_rad0 = rho_rad0 * cfg.a_start**4

    # Visible sector: always exactly symmetric coming out of the transition.
    N_matter0 = cfg.visible_sector_seed_number / 2.0
    N_antimatter0 = cfg.visible_sector_seed_number / 2.0

    provenance = {
        "transition_type": cfg.transition_type.value,
        "dark_sector_survival_fraction": survival,
        "pre_transition_density": pre.density_pre,
        "entropy_production": cfg.entropy_production,
        "transition_energy_scale": cfg.transition_energy_scale,
        "visible_sector_seeded_symmetric": True,
    }

    return HotEarlyUniverseState(
        a0=cfg.a_start,
        N_matter0=N_matter0,
        N_antimatter0=N_antimatter0,
        N_dark0=N_dark0,
        E_rad0=E_rad0,
        T0=T0,
        transition_duration=cfg.transition_duration,
        coupling_to_matter=cfg.coupling_to_matter,
        coupling_to_antimatter=cfg.coupling_to_antimatter,
        expansion_power=cfg.expansion_power_during_transition,
        provenance=provenance,
    )


def reaction_activation_factor(t: float, transition_duration: float) -> float:
    """
    Smooth switch-on for the dark<->visible reaction channels:
    act(t) = 1 - exp(-t / tau), tau = max(transition_duration, eps).

    Represents the physical expectation that a transition spread over a
    finite duration does not instantaneously couple the sectors at full
    strength. NUMERICAL APPROXIMATION -- the exact functional form is a
    modeling choice, not derived from a specific mechanism.
    """
    tau = max(transition_duration, 1e-6)
    if t <= 0:
        return 0.0
    import math

    return 1.0 - math.exp(-t / tau)

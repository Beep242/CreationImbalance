"""
The Phase-2 (post-transition, hot-early-universe) ODE system.

State vector y = [a, N_matter, N_antimatter, N_dark, E_rad], all in
comoving units (N = n * a^3, E_rad = rho_rad * a^4), so that pure Hubble
dilution does not need to appear as an explicit term -- only genuine
reactions and the scale-factor equation change these comoving quantities.

ESTABLISHED PHYSICS (functional form): da/dt = H(a) * a; comoving particle
number and comoving radiation energy change only via source/sink terms
(reactions), not via expansion, which is the entire point of using
comoving variables -- this is the standard trick for keeping stiff
reaction-network + expansion ODEs numerically well-behaved.

NUMERICAL APPROXIMATION: constant g_star, a single representative mass per
species, and the specific reaction channels in reactions.dark_interactions
are all simplifications; see docs/physics_limitations.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..cosmology.constants import DEFAULT_G_STAR, PI
from ..cosmology.expansion import ExpansionModel
from ..reactions.annihilation import AnnihilationParams
from ..reactions.dark_interactions import DarkInteractionParams
from ..transition.transition import reaction_activation_factor

Y_LABELS = ["a", "N_matter", "N_antimatter", "N_dark", "E_rad"]


@dataclass
class PhysicsParams:
    expansion_model: ExpansionModel
    ann_params: AnnihilationParams
    dark_params: DarkInteractionParams
    transition_duration: float = 0.1
    g_star: float = DEFAULT_G_STAR


def temperature_from_E_rad(E_rad: float, a: float, g_star: float) -> float:
    a = max(a, 1e-12)
    rho_rad = max(E_rad, 0.0) / a**4
    return (30.0 * rho_rad / (PI**2 * g_star)) ** 0.25


def _reaction_terms(t: float, a: float, N_M: float, N_A: float, N_D: float,
                     params: PhysicsParams) -> dict:
    """
    Single source of truth for every reaction rate and energy-transfer term
    in the model. Both `rhs` (the ODE right-hand side) and
    `reaction_diagnostics` (used for logging and conservation checks) call
    this exact function so the two can never drift out of sync with each
    other -- see src/analysis/conservation_checks.py, which relies on that
    guarantee to test for coding bugs rather than physical effects.
    """
    ann = params.ann_params
    dark = params.dark_params
    act = reaction_activation_factor(t, params.transition_duration)

    ann_rate = ann.comoving_rate(N_M, N_A, a)  # negative, symmetric loss
    d_to_m = act * dark.comoving_D_to_M_net(N_D, N_M, a)
    d_to_a = act * dark.comoving_D_to_A_net(N_D, N_A, a)
    self_ann = dark.comoving_dark_self_annihilation(N_D, a)  # negative

    E_ann = ann.comoving_energy_release_rate(N_M, N_A, a)  # positive
    E_dtom = d_to_m * (dark.m_dark - dark.m_matter) * a
    E_dtoa = d_to_a * (dark.m_dark - dark.m_antimatter) * a
    E_selfann = -self_ann * dark.m_dark * a  # positive
    # E_elastic is a deliberately OPEN (non-conservative) energy injection:
    # it represents the dark sector depositing energy into radiation via a
    # number-conserving channel with no corresponding tracked energy
    # reservoir to draw down (see docs/physics_limitations.md). It is
    # therefore excluded from the closed-system energy-conservation check
    # in src/analysis/conservation_checks.py and defaults to 0 in both
    # Model A and the R/B-violation/CP/equilibrium experiments; it is only
    # exercised in dedicated coupling-to-visible sweeps, clearly labeled.
    E_elastic = act * dark.comoving_elastic_heating_rate(N_D, a)  # positive

    return {
        "activation_factor": act,
        "ann_rate": ann_rate,
        "d_to_m_net": d_to_m,
        "d_to_a_net": d_to_a,
        "self_ann_rate": self_ann,
        "E_ann": E_ann,
        "E_dtom": E_dtom,
        "E_dtoa": E_dtoa,
        "E_selfann": E_selfann,
        "E_elastic": E_elastic,
        "energy_source_total": E_ann + E_dtom + E_dtoa + E_selfann + E_elastic,
    }


def rhs(t: float, y, params: PhysicsParams):
    a, N_M, N_A, N_D, E_rad = y
    a = max(a, 1e-12)
    N_M = max(N_M, 0.0)
    N_A = max(N_A, 0.0)
    N_D = max(N_D, 0.0)
    E_rad = max(E_rad, 0.0)

    ann = params.ann_params
    dark = params.dark_params

    rho_rad = E_rad / a**4
    rho_M = ann.m_matter * N_M / a**3
    rho_A = ann.m_antimatter * N_A / a**3
    rho_D = dark.m_dark * N_D / a**3
    rho_total = rho_M + rho_A + rho_D + rho_rad

    H = params.expansion_model.hubble_rate(a, rho_total)
    da_dt = H * a

    terms = _reaction_terms(t, a, N_M, N_A, N_D, params)

    dN_M_dt = terms["ann_rate"] + terms["d_to_m_net"]
    dN_A_dt = terms["ann_rate"] + terms["d_to_a_net"]
    dN_D_dt = -terms["d_to_m_net"] - terms["d_to_a_net"] + terms["self_ann_rate"]
    dE_rad_dt = terms["energy_source_total"]

    return [da_dt, dN_M_dt, dN_A_dt, dN_D_dt, dE_rad_dt]


def reaction_diagnostics(t: float, y, params: PhysicsParams) -> dict:
    """Recompute each individual rate term at a given state, for logging
    (reaction rates output column) and for the conservation-check module."""
    a, N_M, N_A, N_D, E_rad = y
    a = max(a, 1e-12)
    N_M, N_A, N_D, E_rad = (max(v, 0.0) for v in (N_M, N_A, N_D, E_rad))
    return _reaction_terms(t, a, N_M, N_A, N_D, params)

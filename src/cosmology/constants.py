"""
Physical constants and unit conventions.

NUMERICAL APPROXIMATION NOTE
-----------------------------
This project does NOT attempt to model literal GeV-scale reheating
temperatures, the true Planck mass, or real particle rest masses. Doing so
accurately would require a full Boltzmann-equation treatment with
temperature-dependent degrees of freedom (g_*(T)), which is out of scope for
a toy hypothesis-testing model.

Instead we work in a set of internal "model units" where:
  - time, mass, energy, temperature, and density are all dimensionless
    numbers whose *ratios* and *sweeps* are physically meaningful, but whose
    absolute scale should NOT be read as a real GeV/second value unless
    explicitly rescaled.
  - The one exception is the reduced Planck mass M_PL, used only by the
    optional Friedmann expansion model, expressed in the same model-unit
    system so that H^2 ~ rho / M_PL^2 has the correct *functional form*
    (established physics) even though the numerical value is a stand-in.

This keeps the ODE system numerically well-conditioned while being explicit
that we are not fitting real cosmological data.
"""

from __future__ import annotations

# --- Established-physics functional relationships, model-unit normalized ---

# Radiation energy density: rho_rad = (pi^2 / 30) * g_star * T^4
# (Stefan-Boltzmann-like relation for a relativistic plasma; ESTABLISHED
#  PHYSICS in its functional form. g_star is the effective number of
#  relativistic degrees of freedom.)
PI = 3.14159265358979323846

# Default effective relativistic degrees of freedom.
# Real g_*(T) varies from ~106.75 (Standard Model, T >> 100 GeV) down to
# ~3.36 today. We use a single constant value as a NUMERICAL APPROXIMATION;
# see docs/physics_limitations.md.
DEFAULT_G_STAR = 10.0

# Reduced Planck mass, in model units (only used by FriedmannExpansion).
# Establishing an absolute correspondence to 2.4e18 GeV is deliberately not
# attempted; see docs/physics_limitations.md.
M_PL_MODEL_UNITS = 1.0e4

# Observationally measured present-day baryon-to-photon ratio (ESTABLISHED
# PHYSICS, from Planck 2018 CMB fits): eta_B ~ 6.1e-10. This is *not* the
# eta = (N_matter - N_antimatter)/(N_matter + N_antimatter) tracked in this
# code (that quantity is the fractional matter/antimatter asymmetry among
# baryons themselves, not the baryon-to-photon ratio). It is provided here
# only as an external reference point used in the observational-consequence
# discussion, not as a target the simulation is tuned to hit.
OBSERVED_BARYON_TO_PHOTON_RATIO = 6.1e-10

# Reproducibility.
DEFAULT_RANDOM_SEED = 42

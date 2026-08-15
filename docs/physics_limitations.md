# Physics Limitations

This document lists every significant NUMERICAL APPROXIMATION and
structural simplification in the codebase, and what a more complete
treatment would need to do instead. None of these invalidate the
qualitative conclusions drawn in `docs/results.md` (which are about
whether the *mechanism class* can work at all, under favorable
assumptions), but they mean no number in this project should be read as a
quantitative cosmological prediction.

## 1. Model units, not physical units

Time, temperature, mass, and energy are all dimensionless "model units"
(`src/cosmology/constants.py`). No rescaling to real GeV/second/Kelvin
values is attempted. Consequences:

- `transition_energy_scale` values used in the sweeps (0.1-30) are **not**
  GeV. They should be read only as relative comparisons within a single
  run.
- The reduced Planck mass used by `FriedmannExpansion` (`M_PL_MODEL_UNITS`)
  is a numerical stand-in, not 2.4 x 10^18 GeV.

## 2. Constant effective degrees of freedom (g_star)

Real g_*(T) varies from ~106.75 (Standard Model, T >> 100 GeV) down to
~3.36 today, and drives the standard-cosmology entropy/temperature
relationship. This project holds `g_star` fixed
(`DEFAULT_G_STAR = 10.0`), which is a coarse approximation everywhere
except in a narrow temperature window.

## 3. Simplified (kinematic) expansion history by default

`SimplifiedExpansion` imposes `H(a)` as a fixed power law rather than
deriving it from the actually-tracked energy content. This means energy
injected or removed by the reaction network does **not** feed back into
the expansion rate in the default configuration. `FriedmannExpansion` is
provided as a structurally interchangeable alternative
(`src/cosmology/expansion.py`) precisely so this limitation can be lifted
by users of the codebase, but it is not the default because it couples the
expansion equation to the (already toy) energy budget, potentially double-
counting approximations rather than removing them.

## 4. A single, toy baryon-number-violating channel

D -> M / D -> A is not a fit to any specific particle-physics model (no
GUT-scale operator, no heavy right-handed neutrino, no electroweak
sphaleron). It is the simplest possible number-violating channel that
still lets Sakharov's three conditions be tested independently. A real
model would need to specify: what D actually is, what conserves/violates
which quantum numbers at the Lagrangian level, and what the actual
matrix element (not just a rate constant) is.

## 5. Toy detailed balance, not full statistical mechanics

The "washout" (thermal equilibrium) reverse reactions use
`reverse_rate = equilibrium_factor * forward_rate_constant * N_species`,
rather than a proper detailed-balance condition derived from equilibrium
number densities (`n_i^eq(T)`) via the full collision term. This is why,
as reported honestly in `docs/results.md`, setting `thermal_equilibrium =
True` strongly *suppresses* but does not always drive eta to *exactly*
zero in this implementation -- a full Boltzmann treatment with correctly
computed equilibrium densities would likely wash it out more completely.
This is flagged as a limitation, not silently smoothed over.

## 6. No temperature dependence in reaction rates

`sigma_ann`, `sigma_DM_matter`, `sigma_DM_antimatter`, and `sigma_DD` are
held constant. Real cross-sections generically depend on temperature/
energy (e.g. Boltzmann-suppressed heavy-particle decays, resonances,
threshold effects). This project's parameter sweeps substitute for this by
directly varying the constants rather than deriving their
temperature-dependence from an underlying theory.

## 7. Representative masses, not a particle spectrum

Each species (matter, antimatter, dark) carries one representative mass
(default 1.0 for all three, in model units). Real particle content has a
spectrum of masses and, in general, differing masses would need to be
handled with actual relativistic kinematics (thresholds, phase space) not
just a linear rest-mass energy bookkeeping term.

## 8. The `coupling_to_visible` (elastic heating) channel is not closed

As documented directly in `src/simulation/ode_system.py` and
`src/analysis/conservation_checks.py`: this channel injects energy into
radiation from the dark sector without a correspondingly tracked energy
reservoir on the dark side (the dark sector here has no separate
"kinetic energy" pool beyond its rest-mass-equivalent number density). It
is therefore excluded from the strict energy-conservation check and
defaults to 0 in every experiment that matters for the headline
conclusions; it exists only so that a future extension (e.g. giving the
dark sector its own temperature) has a natural place to plug in.

## 9. No real perturbation theory / structure formation

This project tracks homogeneous, background-level quantities only. It
says nothing about density perturbations, structure formation, or the
matter power spectrum -- claims in `docs/observational_constraints.md`
about large-scale structure are explicitly qualitative, not computed.

## 10. Small, fixed reaction network

Only four processes are modeled (annihilation, D<->M, D<->A, D
self-annihilation). No inverse-decay chains beyond what is described, no
multi-step cascades, no additional dark-sector species.

## What would be needed for a "real" version of this project

- A specific particle-physics Lagrangian for the dark-sector coupling
  (fixing what actually violates baryon number and by how much).
- Temperature-dependent g_*(T) and rate constants computed from real
  cross-sections/decay widths.
- A full Boltzmann collision-term treatment of the washout reactions.
- A genuine Friedmann-equation-driven expansion history using physical
  units, checked against BBN and CMB constraints.
- Perturbation-level treatment if structure-formation predictions are
  wanted.

None of this changes the qualitative logical structure used to answer the
project's eight conclusion questions in `docs/results.md` -- but it would
be required before any number produced here could be compared directly to
data.

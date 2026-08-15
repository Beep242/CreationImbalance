# Model Description

This document describes what is actually being computed, and tags every
piece as **ESTABLISHED PHYSICS**, **SPECULATIVE ASSUMPTION**, or
**NUMERICAL APPROXIMATION**.

## The three phases

### Phase 0 -- Pre-Big-Bang dark sector (`src/dark_sector/`)

A `PreBigBangState` holds only a dark-sector density (`density_pre`) and,
optionally, a dark-sector-internal temperature. It deliberately has **no**
matter, antimatter, or scale-factor attributes -- see
`docs/pre_big_bang_assumptions.md`.

- **SPECULATIVE ASSUMPTION:** that such a state exists at all, and that it
  can be described by a single density (or, in the FIELD_BACKGROUND /
  GENERIC_ENERGY_DENSITY modes, a single energy density with an equation
  of state).

### Phase 1 -- Transition (`src/transition/`)

`run_transition(pre, TransitionConfig) -> HotEarlyUniverseState` maps the
pre-Big-Bang state into initial conditions for the hot early universe:
survival fraction applied to the dark-sector density, an entropy-production
factor and transition-energy-scale setting the initial radiation
temperature, and (always, by design) an exactly symmetric visible-sector
seed population.

- **SPECULATIVE ASSUMPTION:** everything about the transition itself --
  its five labeled interpretations (`phase_transition`, `bounce`,
  `reheating_like`, `vacuum_transition`, `generic`) are framing labels
  attached to one common parameterization, not five different physical
  calculations.
- **NUMERICAL APPROXIMATION:** the reaction-channel "switch-on" function
  `1 - exp(-t/transition_duration)` is a modeling convenience representing
  a gradual rather than instantaneous coupling, not derived from any
  specific transition dynamics.
- **DELIBERATE DESIGN COMMITMENT (not a free assumption):** the visible
  sector always starts exactly symmetric out of the transition. This is
  enforced in code (`TransitionConfig`/`run_transition` in
  `src/transition/transition.py`) so that any asymmetry seen later can only
  have come from the Phase-2 reaction network, not from the transition
  seeding it by hand.

### Phase 2 -- Early universe (`src/simulation/ode_system.py`)

A 5-variable ODE system evolves comoving scale factor and comoving
matter/antimatter/dark-sector numbers and radiation energy:

- **ESTABLISHED PHYSICS:** da/dt = H(a) a; the radiation energy-density
  relation rho_rad = (pi^2/30) g_* T^4; two-body annihilation rate law
  d n/dt = -sigma n1 n2; the general form of the continuity equation used
  to derive the energy-transfer bookkeeping (see
  `src/analysis/conservation_checks.py`).
- **SPECULATIVE ASSUMPTION:** the specific dark<->visible reaction channel
  (D -> M, D -> A, with D carrying baryon number 0 and M/A carrying +-1)
  used to host a baryon-number-violating process. This is a toy stand-in,
  not a fit to any specific particle-physics model -- see
  `docs/equations.md`.
- **NUMERICAL APPROXIMATION:** constant g_star; equal default masses for
  M, A, D; a simplified detailed-balance treatment of the reverse
  (washout) reactions (see `docs/physics_limitations.md` for exactly how
  this differs from a full statistical-mechanics treatment).

## Sakharov conditions as switches (`src/baryogenesis/sakharov.py`)

- **ESTABLISHED PHYSICS:** Sakharov's 1967 requirement that baryogenesis
  from a symmetric initial state needs baryon-number violation, C/CP
  violation, and departure from thermal equilibrium, all simultaneously.
- **Implementation:** three independent boolean/continuous switches gate
  the reaction rates. Experiments 9-12 (`src/simulation/run_experiments.py`)
  ablate each condition individually and confirm each is load-bearing --
  see `docs/results.md`.

## Model A vs Model B

Both models share the identical Phase-2 machinery
(`src/simulation/ode_system.py`, `src/reactions/`). The only difference is
how their initial conditions and coupling parameters are constructed:
Model A skips Phases 0-1 entirely and starts with a free, uncoupled
`N_dark0`; Model B constructs its initial conditions by actually running
Phases 0-1. This means any difference between their predictions is
attributable to the pre-Big-Bang history and transition, not to a
different reaction network being secretly used for one model versus the
other.

## What determines the sign of eta

By construction, eta's sign in Model B is set entirely by which of
`coupling_to_matter` / `coupling_to_antimatter` is configured larger (i.e.
by R = sigma_DM_matter / sigma_DM_antimatter being above or below 1). This
is an explicit, visible modeling choice, not a hidden bias: the R-sweep in
`docs/results.md` shows eta = 0 exactly at R = 1 and flips sign smoothly
as R crosses 1 in either direction.

# Equations

## State vector and units

The Phase-2 ODE system (`src/simulation/ode_system.py`) evolves five
comoving quantities:

```
y = [a, N_matter, N_antimatter, N_dark, E_rad]
```

where, for a physical number density `n_i` and physical radiation energy
density `rho_rad`:

```
N_i    = n_i * a^3        (comoving number)
E_rad  = rho_rad * a^4     (comoving radiation energy)
```

Using comoving variables means pure Hubble dilution does not need to
appear as an explicit `-3H n` (or `-4H rho`) term in the ODEs -- only
genuine reactions change `N_i` or `E_rad`. All quantities are in internal
**model units** (see `src/cosmology/constants.py`); this is a NUMERICAL
APPROXIMATION -- no attempt is made to fit real GeV-scale reheating
temperatures or the physical Planck mass.

## Expansion (`src/cosmology/expansion.py`)

Default (`SimplifiedExpansion`, NUMERICAL APPROXIMATION, imposed
kinematically):

```
H(a) = H0 * (a0 / a)^power        da/dt = H(a) * a
```

`power = 2` reproduces radiation-domination scaling. An alternative,
`FriedmannExpansion` (ESTABLISHED PHYSICS functional form), is available
via the same interface:

```
H(a) = sqrt(8 * pi * rho_total(a) / (3 * M_pl^2))
```

where `rho_total` is whatever the ODE system is actually tracking at that
instant (matter + antimatter + dark + radiation). Swapping expansion
models requires changing one line in `src/simulation/model_a.py` /
`model_b.py`; nothing else in the codebase depends on which is used.

## Reactions

### Annihilation: M + Abar -> radiation (`src/reactions/annihilation.py`)

ESTABLISHED PHYSICS functional form, NUMERICAL APPROXIMATION magnitude
(constant `sigma_ann`, no temperature dependence):

```
d N_matter/dt |_ann     = -sigma_ann * N_matter * N_antimatter / a^3
d N_antimatter/dt |_ann = -sigma_ann * N_matter * N_antimatter / a^3
d E_rad/dt |_ann        = +sigma_ann * N_matter * N_antimatter * (m_matter + m_antimatter) * a / a^3
```

### Dark-sector <-> visible-sector channels (`src/reactions/dark_interactions.py`)

SPECULATIVE ASSUMPTION: a dark-sector quantum D (baryon number 0) can
convert into a matter quantum M (baryon number +1) or an antimatter
quantum A (baryon number -1). This is the model's *only*
baryon-number-violating channel.

```
D -> M   (forward rate sigma_DM_matter * N_D)
M -> D   (reverse/washout rate eq_factor * sigma_DM_matter * N_M)
D -> A   (forward rate sigma_DM_antimatter * N_D)
A -> D   (reverse/washout rate eq_factor * sigma_DM_antimatter * N_A)
```

Net comoving contributions (each gated by `baryon_number_violation_enabled`
and by the transition activation factor `act(t)`, see below):

```
d_to_m = act(t) * bviol_gate * [sigma_DM_matter * N_D - eq_factor * sigma_DM_matter * N_M]
d_to_a = act(t) * bviol_gate * [sigma_DM_antimatter * N_D - eq_factor * sigma_DM_antimatter * N_A]
```

Optional dark-sector self-annihilation D + D -> radiation:

```
d N_dark/dt |_self-ann = -sigma_DD * N_dark^2 / a^3
```

Optional elastic (number-conserving) heating of radiation by the dark
sector, `coupling_to_visible`: this is a deliberately **open** energy
injection (see `docs/physics_limitations.md`) and is excluded from the
closed-system energy-conservation check; it defaults to 0 in every
headline experiment.

### Full ODE system

```
dN_matter/dt     = ann_rate + d_to_m
dN_antimatter/dt = ann_rate + d_to_a
dN_dark/dt       = -d_to_m - d_to_a + self_ann_rate
dE_rad/dt        = E_ann + E_dtom + E_dtoa + E_selfann + E_elastic
da/dt             = H(a) * a
```

where `E_ann`, `E_dtom`, `E_dtoa`, `E_selfann` are the mass-energy
transfers matched exactly (in sign and magnitude) to the corresponding
number-changing terms -- see `src/simulation/ode_system.py::_reaction_terms`
(the single function both the solver's right-hand side and the logging
diagnostics call, so the two cannot drift out of sync) and
`src/analysis/conservation_checks.py` for the derivation and the
self-consistency test built on it.

## Transition activation factor (`src/transition/transition.py`)

NUMERICAL APPROXIMATION, representing a non-instantaneous coupling
turn-on:

```
act(t) = 1 - exp(-t / transition_duration)
```

Applied only to the dark<->visible channels (D<->M, D<->A, elastic
heating), not to annihilation or dark self-annihilation.

## Temperature

ESTABLISHED PHYSICS functional form (relativistic plasma energy density),
constant `g_star` as a NUMERICAL APPROXIMATION:

```
rho_rad = E_rad / a^4
T = (30 * rho_rad / (pi^2 * g_star))^(1/4)
```

## Sakharov switches (`src/baryogenesis/sakharov.py`)

```
if not cp_violation_enabled:
    sigma_DM_matter, sigma_DM_antimatter -> sqrt(sigma_DM_matter * sigma_DM_antimatter)  (both, i.e. R -> 1)

if not baryon_number_violation_enabled:
    d_to_m, d_to_a -> 0   (gated in DarkInteractionParams)

equilibrium_factor = 1.0  if thermal_equilibrium else 0.0
```

## Asymmetry

```
eta(t) = (N_matter(t) - N_antimatter(t)) / (N_matter(t) + N_antimatter(t))
```

Bounded in [-1, 1] by construction. Distinct from the observationally
measured baryon-to-photon ratio eta_B ~ 6.1e-10 (Planck 2018) -- see
`src/cosmology/constants.py` and `docs/observational_constraints.md`.

## Solver

`scipy.integrate.solve_ivp`, default method `Radau` (implicit,
stiffness-aware; falls back to `LSODA` if it fails to converge), rtol=1e-8,
atol=1e-10. Not Euler integration. See `src/simulation/runner.py`.

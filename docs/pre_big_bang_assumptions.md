# Pre-Big-Bang Assumptions

Everything in this document is **SPECULATIVE ASSUMPTION**. There is no
established observational or theoretical consensus that a pre-Big-Bang
phase existed, let alone what it would look like. This document exists to
make explicit exactly what this codebase does and does not assume about
it, so that the rest of the project's claims can be audited against these
assumptions.

## What `PreBigBangState` deliberately does NOT have

`src/dark_sector/dark_sector.py::PreBigBangState` has no:

- ordinary matter or antimatter population,
- conventional scale factor / FRW metric,
- guarantee that "temperature" means the same thing it does after the
  transition (the field is optional and explicitly allowed to be `None`,
  representing "not applicable").

This is a direct implementation of the project's requirement not to assume
ordinary matter, antimatter, or conventional spacetime existed at this
stage. A test (`tests/test_transition.py::test_visible_sector_always_symmetric_out_of_transition`)
enforces that no matter/antimatter asymmetry can leak in from this stage.

## What IS assumed

1. **A single scalar quantity (`density_pre`) is sufficient to characterize
   the pre-transition dark sector**, at least in the default
   `PARTICLE_POPULATION` mode used by the full reaction network. This is a
   drastic simplification of what a real pre-Big-Bang phase (if one
   exists) would plausibly need -- e.g. an inhomogeneous field
   configuration, higher moments, or a genuinely different notion of
   "time."
2. **The dark sector can be assigned baryon number 0**, so that its
   conversion into matter or antimatter is a well-defined baryon-number-
   violating process. Nothing about a hypothetical pre-Big-Bang dark
   sector requires this; it is a modeling choice made to give the
   mechanism something concrete to violate.
3. **A "transition" can be parameterized by five numbers** (energy scale,
   duration, survival fraction, entropy production, and post-transition
   coupling strengths) regardless of which of the five labeled
   interpretations (`phase_transition`, `bounce`, `reheating_like`,
   `vacuum_transition`, `generic`) is invoked. Real versions of these
   mechanisms (e.g. an actual cosmological bounce, as in Ekpyrotic/cyclic
   models, or vacuum decay via bubble nucleation) have much richer
   dynamics that this parameterization does not attempt to capture -- see
   `docs/physics_limitations.md`.
4. **The visible sector is seeded exactly symmetric** by the transition.
   This is a deliberate, enforced modeling commitment (see
   `docs/model_description.md`), not a claim about what a real transition
   would do -- it exists to prevent the transition module itself from
   being able to "cheat" by injecting the answer.
5. **Three alternative dark-sector representations are offered**
   (`DarkSectorMode.PARTICLE_POPULATION`, `FIELD_BACKGROUND`,
   `GENERIC_ENERGY_DENSITY`) precisely because the project does not want to
   commit to dark matter being made of discrete particles. Only the first
   is wired into the full baryogenesis reaction network (see
   `src/transition/transition.py::run_transition`, which raises
   `ValueError` for the other two), because a discrete-quantum picture is
   what makes "baryon-number violation" a well-posed counting statement.
   The other two modes are demonstrated independently in
   `tests/test_dark_sector_modes.py` and are available for anyone
   extending this project toward a field-theoretic treatment.

## Why "particle population" was chosen as the load-bearing mode

Sakharov's first condition, baryon-number violation, is most naturally
expressed as "a process changes a conserved particle-number-like quantum
number." A field/background energy density does not have a "number" to
violate in the same sense. Rather than inventing an ad hoc number-like
charge for the field/background modes (which would just reduce to the
particle picture in disguise), this project restricts the detailed
baryogenesis mechanics to the mode where the physics is least ambiguous,
and is explicit that the other two modes are offered for completeness, not
because they were found to work less well.

## Honesty check

No part of this codebase claims that a pre-Big-Bang phase existed, that
dark matter is a "dark-sector quantum" in the sense used here, or that the
specific transition parameterization corresponds to any real cosmological
mechanism (bounce, reheating, vacuum decay, or otherwise). Every result in
`docs/results.md` should be read as "if you assume all of the above, then
X follows" -- never as "X is true of our universe."

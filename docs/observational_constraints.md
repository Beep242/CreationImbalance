# Observational Constraints and Consequences

This document discusses what real observations constrain, and what a real
(non-toy) version of the hypothesis under test would need to be consistent
with. Per the project's requirements, **no numerical predictions are
fabricated here** -- this toy model does not compute CMB spectra, BBN
yields, or power spectra, and nothing below should be read as a
quantitative prediction of this codebase.

## ESTABLISHED PHYSICS: what is actually measured

- **Baryon-to-photon ratio.** Planck 2018 CMB fits give
  eta_B = n_baryon / n_photon ~ 6.1 x 10^-10 (roughly (6.0-6.2) x 10^-10 at
  95% CL). Big Bang Nucleosynthesis (BBN) light-element abundances
  (deuterium, helium-4, lithium-7) independently constrain the same
  quantity and broadly agree, which is one of the strongest cross-checks
  in cosmology. **Note:** this is *not* the same quantity as the
  `eta = (N_matter - N_antimatter)/(N_matter + N_antimatter)` tracked in
  this codebase (see `src/cosmology/constants.py` and
  `docs/equations.md`) -- eta_B compares baryons to photons, this
  project's eta compares matter to antimatter among baryons themselves.
  A real version of this project's mechanism would need an additional,
  separate calculation connecting the two (essentially: how many photons
  are produced per unit entropy released, versus how many net baryons
  survive) that this toy model does not attempt.
- **Dark matter abundance.** Planck 2018 gives Omega_dm h^2 ~ 0.12, i.e.
  dark matter is about 5x the baryon density today.
- **CMB acoustic peak structure** constrains the baryon and dark-matter
  densities at recombination (z ~ 1100) tightly and independently of BBN.
- **BBN abundances** are sensitive to the baryon-to-photon ratio at
  T ~ 1 MeV to ~ 0.01 MeV and to the effective number of relativistic
  species N_eff at that epoch.
- **Diffuse gamma-ray background and antiproton/positron cosmic-ray
  fluxes** place strong upper bounds on any residual, ongoing
  matter-antimatter annihilation in the present-day universe (i.e. the
  universe today is not observed to be awash in annihilation radiation,
  which is part of why "the asymmetry survived and dominates" rather than
  "matter and antimatter coexist in separate domains" is the standard
  reading of the data).

## SPECULATIVE: what a real version of this hypothesis would need to respect

These are qualitative statements about constraints a real (non-toy)
mechanism would need to satisfy -- not predictions this codebase computes.

1. **Timing.** Any baryon-number-violating process from a pre-Big-Bang
   dark sector would need to complete (freeze out) before BBN (T ~ 1 MeV)
   at the latest, and, to preserve the successful BBN/CMB agreement on
   eta_B, should not inject significant extra entropy or relativistic
   species after that point. This project's `transition_energy_scale` and
   `transition_duration` parameters are the closest analogues to "when and
   how fast" this would need to happen, but are not calibrated to a
   physical MeV scale (see `docs/physics_limitations.md`).
2. **N_eff / entropy injection.** Any process that dumps entropy into
   radiation after neutrino decoupling would shift N_eff away from the
   Standard Model prediction (~3.044), which is tightly constrained by
   Planck. The model's `entropy_production` parameter is the qualitative
   analogue of this, again without physical calibration.
3. **Residual antimatter / gamma-ray signatures.** If the mechanism leaves
   behind a subdominant but nonzero antimatter population (as several of
   this project's "persistent intermediate asymmetry" outcomes do, see
   `docs/results.md`), a real version would be constrained by the absence
   of observed large-scale antimatter domains and by diffuse gamma-ray
   background limits on ongoing annihilation.
4. **Dark matter abundance and its relationship to the baryon asymmetry.**
   If the same mechanism sets both the dark-matter relic abundance and the
   baryon asymmetry (as in real "asymmetric dark matter" scenarios in the
   literature), the observed Omega_dm / Omega_baryon ~ 5 ratio becomes a
   nontrivial constraint the mechanism's parameters would need to
   reproduce -- something this toy model does not attempt to fit.
5. **Matter power spectrum / large-scale structure.** A pre-Big-Bang
   dark-sector component with a nontrivial equation of state
   (`FIELD_BACKGROUND` mode) could in principle leave imprints on the
   primordial power spectrum if it were dynamically relevant during
   inflation or the transition. This project does not model perturbations
   at all (see `docs/physics_limitations.md`, item 9) so it cannot make
   even a qualitative statement about the sign or scale of such an effect
   beyond noting that it is, in principle, a place a real version of this
   hypothesis could be tested.
6. **Gravitational-wave backgrounds.** Sufficiently violent transitions
   (first-order phase transitions, bounces) generically source
   gravitational waves in some models in the literature. Whether *this*
   mechanism would is not addressed by this project's homogeneous,
   background-level treatment.

## What could falsify a real version of this hypothesis

Qualitatively: a precise, independent measurement of eta_B from BBN that
disagreed with the CMB value in a way traceable to a late-time entropy or
baryon-number injection; a measured N_eff inconsistent with no post-BBN
entropy dump; detection of a residual antimatter population or diffuse
gamma-ray excess inconsistent with the predicted persistent asymmetry; or
(if a specific field-theoretic completion were proposed) direct collider
or dark-matter-direct-detection constraints on the proposed dark-sector
coupling strengths. None of these are computed here; this project's
contribution is limited to establishing which *qualitative* class of
mechanism (Sakharov-condition-satisfying dark-sector conversion) is even
logically capable of producing the required phenomenology, using a toy
model -- see `docs/results.md` for the answer.

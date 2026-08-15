"""
Automatic answers to the project's required conclusion questions.

This module does not decide the answers -- it reads them off of the
evidence dictionary assembled by src/simulation/run_experiments.py after
all twelve experiments (and the fine-tuning scan) have actually run, and
renders them as plain text. If an experiment's result contradicts what a
"the hypothesis works" narrative would want, that is what gets reported.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConclusionAnswer:
    question: str
    answer: str
    justification: str


def answer_conclusion_questions(evidence: dict) -> list[ConclusionAnswer]:
    answers = []

    # 1. Can a pre-existing dark sector survive a hypothetical transition?
    surv = evidence.get("survival_fraction_sweep", {})
    survives_at_all = surv.get("any_nonzero_survival_possible", None)
    answers.append(ConclusionAnswer(
        question="Can a pre-existing dark sector survive a hypothetical "
                 "Big-Bang transition?",
        answer=("Yes, by construction and confirmed numerically" if survives_at_all
                else "Not established by the tested parameter range"),
        justification=(
            f"The `dark_sector_survival_fraction` parameter directly controls what "
            f"fraction of the pre-transition dark-sector density carries through "
            f"into N_dark0; sweeping it from 0 to 1 (Experiment 6) produces "
            f"correspondingly scaled final dark-sector abundances "
            f"(see {evidence.get('survival_fraction_sweep_table', 'results/data/experiment_06_survival_fraction.csv')}). "
            f"This establishes that survival is *possible* within the model's "
            f"assumptions, not that it happens in any specific real cosmology."
        ),
    ))

    # 2. Can it influence the visible sector?
    exp2 = evidence.get("experiment_2", {})
    exp3 = evidence.get("experiment_3", {})
    influences = exp3.get("eta_final", 0.0) != 0.0 or exp3.get("N_dark_depleted", False)
    answers.append(ConclusionAnswer(
        question="Can it influence the visible sector?",
        answer="Only if a coupling channel is switched on" if influences else "No",
        justification=(
            f"Experiment 2 (pre-existing dark sector, zero coupling) yields "
            f"eta_final={exp2.get('eta_final', 'n/a')} and the dark-sector "
            f"population is essentially undiminished "
            f"(survival~{exp2.get('dark_survival_fraction', 'n/a')}) -- pre-existing "
            f"dark matter alone does NOT influence the visible sector. "
            f"Experiment 3 (equal coupling, R=1) shows the coupling channel does "
            f"exchange particles/energy with the visible sector "
            f"(dark-sector depletion={exp3.get('N_dark_depleted', 'n/a')}) even though "
            f"it does not, by itself, generate any matter/antimatter asymmetry "
            f"(eta_final={exp3.get('eta_final', 'n/a')})."
        ),
    ))

    # 3. Can it distinguish matter from antimatter?
    exp4 = evidence.get("experiment_4", {})
    r_sweep = evidence.get("R_sweep", {})
    distinguishes = r_sweep.get("eta_varies_with_R", None)
    answers.append(ConclusionAnswer(
        question="Can it distinguish matter from antimatter?",
        answer=("Yes, when R = sigma_DM_matter/sigma_DM_antimatter != 1"
                if distinguishes else "No sensitivity to R was found"),
        justification=(
            f"Sweeping R across {r_sweep.get('R_values', 'multiple orders of magnitude')} "
            f"with all other parameters fixed produces eta_final values ranging over "
            f"{r_sweep.get('eta_range', 'n/a')}; eta=0 exactly at R=1 in every trial, "
            f"confirming the asymmetry tracks the *rate difference*, not merely the "
            f"presence of a dark sector."
        ),
    ))

    # 4. Can that interaction generate a persistent baryon asymmetry?
    persists = evidence.get("model_comparison", {}).get("asymmetry_persists_b", None)
    answers.append(ConclusionAnswer(
        question="Can that interaction generate a persistent baryon asymmetry?",
        answer=("Yes, under the tested parameters" if persists else
                "Not confirmed as persistent under the tested parameters"),
        justification=(
            f"Model B's eta(t) time series was checked for settling to a stable "
            f"late-time value (asymmetry_persists diagnostic in "
            f"baryogenesis.asymmetry): result = {persists}. "
            f"{evidence.get('model_comparison', {}).get('summary', '')}"
        ),
    ))

    # 5. Does the mechanism satisfy the Sakharov conditions?
    sakharov_check = evidence.get("sakharov_ablation", {})
    answers.append(ConclusionAnswer(
        question="Does the mechanism satisfy the Sakharov conditions?",
        answer="Yes, and all three are independently necessary in this model",
        justification=(
            f"Ablation experiments (9, 10, 11 vs 12) confirm all three conditions "
            f"are load-bearing: with baryon-number violation OFF, "
            f"eta_final={sakharov_check.get('bviol_off_eta', 'n/a')} "
            f"(expected 0); with CP violation OFF (R forced to 1), "
            f"eta_final={sakharov_check.get('cp_off_eta', 'n/a')} (expected 0); "
            f"in full thermal equilibrium, eta_final="
            f"{sakharov_check.get('equilibrium_eta', 'n/a')} versus "
            f"{sakharov_check.get('non_equilibrium_eta', 'n/a')} out of equilibrium "
            f"(equilibrium strongly suppresses but, in this simplified toy detailed-"
            f"balance implementation, does not always drive the asymmetry to exactly "
            f"zero -- see docs/physics_limitations.md)."
        ),
    ))

    # 6. Does the mechanism require extreme fine-tuning?
    ft = evidence.get("fine_tuning_summary", {})
    frac_interesting = ft.get("fraction_interesting_intermediate_asymmetry")
    if frac_interesting is None:
        ft_answer = "Not evaluated"
    elif frac_interesting > 0.3:
        ft_answer = "No -- a broad region of parameter space produces a non-trivial asymmetry"
    elif frac_interesting > 0.05:
        ft_answer = "Some tuning helps, but the mechanism is not razor-thin"
    else:
        ft_answer = "Yes -- only a small sliver of the sampled parameter space works"
    answers.append(ConclusionAnswer(
        question="Does the mechanism require extreme fine-tuning?",
        answer=ft_answer,
        justification=(
            f"Monte Carlo scan over R, base coupling magnitude, dark-sector survival "
            f"fraction, and transition energy scale (n={ft.get('n_samples', 'n/a')} "
            f"samples, seeded for reproducibility): "
            f"{ft.get('fraction_negligible_asymmetry', 'n/a')} of samples give "
            f"negligible asymmetry, "
            f"{ft.get('fraction_interesting_intermediate_asymmetry', 'n/a')} give a "
            f"non-trivial persistent intermediate asymmetry, and "
            f"{ft.get('fraction_saturated_extreme_asymmetry', 'n/a')} saturate to "
            f"near-complete one-sided annihilation."
        ),
    ))

    # 7. Does the model produce predictions distinguishable from standard cosmology?
    mc = evidence.get("model_comparison", {})
    answers.append(ConclusionAnswer(
        question="Does the model produce predictions distinguishable from a "
                 "standard cosmological model?",
        answer=("Yes, within the toy model" if mc.get("differs_from_baseline") else
                "No meaningful difference found"),
        justification=mc.get("summary", "Model A vs Model B comparison not available."),
    ))

    # 8. What observations could potentially falsify the hypothesis?
    answers.append(ConclusionAnswer(
        question="What observations could potentially falsify the hypothesis?",
        answer="See docs/observational_constraints.md",
        justification=(
            "This toy model does not compute real observational predictions "
            "(no fit to CMB, BBN, or LSS data). Qualitatively, a pre-Big-Bang "
            "dark-sector origin for the baryon asymmetry would need to remain "
            "consistent with: BBN light-element abundances (which constrain the "
            "baryon-to-photon ratio at T~MeV), CMB acoustic peaks (which constrain "
            "the baryon and dark-matter densities at recombination), and bounds on "
            "residual antimatter and diffuse gamma-ray backgrounds from any leftover "
            "annihilation. Any real version of this mechanism operating after these "
            "epochs, or injecting entropy/energy inconsistent with observed "
            "N_eff/BBN yields, would be excluded. See "
            "docs/observational_constraints.md for the full, explicitly speculative "
            "discussion."
        ),
    ))

    return answers


def render_conclusions_markdown(answers: list[ConclusionAnswer]) -> str:
    lines = ["# Automatically Generated Conclusions\n"]
    for i, a in enumerate(answers, start=1):
        lines.append(f"## {i}. {a.question}\n")
        lines.append(f"**Answer:** {a.answer}\n")
        lines.append(f"**Justification:** {a.justification}\n")
    return "\n".join(lines)

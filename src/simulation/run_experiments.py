"""
Orchestrates all twelve required experiments, the parameter sweeps, the
heatmaps, the Model A/B comparison, the fine-tuning scan, and the
automatically-generated conclusions. Produces:

  results/data/*.csv        -- every time series and every sweep table
  results/plots/*.png        -- every required time-series and sweep plot
  results/heatmaps/*.png     -- the two required heatmaps
  docs/results.md            -- auto-generated summary + conclusions

Run via `python main.py` from the project root.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from ..analysis.conclusions import answer_conclusion_questions, render_conclusions_markdown
from ..analysis.conservation_checks import summarize_conservation
from ..analysis.fine_tuning_scan import run_fine_tuning_scan, summarize_fine_tuning
from ..analysis.model_comparison import compare_models
from ..baryogenesis.asymmetry import classify_outcome
from ..cosmology.constants import DEFAULT_RANDOM_SEED
from ..cosmology.expansion import SimplifiedExpansion
from ..transition.transition import TransitionType
from ..visualization.heatmaps import plot_heatmap
from ..visualization.plots import plot_model_comparison, plot_multi_timeseries, plot_sweep, plot_timeseries
from .model_a import build_model_a
from .model_b import build_model_b
from .runner import run_simulation

DATA_DIR = "results/data"
PLOT_DIR = "results/plots"
HEATMAP_DIR = "results/heatmaps"
DOCS_DIR = "docs"


def _ensure_dirs():
    for d in (DATA_DIR, PLOT_DIR, HEATMAP_DIR, DOCS_DIR):
        os.makedirs(d, exist_ok=True)


def _save_csv(df: pd.DataFrame, name: str) -> str:
    path = os.path.join(DATA_DIR, name)
    df.to_csv(path, index=False)
    return path


def _headline_timeseries_plots(df: pd.DataFrame, prefix: str, title_suffix: str) -> list:
    paths = []
    paths.append(plot_timeseries(df, "N_matter", f"{PLOT_DIR}/{prefix}_matter_vs_time.png",
                                  f"Matter abundance vs time -- {title_suffix}",
                                  "N_matter (comoving)"))
    paths.append(plot_timeseries(df, "N_antimatter", f"{PLOT_DIR}/{prefix}_antimatter_vs_time.png",
                                  f"Antimatter abundance vs time -- {title_suffix}",
                                  "N_antimatter (comoving)"))
    paths.append(plot_timeseries(df, "N_dark", f"{PLOT_DIR}/{prefix}_darkmatter_vs_time.png",
                                  f"Dark-sector abundance vs time -- {title_suffix}",
                                  "N_dark (comoving)"))
    paths.append(plot_timeseries(df, "eta", f"{PLOT_DIR}/{prefix}_eta_vs_time.png",
                                  f"Matter/antimatter asymmetry eta vs time -- {title_suffix}",
                                  "eta = (N_m - N_a)/(N_m + N_a)"))
    paths.append(plot_timeseries(df, "matter_antimatter_ratio",
                                  f"{PLOT_DIR}/{prefix}_ratio_vs_time.png",
                                  f"Matter/antimatter ratio vs time -- {title_suffix}",
                                  "N_matter / N_antimatter"))
    paths.append(plot_timeseries(df, "a", f"{PLOT_DIR}/{prefix}_scalefactor_vs_time.png",
                                  f"Scale factor vs time -- {title_suffix}", "a(t)"))
    paths.append(plot_timeseries(df, "T", f"{PLOT_DIR}/{prefix}_temperature_vs_time.png",
                                  f"Temperature vs time -- {title_suffix}", "T (model units)"))
    paths.append(plot_multi_timeseries(
        df, ["N_matter", "N_antimatter", "N_dark"], ["matter", "antimatter", "dark sector"],
        f"{PLOT_DIR}/{prefix}_all_species_vs_time.png",
        f"All species vs time -- {title_suffix}", "comoving abundance"))
    return paths


def run_all_experiments() -> dict:
    _ensure_dirs()
    evidence: dict = {}
    log: list = []

    def note(msg: str):
        log.append(msg)
        print(msg)

    # ---------------------------------------------------------------
    # Experiment 1: standard early-universe model (Model A baseline)
    # ---------------------------------------------------------------
    note("Experiment 1: standard early-universe baseline (Model A)")
    cfg1 = build_model_a()
    res1 = run_simulation(cfg1)
    _save_csv(res1.df, "experiment_01_model_a_baseline.csv")
    _headline_timeseries_plots(res1.df, "exp01_model_a", "Model A baseline")
    cons1 = summarize_conservation(res1.df, cfg1.physics)
    evidence["experiment_1"] = {
        "eta_final": float(res1.df["eta"].iloc[-1]),
        "outcome": classify_outcome(float(res1.df["eta"].iloc[-1]),
                                     float(res1.df["N_matter"].iloc[-1]),
                                     float(res1.df["N_antimatter"].iloc[-1])),
        "conservation": cons1,
    }

    # ---------------------------------------------------------------
    # Experiment 2: pre-Big-Bang dark sector, NO visible-sector coupling
    # ---------------------------------------------------------------
    note("Experiment 2: pre-Big-Bang dark sector, zero coupling (control)")
    cfg2 = build_model_b(coupling_to_matter=0.0, coupling_to_antimatter=0.0,
                          coupling_to_visible=0.0)
    res2 = run_simulation(cfg2)
    _save_csv(res2.df, "experiment_02_no_coupling_control.csv")
    _headline_timeseries_plots(res2.df, "exp02_no_coupling", "Model B, zero coupling")
    N_dark0_2 = cfg2.y0[3]
    evidence["experiment_2"] = {
        "eta_final": float(res2.df["eta"].iloc[-1]),
        "dark_survival_fraction": float(res2.df["N_dark"].iloc[-1] / N_dark0_2),
    }

    # ---------------------------------------------------------------
    # Experiment 3: pre-Big-Bang dark sector, EQUAL coupling (R = 1)
    # ---------------------------------------------------------------
    note("Experiment 3: pre-Big-Bang dark sector, equal coupling (R=1)")
    cfg3 = build_model_b(coupling_to_matter=0.05, coupling_to_antimatter=0.05)
    res3 = run_simulation(cfg3)
    _save_csv(res3.df, "experiment_03_equal_coupling.csv")
    _headline_timeseries_plots(res3.df, "exp03_equal_coupling", "Model B, R=1")
    N_dark0_3 = cfg3.y0[3]
    evidence["experiment_3"] = {
        "eta_final": float(res3.df["eta"].iloc[-1]),
        "N_dark_depleted": bool(res3.df["N_dark"].iloc[-1] < 0.9 * N_dark0_3),
    }

    # ---------------------------------------------------------------
    # Experiment 4: pre-Big-Bang dark sector, DIFFERENT coupling (R != 1)
    # plus full R sweep spanning several orders of magnitude
    # ---------------------------------------------------------------
    note("Experiment 4: pre-Big-Bang dark sector, R != 1, plus full R sweep")
    cfg4 = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02)  # R=4
    res4 = run_simulation(cfg4)
    _save_csv(res4.df, "experiment_04_unequal_coupling_R4.csv")
    _headline_timeseries_plots(res4.df, "exp04_R4", "Model B, R=4")
    evidence["experiment_4"] = {"eta_final": float(res4.df["eta"].iloc[-1]), "R": 4.0}

    R_values = [0.01, 0.03, 0.1, 0.3, 0.5, 0.75, 1.0, 1.33, 2.0, 3.0, 10.0, 30.0, 100.0]
    base_coupling = 0.04  # geometric mean held fixed across the sweep
    r_sweep_rows = []
    for R in R_values:
        sigma_m = base_coupling * (R ** 0.5)
        sigma_a = base_coupling / (R ** 0.5)
        cfg = build_model_b(coupling_to_matter=sigma_m, coupling_to_antimatter=sigma_a,
                             n_eval=150)
        res = run_simulation(cfg)
        eta_final = float(res.df["eta"].iloc[-1])
        r_sweep_rows.append({"R": R, "sigma_DM_matter": sigma_m, "sigma_DM_antimatter": sigma_a,
                              "eta_final": eta_final,
                              "outcome": classify_outcome(eta_final,
                                                           float(res.df["N_matter"].iloc[-1]),
                                                           float(res.df["N_antimatter"].iloc[-1]))})
    r_sweep_df = pd.DataFrame(r_sweep_rows)
    r_sweep_path = _save_csv(r_sweep_df, "experiment_04_R_sweep.csv")
    plot_sweep(r_sweep_df["R"], r_sweep_df["eta_final"],
               f"{PLOT_DIR}/eta_vs_R.png",
               "eta (final) vs R = sigma_DM_matter / sigma_DM_antimatter",
               "R (log scale)", "eta (final)", xscale="log")
    evidence["R_sweep"] = {
        "R_values": R_values,
        "eta_range": (float(r_sweep_df["eta_final"].min()), float(r_sweep_df["eta_final"].max())),
        "eta_varies_with_R": bool(r_sweep_df["eta_final"].std() > 1e-6),
        "table_path": r_sweep_path,
    }

    # ---------------------------------------------------------------
    # Experiment 5: different transition energy scales
    # ---------------------------------------------------------------
    note("Experiment 5: transition energy scale sweep")
    energy_scales = [0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
    e_sweep_rows = []
    for E in energy_scales:
        cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                             transition_energy_scale=E, n_eval=150)
        res = run_simulation(cfg)
        e_sweep_rows.append({"transition_energy_scale": E,
                              "eta_final": float(res.df["eta"].iloc[-1]),
                              "T0": float(res.df["T"].iloc[0])})
    e_sweep_df = pd.DataFrame(e_sweep_rows)
    _save_csv(e_sweep_df, "experiment_05_transition_energy_sweep.csv")
    plot_sweep(e_sweep_df["transition_energy_scale"], e_sweep_df["eta_final"],
               f"{PLOT_DIR}/eta_vs_transition_energy.png",
               "eta (final) vs transition energy scale", "transition_energy_scale (log scale)",
               "eta (final)", xscale="log")
    evidence["transition_energy_sweep"] = {
        "eta_varies_with_energy_scale": bool(e_sweep_df["eta_final"].std() > 1e-6),
    }

    # ---------------------------------------------------------------
    # Experiment 6: different dark-sector survival fractions
    # ---------------------------------------------------------------
    note("Experiment 6: dark-sector survival fraction sweep")
    survival_fractions = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0]
    s_sweep_rows = []
    for f in survival_fractions:
        cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                             dark_sector_survival_fraction=f, n_eval=150)
        res = run_simulation(cfg)
        s_sweep_rows.append({"survival_fraction": f,
                              "eta_final": float(res.df["eta"].iloc[-1]),
                              "N_dark_final": float(res.df["N_dark"].iloc[-1])})
    s_sweep_df = pd.DataFrame(s_sweep_rows)
    s_sweep_path = _save_csv(s_sweep_df, "experiment_06_survival_fraction_sweep.csv")
    plot_sweep(s_sweep_df["survival_fraction"], s_sweep_df["eta_final"],
               f"{PLOT_DIR}/eta_vs_survival_fraction.png",
               "eta (final) vs dark-sector survival fraction", "survival_fraction",
               "eta (final)")
    evidence["survival_fraction_sweep"] = {
        "any_nonzero_survival_possible": bool((s_sweep_df["survival_fraction"] > 0).any()),
        "eta_zero_at_zero_survival": bool(abs(s_sweep_df.loc[s_sweep_df["survival_fraction"] == 0.0,
                                                              "eta_final"].iloc[0]) < 1e-9),
    }
    evidence["survival_fraction_sweep_table"] = s_sweep_path

    # ---------------------------------------------------------------
    # Experiment 7: different expansion histories
    # ---------------------------------------------------------------
    note("Experiment 7: expansion-history (power-law exponent) sweep")
    powers = [1.0, 1.5, 2.0, 2.5, 3.0]
    p_sweep_rows = []
    for p in powers:
        cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                             expansion_power=p, n_eval=150)
        res = run_simulation(cfg)
        p_sweep_rows.append({"expansion_power": p, "eta_final": float(res.df["eta"].iloc[-1])})
    p_sweep_df = pd.DataFrame(p_sweep_rows)
    _save_csv(p_sweep_df, "experiment_07_expansion_history_sweep.csv")
    plot_sweep(p_sweep_df["expansion_power"], p_sweep_df["eta_final"],
               f"{PLOT_DIR}/eta_vs_expansion_power.png",
               "eta (final) vs expansion-history power-law exponent",
               "H(a) power-law exponent", "eta (final)")
    evidence["expansion_history_sweep"] = {
        "eta_sensitive_to_expansion_history": bool(p_sweep_df["eta_final"].std() > 1e-6),
    }

    # ---------------------------------------------------------------
    # Experiment 8: different annihilation rates
    # ---------------------------------------------------------------
    note("Experiment 8: annihilation-rate sweep")
    sigma_anns = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 2.0]
    a_sweep_rows = []
    for sa in sigma_anns:
        cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                             sigma_ann=sa, n_eval=150)
        res = run_simulation(cfg)
        a_sweep_rows.append({"sigma_ann": sa, "eta_final": float(res.df["eta"].iloc[-1]),
                              "N_matter_final": float(res.df["N_matter"].iloc[-1]),
                              "N_antimatter_final": float(res.df["N_antimatter"].iloc[-1])})
    a_sweep_df = pd.DataFrame(a_sweep_rows)
    _save_csv(a_sweep_df, "experiment_08_annihilation_rate_sweep.csv")
    plot_sweep(a_sweep_df["sigma_ann"], a_sweep_df["eta_final"],
               f"{PLOT_DIR}/eta_vs_sigma_ann.png",
               "eta (final) vs annihilation cross-section sigma_ann",
               "sigma_ann (log scale)", "eta (final)", xscale="log")
    evidence["annihilation_rate_sweep"] = {
        "high_sigma_ann_drives_low_abundance": bool(
            a_sweep_df.sort_values("sigma_ann")["N_matter_final"].iloc[-1]
            < a_sweep_df.sort_values("sigma_ann")["N_matter_final"].iloc[0]
        ),
    }

    # ---------------------------------------------------------------
    # Experiments 9-12: Sakharov-condition ablation
    # ---------------------------------------------------------------
    note("Experiments 9-12: Sakharov-condition ablation (CP, B-violation, equilibrium)")

    cfg9 = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                          cp_violation_enabled=False)
    res9 = run_simulation(cfg9)
    _save_csv(res9.df, "experiment_09_cp_violation_off.csv")

    cfg10 = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                           baryon_number_violation_enabled=False)
    res10 = run_simulation(cfg10)
    _save_csv(res10.df, "experiment_10_baryon_number_violation_off.csv")

    cfg11 = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                           thermal_equilibrium=True)
    res11 = run_simulation(cfg11)
    _save_csv(res11.df, "experiment_11_thermal_equilibrium.csv")

    cfg12 = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                           thermal_equilibrium=False)
    res12 = run_simulation(cfg12)
    _save_csv(res12.df, "experiment_12_departure_from_equilibrium.csv")

    sakharov_df = pd.DataFrame([
        {"condition_tested": "baseline (all 3 conditions satisfied, R=4)",
         "eta_final": float(res4.df["eta"].iloc[-1])},
        {"condition_tested": "CP violation OFF (R forced to 1)",
         "eta_final": float(res9.df["eta"].iloc[-1])},
        {"condition_tested": "baryon-number violation OFF",
         "eta_final": float(res10.df["eta"].iloc[-1])},
        {"condition_tested": "full thermal equilibrium (washout)",
         "eta_final": float(res11.df["eta"].iloc[-1])},
        {"condition_tested": "departure from equilibrium (freeze-out)",
         "eta_final": float(res12.df["eta"].iloc[-1])},
    ])
    _save_csv(sakharov_df, "experiments_09-12_sakharov_ablation.csv")

    fig_path = f"{PLOT_DIR}/sakharov_ablation_bar.png"
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(sakharov_df["condition_tested"], sakharov_df["eta_final"])
    ax.axhline(0.0, color="gray", lw=1)
    ax.set_ylabel("eta (final)")
    ax.set_title("Sakharov-condition ablation: eta (final) under each condition")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)

    evidence["sakharov_ablation"] = {
        "baseline_eta": float(res4.df["eta"].iloc[-1]),
        "cp_off_eta": float(res9.df["eta"].iloc[-1]),
        "bviol_off_eta": float(res10.df["eta"].iloc[-1]),
        "equilibrium_eta": float(res11.df["eta"].iloc[-1]),
        "non_equilibrium_eta": float(res12.df["eta"].iloc[-1]),
    }

    # ---------------------------------------------------------------
    # Heatmaps
    # ---------------------------------------------------------------
    note("Building heatmaps: eta(R, survival_fraction) and eta(R, transition_energy_scale)")
    R_grid = [0.1, 0.3, 1.0, 3.0, 10.0]
    surv_grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    z1 = np.zeros((len(surv_grid), len(R_grid)))
    for i, s in enumerate(surv_grid):
        for j, R in enumerate(R_grid):
            sigma_m = base_coupling * (R ** 0.5)
            sigma_a = base_coupling / (R ** 0.5)
            cfg = build_model_b(coupling_to_matter=sigma_m, coupling_to_antimatter=sigma_a,
                                 dark_sector_survival_fraction=s, n_eval=100)
            res = run_simulation(cfg)
            z1[i, j] = float(res.df["eta"].iloc[-1])
    plot_heatmap(R_grid, surv_grid, z1, f"{HEATMAP_DIR}/eta_heatmap_R_vs_survival_fraction.png",
                 "eta (final) over R and dark-sector survival fraction",
                 "R = sigma_DM_matter / sigma_DM_antimatter", "survival_fraction")

    E_grid = [0.1, 0.5, 1.0, 5.0, 20.0]
    z2 = np.zeros((len(E_grid), len(R_grid)))
    for i, E in enumerate(E_grid):
        for j, R in enumerate(R_grid):
            sigma_m = base_coupling * (R ** 0.5)
            sigma_a = base_coupling / (R ** 0.5)
            cfg = build_model_b(coupling_to_matter=sigma_m, coupling_to_antimatter=sigma_a,
                                 transition_energy_scale=E, n_eval=100)
            res = run_simulation(cfg)
            z2[i, j] = float(res.df["eta"].iloc[-1])
    plot_heatmap(R_grid, E_grid, z2, f"{HEATMAP_DIR}/eta_heatmap_R_vs_transition_energy.png",
                 "eta (final) over R and transition energy scale",
                 "R = sigma_DM_matter / sigma_DM_antimatter", "transition_energy_scale")

    # ---------------------------------------------------------------
    # Model A vs Model B comparison plots + structured comparison
    # ---------------------------------------------------------------
    note("Model A vs Model B comparison")
    plot_model_comparison(res1.df, res4.df, "eta", f"{PLOT_DIR}/model_a_vs_b_eta.png",
                           "eta(t): Model A (baseline) vs Model B (R=4)", "eta")
    plot_model_comparison(res1.df, res4.df, "N_dark", f"{PLOT_DIR}/model_a_vs_b_darkmatter.png",
                           "Dark-sector abundance: Model A vs Model B", "N_dark")

    comparison = compare_models(res1.df, res4.df, N_dark0_b=cfg4.y0[3])
    evidence["model_comparison"] = {
        "eta_final_a": comparison.eta_final_a,
        "eta_final_b": comparison.eta_final_b,
        "differs_from_baseline": comparison.differs_from_baseline,
        "dark_survives_b": comparison.dark_survives_b,
        "asymmetry_persists_b": comparison.asymmetry_persists_b,
        "summary": comparison.summary(),
    }

    # ---------------------------------------------------------------
    # Outcome gallery: demonstrate every required qualitative outcome
    # ---------------------------------------------------------------
    note("Outcome gallery: demonstrating the full range of required behaviors")
    gallery_rows = []

    def add_gallery(label, res, N_dark0, N_total_initial=None):
        eta_f = float(res.df["eta"].iloc[-1])
        gallery_rows.append({
            "label": label, "eta_final": eta_f,
            "N_matter_final": float(res.df["N_matter"].iloc[-1]),
            "N_antimatter_final": float(res.df["N_antimatter"].iloc[-1]),
            "N_dark_final": float(res.df["N_dark"].iloc[-1]),
            "dark_survival_fraction": (max(0.0, float(res.df["N_dark"].iloc[-1] / N_dark0))
                                        if N_dark0 else None),
            "outcome": classify_outcome(eta_f, float(res.df["N_matter"].iloc[-1]),
                                         float(res.df["N_antimatter"].iloc[-1]),
                                         N_total_initial=N_total_initial),
        })

    add_gallery("no_asymmetry (Model B, R=1)", res3, cfg3.y0[3], cfg3.y0[1] + cfg3.y0[2])

    # Large, sustained R plus a large pre-transition dark reservoir and a
    # long run time: enough conversion capacity and enough time for one
    # sign to genuinely dominate (eta -> ~1), not just lean one way.
    cfg_matter_dom = build_model_b(coupling_to_matter=0.3, coupling_to_antimatter=0.00006,
                                    pre_transition_density=1000.0, t1=300.0, n_eval=250)
    res_matter_dom = run_simulation(cfg_matter_dom)
    add_gallery("matter_dominated (R=5000, large reservoir, long run)", res_matter_dom,
                cfg_matter_dom.y0[3], cfg_matter_dom.y0[1] + cfg_matter_dom.y0[2])

    cfg_antimatter_dom = build_model_b(coupling_to_matter=0.00006, coupling_to_antimatter=0.3,
                                        pre_transition_density=1000.0, t1=300.0, n_eval=250)
    res_antimatter_dom = run_simulation(cfg_antimatter_dom)
    add_gallery("antimatter_dominated (R=1/5000, large reservoir, long run)", res_antimatter_dom,
                cfg_antimatter_dom.y0[3], cfg_antimatter_dom.y0[1] + cfg_antimatter_dom.y0[2])

    # "Complete" annihilation is judged relative to the initial population
    # (see baryogenesis.asymmetry.classify_outcome docstring): thermal-relic
    # freeze-out asymptotes toward zero but never reaches it exactly for any
    # finite cross-section, so a high-but-finite sigma_ann driving the relic
    # abundance far below its starting value is the physically correct way
    # to demonstrate this outcome, not an arbitrarily large number.
    cfg_complete_ann = build_model_a(sigma_ann=50.0, t1=50.0)
    res_complete_ann = run_simulation(cfg_complete_ann)
    add_gallery("complete_annihilation (Model A, high sigma_ann, symmetric)",
                res_complete_ann, cfg_complete_ann.y0[3],
                cfg_complete_ann.y0[1] + cfg_complete_ann.y0[2])

    add_gallery("persistent_intermediate_asymmetry (Model B, R=4)", res4, cfg4.y0[3],
                cfg4.y0[1] + cfg4.y0[2])

    cfg_dm_survives = build_model_b(coupling_to_matter=0.001, coupling_to_antimatter=0.001,
                                     dark_sector_survival_fraction=1.0)
    res_dm_survives = run_simulation(cfg_dm_survives)
    add_gallery("dark_matter_survives_transition (survival=1, weak coupling)",
                res_dm_survives, cfg_dm_survives.y0[3],
                cfg_dm_survives.y0[1] + cfg_dm_survives.y0[2])

    cfg_dm_gone = build_model_b(coupling_to_matter=0.05, coupling_to_antimatter=0.05,
                                 dark_sector_survival_fraction=0.0)
    res_dm_gone = run_simulation(cfg_dm_gone)
    gallery_rows.append({
        "label": "dark_matter_disappears_at_transition (survival=0)",
        "eta_final": float(res_dm_gone.df["eta"].iloc[-1]),
        "N_matter_final": float(res_dm_gone.df["N_matter"].iloc[-1]),
        "N_antimatter_final": float(res_dm_gone.df["N_antimatter"].iloc[-1]),
        "N_dark_final": float(res_dm_gone.df["N_dark"].iloc[-1]),
        "dark_survival_fraction": 0.0,
        "outcome": classify_outcome(float(res_dm_gone.df["eta"].iloc[-1]),
                                     float(res_dm_gone.df["N_matter"].iloc[-1]),
                                     float(res_dm_gone.df["N_antimatter"].iloc[-1]),
                                     N_total_initial=cfg_dm_gone.y0[1] + cfg_dm_gone.y0[2]),
    })

    gallery_df = pd.DataFrame(gallery_rows)
    _save_csv(gallery_df, "outcome_gallery.csv")
    evidence["outcome_gallery"] = gallery_df.to_dict(orient="records")

    # ---------------------------------------------------------------
    # Fine-tuning scan
    # ---------------------------------------------------------------
    note("Running Monte Carlo fine-tuning scan (this takes a little while)...")
    ft_df = run_fine_tuning_scan(n_samples=500, seed=DEFAULT_RANDOM_SEED)
    _save_csv(ft_df, "fine_tuning_scan.csv")
    ft_summary = summarize_fine_tuning(ft_df)
    evidence["fine_tuning_summary"] = ft_summary

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(ft_df["eta_final"], bins=40)
    ax.set_xlabel("eta (final)")
    ax.set_ylabel("count")
    ax.set_title(f"Fine-tuning scan: distribution of eta (final), n={len(ft_df)}")
    fig.tight_layout()
    fig.savefig(f"{PLOT_DIR}/fine_tuning_eta_histogram.png", dpi=140)
    plt.close(fig)

    # ---------------------------------------------------------------
    # Conclusions
    # ---------------------------------------------------------------
    note("Generating conclusions")
    answers = answer_conclusion_questions(evidence)
    conclusions_md = render_conclusions_markdown(answers)

    evidence["_log"] = log
    evidence["_conclusions_markdown"] = conclusions_md
    evidence["_experiment_results_for_docs"] = {
        "exp1": res1, "exp2": res2, "exp3": res3, "exp4": res4,
        "exp9": res9, "exp10": res10, "exp11": res11, "exp12": res12,
        "r_sweep_df": r_sweep_df, "e_sweep_df": e_sweep_df, "s_sweep_df": s_sweep_df,
        "p_sweep_df": p_sweep_df, "a_sweep_df": a_sweep_df, "gallery_df": gallery_df,
        "ft_df": ft_df,
    }

    return evidence

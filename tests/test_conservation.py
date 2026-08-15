import pytest

from src.analysis.conservation_checks import (
    closed_energy_conservation_residual,
    dark_number_conservation_when_b_violation_off,
    summarize_conservation,
)
from src.simulation.model_a import build_model_a
from src.simulation.model_b import build_model_b
from src.simulation.runner import run_simulation


def test_energy_conservation_holds_for_model_a():
    cfg = build_model_a()
    res = run_simulation(cfg)
    resid = closed_energy_conservation_residual(res.df, cfg.physics)
    scale = max(res.df["E_rad"].abs().max(), 1.0)
    assert resid.abs().max() / scale < 1e-8


def test_energy_conservation_holds_for_model_b_with_unequal_coupling():
    cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02)
    res = run_simulation(cfg)
    resid = closed_energy_conservation_residual(res.df, cfg.physics)
    scale = max(res.df["E_rad"].abs().max(), res.df["N_matter"].abs().max(), 1.0)
    assert resid.abs().max() / scale < 1e-8


def test_energy_conservation_holds_with_dark_self_annihilation():
    cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02, sigma_DD=0.01)
    res = run_simulation(cfg)
    resid = closed_energy_conservation_residual(res.df, cfg.physics)
    scale = max(res.df["E_rad"].abs().max(), res.df["N_matter"].abs().max(), 1.0)
    assert resid.abs().max() / scale < 1e-8


def test_dark_number_conservation_when_b_violation_disabled():
    cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02,
                         baryon_number_violation_enabled=False)
    res = run_simulation(cfg)
    leak = dark_number_conservation_when_b_violation_off(res.df, cfg.physics)
    assert leak.abs().max() == pytest.approx(0.0, abs=1e-12)


def test_summarize_conservation_reports_none_when_b_violation_enabled():
    cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02)
    res = run_simulation(cfg)
    summary = summarize_conservation(res.df, cfg.physics)
    assert summary["max_abs_b_violation_leak"] is None


def test_no_negative_populations():
    cfg = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02, sigma_DD=0.01)
    res = run_simulation(cfg)
    for col in ("N_matter", "N_antimatter", "N_dark", "E_rad"):
        assert (res.df[col] >= -1e-6).all(), f"{col} went significantly negative"

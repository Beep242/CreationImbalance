"""
Time-series and parameter-sweep plotting.

All functions save a PNG to the given path and return that path. Uses
matplotlib only (no seaborn dependency). Kept deliberately simple:
functions take already-computed DataFrames/arrays, no physics logic here.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _finish(fig, path: str) -> str:
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_timeseries(df: pd.DataFrame, y_col: str, path: str, title: str,
                     ylabel: str, x_col: str = "t", xlabel: str = "time t (model units)",
                     yscale: str = "linear", label: str | None = None) -> str:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(df[x_col], df[y_col], lw=2, label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_yscale(yscale)
    ax.grid(alpha=0.3)
    if label:
        ax.legend()
    return _finish(fig, path)


def plot_multi_timeseries(df: pd.DataFrame, y_cols: list, labels: list, path: str,
                           title: str, ylabel: str, x_col: str = "t",
                           xlabel: str = "time t (model units)", yscale: str = "linear") -> str:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for col, lab in zip(y_cols, labels):
        ax.plot(df[x_col], df[col], lw=2, label=lab)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_yscale(yscale)
    ax.grid(alpha=0.3)
    ax.legend()
    return _finish(fig, path)


def plot_model_comparison(df_a: pd.DataFrame, df_b: pd.DataFrame, y_col: str, path: str,
                           title: str, ylabel: str, yscale: str = "linear") -> str:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(df_a["t"], df_a[y_col], lw=2, label="Model A (baseline)", linestyle="--")
    ax.plot(df_b["t"], df_b[y_col], lw=2, label="Model B (pre-Big-Bang dark sector)")
    ax.set_xlabel("time t (model units)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_yscale(yscale)
    ax.grid(alpha=0.3)
    ax.legend()
    return _finish(fig, path)


def plot_sweep(x_values, y_values, path: str, title: str, xlabel: str, ylabel: str,
                xscale: str = "linear", yscale: str = "linear",
                mark_zero: bool = True) -> str:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(x_values, y_values, marker="o", lw=1.5)
    if mark_zero:
        ax.axhline(0.0, color="gray", lw=1, linestyle=":")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.grid(alpha=0.3)
    return _finish(fig, path)

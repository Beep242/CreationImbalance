"""Heatmaps for two-parameter sweeps of eta (or any scalar outcome)."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_heatmap(
    x_values, y_values, z_grid, path: str, title: str, xlabel: str, ylabel: str,
    zlabel: str = "eta (final)", cmap: str = "RdBu_r", vmin: float | None = -1.0,
    vmax: float | None = 1.0,
) -> str:
    """
    z_grid must have shape (len(y_values), len(x_values)) -- i.e. rows are
    y, columns are x, matching numpy meshgrid/imshow conventions.
    """
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    im = ax.imshow(
        z_grid, aspect="auto", origin="lower", cmap=cmap, vmin=vmin, vmax=vmax,
        extent=[0, len(x_values) - 1, 0, len(y_values) - 1],
    )
    ax.set_xticks(np.arange(len(x_values)))
    ax.set_xticklabels([f"{v:.3g}" for v in x_values], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(y_values)))
    ax.set_yticklabels([f"{v:.3g}" for v in y_values])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(zlabel)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path

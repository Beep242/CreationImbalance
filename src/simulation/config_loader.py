"""
Load Model A / Model B parameter sets from YAML files in configs/, for
reproducibility and so parameter sets don't have to live only as Python
literals inside src/simulation/run_experiments.py.

TransitionType is passed as its string value in YAML (e.g. "bounce") and
converted to the enum here.
"""

from __future__ import annotations

import yaml

from ..transition.transition import TransitionType
from .model_a import build_model_a
from .model_b import build_model_b
from .runner import SimulationConfig


def load_model_a_config(path: str) -> SimulationConfig:
    with open(path, "r", encoding="utf-8") as f:
        params = yaml.safe_load(f) or {}
    return build_model_a(**params)


def load_model_b_config(path: str) -> SimulationConfig:
    with open(path, "r", encoding="utf-8") as f:
        params = yaml.safe_load(f) or {}
    if "transition_type" in params:
        params["transition_type"] = TransitionType(params["transition_type"])
    return build_model_b(**params)

"""Thin wrapper kept for the legacy ``utils/`` Gradio scaffold.

The single source of truth for graph topology lives in ``configs/graph.yaml``
and ``pangpang_pathfinder.route``. Prefer importing from there in new code.
"""
from __future__ import annotations

from pangpang_pathfinder.config import load_graph_config
from pangpang_pathfinder.route.graph import CampusGraph
from pangpang_pathfinder.route.planner import Route, plan_route  # noqa: F401

_GRAPH: CampusGraph | None = None


def get_graph() -> CampusGraph:
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = CampusGraph.from_config(load_graph_config())
    return _GRAPH

from __future__ import annotations

from pathlib import Path

import networkx as nx


def build_graph(graph_cfg: dict) -> nx.Graph:
    nodes = graph_cfg.get("nodes", [])
    edges = graph_cfg.get("edges", [])
    if not nodes:
        raise ValueError("graph.yaml: nodes must not be empty")
    g = nx.Graph()
    for node in nodes:
        g.add_node(node)
    for edge in edges:
        src, dst = edge["src"], edge["dst"]
        if src not in g or dst not in g:
            raise ValueError(f"Invalid edge ({src}, {dst}): node missing")
        g.add_edge(src, dst, weight=float(edge.get("weight", 1.0)), clip_path=edge.get("clip_path"))
    return g


def extract_clips_for_path(g: nx.Graph, node_path: list[str]) -> tuple[list[str], list[str]]:
    clips: list[str] = []
    missing: list[str] = []
    for i in range(len(node_path) - 1):
        src, dst = node_path[i], node_path[i + 1]
        edge = g.get_edge_data(src, dst) or {}
        clip = edge.get("clip_path")
        if clip and Path(clip).exists():
            clips.append(clip)
        else:
            missing.append(f"{src}->{dst}")
    return clips, missing

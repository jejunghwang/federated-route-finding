from __future__ import annotations

import networkx as nx

from pangpang_pathfinder.route.graph import extract_clips_for_path


def plan_route(g: nx.Graph, src_node: str, dst_node: str) -> dict:
    if src_node not in g:
        raise ValueError(f"Source node not found: {src_node}")
    if dst_node not in g:
        raise ValueError(f"Destination node not found: {dst_node}")
    node_path = nx.shortest_path(g, source=src_node, target=dst_node, weight="weight")
    clips, missing = extract_clips_for_path(g, node_path)
    return {"node_path": node_path, "clips": clips, "missing_clips": missing}

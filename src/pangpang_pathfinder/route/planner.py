from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx

from .graph import CampusGraph, Edge


@dataclass(frozen=True)
class Route:
    nodes: list[str] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.nodes

    @property
    def hops(self) -> int:
        return len(self.edges)


def plan_route(graph: CampusGraph, start_id: str, goal_id: str) -> Route:
    """Reconstruct the shortest path from precomputed Floyd-Warshall tables.

    - ``start == goal``: ``Route(nodes=[start], edges=[])``
    - no path between components: empty ``Route`` (no exception)
    - unknown id: ``ValueError``
    """
    if not graph.has_node(start_id):
        raise ValueError(f"unknown start node: {start_id}")
    if not graph.has_node(goal_id):
        raise ValueError(f"unknown goal node: {goal_id}")
    if start_id == goal_id:
        return Route(nodes=[start_id], edges=[])

    try:
        path = nx.reconstruct_path(start_id, goal_id, graph.fw_predecessors)
    except KeyError:
        return Route(nodes=[], edges=[])
    if not path:
        return Route(nodes=[], edges=[])

    edges = [Edge(a, b) for a, b in zip(path, path[1:])]
    return Route(nodes=list(path), edges=edges)

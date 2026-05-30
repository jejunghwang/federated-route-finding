from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable

import networkx as nx


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    building: str
    is_indoor: bool


@dataclass(frozen=True)
class Edge:
    a: str
    b: str

    def reversed(self) -> "Edge":
        return Edge(self.b, self.a)


class CampusGraph:
    """Undirected campus graph backed by configs/graph.yaml.

    All-pairs shortest paths are precomputed at construction time via
    Floyd-Warshall, so route lookups in :func:`plan_route` are O(path_length)
    matrix reconstructions rather than fresh searches.
    """

    def __init__(self, nx_graph: nx.Graph, nodes: dict[str, Node]) -> None:
        self._g = nx_graph
        self._nodes = nodes
        self._name_to_id = {node.name: node_id for node_id, node in nodes.items()}
        self._fw_pred, self._fw_dist = nx.floyd_warshall_predecessor_and_distance(nx_graph)

    @classmethod
    def from_config(cls, config: dict) -> "CampusGraph":
        if "version" not in config:
            raise ValueError("graph config missing required field: version")

        raw_nodes = config.get("nodes") or []
        raw_edges = config.get("edges") or []

        nodes: dict[str, Node] = {}
        seen_names: dict[str, str] = {}
        for entry in raw_nodes:
            node_id = entry["id"]
            if node_id in nodes:
                raise ValueError(f"duplicate node id: {node_id}")
            name = entry["name"]
            if name in seen_names:
                raise ValueError(
                    f"duplicate node name: {name!r} used by {seen_names[name]!r} and {node_id!r}"
                )
            seen_names[name] = node_id
            nodes[node_id] = Node(
                id=node_id,
                name=name,
                building=entry.get("building", ""),
                is_indoor=bool(entry.get("is_indoor", False)),
            )

        g = nx.Graph()
        for node_id in nodes:
            g.add_node(node_id)

        seen_edges: set[frozenset[str]] = set()
        for raw in raw_edges:
            a, b = raw[0], raw[1]
            if a == b:
                raise ValueError(f"self-loop is not allowed: ({a}, {b})")
            if a not in nodes:
                raise ValueError(f"edge endpoint not in nodes: {a}")
            if b not in nodes:
                raise ValueError(f"edge endpoint not in nodes: {b}")
            key = frozenset((a, b))
            if key in seen_edges:
                raise ValueError(f"duplicate edge: ({a}, {b})")
            seen_edges.add(key)
            g.add_edge(a, b)

        isolated = [n for n in g.nodes if g.degree(n) == 0]
        if isolated:
            warnings.warn(
                f"graph has isolated nodes (no edges): {sorted(isolated)}",
                stacklevel=2,
            )

        return cls(g, nodes)

    @property
    def node_ids(self) -> list[str]:
        return list(self._nodes.keys())

    @property
    def node_names(self) -> list[str]:
        return [self._nodes[i].name for i in self._nodes]

    def get_node(self, node_id: str) -> Node:
        if node_id not in self._nodes:
            raise ValueError(f"unknown node id: {node_id}")
        return self._nodes[node_id]

    def id_by_name(self, name: str) -> str:
        if name not in self._name_to_id:
            raise ValueError(f"unknown node name: {name!r}")
        return self._name_to_id[name]

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def neighbors(self, node_id: str) -> list[str]:
        if node_id not in self._nodes:
            raise ValueError(f"unknown node id: {node_id}")
        return list(self._g.neighbors(node_id))

    @property
    def nx(self) -> nx.Graph:
        return self._g

    @property
    def fw_predecessors(self) -> dict:
        return self._fw_pred

    @property
    def fw_distances(self) -> dict:
        return self._fw_dist


def validate_classes_subset(graph: CampusGraph, class_ids: Iterable[str]) -> None:
    missing = [cid for cid in class_ids if not graph.has_node(cid)]
    if missing:
        raise ValueError(
            f"classifier class ids not found in graph nodes: {missing}"
        )

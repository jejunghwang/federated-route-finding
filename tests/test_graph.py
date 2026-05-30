import pytest

from pangpang_pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pangpang_pathfinder.route.graph import (
    CampusGraph,
    Edge,
    validate_classes_subset,
)
from pangpang_pathfinder.route.planner import plan_route


@pytest.fixture(scope="module")
def graph() -> CampusGraph:
    return CampusGraph.from_config(load_graph_config())


def test_graph_loads(graph):
    assert len(graph.node_ids) >= 15
    assert "bima_2f_corridor" in graph.node_ids
    assert graph.get_node("bima_2f_corridor").name == "비마관 2층 복도"


def test_self_path(graph):
    r = plan_route(graph, "bima_2f_corridor", "bima_2f_corridor")
    assert r.nodes == ["bima_2f_corridor"]
    assert r.edges == []


def test_one_hop(graph):
    r = plan_route(graph, "bima_2f_corridor", "bima_101_front")
    assert r.nodes == ["bima_2f_corridor", "bima_101_front"]
    assert r.edges == [Edge("bima_2f_corridor", "bima_101_front")]


def test_multi_hop(graph):
    r = plan_route(graph, "bima_101_front", "centennial_2f_lobby")
    assert r.nodes[0] == "bima_101_front"
    assert r.nodes[-1] == "centennial_2f_lobby"
    assert r.hops >= 4
    for e in r.edges:
        assert e.b in graph.neighbors(e.a)


def test_unknown_node_raises(graph):
    with pytest.raises(ValueError):
        plan_route(graph, "not_a_node", "bima_2f_corridor")


def test_no_self_loops_in_config():
    cfg = load_graph_config()
    for a, b in cfg["edges"]:
        assert a != b


def test_classes_subset_of_graph(graph):
    classes = load_classes_map("configs/classes.yaml")
    if not classes:
        pytest.skip("configs/classes.yaml is empty")
    validate_classes_subset(graph, classes.keys())

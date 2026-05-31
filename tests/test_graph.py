import pytest

from pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pathfinder.route.graph import (
    CampusGraph,
    Edge,
    validate_classes_subset,
)
from pathfinder.route.planner import plan_route


@pytest.fixture(scope="module")
def graph() -> CampusGraph:
    return CampusGraph.from_config(load_graph_config())


def test_graph_loads(graph):
    assert len(graph.node_ids) == 8
    assert "main_gate" in graph.node_ids
    assert graph.get_node("main_gate").name == "정문"


def test_self_path(graph):
    r = plan_route(graph, "main_gate", "main_gate")
    assert r.nodes == ["main_gate"]
    assert r.edges == []


def test_one_hop(graph):
    r = plan_route(graph, "main_gate", "central_plaza")
    assert r.nodes == ["main_gate", "central_plaza"]
    assert r.edges == [Edge("main_gate", "central_plaza")]


def test_multi_hop(graph):
    r = plan_route(graph, "main_gate", "saebit")
    assert r.nodes[0] == "main_gate"
    assert r.nodes[-1] == "saebit"
    assert r.hops >= 3
    for e in r.edges:
        assert e.b in graph.neighbors(e.a)


def test_unknown_node_raises(graph):
    with pytest.raises(ValueError):
        plan_route(graph, "not_a_node", "main_gate")


def test_no_self_loops_in_config():
    cfg = load_graph_config()
    for a, b in cfg["edges"]:
        assert a != b


def test_classes_subset_of_graph(graph):
    classes = load_classes_map("configs/classes.yaml")
    if not classes:
        pytest.skip("configs/classes.yaml is empty")
    validate_classes_subset(graph, classes.keys())

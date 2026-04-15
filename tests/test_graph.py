from pangpang_pathfinder.config import load_yaml
from pangpang_pathfinder.route.graph import build_graph
from pangpang_pathfinder.route.planner import plan_route


def test_graph_build_and_route():
    graph = build_graph(load_yaml("configs/graph.yaml"))
    route = plan_route(graph, "bima_2f_corridor", "bima_101_front")
    assert route["node_path"][0] == "bima_2f_corridor"
    assert route["node_path"][-1] == "bima_101_front"


def test_missing_node_raises():
    graph = build_graph(load_yaml("configs/graph.yaml"))
    try:
        plan_route(graph, "not_exist", "bima_101_front")
    except ValueError as exc:
        assert "Source node not found" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing node")

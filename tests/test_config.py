from pathfinder.config import load_classes_map, load_graph_config, load_yaml
from pathfinder.app.simple_demo import _resolve_indoor_chain, _resolve_indoor_route_entry
from pathfinder.route.class_mapping import load_class_route_map, validate_class_routes
from pathfinder.route.graph import CampusGraph


def test_classes_config_has_entries():
    classes = load_classes_map("configs/classes.yaml")
    assert len(classes) == 8
    assert "main_gate" in classes


def test_clients_config_has_four_members():
    clients = load_yaml("configs/clients.yaml")["clients"]
    assert set(clients.keys()) == {"hwang", "shin", "jung", "kim"}


def test_class_route_map_covers_current_checkpoint_classes():
    route_map = load_class_route_map("configs/class_route_map.yaml")
    expected_classes = {
        "80_310_back",
        "80_310_front",
        "80_jiphyeonjeon",
        "80_reading_room_1",
        "80_reading_room_3",
        "chambit_B1",
        "chambit_B101",
        "chambit_clock",
        "chambit_park",
        "chambit_smoking",
    }
    assert set(route_map) == expected_classes


def test_class_route_map_targets_graph_nodes():
    graph = CampusGraph.from_config(load_graph_config())
    route_map = load_class_route_map("configs/class_route_map.yaml")
    validate_class_routes(graph, set(route_map), route_map)


def test_current_checkpoint_special_locations_route_to_expected_anchor():
    route_map = load_class_route_map("configs/class_route_map.yaml")
    assert route_map["chambit_smoking"].route_node == "bima_smoking"
    assert route_map["80_310_front"].indoor_target == "central_library_310_front"


def test_central_library_310_detail_uses_existing_clip_from_main_gate():
    graph = CampusGraph.from_config(load_graph_config())
    chain = _resolve_indoor_chain("central_library", "central_library_310_front")

    assert [path.name for path in chain] == ["main_gate__central_library_301_front.mp4"]
    assert _resolve_indoor_route_entry(
        graph,
        "central_library",
        "central_library_310_front",
    ) == "main_gate"

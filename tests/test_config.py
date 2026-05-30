from pangpang_pathfinder.config import load_classes_map, load_yaml


def test_classes_config_has_entries():
    classes = load_classes_map("configs/classes.yaml")
    assert len(classes) >= 12
    assert "bima_2f_corridor" in classes


def test_clients_config_has_four_members():
    clients = load_yaml("configs/clients.yaml")["clients"]
    assert set(clients.keys()) == {"hwang", "shin", "jung", "kim"}

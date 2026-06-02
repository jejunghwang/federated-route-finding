from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pathfinder.config import load_yaml
from pathfinder.route.graph import CampusGraph


@dataclass(frozen=True)
class ClassRoute:
    class_slug: str
    route_node: str
    indoor_target: str | None = None
    display_name_ko: str | None = None


def load_class_route_map(path: str | Path = "configs/class_route_map.yaml") -> dict[str, ClassRoute]:
    config = load_yaml(path)
    raw_routes = config.get("class_routes", {})
    if not isinstance(raw_routes, dict):
        raise ValueError("class_route_map missing object field: class_routes")

    routes = {}
    for class_slug, item in raw_routes.items():
        if not isinstance(item, dict):
            raise ValueError(f"Invalid class route entry: {class_slug}")
        route_node = item.get("route_node")
        if not isinstance(route_node, str) or not route_node:
            raise ValueError(f"Class route missing route_node: {class_slug}")
        indoor_target = item.get("indoor_target")
        if indoor_target is not None and not isinstance(indoor_target, str):
            raise ValueError(f"Class route has invalid indoor_target: {class_slug}")
        display_name_ko = item.get("display_name_ko")
        if display_name_ko is not None and not isinstance(display_name_ko, str):
            raise ValueError(f"Class route has invalid display_name_ko: {class_slug}")
        routes[class_slug] = ClassRoute(
            class_slug=class_slug,
            route_node=route_node,
            indoor_target=indoor_target,
            display_name_ko=display_name_ko,
        )
    return routes


def validate_class_routes(
    graph: CampusGraph,
    class_ids: list[str] | set[str] | dict,
    class_routes: dict[str, ClassRoute],
) -> None:
    missing = [
        class_id
        for class_id in class_ids
        if not graph.has_node(class_id) and class_id not in class_routes
    ]
    if missing:
        raise ValueError(f"class ids cannot be mapped to route graph nodes: {missing}")

    bad_targets = [
        route.class_slug
        for route in class_routes.values()
        if not graph.has_node(route.route_node)
    ]
    if bad_targets:
        raise ValueError(f"class_route_map targets unknown graph nodes: {bad_targets}")


def resolve_route_node(
    class_id: str,
    graph: CampusGraph,
    class_routes: dict[str, ClassRoute],
) -> ClassRoute:
    mapped = class_routes.get(class_id)
    if mapped is not None:
        if not graph.has_node(mapped.route_node):
            raise ValueError(f"class route target is not in graph: {class_id} -> {mapped.route_node}")
        return mapped
    if graph.has_node(class_id):
        return ClassRoute(class_slug=class_id, route_node=class_id)
    raise ValueError(f"class id cannot be mapped to a route graph node: {class_id}")

#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pathfinder.inference import infer_single_image
from pathfinder.models.classifier import load_checkpoint
from pathfinder.route.class_mapping import (
    load_class_route_map,
    resolve_route_node,
    validate_class_routes,
)
from pathfinder.route.graph import CampusGraph
from pathfinder.route.planner import plan_route
from pathfinder.route.stitching import stitch_clips


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-photo", required=True)
    parser.add_argument("--destination-class")
    parser.add_argument("--peer-photo")
    parser.add_argument("--checkpoint", default="outputs/checkpoints/global_merged.pt")
    parser.add_argument("--graph-config", default="configs/graph.yaml")
    args = parser.parse_args()

    classes_map = load_classes_map("configs/classes.yaml")
    ckpt = load_checkpoint(args.checkpoint)
    class_to_idx = ckpt["class_to_idx"]
    model_name = ckpt["model_name"]

    current = infer_single_image(args.current_photo, args.checkpoint, model_name, class_to_idx)
    src = current["predicted_class"]

    if args.peer_photo:
        peer = infer_single_image(args.peer_photo, args.checkpoint, model_name, class_to_idx)
        dst = peer["predicted_class"]
    else:
        if not args.destination_class:
            raise ValueError("Provide --destination-class or --peer-photo")
        dst = args.destination_class

    graph = CampusGraph.from_config(load_graph_config(args.graph_config))
    class_routes = load_class_route_map()
    validate_class_routes(graph, class_to_idx.keys(), class_routes)
    src_route = resolve_route_node(src, graph, class_routes)
    dst_route = resolve_route_node(dst, graph, class_routes)

    route = plan_route(graph, src_route.route_node, dst_route.route_node)
    node_path = list(route.nodes)
    edges = route.edges
    if edges:
        Path("outputs/reports").mkdir(parents=True, exist_ok=True)
        full_stitched = stitch_clips(edges, output_path="outputs/reports/stitched_route.mp4")
        stitch_msg = "stitched" if full_stitched else "no clip available for the route"
    else:
        full_stitched, stitch_msg = None, "no clip available for the route"

    payload = {
        "predicted_class": src,
        "predicted_class_ko": classes_map.get(src, {}).get("display_name_ko", src),
        "source_route_node": src_route.route_node,
        "destination_class": dst,
        "destination_route_node": dst_route.route_node,
        "top3_predictions": current["top3"],
        "node_path": node_path,
        "edge_count": len(edges),
        "stitched_video_path": full_stitched,
        "stitch_status": stitch_msg,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

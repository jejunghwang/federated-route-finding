from __future__ import annotations

from collections import OrderedDict

import torch


def merge_state_dicts(weighted_state_dicts: list[tuple[dict, float]], include_batchnorm_buffers: bool = True) -> OrderedDict:
    total_weight = sum(w for _, w in weighted_state_dicts)
    if total_weight <= 0:
        raise ValueError("Total merge weight must be positive")

    keys = weighted_state_dicts[0][0].keys()
    merged = OrderedDict()
    for key in keys:
        if not include_batchnorm_buffers and ("running_mean" in key or "running_var" in key or "num_batches_tracked" in key):
            merged[key] = weighted_state_dicts[0][0][key].clone()
            continue
        acc = None
        for state_dict, weight in weighted_state_dicts:
            tensor = state_dict[key].float() * (weight / total_weight)
            acc = tensor if acc is None else acc + tensor
        merged[key] = acc.type_as(weighted_state_dicts[0][0][key])
    return merged

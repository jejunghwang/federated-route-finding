"""Optional extension point for future Flower-based simulation.

This module is intentionally minimal so that MVP remains runnable without Flower.
"""


def run_flower_simulation_stub() -> str:
    return "Flower simulation is optional and not enabled in MVP. Use checkpoint merge workflow."

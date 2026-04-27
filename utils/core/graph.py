"""Dummy graph — 추후 실제 graph + BFS로 교체."""


def shortest_path(start: str, goal: str) -> list[str]:
    """node 이름 두 개를 받아 경로(노드 이름 리스트) 반환.
    Dummy: start, 중앙광장, goal 만 끼워 반환. 동일 노드면 [start] 반환."""
    if start == goal:
        return [start]
    if "중앙광장" in (start, goal):
        return [start, goal]
    return [start, "중앙광장", goal]

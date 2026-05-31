# route/ — 그래프 + 최단경로 + 영상 stitching

캠퍼스 그래프 정의/조회와 최단경로 계산. 본 모듈이 단일 진실 (single source of truth).

## 모듈

```
파일             노출                                                       비고
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
graph.py         CampusGraph, Node, Edge, validate_classes_subset           networkx 무방향 그래프 + Floyd-Warshall precompute
planner.py       plan_route, Route                                          F-W 행렬 기반 O(path_length) 경로 복원
stitching.py     stitch_clips, stitch_clips_ffmpeg, build_concat_file       edge → mp4 매칭 + ffmpeg concat 헬퍼
```

## Floyd-Warshall 설계

`CampusGraph.__init__`에서 `nx.floyd_warshall_predecessor_and_distance(g)`로 **all-pairs predecessor/distance 행렬을 1회 precompute**해 보관. 이후 쿼리는:

```python
nx.reconstruct_path(start_id, goal_id, graph.fw_predecessors)
```

으로 O(path_length) 복원. 새 탐색 안 함.

### BFS와 비교

- 무방향 + unweighted 그래프에서는 결과 동일
- F-W 선택 이유:
  1. 데모 응답 즉시 (precompute 1회 후 lookup)
  2. edge weight 도입 시 코드 변경 0 (`weight=` 인자 없는 reconstruct_path 그대로)
  3. distance matrix를 시각화 자산으로 활용 가능
  4. V=20 규모에선 8000 연산이라 startup 비용 무시 가능

## 그래프 데이터

`configs/graph.yaml`이 단일 소스. 노드/엣지 추가 시 yaml만 수정 — 코드 변경 0.

### 노드 추가 예시

```yaml
nodes:
  ...
  - id: student_hall_1f
    name: 학생회관 1층
    building: 학생회관
    is_indoor: true

edges:
  ...
  - [outdoor_central_plaza, student_hall_1f]
```

자동 반영되는 곳:
- 양쪽 데모 드롭다운
- F-W 행렬 재계산
- 분류기 후보 노드 (utils dummy)
- `data/route_clips/student_hall_1f__outdoor_central_plaza.mp4` 매칭

## API 시그니처

```python
@dataclass(frozen=True)
class Node:
    id: str
    name: str
    building: str
    is_indoor: bool

@dataclass(frozen=True)
class Edge:
    a: str
    b: str
    def reversed(self) -> "Edge": ...

class CampusGraph:
    @classmethod
    def from_config(cls, config: dict) -> "CampusGraph": ...

    @property
    def node_ids(self) -> list[str]: ...
    @property
    def node_names(self) -> list[str]: ...
    @property
    def fw_predecessors(self) -> dict: ...
    @property
    def fw_distances(self) -> dict: ...

    def get_node(self, node_id: str) -> Node: ...
    def id_by_name(self, name: str) -> str: ...
    def has_node(self, node_id: str) -> bool: ...
    def neighbors(self, node_id: str) -> list[str]: ...

@dataclass(frozen=True)
class Route:
    nodes: list[str]
    edges: list[Edge]
    @property
    def is_empty(self) -> bool: ...
    @property
    def hops(self) -> int: ...

def plan_route(graph: CampusGraph, start_id: str, goal_id: str) -> Route:
    """F-W lookup. start==goal → [start]. disconnected → empty Route. unknown id → ValueError."""
```

## stitching

`stitch_clips(edges, clips_dir=...)`:
- 첫 매칭되는 `<a>__<b>.mp4` 또는 `<b>__<a>.mp4` 1개 path 반환 (placeholder)
- 매칭 없거나 `edges=[]`면 None
- 절대경로 인자 명시 권장 (cwd 의존 회피)

`stitch_clips_ffmpeg(clips, output_path)`:
- 진짜 ffmpeg `-f concat -c copy` 호출
- 현재 데모에선 호출 안 함 (follow-up PR)

## 검증

```bash
pytest tests/test_graph.py -v
```

7개 테스트: graph 로딩, self path, 1-hop, multi-hop, unknown id, no self-loops, classes ⊆ nodes.

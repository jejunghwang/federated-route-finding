# tests/ — 경량 CPU 테스트

pytest 기반. CPU에서 빠르게 돌도록 작성 — GPU/대용량 데이터 의존 X.

## 실행

```bash
pytest -v                  # 전체
pytest tests/test_graph.py -v   # 단일 파일
pytest -k "multi_hop"      # 이름 패턴
```

`pyproject.toml`에 pytest 설정 포함 (rootdir 자동 인식).

## 파일별 범위

```
파일                       검증 대상
─────────────────────────────────────────────────────────────────────────────────────────────────────
test_graph.py              CampusGraph 로딩, plan_route 동작 (self/1-hop/multi-hop/disconnected/unknown), classes ⊆ nodes
test_config.py             yaml 로더 (load_graph_config, load_classes_map)
test_model_forward.py      모델 factory + forward shape sanity
```

## 새 테스트 추가 가이드

- 픽스처는 `@pytest.fixture(scope="module")`로 graph/config 캐싱 (init 시 F-W precompute 비용)
- 한국어 노드명 검증은 `configs/graph.yaml` 변경에 취약하므로 id 우선
- 새 노드/엣지 추가 시 `test_graph.py`의 `assert len(graph.node_ids) >= N` 임계값 갱신

## 검증된 시나리오

`pytest tests/test_graph.py -v` (7/7 통과 기준):
- graph 로딩, self path (hops=0)
- 1-hop / multi-hop (≥4) 경로 일관성
- 미존재 노드 → ValueError
- self-loop 없음 (config 검증)
- classes.yaml의 모든 slug ∈ graph.yaml의 id

"""Dummy classifier — 추후 실제 모델로 교체."""
from PIL import Image

NODE_NAMES = [
    "정문",
    "중앙광장",
    "비마관 1층 로비",
    "비마관 2층 복도",
    "새빛관 로비",
    "새빛관 4층 학과사무실",
    "화도관 1층 입구",
    "화도관 3층 강의실",
    "옥의관 1층 입구",
    "도서관 정문",
    "기숙사 입구",
    "아이스링크장 입구",
]


def classify(image: Image.Image) -> tuple[str, float]:
    """이미지를 받아 (node_name, confidence) 반환.
    Dummy: NODE_NAMES 중 hash 기반으로 deterministic 선택."""
    import hashlib
    h = int(hashlib.md5(image.tobytes()).hexdigest(), 16)
    name = NODE_NAMES[h % len(NODE_NAMES)]
    conf = 0.7 + (h % 30) / 100  # 0.70 ~ 0.99
    return name, round(conf, 2)

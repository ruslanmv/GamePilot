from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class DetectorConfig:
    kind: str = "mock"


class BaseDetector:
    def detect(self, frame: Any) -> dict:
        raise NotImplementedError


class MockDetector(BaseDetector):
    def detect(self, frame: Any) -> dict:
        _ = frame
        return {
            "hp": 72,
            "enemy_near": False,
            "loot_visible": False,
            "npc_visible": False,
            "quest_marker": "north",
            "stuck": False,
            "quest_changed": False,
        }


class OpenCVDetector(BaseDetector):
    def detect(self, frame: Any) -> dict:
        arr = np.asarray(frame)
        brightness = float(arr.mean()) if arr.size else 0.0
        return {
            "hp": max(5, min(100, int(100 - brightness / 3))),
            "enemy_near": brightness < 60,
            "loot_visible": brightness > 180,
            "npc_visible": 90 < brightness < 150,
            "quest_marker": "north",
            "stuck": False,
            "quest_changed": False,
        }


class YOLODetector(BaseDetector):
    def detect(self, frame: Any) -> dict:
        return OpenCVDetector().detect(frame)


def create_detector(kind: str = "mock") -> BaseDetector:
    if kind == "opencv":
        return OpenCVDetector()
    if kind == "yolo":
        return YOLODetector()
    return MockDetector()


class Detector(MockDetector):
    pass

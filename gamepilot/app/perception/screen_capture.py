from pathlib import Path
from typing import Any

import numpy as np


def capture_screen() -> Any:
    return np.zeros((480, 640, 3), dtype=np.uint8)


def capture_video_frame(video_path: str, frame_idx: int = 0) -> Any:
    import cv2

    if not Path(video_path).exists():
        raise FileNotFoundError(video_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError(f"Could not open video: {video_path}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not read frame {frame_idx} from {video_path}")
    return frame


def iter_video_frames(video_path: str, every: int = 30, max_frames: int = 10):
    import cv2

    if not Path(video_path).exists():
        raise FileNotFoundError(video_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError(f"Could not open video: {video_path}")

    frame_idx = 0
    yielded = 0
    while yielded < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        yield frame_idx, frame
        frame_idx += every
        yielded += 1
    cap.release()

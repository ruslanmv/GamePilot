"""
Video Observer Environment
Analyzes pre-recorded gameplay videos
"""
from typing import Optional, Iterator
import numpy as np
from datetime import datetime
from .base import BaseEnvironment
from gamepilot.core import Observation, Action, WorldState


class VideoObserver(BaseEnvironment):
    """
    Environment that reads from video files.
    
    Used for:
    - Analyzing gameplay recordings
    - Creating training datasets
    - Generating guides from playthroughs
    - Research and benchmarking
    """
    
    def __init__(self, video_path: str):
        super().__init__(environment_id=f"video:{video_path}")
        self.video_path = video_path
        self.video_capture = None
        self.current_frame_index = 0
        self._init_video()
    
    def _init_video(self):
        """Initialize video capture."""
        try:
            import cv2
            self.video_capture = cv2.VideoCapture(self.video_path)
            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        except ImportError:
            self.video_capture = None
            self.fps = 30
            self.total_frames = 0
    
    def observe(self) -> Observation:
        """Read next frame from video."""
        if self.video_capture:
            ret, frame = self.video_capture.read()
            if not ret:
                # Video ended
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            else:
                frame = frame[:, :, ::-1]  # BGR to RGB
        else:
            # Mock frame
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        obs = Observation(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            frame=frame,
            resolution=frame.shape[:2],
            frame_index=self.current_frame_index,
            metadata={
                "video_path": self.video_path,
                "fps": self.fps,
                "total_frames": self.total_frames
            }
        )
        
        self.current_frame_index += 1
        self.current_observation = obs
        return obs
    
    def get_state(self) -> WorldState:
        """Extract state from video frame."""
        state = WorldState(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            metadata={"source": "video", "frame": self.current_frame_index}
        )
        self.current_state = state
        return state
    
    def execute_action(self, action: Action) -> tuple[Observation, float, bool]:
        """Cannot execute actions in video."""
        raise NotImplementedError("VideoObserver is read-only")
    
    def reset(self) -> Observation:
        """Reset video to beginning."""
        if self.video_capture:
            self.video_capture.set(1, 0)  # CAP_PROP_POS_FRAMES
        self.current_frame_index = 0
        return self.observe()
    
    def close(self):
        """Close video file."""
        if self.video_capture:
            self.video_capture.release()
        self.is_running = False
    
    def iter_frames(self, every: int = 1) -> Iterator[Observation]:
        """Iterate through video frames."""
        frame_count = 0
        while True:
            obs = self.observe()
            if obs.frame is None or obs.frame.sum() == 0:
                break
            if frame_count % every == 0:
                yield obs
            frame_count += 1

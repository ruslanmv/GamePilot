"""
Screen Observer Environment
Observes the screen in real-time
"""
from typing import Optional
import numpy as np
from datetime import datetime

from .base import BaseEnvironment
from gamepilot.core import Observation, Action, WorldState, Entity


class ScreenObserver(BaseEnvironment):
    """
    Environment that observes the screen.
    
    Used for real-time game observation without interaction.
    Compatible with any game running on screen.
    """
    
    def __init__(self, monitor_index: int = 0):
        super().__init__(environment_id="screen_observer")
        self.monitor_index = monitor_index
        self.capture_backend = None
        self._init_capture()
    
    def _init_capture(self):
        """Initialize screen capture backend."""
        try:
            import mss
            self.capture_backend = mss.mss()
        except ImportError:
            # Fallback to mock
            self.capture_backend = None
    
    def observe(self) -> Observation:
        """Capture current screen."""
        if self.capture_backend:
            import mss
            monitor = self.capture_backend.monitors[self.monitor_index + 1]
            screenshot = self.capture_backend.grab(monitor)
            frame = np.array(screenshot)[:, :, :3]  # Remove alpha channel
        else:
            # Mock data
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        obs = Observation(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            frame=frame,
            resolution=frame.shape[:2],
            metadata={"monitor_index": self.monitor_index}
        )
        
        self.current_observation = obs
        return obs
    
    def get_state(self) -> WorldState:
        """
        Get world state from screen observation.
        
        In real implementation, this would use perception pipeline
        to extract state from the screen.
        """
        state = WorldState(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            metadata={"source": "screen_capture"}
        )
        
        self.current_state = state
        return state
    
    def execute_action(self, action: Action) -> tuple[Observation, float, bool]:
        """
        Screen observer is read-only.
        Actions are not executed here.
        """
        raise NotImplementedError(
            "ScreenObserver is read-only. Use CompanionOnly or PrivateSandbox for actions."
        )
    
    def reset(self) -> Observation:
        """Reset (just capture a new frame)."""
        return self.observe()
    
    def close(self):
        """Close screen capture."""
        if self.capture_backend:
            try:
                self.capture_backend.close()
            except:
                pass
        self.is_running = False

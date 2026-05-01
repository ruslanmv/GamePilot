"""
Companion-Only Environment
Chat-based interaction without visual observation
"""
from datetime import datetime
from .base import BaseEnvironment
from gamepilot.core import Observation, Action, WorldState


class CompanionOnly(BaseEnvironment):
    """
    Environment for companion chat without visual observation.
    
    User manually provides game state, companion gives advice.
    Safest mode - no screen capture, no automated actions.
    """
    
    def __init__(self):
        super().__init__(environment_id="companion_only")
        self.manual_state = {}
    
    def set_state(self, state_dict: dict):
        """User manually sets current state."""
        self.manual_state = state_dict
    
    def observe(self) -> Observation:
        """Create observation from manual state."""
        obs = Observation(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            text=str(self.manual_state),
            metadata=self.manual_state
        )
        self.current_observation = obs
        return obs
    
    def get_state(self) -> WorldState:
        """Get state from manual input."""
        state = WorldState(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            player_stats=self.manual_state,
            metadata={"mode": "companion_only"}
        )
        self.current_state = state
        return state
    
    def execute_action(self, action: Action) -> tuple[Observation, float, bool]:
        """
        Companion-only mode does not execute actions.
        Only provides advice.
        """
        raise NotImplementedError(
            "CompanionOnly mode is advice-only. No action execution."
        )
    
    def reset(self) -> Observation:
        """Reset manual state."""
        self.manual_state = {}
        return self.observe()
    
    def close(self):
        """Nothing to close."""
        self.is_running = False

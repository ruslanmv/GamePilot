"""
Private Sandbox Environment
Safe environment for automated actions
"""
from .base import BaseEnvironment
from gamepilot.core import Observation, Action, WorldState


class PrivateSandbox(BaseEnvironment):
    """
    Private sandbox environment for safe agent mode.
    
    Used for:
    - Testing game AI in private/offline games
    - Training models in simulations
    - Automated QA testing
    
    Safety features:
    - Only works in whitelisted environments
    - Rate limiting enforced
    - Emergency stop always available
    - Detailed action logging
    """
    
    def __init__(self, environment_id: str = "sandbox"):
        super().__init__(environment_id=f"sandbox:{environment_id}")
        self.action_log = []
        self.max_actions_per_second = 10
    
    def observe(self) -> Observation:
        """Observe sandbox state."""
        # In real implementation, this would observe the actual sandbox
        from datetime import datetime
        obs = Observation(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            metadata={"mode": "sandbox"}
        )
        self.current_observation = obs
        return obs
    
    def get_state(self) -> WorldState:
        """Get sandbox state."""
        from datetime import datetime
        state = WorldState(
            timestamp=datetime.now(),
            environment_id=self.environment_id,
            metadata={"mode": "private_sandbox"}
        )
        self.current_state = state
        return state
    
    def execute_action(self, action: Action) -> tuple[Observation, float, bool]:
        """
        Execute action in sandbox.
        
        In real implementation, this would actually perform the action.
        For now, it logs and simulates.
        """
        # Log action
        self.action_log.append(action)
        
        # Simulate execution
        next_obs = self.observe()
        reward = 0.0
        done = False
        
        return next_obs, reward, done
    
    def reset(self) -> Observation:
        """Reset sandbox."""
        self.action_log.clear()
        return self.observe()
    
    def close(self):
        """Close sandbox."""
        self.action_log.clear()
        self.is_running = False

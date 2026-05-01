"""
Base Environment Interface
All environments inherit from this
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from gamepilot.core import Observation, Action, WorldState, Event


class BaseEnvironment(ABC):
    """
    Universal environment interface.
    
    All environments (games, simulations, VR worlds) inherit from this.
    This ensures GamePilot can work with any interactive environment.
    """
    
    def __init__(self, environment_id: str = "unknown"):
        self.environment_id = environment_id
        self.is_running = False
        self.current_observation: Optional[Observation] = None
        self.current_state: Optional[WorldState] = None
    
    @abstractmethod
    def observe(self) -> Observation:
        """
        Get current observation from environment.
        
        Returns:
            Observation object
        """
        pass
    
    @abstractmethod
    def get_state(self) -> WorldState:
        """
        Get current world state.
        
        Returns:
            WorldState object
        """
        pass
    
    @abstractmethod
    def execute_action(self, action: Action) -> tuple[Observation, float, bool]:
        """
        Execute an action in the environment.
        
        Args:
            action: Action to execute
            
        Returns:
            (next_observation, reward, done)
        """
        pass
    
    @abstractmethod
    def reset(self) -> Observation:
        """
        Reset environment to initial state.
        
        Returns:
            Initial observation
        """
        pass
    
    @abstractmethod
    def close(self):
        """Clean up resources."""
        pass
    
    def start(self):
        """Start the environment."""
        self.is_running = True
    
    def stop(self):
        """Stop the environment."""
        self.is_running = False
    
    def get_info(self) -> Dict[str, Any]:
        """Get environment metadata."""
        return {
            "environment_id": self.environment_id,
            "is_running": self.is_running,
            "type": self.__class__.__name__
        }

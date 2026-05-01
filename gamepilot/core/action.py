"""
Universal Action Model
Represents actions the AI can take in any environment
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum
from datetime import datetime


class ActionType(Enum):
    """Universal action categories."""
    # Input actions
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    GAMEPAD = "gamepad"
    TOUCH = "touch"
    VOICE = "voice"
    
    # Abstract actions
    MOVE = "move"
    INTERACT = "interact"
    ATTACK = "attack"
    USE_ITEM = "use_item"
    COMMUNICATE = "communicate"
    
    # High-level actions
    NAVIGATE_TO = "navigate_to"
    BUILD = "build"
    GATHER = "gather"
    CRAFT = "craft"
    
    # Meta actions
    WAIT = "wait"
    OBSERVE = "observe"
    PLAN = "plan"


@dataclass
class Action:
    """
    Universal action that works across all environments.
    
    Can represent:
    - Keyboard/mouse inputs
    - Abstract game actions
    - High-level plans
    - Voice commands
    """
    
    # Core fields
    action_type: ActionType
    name: str
    
    # Parameters (flexible for any action)
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Execution details
    duration: float = 0.0  # seconds
    priority: int = 0  # Higher = more important
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    environment_id: str = "unknown"
    
    # Safety & validation
    requires_confirmation: bool = False
    risk_level: str = "low"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_type": self.action_type.value,
            "name": self.name,
            "params": self.params,
            "duration": self.duration,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "requires_confirmation": self.requires_confirmation,
            "risk_level": self.risk_level
        }
    
    @classmethod
    def keyboard(cls, key: str, **kwargs) -> 'Action':
        """Create keyboard action."""
        return cls(
            action_type=ActionType.KEYBOARD,
            name=f"press_{key}",
            params={"key": key, **kwargs}
        )
    
    @classmethod
    def mouse(cls, x: int, y: int, button: str = "left", **kwargs) -> 'Action':
        """Create mouse action."""
        return cls(
            action_type=ActionType.MOUSE,
            name=f"click_{button}",
            params={"x": x, "y": y, "button": button, **kwargs}
        )
    
    @classmethod
    def move(cls, direction: str, distance: float = 1.0, **kwargs) -> 'Action':
        """Create movement action."""
        return cls(
            action_type=ActionType.MOVE,
            name=f"move_{direction}",
            params={"direction": direction, "distance": distance, **kwargs}
        )
    
    @classmethod
    def build(cls, structure: str, material: str, **kwargs) -> 'Action':
        """Create building action."""
        return cls(
            action_type=ActionType.BUILD,
            name=f"build_{structure}",
            params={"structure": structure, "material": material, **kwargs}
        )


@dataclass
class ActionSequence:
    """Sequence of actions (a plan)."""
    
    actions: List[Action] = field(default_factory=list)
    sequence_id: str = ""
    description: str = ""
    
    def add(self, action: Action):
        """Add action to sequence."""
        self.actions.append(action)
    
    def get_next(self) -> Optional[Action]:
        """Get next action to execute."""
        return self.actions[0] if self.actions else None
    
    def complete_action(self) -> Optional[Action]:
        """Mark first action as complete and return it."""
        return self.actions.pop(0) if self.actions else None
    
    def __len__(self) -> int:
        return len(self.actions)
    
    def is_empty(self) -> bool:
        return len(self.actions) == 0

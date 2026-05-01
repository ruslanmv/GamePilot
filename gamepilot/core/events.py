"""
Universal Events and Goals Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Types of events that can occur."""
    # Player events
    PLAYER_DAMAGED = "player_damaged"
    PLAYER_HEALED = "player_healed"
    PLAYER_DIED = "player_died"
    
    # Combat events
    ENEMY_SPOTTED = "enemy_spotted"
    ENEMY_KILLED = "enemy_killed"
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    
    # Resource events
    RESOURCE_FOUND = "resource_found"
    RESOURCE_COLLECTED = "resource_collected"
    RESOURCE_DEPLETED = "resource_depleted"
    
    # Construction events
    BUILDING_STARTED = "building_started"
    BUILDING_COMPLETED = "building_completed"
    STRUCTURE_DAMAGED = "structure_damaged"
    
    # World events
    TIME_CHANGED = "time_changed"
    WEATHER_CHANGED = "weather_changed"
    AREA_ENTERED = "area_entered"
    
    # Quest/objective events
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    OBJECTIVE_UPDATED = "objective_updated"
    
    # System events
    EMERGENCY_STOP = "emergency_stop"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"


@dataclass
class Event:
    """
    Universal event that can occur in any environment.
    """
    
    event_type: EventType
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "severity": self.severity
        }


class GoalType(Enum):
    """Types of goals the AI can have."""
    # Survival goals
    SURVIVE = "survive"
    HEAL = "heal"
    FIND_SHELTER = "find_shelter"
    
    # Combat goals
    DEFEAT_ENEMY = "defeat_enemy"
    DEFEND_POSITION = "defend_position"
    ESCAPE_DANGER = "escape_danger"
    
    # Resource goals
    GATHER_RESOURCES = "gather_resources"
    FIND_ITEM = "find_item"
    
    # Construction goals
    BUILD_STRUCTURE = "build_structure"
    REPAIR_STRUCTURE = "repair_structure"
    
    # Exploration goals
    EXPLORE_AREA = "explore_area"
    FIND_LOCATION = "find_location"
    
    # Social goals
    TALK_TO_NPC = "talk_to_npc"
    COMPLETE_QUEST = "complete_quest"
    
    # Meta goals
    LEARN = "learn"
    OPTIMIZE = "optimize"
    EXPERIMENT = "experiment"


@dataclass
class Goal:
    """
    Universal goal that works across all environments.
    """
    
    goal_type: GoalType
    description: str
    priority: int = 5  # 1-10, higher = more important
    
    # Goal parameters
    target: Optional[str] = None
    location: Optional[tuple] = None
    quantity: Optional[int] = None
    
    # Goal state
    progress: float = 0.0  # 0.0 to 1.0
    is_complete: bool = False
    is_failed: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_progress(self, progress: float):
        """Update goal progress."""
        self.progress = min(1.0, max(0.0, progress))
        if self.progress >= 1.0:
            self.is_complete = True
    
    def complete(self):
        """Mark goal as complete."""
        self.is_complete = True
        self.progress = 1.0
    
    def fail(self):
        """Mark goal as failed."""
        self.is_failed = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_type": self.goal_type.value,
            "description": self.description,
            "priority": self.priority,
            "progress": self.progress,
            "is_complete": self.is_complete,
            "is_failed": self.is_failed,
            "target": self.target,
            "metadata": self.metadata
        }


@dataclass
class GoalStack:
    """Stack of goals (current objectives)."""
    
    goals: List[Goal] = field(default_factory=list)
    
    def push(self, goal: Goal):
        """Add goal to stack (sorted by priority)."""
        self.goals.append(goal)
        self.goals.sort(key=lambda g: g.priority, reverse=True)
    
    def pop(self) -> Optional[Goal]:
        """Remove and return highest priority goal."""
        return self.goals.pop(0) if self.goals else None
    
    def get_current(self) -> Optional[Goal]:
        """Get current highest priority goal without removing."""
        return self.goals[0] if self.goals else None
    
    def remove_completed(self):
        """Remove all completed or failed goals."""
        self.goals = [g for g in self.goals if not g.is_complete and not g.is_failed]
    
    def __len__(self) -> int:
        return len(self.goals)

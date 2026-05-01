"""
Universal Memory System
Stores experiences and learns from them
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from .observation import Observation
from .action import Action
from .world_state import WorldState
from .events import Event


@dataclass
class Experience:
    """
    A single experience (observation → action → outcome).
    """
    
    # Input
    observation: Observation
    world_state: WorldState
    
    # Action taken
    action: Optional[Action] = None
    
    # Outcome
    reward: float = 0.0
    next_observation: Optional[Observation] = None
    next_world_state: Optional[WorldState] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def was_successful(self) -> bool:
        """Check if action led to positive outcome."""
        return self.reward > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.to_dict() if self.action else None,
            "reward": self.reward,
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class Session:
    """
    A play session (collection of experiences).
    """
    
    session_id: str
    environment_id: str
    
    # Experiences in this session
    experiences: List[Experience] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    
    # Session metadata
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Session stats
    total_reward: float = 0.0
    num_actions: int = 0
    
    def add_experience(self, experience: Experience):
        """Add experience to session."""
        self.experiences.append(experience)
        self.total_reward += experience.reward
        if experience.action:
            self.num_actions += 1
    
    def add_event(self, event: Event):
        """Add event to session."""
        self.events.append(event)
    
    def end_session(self):
        """Mark session as ended."""
        self.ended_at = datetime.now()
        self.duration_seconds = (self.ended_at - self.started_at).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        return {
            "session_id": self.session_id,
            "environment_id": self.environment_id,
            "duration_seconds": self.duration_seconds,
            "num_experiences": len(self.experiences),
            "num_actions": self.num_actions,
            "num_events": len(self.events),
            "total_reward": self.total_reward,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }


class Memory:
    """
    Universal memory system for storing and retrieving experiences.
    
    Supports:
    - Short-term memory (current session)
    - Long-term memory (across sessions)
    - Episodic memory (specific experiences)
    - Semantic memory (learned patterns)
    """
    
    def __init__(self):
        # Current session
        self.current_session: Optional[Session] = None
        
        # All sessions
        self.sessions: List[Session] = []
        
        # Quick lookup caches
        self.recent_experiences: List[Experience] = []
        self.important_experiences: List[Experience] = []
        
        # Learned patterns (simplified - would be more sophisticated in production)
        self.patterns: Dict[str, Any] = {}
        self.strategies: Dict[str, List[Experience]] = {}
    
    def start_session(self, environment_id: str, session_id: str = None) -> Session:
        """Start a new session."""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = Session(
            session_id=session_id,
            environment_id=environment_id
        )
        return self.current_session
    
    def end_session(self):
        """End current session and store it."""
        if self.current_session:
            self.current_session.end_session()
            self.sessions.append(self.current_session)
            self.current_session = None
    
    def remember(self, experience: Experience):
        """Add experience to memory."""
        if self.current_session:
            self.current_session.add_experience(experience)
        
        # Add to recent experiences (keep last 100)
        self.recent_experiences.append(experience)
        if len(self.recent_experiences) > 100:
            self.recent_experiences.pop(0)
        
        # Tag important experiences
        if experience.reward > 0.5 or experience.reward < -0.5:
            self.important_experiences.append(experience)
    
    def record_event(self, event: Event):
        """Record an event."""
        if self.current_session:
            self.current_session.add_event(event)
    
    def recall_similar(self, current_state: WorldState, limit: int = 5) -> List[Experience]:
        """
        Recall similar past experiences.
        
        In production, this would use embeddings/similarity search.
        For now, it's a simple lookup.
        """
        # Simplified: return recent successful experiences
        successful = [e for e in self.recent_experiences if e.was_successful()]
        return successful[-limit:]
    
    def get_strategy(self, goal_type: str) -> List[Experience]:
        """Get learned strategy for a goal type."""
        return self.strategies.get(goal_type, [])
    
    def learn_pattern(self, pattern_name: str, pattern_data: Any):
        """Learn a new pattern."""
        self.patterns[pattern_name] = pattern_data
    
    def clear_short_term(self):
        """Clear short-term memory (recent experiences)."""
        self.recent_experiences.clear()
    
    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """Get current session summary."""
        if self.current_session:
            return self.current_session.get_summary()
        return None
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get summaries of all past sessions."""
        return [session.get_summary() for session in self.sessions]

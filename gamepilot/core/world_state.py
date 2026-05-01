"""
Universal WorldState Model
Represents the current state of any environment
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Entity:
    """Any object or character in the world."""
    entity_id: str
    entity_type: str  # player, enemy, npc, object, resource
    position: Optional[tuple] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldState:
    """
    Universal world state that works across all environments.
    
    Can represent:
    - Game states (HP, inventory, enemies)
    - VR world states
    - Simulation states
    - Text adventure states
    """
    
    # Core fields
    timestamp: datetime = field(default_factory=datetime.now)
    environment_id: str = "unknown"
    
    # Player state
    player: Optional[Entity] = None
    player_stats: Dict[str, Any] = field(default_factory=dict)
    
    # World entities
    entities: List[Entity] = field(default_factory=list)
    
    # Environment properties
    environment_properties: Dict[str, Any] = field(default_factory=dict)
    
    # Derived states (from perception)
    threats: List[Entity] = field(default_factory=list)
    opportunities: List[Entity] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity
        return None
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]
    
    def has_threats(self) -> bool:
        """Check if there are any threats present."""
        return len(self.threats) > 0
    
    def has_opportunities(self) -> bool:
        """Check if there are any opportunities present."""
        return len(self.opportunities) > 0
    
    def get_player_stat(self, stat_name: str, default: Any = None) -> Any:
        """Get a player stat safely."""
        return self.player_stats.get(stat_name, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "environment_id": self.environment_id,
            "player_stats": self.player_stats,
            "num_entities": len(self.entities),
            "num_threats": len(self.threats),
            "num_opportunities": len(self.opportunities),
            "environment_properties": self.environment_properties,
            "metadata": self.metadata
        }

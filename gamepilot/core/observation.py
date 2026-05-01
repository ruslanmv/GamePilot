"""
Universal Observation Model
Represents what the AI "sees" in any environment
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from datetime import datetime
import numpy as np


@dataclass
class Observation:
    """
    Universal observation that works across all environments.
    
    Can represent:
    - Video frames from games
    - VR environment snapshots
    - Simulation states
    - Text-based game states
    - Sensor data from robotics
    """
    
    # Core fields (always present)
    timestamp: datetime = field(default_factory=datetime.now)
    environment_id: str = "unknown"
    
    # Visual data (optional)
    frame: Optional[np.ndarray] = None  # RGB image (H, W, 3)
    depth: Optional[np.ndarray] = None  # Depth map
    
    # Structured data (optional)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    ui_elements: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None  # For text-based environments
    
    # Metadata
    resolution: Optional[tuple] = None
    frame_index: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_visual_data(self) -> bool:
        """Check if observation contains visual data."""
        return self.frame is not None
    
    def has_structured_data(self) -> bool:
        """Check if observation contains structured data."""
        return len(self.entities) > 0 or len(self.ui_elements) > 0
    
    def is_text_only(self) -> bool:
        """Check if this is a text-based observation."""
        return self.text is not None and self.frame is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes frame data for efficiency)."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "environment_id": self.environment_id,
            "has_visual": self.has_visual_data(),
            "entities": self.entities,
            "ui_elements": self.ui_elements,
            "text": self.text,
            "metadata": self.metadata
        }


@dataclass
class ObservationSequence:
    """Sequence of observations over time."""
    
    observations: List[Observation] = field(default_factory=list)
    sequence_id: str = ""
    
    def add(self, observation: Observation):
        """Add observation to sequence."""
        self.observations.append(observation)
    
    def get_latest(self) -> Optional[Observation]:
        """Get most recent observation."""
        return self.observations[-1] if self.observations else None
    
    def get_window(self, n: int = 10) -> List[Observation]:
        """Get last N observations."""
        return self.observations[-n:]
    
    def __len__(self) -> int:
        return len(self.observations)

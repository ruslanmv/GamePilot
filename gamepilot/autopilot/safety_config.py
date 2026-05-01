"""
Autopilot Safety Configuration
Defines what autopilot is allowed to do
"""
from typing import Set, Dict, Any
from dataclasses import dataclass


@dataclass
class AutopilotSafetyConfig:
    """Safety configuration for autopilot mode."""
    
    # Time limits
    max_session_duration_seconds: int = 600  # 10 minutes default
    absolute_max_duration_seconds: int = 3600  # 1 hour hard limit
    
    # Action limits
    max_actions_per_second: float = 5.0  # Conservative rate
    max_total_actions: int = 3000  # Max actions per session
    
    # Environment restrictions
    allowed_environment_patterns: Set[str] = None
    blocked_environment_patterns: Set[str] = None
    
    # Feature restrictions
    allow_combat: bool = True
    allow_building: bool = True
    allow_trading: bool = False  # Disabled by default (risk of scams)
    allow_chat: bool = False  # Disabled (privacy/social risk)
    
    # Emergency stop settings
    stop_on_low_health: bool = True
    low_health_threshold: float = 0.2  # 20%
    
    stop_on_valuable_item_drop: bool = True
    stop_on_unexpected_location: bool = True
    
    # Logging
    log_all_actions: bool = True
    log_observations: bool = True
    record_video: bool = False  # Optional video recording
    
    def __post_init__(self):
        if self.allowed_environment_patterns is None:
            # Default: only offline/sandbox environments
            self.allowed_environment_patterns = {
                "singleplayer",
                "offline",
                "sandbox",
                "private",
                "local",
                "test"
            }
        
        if self.blocked_environment_patterns is None:
            # Block multiplayer/competitive
            self.blocked_environment_patterns = {
                "multiplayer",
                "online",
                "competitive",
                "ranked",
                "pvp",
                "mmo",
                "battle_royale"
            }
    
    def is_environment_allowed(self, environment_id: str) -> bool:
        """Check if environment is allowed for autopilot."""
        env_lower = environment_id.lower()
        
        # Check blocked patterns first
        for pattern in self.blocked_environment_patterns:
            if pattern in env_lower:
                return False
        
        # Check allowed patterns
        for pattern in self.allowed_environment_patterns:
            if pattern in env_lower:
                return True
        
        # Default: not allowed
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_session_duration": self.max_session_duration_seconds,
            "max_actions_per_second": self.max_actions_per_second,
            "allow_combat": self.allow_combat,
            "allow_building": self.allow_building,
            "allow_trading": self.allow_trading,
            "stop_on_low_health": self.stop_on_low_health,
            "low_health_threshold": self.low_health_threshold
        }


# Preset configurations

SAFE_AFK_CONFIG = AutopilotSafetyConfig(
    max_session_duration_seconds=600,  # 10 min
    max_actions_per_second=2.0,  # Very conservative
    allow_combat=False,  # Just survive, don't fight
    allow_building=False,
    allow_trading=False,
    stop_on_low_health=True,
    low_health_threshold=0.5  # 50% - very cautious
)

MISSION_ASSIST_CONFIG = AutopilotSafetyConfig(
    max_session_duration_seconds=1800,  # 30 min
    max_actions_per_second=5.0,
    allow_combat=True,
    allow_building=False,
    allow_trading=False,
    stop_on_low_health=True,
    low_health_threshold=0.2
)

BUILD_ASSIST_CONFIG = AutopilotSafetyConfig(
    max_session_duration_seconds=3600,  # 1 hour for building
    max_actions_per_second=8.0,  # Building can be faster
    allow_combat=False,  # Focus on building
    allow_building=True,
    allow_trading=False,
    stop_on_low_health=False  # Building is safe
)

RESEARCH_CONFIG = AutopilotSafetyConfig(
    max_session_duration_seconds=7200,  # 2 hours for research
    max_actions_per_second=10.0,
    allow_combat=True,
    allow_building=True,
    allow_trading=False,
    stop_on_low_health=False
)

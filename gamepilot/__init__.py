"""
GamePilot - Universal AI Companion for Any Virtual World

Your copilot for gaming, learning, and exploration.
"""

__version__ = "0.1.0b1"
__author__ = "Ruslan Magana Vsevolodovna"
__email__ = "contact@ruslanmv.com"

# Core models (always available)
from gamepilot.core import (
    Observation,
    Action,
    WorldState,
    Event,
    Goal,
    Memory,
)

# Environments (always available)
from gamepilot.environments import (
    BaseEnvironment,
    CompanionOnly,
)

# Safety (always available)
from gamepilot.safety import (
    Guardrails,
    Permission,
    PermissionManager,
)

__all__ = [
    # Meta
    "__version__",
    "__author__",
    
    # Core
    "Observation",
    "Action",
    "WorldState",
    "Event",
    "Goal",
    "Memory",
    
    # Environments
    "BaseEnvironment",
    "CompanionOnly",
    
    # Safety
    "Guardrails",
    "Permission",
    "PermissionManager",
]

# Optional imports with graceful fallback
try:
    from gamepilot.app.companion import create_companion, Companion
    __all__.extend(["create_companion", "Companion"])
except ImportError:
    pass

try:
    from gamepilot.app.domains.construction import ConstructionPlanner
    __all__.append("ConstructionPlanner")
except ImportError:
    pass

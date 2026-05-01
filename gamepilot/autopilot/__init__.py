"""
GamePilot Autopilot - AI Takes Over Temporarily
Allows AI to play on your behalf for limited time with full safety
"""

from .controller import (
    AutopilotController,
    AutopilotMode,
    AutopilotStatus,
    AutopilotSession
)
from .safety_config import (
    AutopilotSafetyConfig,
    SAFE_AFK_CONFIG,
    MISSION_ASSIST_CONFIG,
    BUILD_ASSIST_CONFIG,
    RESEARCH_CONFIG
)

__all__ = [
    "AutopilotController",
    "AutopilotMode",
    "AutopilotStatus",
    "AutopilotSession",
    "AutopilotSafetyConfig",
    "SAFE_AFK_CONFIG",
    "MISSION_ASSIST_CONFIG",
    "BUILD_ASSIST_CONFIG",
    "RESEARCH_CONFIG",
]

"""
Permission System
Controls what GamePilot is allowed to do
"""
from enum import Enum
from typing import Set


class Permission(Enum):
    """Permissions that can be granted."""
    # Observation permissions
    SCREEN_CAPTURE = "screen_capture"
    VIDEO_ANALYSIS = "video_analysis"
    
    # Interaction permissions
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_INPUT = "mouse_input"
    GAMEPAD_INPUT = "gamepad_input"
    
    # Environment permissions
    SANDBOX_EXECUTION = "sandbox_execution"
    OFFLINE_GAME = "offline_game"
    
    # Data permissions
    SESSION_RECORDING = "session_recording"
    ANALYTICS = "analytics"


class PermissionManager:
    """
    Manages what GamePilot is allowed to do.
    
    Default: Minimal permissions (companion mode only)
    User must explicitly grant additional permissions
    """
    
    def __init__(self):
        # Default: companion-only mode
        self.granted: Set[Permission] = {
            Permission.VIDEO_ANALYSIS
        }
    
    def grant(self, permission: Permission):
        """Grant a permission."""
        self.granted.add(permission)
    
    def revoke(self, permission: Permission):
        """Revoke a permission."""
        self.granted.discard(permission)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if permission is granted."""
        return permission in self.granted
    
    def require_permission(self, permission: Permission):
        """Require a permission or raise error."""
        if not self.has_permission(permission):
            raise PermissionError(
                f"Permission required: {permission.value}. "
                f"Grant with: permissions.grant(Permission.{permission.name})"
            )
    
    def get_all_granted(self) -> Set[Permission]:
        """Get all granted permissions."""
        return self.granted.copy()
    
    def enable_companion_mode(self):
        """Enable companion-only mode (safest)."""
        self.granted = {
            Permission.VIDEO_ANALYSIS,
            Permission.SESSION_RECORDING
        }
    
    def enable_agent_mode_sandbox(self):
        """Enable agent mode for sandbox environments."""
        self.granted.update({
            Permission.SCREEN_CAPTURE,
            Permission.KEYBOARD_INPUT,
            Permission.MOUSE_INPUT,
            Permission.SANDBOX_EXECUTION,
            Permission.SESSION_RECORDING
        })
    
    def enable_all(self):
        """Enable all permissions (use with caution)."""
        self.granted = set(Permission)

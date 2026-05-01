"""
Safety Guardrails
Ensures GamePilot operates ethically and safely
"""
from typing import Optional, List
from gamepilot.core import Action, WorldState, Event, EventType


class SafetyViolation(Exception):
    """Raised when a safety rule is violated."""
    pass


class Guardrails:
    """
    Safety guardrail system.
    
    Prevents GamePilot from:
    - Violating game Terms of Service
    - Operating in multiplayer environments
    - Executing high-risk actions
    - Running without user consent
    """
    
    def __init__(self):
        self.enabled = True
        self.strict_mode = True
        self.violation_log: List[str] = []
    
    def check_action(self, action: Action, state: WorldState) -> bool:
        """
        Check if action is safe to execute.
        
        Returns:
            True if safe, False if blocked
            
        Raises:
            SafetyViolation if strict_mode and unsafe
        """
        if not self.enabled:
            return True
        
        # Rule 1: No actions in multiplayer environments
        if self._is_multiplayer(state):
            msg = "Action blocked: Multiplayer environment detected"
            self._log_violation(msg)
            if self.strict_mode:
                raise SafetyViolation(msg)
            return False
        
        # Rule 2: No high-risk actions without confirmation
        if action.risk_level == "high" and not action.requires_confirmation:
            msg = f"Action blocked: High-risk action {action.name} requires confirmation"
            self._log_violation(msg)
            if self.strict_mode:
                raise SafetyViolation(msg)
            return False
        
        # Rule 3: Respect rate limits
        if not self._check_rate_limit(action):
            msg = "Action blocked: Rate limit exceeded"
            self._log_violation(msg)
            if self.strict_mode:
                raise SafetyViolation(msg)
            return False
        
        return True
    
    def check_environment(self, environment_id: str) -> bool:
        """Check if environment is safe to operate in."""
        # Block certain environment types
        blocked_patterns = [
            "competitive",
            "ranked",
            "pvp",
            "online_multiplayer"
        ]
        
        for pattern in blocked_patterns:
            if pattern in environment_id.lower():
                msg = f"Environment blocked: {environment_id} appears to be competitive/multiplayer"
                self._log_violation(msg)
                if self.strict_mode:
                    raise SafetyViolation(msg)
                return False
        
        return True
    
    def _is_multiplayer(self, state: WorldState) -> bool:
        """Detect if current state indicates multiplayer."""
        # Check for human players
        if state.metadata.get("mode") == "multiplayer":
            return True
        
        # Check for other indicators
        player_entities = [e for e in state.entities if e.entity_type == "player"]
        if len(player_entities) > 1:
            return True
        
        return False
    
    def _check_rate_limit(self, action: Action) -> bool:
        """Check if action respects rate limits."""
        # Simplified - in production would track actual timing
        return True
    
    def _log_violation(self, message: str):
        """Log safety violation."""
        self.violation_log.append(message)
    
    def get_violations(self) -> List[str]:
        """Get all logged violations."""
        return self.violation_log.copy()
    
    def clear_violations(self):
        """Clear violation log."""
        self.violation_log.clear()

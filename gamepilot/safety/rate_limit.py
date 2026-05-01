"""
Rate Limiting
Prevents excessive action frequency
"""
import time
from collections import deque
from typing import Deque


class RateLimiter:
    """
    Rate limiter for actions.
    
    Prevents GamePilot from executing actions too quickly,
    which could:
    - Trigger anti-cheat systems
    - Cause unnatural behavior
    - Harm the gaming experience
    """
    
    def __init__(self, max_per_second: float = 10.0):
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second
        self.action_times: Deque[float] = deque(maxlen=int(max_per_second * 10))
        self.last_action_time = 0.0
    
    def check(self) -> bool:
        """
        Check if an action can be executed now.
        
        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()
        
        # Check minimum interval since last action
        if current_time - self.last_action_time < self.min_interval:
            return False
        
        # Check actions in last second
        cutoff_time = current_time - 1.0
        recent_actions = sum(1 for t in self.action_times if t > cutoff_time)
        
        if recent_actions >= self.max_per_second:
            return False
        
        return True
    
    def record_action(self):
        """Record that an action was executed."""
        current_time = time.time()
        self.action_times.append(current_time)
        self.last_action_time = current_time
    
    def wait_if_needed(self):
        """Block until an action can be executed."""
        while not self.check():
            time.sleep(0.01)
    
    def get_current_rate(self) -> float:
        """Get current actions per second."""
        current_time = time.time()
        cutoff_time = current_time - 1.0
        recent = sum(1 for t in self.action_times if t > cutoff_time)
        return float(recent)

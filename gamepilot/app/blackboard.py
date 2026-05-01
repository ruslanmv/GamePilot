from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Blackboard:
    current_goal: str = "explore"
    current_mode: str = "demo"
    last_state: dict[str, Any] = field(default_factory=dict)
    last_action: str = "idle"
    emergency_stop: bool = False
    planner_status: str = "idle"
    last_planner_run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


blackboard = Blackboard()

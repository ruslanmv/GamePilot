"""
Autopilot Mode - AI Takes Over Temporarily
Allows AI to play on your behalf for limited time with full safety controls
"""
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import time
import threading

from gamepilot.core import Action, Observation, WorldState, Goal, GoalType
from gamepilot.environments import BaseEnvironment
from gamepilot.safety import Guardrails, PermissionManager, Permission, RateLimiter


class AutopilotMode(Enum):
    """Types of autopilot assistance."""
    COMPLETE_MISSION = "complete_mission"  # Beat boss, finish quest
    BUILD_STRUCTURE = "build_structure"    # Build something
    STAY_ALIVE = "stay_alive"              # Just survive (AFK mode)
    GATHER_RESOURCES = "gather_resources"  # Farm resources
    TRAVEL_TO = "travel_to"                # Navigate to location
    CUSTOM = "custom"                      # Custom goal


class AutopilotStatus(Enum):
    """Autopilot status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EMERGENCY_STOPPED = "emergency_stopped"


class AutopilotSession:
    """
    Represents one autopilot session.
    
    Tracks what the AI did while in control.
    """
    
    def __init__(
        self,
        session_id: str,
        mode: AutopilotMode,
        goal_description: str,
        max_duration_seconds: int
    ):
        self.session_id = session_id
        self.mode = mode
        self.goal_description = goal_description
        self.max_duration_seconds = max_duration_seconds
        
        # Tracking
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = AutopilotStatus.IDLE
        
        # Actions taken
        self.actions_taken: List[Action] = []
        self.observations: List[Observation] = []
        
        # Results
        self.success = False
        self.completion_percentage = 0.0
        self.notes = ""
    
    def get_elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_time_remaining(self) -> float:
        """Get remaining time in seconds."""
        elapsed = self.get_elapsed_seconds()
        return max(0, self.max_duration_seconds - elapsed)
    
    def is_time_expired(self) -> bool:
        """Check if time limit reached."""
        return self.get_elapsed_seconds() >= self.max_duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/UI."""
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "goal": self.goal_description,
            "status": self.status.value,
            "elapsed_seconds": self.get_elapsed_seconds(),
            "time_remaining": self.get_time_remaining(),
            "max_duration": self.max_duration_seconds,
            "actions_count": len(self.actions_taken),
            "success": self.success,
            "completion": self.completion_percentage,
            "notes": self.notes
        }


class AutopilotController:
    """
    Main autopilot controller.
    
    Handles AI taking over gameplay temporarily with full safety.
    """
    
    def __init__(
        self,
        environment: BaseEnvironment,
        guardrails: Optional[Guardrails] = None,
        permissions: Optional[PermissionManager] = None
    ):
        self.environment = environment
        self.guardrails = guardrails or Guardrails()
        self.permissions = permissions or PermissionManager()
        
        # Current session
        self.current_session: Optional[AutopilotSession] = None
        self.is_running = False
        
        # Safety limits
        self.max_duration_seconds = 600  # 10 minutes default
        self.absolute_max_duration = 3600  # 1 hour hard limit
        
        # Rate limiting
        self.rate_limiter = RateLimiter(max_per_second=5.0)  # Conservative
        
        # Emergency stop callback
        self.emergency_stop_callback: Optional[Callable] = None
        
        # Session history
        self.session_history: List[AutopilotSession] = []
        
        # Control thread
        self._control_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
    
    def start_autopilot(
        self,
        mode: AutopilotMode,
        goal_description: str,
        duration_seconds: int,
        goal_params: Optional[Dict[str, Any]] = None
    ) -> AutopilotSession:
        """
        Start autopilot mode.
        
        Args:
            mode: What the AI should do
            goal_description: Natural language goal
            duration_seconds: Max time to run
            goal_params: Additional parameters
            
        Returns:
            AutopilotSession tracking the session
            
        Raises:
            PermissionError: If permissions not granted
            SafetyViolation: If environment not safe
        """
        # Safety checks
        self._check_can_start()
        
        # Enforce time limits
        duration_seconds = min(duration_seconds, self.absolute_max_duration)
        
        # Create session
        session_id = f"autopilot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = AutopilotSession(
            session_id=session_id,
            mode=mode,
            goal_description=goal_description,
            max_duration_seconds=duration_seconds
        )
        
        self.current_session = session
        session.status = AutopilotStatus.RUNNING
        self.is_running = True
        
        # Start control loop in background thread
        self._stop_flag.clear()
        self._control_thread = threading.Thread(
            target=self._control_loop,
            args=(session, goal_params or {}),
            daemon=True
        )
        self._control_thread.start()
        
        return session
    
    def pause_autopilot(self):
        """Pause autopilot (can be resumed)."""
        if self.current_session:
            self.current_session.status = AutopilotStatus.PAUSED
            self.is_running = False
    
    def resume_autopilot(self):
        """Resume paused autopilot."""
        if self.current_session and self.current_session.status == AutopilotStatus.PAUSED:
            self.current_session.status = AutopilotStatus.RUNNING
            self.is_running = True
    
    def stop_autopilot(self, reason: str = "user_requested"):
        """
        Stop autopilot and return control to user.
        
        Args:
            reason: Why autopilot stopped
        """
        self._stop_flag.set()
        self.is_running = False
        
        if self.current_session:
            self.current_session.status = AutopilotStatus.COMPLETED
            self.current_session.end_time = datetime.now()
            self.current_session.notes = f"Stopped: {reason}"
            
            # Save to history
            self.session_history.append(self.current_session)
            self.current_session = None
        
        # Wait for thread to finish
        if self._control_thread:
            self._control_thread.join(timeout=2.0)
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all actions."""
        self._stop_flag.set()
        self.is_running = False
        
        if self.current_session:
            self.current_session.status = AutopilotStatus.EMERGENCY_STOPPED
            self.current_session.end_time = datetime.now()
            self.session_history.append(self.current_session)
            self.current_session = None
        
        # Call emergency callback if set
        if self.emergency_stop_callback:
            self.emergency_stop_callback()
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current autopilot status."""
        if self.current_session:
            return self.current_session.to_dict()
        return None
    
    def _check_can_start(self):
        """Verify autopilot can start safely."""
        # Check permissions
        self.permissions.require_permission(Permission.KEYBOARD_INPUT)
        self.permissions.require_permission(Permission.SANDBOX_EXECUTION)
        
        # Check environment safety
        if not self.guardrails.check_environment(self.environment.environment_id):
            raise Exception("Environment not approved for autopilot")
        
        # Check not already running
        if self.is_running:
            raise Exception("Autopilot already running")
    
    def _control_loop(self, session: AutopilotSession, goal_params: Dict[str, Any]):
        """
        Main control loop - runs in background thread.
        
        This is where AI makes decisions and executes actions.
        """
        try:
            while not self._stop_flag.is_set():
                # Check time limit
                if session.is_time_expired():
                    self.stop_autopilot("time_limit_reached")
                    break
                
                # Check if paused
                if session.status == AutopilotStatus.PAUSED:
                    time.sleep(0.1)
                    continue
                
                # Observe current state
                obs = self.environment.observe()
                state = self.environment.get_state()
                
                session.observations.append(obs)
                
                # Decide next action based on mode
                action = self._decide_action(session.mode, state, goal_params)
                
                if action:
                    # Safety check
                    if not self.guardrails.check_action(action, state):
                        self.emergency_stop()
                        break
                    
                    # Rate limiting
                    self.rate_limiter.wait_if_needed()
                    
                    # Execute action
                    next_obs, reward, done = self.environment.execute_action(action)
                    
                    # Record
                    session.actions_taken.append(action)
                    self.rate_limiter.record_action()
                    
                    # Check if goal completed
                    if self._check_goal_completed(session.mode, state, goal_params):
                        session.success = True
                        session.completion_percentage = 100.0
                        self.stop_autopilot("goal_completed")
                        break
                
                # Small delay
                time.sleep(0.1)
        
        except Exception as e:
            session.status = AutopilotStatus.FAILED
            session.notes = f"Error: {str(e)}"
            self.stop_autopilot(f"error: {e}")
    
    def _decide_action(
        self,
        mode: AutopilotMode,
        state: WorldState,
        params: Dict[str, Any]
    ) -> Optional[Action]:
        """
        Decide what action to take based on mode and state.
        
        This is where AI decision-making happens.
        In production, this would use:
        - Reinforcement learning models
        - Behavior cloning
        - LLM-based planning
        
        For now, simplified rule-based logic.
        """
        if mode == AutopilotMode.STAY_ALIVE:
            # AFK mode - just survive
            if state.has_threats():
                # Run away
                return Action.keyboard("SHIFT")  # Sneak/hide
            else:
                # Stay put
                return None
        
        elif mode == AutopilotMode.COMPLETE_MISSION:
            # Try to complete objective
            # In production: use RL model trained on this task
            return self._get_mission_action(state, params)
        
        elif mode == AutopilotMode.BUILD_STRUCTURE:
            # Execute construction plan
            return self._get_construction_action(state, params)
        
        elif mode == AutopilotMode.GATHER_RESOURCES:
            # Gather resources
            return self._get_gathering_action(state, params)
        
        elif mode == AutopilotMode.TRAVEL_TO:
            # Navigate to location
            return self._get_navigation_action(state, params)
        
        return None
    
    def _check_goal_completed(
        self,
        mode: AutopilotMode,
        state: WorldState,
        params: Dict[str, Any]
    ) -> bool:
        """Check if goal is completed."""
        # Simplified - in production would be more sophisticated
        if mode == AutopilotMode.STAY_ALIVE:
            # Never "complete" - runs until time expires
            return False
        
        # Other modes would check specific completion criteria
        return False
    
    def _get_mission_action(self, state: WorldState, params: Dict) -> Optional[Action]:
        """Get action for mission completion mode."""
        # Placeholder - would use trained model
        return None
    
    def _get_construction_action(self, state: WorldState, params: Dict) -> Optional[Action]:
        """Get action for building mode."""
        # Could integrate with ConstructionPlanner
        return None
    
    def _get_gathering_action(self, state: WorldState, params: Dict) -> Optional[Action]:
        """Get action for resource gathering."""
        # Placeholder - would use pathfinding + collection logic
        return None
    
    def _get_navigation_action(self, state: WorldState, params: Dict) -> Optional[Action]:
        """Get action for navigation."""
        # Placeholder - would use pathfinding
        return None

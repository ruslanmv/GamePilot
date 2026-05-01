from datetime import datetime, timezone

from gamepilot.app.blackboard import blackboard
from gamepilot.app.decision.planner_llm import plan_goal
from gamepilot.app.decision.policy_selector import select_policy
from gamepilot.app.decision.rules import choose_rule_action
from gamepilot.app.decision.triggers import should_trigger_planner
from gamepilot.app.executor.controls import ControlExecutor
from gamepilot.app.models.registry import RuntimeRegistry
from gamepilot.app.perception.detector import Detector
from gamepilot.app.perception.screen_capture import capture_screen
from gamepilot.app.perception.state_builder import build_state


def run(iterations: int = 5, dry_run: bool = True) -> None:
    detector = Detector()
    executor = ControlExecutor(dry_run=dry_run)
    runtime_registry = RuntimeRegistry()

    for _ in range(iterations):
        if blackboard.emergency_stop:
            executor.execute("stop")
            blackboard.last_action = "stop"
            continue

        state = build_state(detector.detect(capture_screen()))
        blackboard.last_state = state

        if should_trigger_planner(state, blackboard.last_planner_run_at):
            blackboard.current_goal = plan_goal(state)
            blackboard.last_planner_run_at = datetime.now(timezone.utc)
            blackboard.planner_status = "updated"

        goal = choose_rule_action(state, blackboard.current_goal)
        policy = select_policy(goal)
        action = runtime_registry.predict(policy, state, goal)
        blackboard.last_action = action
        executor.execute(action)

from datetime import datetime, timedelta, timezone

from gamepilot.app.blackboard import blackboard
from gamepilot.app.orchestrator import run


def test_orchestrator_updates_planner_timestamp(monkeypatch):
    monkeypatch.setattr("gamepilot.app.orchestrator.capture_screen", lambda: [[0]])
    monkeypatch.setattr("gamepilot.app.orchestrator.should_trigger_planner", lambda *_args, **_kwargs: True)
    before = datetime.now(timezone.utc) - timedelta(minutes=1)
    blackboard.last_planner_run_at = before
    blackboard.emergency_stop = False
    run(iterations=1)
    assert blackboard.last_planner_run_at > before


def test_orchestrator_emergency_stop(monkeypatch):
    actions = []

    class E:
        def execute(self, action: str) -> None:
            actions.append(action)

    monkeypatch.setattr("gamepilot.app.orchestrator.ControlExecutor", lambda dry_run=True: E())
    blackboard.emergency_stop = True
    run(iterations=1)
    blackboard.emergency_stop = False
    assert actions == ["stop"]

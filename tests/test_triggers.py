from datetime import datetime, timedelta, timezone

from gamepilot.app.decision.triggers import should_trigger_planner


def test_triggers():
    now = datetime.now(timezone.utc)
    assert should_trigger_planner({"stuck": True}, now) is True
    assert should_trigger_planner({"stuck": False, "quest_changed": False}, now - timedelta(seconds=15)) is True

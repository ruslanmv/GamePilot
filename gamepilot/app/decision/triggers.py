from datetime import datetime, timedelta, timezone


def should_trigger_planner(state: dict, last_planner_run_at: datetime, interval_seconds: int = 10) -> bool:
    if state.get("stuck") or state.get("quest_changed"):
        return True
    return datetime.now(timezone.utc) - last_planner_run_at >= timedelta(seconds=interval_seconds)

from dataclasses import dataclass


@dataclass
class CommandResult:
    goal: str | None = None
    emergency_stop: bool | None = None


def parse_command(text: str) -> CommandResult:
    normalized = text.strip().lower()
    if "stop" in normalized or "pause" in normalized:
        return CommandResult(emergency_stop=True)
    if "resume" in normalized:
        return CommandResult(emergency_stop=False)
    if "loot" in normalized:
        return CommandResult(goal="loot")
    if "fight" in normalized or "combat" in normalized or "farm" in normalized:
        return CommandResult(goal="fight")
    if "heal" in normalized:
        return CommandResult(goal="heal")
    return CommandResult(goal="explore")

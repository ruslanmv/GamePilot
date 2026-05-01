def choose_rule_action(state: dict, current_goal: str) -> str:
    if state.get("hp", 100) < 30:
        return "heal"
    if state.get("enemy_near", False):
        return "fight"
    if state.get("loot_visible", False):
        return "loot"
    return current_goal

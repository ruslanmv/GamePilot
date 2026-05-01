def select_policy(goal: str) -> str:
    mapping = {
        "fight": "imitation_combat",
        "loot": "imitation_loot",
        "heal": "rules_heal",
        "explore": "transformer_explore",
    }
    return mapping.get(goal, "transformer_explore")

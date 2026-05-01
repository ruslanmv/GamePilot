from gamepilot.app.decision.rules import choose_rule_action


def test_rules_priority():
    assert choose_rule_action({"hp": 10, "enemy_near": True, "loot_visible": False}, "explore") == "heal"
    assert choose_rule_action({"hp": 90, "enemy_near": True, "loot_visible": False}, "explore") == "fight"

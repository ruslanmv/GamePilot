from gamepilot.app.decision.policy_selector import select_policy


def test_policy_selector():
    assert select_policy("fight") == "imitation_combat"
    assert select_policy("unknown") == "transformer_explore"

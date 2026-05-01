from gamepilot.app.action_mapping import load_action_mapping


def test_default_mapping():
    mapping = load_action_mapping()
    assert mapping["loot"] == "F"

from gamepilot.app.commands import parse_command


def test_parse_command_stop():
    assert parse_command("stop now").emergency_stop is True


def test_parse_command_goal():
    assert parse_command("please loot").goal == "loot"

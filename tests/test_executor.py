import pytest

from gamepilot.app.executor.controls import ControlExecutor


def test_executor_raises_when_not_dry_run():
    with pytest.raises(NotImplementedError):
        ControlExecutor(dry_run=False).execute('attack')

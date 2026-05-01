from gamepilot.app.main import main


def test_demo_video(monkeypatch):
    monkeypatch.setattr("gamepilot.app.main.iter_video_frames", lambda *_args, **_kwargs: [(0, [[0]])])
    monkeypatch.setattr("sys.argv", ["gamepilot", "demo", "--video", "dummy.mp4"])
    assert main() == 0

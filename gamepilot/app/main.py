import argparse
import json
import subprocess
from pathlib import Path

from gamepilot.app.decision.planner_llm import plan_goal
from gamepilot.app.decision.policy_selector import select_policy
from gamepilot.app.models.registry import RuntimeRegistry
from gamepilot.app.orchestrator import run
from gamepilot.app.perception.detector import create_detector
from gamepilot.app.perception.screen_capture import iter_video_frames
from gamepilot.app.perception.state_builder import build_state

MODEL_HOME = Path.home() / ".gamepilot" / "models"


def main() -> int:
    parser = argparse.ArgumentParser(prog="gamepilot")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("start")
    demo = sub.add_parser("demo")
    demo.add_argument("--video", required=True)
    demo.add_argument("--every", type=int, default=30)
    demo.add_argument("--max-frames", type=int, default=10)
    demo.add_argument("--detector", choices=["mock", "opencv", "yolo"], default="opencv")
    sub.add_parser("api")
    models = sub.add_parser("models")
    models_sub = models.add_subparsers(dest="models_cmd")
    models_sub.add_parser("list")
    dl = models_sub.add_parser("download")
    dl.add_argument("name", help="Hugging Face repo id, e.g. org/model")
    models_sub.add_parser("path")

    args = parser.parse_args()

    if args.cmd in (None, "start"):
        run()
    elif args.cmd == "demo":
        detector = create_detector(args.detector)
        runtime = RuntimeRegistry()
        timeline = []
        for frame_idx, frame in iter_video_frames(args.video, every=args.every, max_frames=args.max_frames):
            state = build_state(detector.detect(frame))
            goal = plan_goal(state)
            policy = select_policy(goal)
            action = runtime.predict(policy, state, goal)
            timeline.append({"frame": frame_idx, "state": state, "goal": goal, "policy": policy, "action": action})
        print(json.dumps(timeline, indent=2))
    elif args.cmd == "api":
        subprocess.run(["uvicorn", "gamepilot.app.api.server:app", "--host", "0.0.0.0", "--port", "8000"], check=False)
    elif args.cmd == "models":
        MODEL_HOME.mkdir(parents=True, exist_ok=True)
        if args.models_cmd == "list":
            models_found = sorted([p.name for p in MODEL_HOME.iterdir() if p.is_dir()])
            print(json.dumps({"models": models_found}, indent=2))
        elif args.models_cmd == "download":
            from huggingface_hub import snapshot_download

            local_dir = snapshot_download(repo_id=args.name, local_dir=str(MODEL_HOME / args.name.replace('/', '__')), local_dir_use_symlinks=False)
            print(json.dumps({"downloaded": args.name, "path": str(local_dir)}, indent=2))
        elif args.models_cmd == "path":
            print(str(MODEL_HOME))
    return 0

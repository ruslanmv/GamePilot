import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from gamepilot.app.blackboard import blackboard
from gamepilot.app.commands import parse_command
from gamepilot.app.decision.planner_llm import plan_goal
from gamepilot.app.decision.policy_selector import select_policy
from gamepilot.app.models.registry import RuntimeRegistry
from gamepilot.app.perception.detector import create_detector
from gamepilot.app.perception.screen_capture import iter_video_frames
from gamepilot.app.perception.state_builder import build_state

app = FastAPI(title="GamePilot API")
registry = RuntimeRegistry()


class CommandPayload(BaseModel):
    text: str


class DemoPredictPayload(BaseModel):
    hp: int = 72
    enemy_near: bool = False
    loot_visible: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/state")
def state() -> dict:
    return blackboard.__dict__.copy()


@app.get("/safety")
def safety() -> dict:
    return {"emergency_stop": blackboard.emergency_stop}


@app.post("/command")
def command(payload: CommandPayload) -> dict:
    result = parse_command(payload.text)
    if result.emergency_stop is not None:
        blackboard.emergency_stop = result.emergency_stop
    if result.goal:
        blackboard.current_goal = result.goal
    return {"ok": True, "goal": blackboard.current_goal, "emergency_stop": blackboard.emergency_stop}


@app.post("/stop")
def stop() -> dict:
    blackboard.emergency_stop = True
    return {"ok": True}


@app.post("/resume")
def resume() -> dict:
    blackboard.emergency_stop = False
    return {"ok": True}


@app.post("/demo/predict")
def demo_predict(payload: DemoPredictPayload) -> dict:
    state = build_state(payload.model_dump())
    goal = plan_goal(state)
    policy = select_policy(goal)
    action = registry.predict(policy, state, goal)
    return {"state": state, "goal": goal, "policy": policy, "action": action}


@app.post('/demo/video')
async def demo_video(file: UploadFile = File(...)) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / file.filename
        target.write_bytes(await file.read())
        detector = create_detector("opencv")
        timeline = []
        for frame_idx, frame in iter_video_frames(str(target), every=30, max_frames=10):
            state = build_state(detector.detect(frame))
            goal = plan_goal(state)
            policy = select_policy(goal)
            action = registry.predict(policy, state, goal)
            timeline.append({"frame": frame_idx, "goal": goal, "policy": policy, "action": action})
    return {"timeline": timeline}

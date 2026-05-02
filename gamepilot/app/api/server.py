import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gamepilot.app.api.frontend_compat import router as frontend_compat_router
from gamepilot.app.blackboard import blackboard
from gamepilot.app.commands import parse_command
from gamepilot.app.decision.planner_llm import plan_goal
from gamepilot.app.decision.policy_selector import select_policy
from gamepilot.app.discover import build_news_service
from gamepilot.app.models.registry import RuntimeRegistry
from gamepilot.app.perception.detector import create_detector
from gamepilot.app.perception.screen_capture import iter_video_frames
from gamepilot.app.perception.state_builder import build_state

LOG = logging.getLogger("gamepilot.api")

app = FastAPI(title="GamePilot API")
app.include_router(frontend_compat_router)
registry = RuntimeRegistry()


def _resolve_frontend_dir() -> Optional[Path]:
    """Find the GamePilot frontend directory across install layouts.

    Why this is non-trivial: when ``uv sync`` installs the project as a
    regular wheel (the default), the ``gamepilot`` package lives at
    ``<venv>/Lib/site-packages/gamepilot/`` and ``Path(__file__).parents[3]``
    points at ``site-packages`` — which has no ``frontend/`` sibling. The
    server then 404s on ``/`` and ``/app``. Editable installs and
    ``uvicorn --app-dir <repo>`` happen to work, which masked this in dev.

    Resolution order — first hit wins:

    1. ``$GAMEPILOT_FRONTEND_DIR`` env var (operator override).
    2. ``<cwd>/frontend`` — `make start` runs uvicorn from the repo root.
    3. Walk up from this file looking for a ``frontend/landing.html``
       sibling next to a ``pyproject.toml`` / ``.git`` (editable installs).
    """
    candidates = []

    env_override = os.environ.get("GAMEPILOT_FRONTEND_DIR")
    if env_override:
        candidates.append(Path(env_override).expanduser())

    candidates.append(Path.cwd() / "frontend")

    here = Path(__file__).resolve()
    for ancestor in [here, *here.parents]:
        candidates.append(ancestor / "frontend")
        if (ancestor / "pyproject.toml").exists() or (ancestor / ".git").exists():
            # Don't crawl past the repo root.
            break

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            continue
        if (resolved / "landing.html").is_file():
            return resolved

    return None


FRONTEND_DIR: Optional[Path] = _resolve_frontend_dir()
if FRONTEND_DIR is None:
    LOG.warning(
        "Could not locate the GamePilot frontend dir. "
        "Set GAMEPILOT_FRONTEND_DIR=<repo>/frontend, or run uvicorn from "
        "the repository root. /, /app, /dashboard will return a hint."
    )
else:
    LOG.info("GamePilot frontend dir: %s", FRONTEND_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# ---- Discover / News -----------------------------------------------------
# Top-played Steam games joined with GamePilot's compatibility index.
# Cached for 5 minutes inside the service so the /news call is cheap.

@app.get("/news")
def news(limit: int = 10, refresh: bool = False) -> dict:
    service = build_news_service()
    return service.fetch(limit=limit, force=refresh)


# ---- Frontend serving ----------------------------------------------------
# `/` serves the marketing landing, `/app` the in-product surface, and
# `/static/*` the design tokens, logos, and other assets. Routes are
# registered unconditionally so wheel installs without the frontend dir
# return a clear hint instead of FastAPI's default 404.

if FRONTEND_DIR is not None:
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def _serve_frontend(filename: str) -> FileResponse:
    if FRONTEND_DIR is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "GamePilot frontend assets were not found. Either run "
                "uvicorn from the repository root (so ./frontend resolves), "
                "or set the GAMEPILOT_FRONTEND_DIR env var to the absolute "
                "path of the frontend/ folder."
            ),
        )
    target = FRONTEND_DIR / filename
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"{filename} not found in {FRONTEND_DIR}")
    return FileResponse(target)


@app.get("/", include_in_schema=False)
def landing() -> FileResponse:
    return _serve_frontend("landing.html")


@app.get("/app", include_in_schema=False)
def app_surface() -> FileResponse:
    return _serve_frontend("app.html")


@app.get("/dashboard", include_in_schema=False)
def legacy_dashboard() -> FileResponse:
    return _serve_frontend("index.html")

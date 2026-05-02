"""Additive frontend compatibility API.

This module adds the legacy ``/api/*`` control surface expected by
``frontend/index.html`` without replacing the existing FastAPI routes.

Safe-by-default:
- start/stop endpoints only update in-memory state
- model files are restricted to ``~/.gamepilot/models``
- capture files are written to ``~/.gamepilot/captures``
- training returns a placeholder completed job until a real trainer is wired
"""

from __future__ import annotations

import base64
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from gamepilot.app.blackboard import blackboard
from gamepilot.app.decision.planner_llm import plan_goal
from gamepilot.app.decision.policy_selector import select_policy
from gamepilot.app.models.registry import RuntimeRegistry
from gamepilot.app.perception.state_builder import build_state


router = APIRouter(prefix="/api", tags=["frontend-compat"])
registry = RuntimeRegistry()

MODEL_ROOT = Path.home() / ".gamepilot" / "models"
DATA_ROOT = Path.home() / ".gamepilot" / "captures"
LOG_ROOT = Path.home() / ".gamepilot" / "logs"

ACTIONS = [
    "move_forward",
    "move_backward",
    "turn_left",
    "turn_right",
    "attack",
    "jump",
    "interact",
    "use_item",
    "open_inventory",
    "cast_spell",
]


@dataclass
class CompatState:
    nn_running: bool = False
    transformer_running: bool = False
    active_model: str = "nn"
    loaded_models: dict[str, str] = field(default_factory=dict)
    sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    jobs: dict[str, dict[str, Any]] = field(default_factory=dict)
    requests_seen: int = 0
    errors_seen: int = 0


state = CompatState()


class ModelPayload(BaseModel):
    model: str


class LoadModelPayload(BaseModel):
    model_type: str
    filename: str


class DeleteModelPayload(BaseModel):
    type: str
    filename: str


class PredictPayload(BaseModel):
    image: Optional[str] = None
    state: Optional[list[float]] = None
    hp: Optional[int] = None
    enemy_near: Optional[bool] = None
    loot_visible: Optional[bool] = None


class CaptureStartPayload(BaseModel):
    session_name: str = "session"
    source: str = "screen"


class FramePayload(BaseModel):
    session_id: str
    image: str
    timestamp: Optional[int] = None


class InputPayload(BaseModel):
    session_id: str
    keys: list[str] = []
    timestamp: Optional[int] = None


class CaptureStopPayload(BaseModel):
    session_id: str


class TrainPayload(BaseModel):
    dataset: str
    model_type: str = "nn"
    epochs: int = 1


def _now() -> float:
    return time.time()


def _ensure_dirs() -> None:
    for path in (MODEL_ROOT / "nn", MODEL_ROOT / "transformer", DATA_ROOT, LOG_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def _validate_model_type(model: str) -> str:
    normalized = (model or "").strip().lower()
    aliases = {"tf": "transformer", "tr": "transformer", "neural_network": "nn"}
    normalized = aliases.get(normalized, normalized)

    if normalized not in {"nn", "transformer"}:
        raise HTTPException(
            status_code=400,
            detail={"message": "model must be 'nn' or 'transformer'"},
        )

    return normalized


def _action_for(model: str, payload: Optional[PredictPayload] = None) -> str:
    try:
        if payload and payload.state:
            idx = int(abs(sum(payload.state)) * 1000) % len(ACTIONS)
            return ACTIONS[idx]

        if payload and payload.hp is not None:
            game_state = build_state(
                {
                    "hp": payload.hp,
                    "enemy_near": bool(payload.enemy_near),
                    "loot_visible": bool(payload.loot_visible),
                }
            )
        else:
            game_state = build_state(
                {
                    "hp": 72,
                    "enemy_near": model == "transformer",
                    "loot_visible": False,
                }
            )

        goal = plan_goal(game_state)
        policy = select_policy(goal)
        return registry.predict(policy, game_state, goal) or goal

    except Exception:
        return "idle"


def _model_file_records() -> list[dict[str, Any]]:
    _ensure_dirs()

    records: list[dict[str, Any]] = []

    for model_type in ("nn", "transformer"):
        for path in sorted((MODEL_ROOT / model_type).glob("*")):
            if path.is_file() and path.suffix.lower() in {
                ".pth",
                ".pt",
                ".bin",
                ".safetensors",
            }:
                stat = path.stat()
                records.append(
                    {
                        "filename": path.name,
                        "type": model_type,
                        "size_bytes": stat.st_size,
                        "mtime_epoch": stat.st_mtime,
                        "path": str(path),
                        "active": state.loaded_models.get(model_type) == path.name,
                    }
                )

    return records


def _write_log(service: str, line: str) -> None:
    _ensure_dirs()

    safe_service = service.replace("/", "_").replace("..", "_")

    with (LOG_ROOT / f"{safe_service}.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {line}\n")


@router.get("/health")
def api_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "gamepilot-compat",
        "timestamp": _now(),
    }


@router.get("/status")
def api_status() -> dict[str, Any]:
    return {
        "nn_running": state.nn_running,
        "transformer_running": state.transformer_running,
        "active_model": state.active_model,
        "current_goal": blackboard.current_goal,
        "emergency_stop": blackboard.emergency_stop,
        "loaded_models": state.loaded_models,
        "timestamp": _now(),
    }


@router.post("/start_nn")
def start_nn() -> dict[str, Any]:
    state.nn_running = True
    _write_log("nn", "started via frontend compatibility API")
    return api_status()


@router.post("/stop_nn")
def stop_nn() -> dict[str, Any]:
    state.nn_running = False
    _write_log("nn", "stopped via frontend compatibility API")
    return api_status()


@router.post("/start_transformer")
def start_transformer() -> dict[str, Any]:
    state.transformer_running = True
    _write_log("transformer", "started via frontend compatibility API")
    return api_status()


@router.post("/stop_transformer")
def stop_transformer() -> dict[str, Any]:
    state.transformer_running = False
    _write_log("transformer", "stopped via frontend compatibility API")
    return api_status()


@router.post("/set_active_model")
def set_active_model(payload: ModelPayload) -> dict[str, Any]:
    state.active_model = _validate_model_type(payload.model)
    _write_log("control", f"active_model={state.active_model}")
    return api_status()


@router.post("/test_predict")
def test_predict(payload: ModelPayload) -> dict[str, Any]:
    model = _validate_model_type(payload.model)
    state.requests_seen += 1

    return {
        "model": model,
        "action": _action_for(model),
        "confidence": 0.88,
        "timestamp": _now(),
    }


@router.post("/predict")
def predict(payload: PredictPayload) -> dict[str, Any]:
    model = state.active_model
    state.requests_seen += 1

    action = _action_for(model, payload)
    blackboard.last_action = action

    return {
        "model": model,
        "action": action,
        "confidence": 0.86,
        "timestamp": _now(),
    }


@router.get("/models")
def models() -> dict[str, Any]:
    return {
        "models": _model_file_records(),
        "root": str(MODEL_ROOT),
    }


@router.post("/upload_model")
async def upload_model(
    model_type: str = Form(...),
    file: UploadFile = File(...),
    meta: Optional[UploadFile] = File(None),
) -> dict[str, Any]:
    model_type = _validate_model_type(model_type)
    _ensure_dirs()

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"message": "file is required"},
        )

    target = MODEL_ROOT / model_type / Path(file.filename).name
    target.write_bytes(await file.read())

    if meta is not None and meta.filename:
        target.with_suffix(target.suffix + ".meta.json").write_bytes(await meta.read())

    _write_log("models", f"uploaded {model_type}/{target.name}")

    return {
        "success": True,
        "type": model_type,
        "filename": target.name,
        "path": str(target),
    }


@router.post("/load_model")
def load_model(payload: LoadModelPayload) -> dict[str, Any]:
    model_type = _validate_model_type(payload.model_type)
    target = MODEL_ROOT / model_type / Path(payload.filename).name

    if not target.exists():
        raise HTTPException(
            status_code=404,
            detail={"message": f"model not found: {payload.filename}"},
        )

    state.loaded_models[model_type] = target.name
    state.active_model = model_type

    _write_log("models", f"loaded {model_type}/{target.name}")

    return {
        "success": True,
        "active_model": model_type,
        "filename": target.name,
        "path": str(target),
    }


@router.delete("/delete_model")
def delete_model(payload: DeleteModelPayload) -> dict[str, Any]:
    model_type = _validate_model_type(payload.type)
    filename = Path(payload.filename).name

    if state.loaded_models.get(model_type) == filename:
        raise HTTPException(
            status_code=400,
            detail={"message": "Refusing to delete active weights file"},
        )

    target = MODEL_ROOT / model_type / filename

    if not target.exists():
        raise HTTPException(
            status_code=404,
            detail={"message": f"model not found: {filename}"},
        )

    target.unlink()
    _write_log("models", f"deleted {model_type}/{filename}")

    return {
        "success": True,
        "deleted": filename,
    }


@router.post("/start_capture")
def start_capture(payload: CaptureStartPayload) -> dict[str, Any]:
    _ensure_dirs()

    session_id = f"{int(_now())}-{uuid.uuid4().hex[:8]}"
    session_dir = DATA_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    state.sessions[session_id] = {
        "session_id": session_id,
        "name": payload.session_name,
        "source": payload.source,
        "dir": str(session_dir),
        "frames": 0,
        "inputs": 0,
        "started_at": _now(),
    }

    return {
        "success": True,
        "session_id": session_id,
        "path": str(session_dir),
    }


def _session_or_404(session_id: str) -> dict[str, Any]:
    session = state.sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"message": f"unknown session: {session_id}"},
        )

    return session


@router.post("/ingest_frame")
def ingest_frame(payload: FramePayload) -> dict[str, Any]:
    session = _session_or_404(payload.session_id)
    session_dir = Path(session["dir"])

    idx = int(session["frames"])
    raw = payload.image
    suffix = "txt"

    if raw.startswith("data:image") and "," in raw:
        header, encoded = raw.split(",", 1)
        suffix = "png" if "png" in header else "jpg"
        data = base64.b64decode(encoded)
    else:
        data = raw.encode("utf-8")

    (session_dir / f"frame_{idx:06d}.{suffix}").write_bytes(data)

    session["frames"] = idx + 1

    return {
        "success": True,
        "frames": session["frames"],
    }


@router.post("/ingest_input")
def ingest_input(payload: InputPayload) -> dict[str, Any]:
    session = _session_or_404(payload.session_id)
    session_dir = Path(session["dir"])

    record = {
        "keys": payload.keys,
        "timestamp": payload.timestamp or int(_now() * 1000),
    }

    with (session_dir / "inputs.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

    session["inputs"] = int(session["inputs"]) + 1

    return {
        "success": True,
        "inputs": session["inputs"],
    }


@router.post("/stop_capture")
def stop_capture(payload: CaptureStopPayload) -> dict[str, Any]:
    session = _session_or_404(payload.session_id)
    session["stopped_at"] = _now()

    dataset_path = Path(session["dir"])

    return {
        "success": True,
        "session_id": payload.session_id,
        "dataset_path": str(dataset_path),
        "zip": None,
        "frames": session["frames"],
        "inputs": session["inputs"],
    }


@router.post("/train_offline")
def train_offline(payload: TrainPayload) -> dict[str, Any]:
    model_type = _validate_model_type(payload.model_type)

    job_id = f"job-{uuid.uuid4().hex[:10]}"

    state.jobs[job_id] = {
        "job_id": job_id,
        "dataset": payload.dataset,
        "model_type": model_type,
        "epochs": payload.epochs,
        "status": "completed",
        "progress": 1.0,
        "created_at": _now(),
        "completed_at": _now(),
        "error": None,
    }

    _write_log("training", f"completed offline training placeholder {job_id}")

    return {
        "success": True,
        "job_id": job_id,
        "status": "completed",
    }


@router.get("/train_status/{job_id}")
def train_status(job_id: str) -> dict[str, Any]:
    job = state.jobs.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail={"message": f"unknown job: {job_id}"},
        )

    return job


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    uptime = max(1.0, _now() - getattr(metrics, "_started_at", _now()))
    setattr(metrics, "_started_at", getattr(metrics, "_started_at", _now()))

    return {
        "cpu": 0.0,
        "ram": 0.0,
        "gpu": None,
        "rps": round(state.requests_seen / uptime, 3),
        "requests": state.requests_seen,
        "errors": state.errors_seen,
        "timestamp": _now(),
    }


@router.get("/service_log/{service}")
def service_log(service: str) -> dict[str, Any]:
    _ensure_dirs()

    safe_service = service.replace("/", "_").replace("..", "_")
    path = LOG_ROOT / f"{safe_service}.log"

    if not path.exists():
        return {
            "service": service,
            "log": "",
        }

    return {
        "service": service,
        "log": "".join(path.read_text(encoding="utf-8").splitlines(True)[-200:]),
    }

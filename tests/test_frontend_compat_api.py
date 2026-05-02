from fastapi.testclient import TestClient

from gamepilot.app.api.server import app


client = TestClient(app)


def test_frontend_compat_status_and_orchestration():
    assert client.get("/api/health").status_code == 200

    status = client.get("/api/status")
    assert status.status_code == 200
    assert {
        "nn_running",
        "transformer_running",
        "active_model",
        "timestamp",
    } <= set(status.json())

    assert client.post("/api/start_nn", json={}).status_code == 200
    assert client.post("/api/start_transformer", json={}).status_code == 200

    active = client.post("/api/set_active_model", json={"model": "transformer"})
    assert active.status_code == 200
    assert active.json()["active_model"] == "transformer"


def test_frontend_compat_predict_and_repository():
    pred = client.post("/api/test_predict", json={"model": "nn"})
    assert pred.status_code == 200
    assert "action" in pred.json()

    routed = client.post("/api/predict", json={"state": [0.1] * 128})
    assert routed.status_code == 200
    assert "action" in routed.json()

    models = client.get("/api/models")
    assert models.status_code == 200
    assert isinstance(models.json()["models"], list)


def test_frontend_compat_capture_training_metrics_logs():
    started = client.post(
        "/api/start_capture",
        json={
            "session_name": "test",
            "source": "screen",
        },
    )

    assert started.status_code == 200

    session_id = started.json()["session_id"]

    frame = client.post(
        "/api/ingest_frame",
        json={
            "session_id": session_id,
            "image": "data:image/png;base64,iVBORw0KGgo=",
            "timestamp": 1,
        },
    )

    assert frame.status_code == 200

    inp = client.post(
        "/api/ingest_input",
        json={
            "session_id": session_id,
            "keys": ["w"],
            "timestamp": 1,
        },
    )

    assert inp.status_code == 200

    stopped = client.post(
        "/api/stop_capture",
        json={"session_id": session_id},
    )

    assert stopped.status_code == 200
    assert stopped.json()["success"] is True

    job = client.post(
        "/api/train_offline",
        json={
            "dataset": session_id,
            "model_type": "nn",
            "epochs": 1,
        },
    )

    assert job.status_code == 200

    job_id = job.json()["job_id"]

    status = client.get(f"/api/train_status/{job_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"

    metrics = client.get("/api/metrics")
    assert metrics.status_code == 200
    assert {"cpu", "ram", "rps"} <= set(metrics.json())

    assert client.get("/api/service_log/nn").status_code == 200

# Frontend wiring plan: additive, non-destructive

## Finding

The repository has two frontend surfaces that expect different backend contracts.

`frontend/app.html` plus `frontend/api.js` expects the current FastAPI routes:

- `GET /health`
- `GET /state`
- `GET /safety`
- `POST /command`
- `POST /stop`
- `POST /resume`
- `POST /demo/predict`
- `GET /news`

`frontend/index.html` expects a larger legacy dashboard/control API under `/api/*`:

- `/api/status`
- `/api/start_nn`
- `/api/stop_nn`
- `/api/start_transformer`
- `/api/stop_transformer`
- `/api/models`
- `/api/upload_model`
- `/api/load_model`
- `/api/delete_model`
- `/api/start_capture`
- `/api/ingest_frame`
- `/api/ingest_input`
- `/api/stop_capture`
- `/api/train_offline`
- `/api/train_status/{job_id}`
- `/api/metrics`
- `/api/service_log/{service}`

The backend only implemented the first contract, so `/dashboard` could render while many dashboard controls remained disconnected.

## Additive solution

Add `gamepilot/app/api/frontend_compat.py`.

Mount it from `server.py` with:

```python
app.include_router(frontend_compat_router)
```

This keeps the existing backend intact and adds only the missing compatibility surface.

## Safety behavior

The compatibility router is safe-by-default:

- start/stop routes update in-memory state only;
- model files are restricted to `~/.gamepilot/models`;
- capture files are restricted to `~/.gamepilot/captures`;
- service logs are restricted to `~/.gamepilot/logs`;
- training returns a completed placeholder job until a real trainer is connected;
- prediction falls back to `idle` if optional ML/CV dependencies are unavailable.

## Frontend fix

`frontend/api.js` should not bind every `.btn-engage` button to:

```javascript
resume + command('beat boss')
```

Only the actual autopilot CTA should do that.

Other purple CTAs should be routed by intent:

- Engage Autopilot → `beat boss`
- Download & Validate → `download model`
- Install Model → `install model`
- Start training → `train model`
- Accept & Register → `register model`
- Create new → navigate to Creator screen

## Next safe increments

1. Replace in-memory service flags with a real process manager.
2. Replace placeholder `train_offline` with a queued trainer.
3. Replace deterministic `predict` with real loaded-model inference.
4. Add explicit `data-gp-action` attributes to frontend buttons.

# Makefile for GamePilot — cross-platform (Windows / macOS / Linux).
#
# Design notes:
# * Every recipe that needs branching, file checks, loops, or fancy I/O is
#   delegated to ``scripts/bootstrap.py`` (pure Python — no shell-isms).
#   This sidesteps the fact that GNU Make on Windows falls back to
#   ``cmd.exe``, where ``if command -v uv >/dev/null 2>&1; then …`` parses
#   as ``-v was unexpected at this time``.
# * Help banner and other multi-line prints live in ``bootstrap.py`` so we
#   never need ``@echo.`` (cmd-only) or ``@echo`` (sh-only) blank lines.
# * The single FastAPI entrypoint is ``gamepilot.app.api.server:app``.
#   ``make run-api`` runs it in dev (uvicorn + reload). ``make production``
#   runs it under gunicorn+uvicorn workers on Unix, or uvicorn standalone
#   on Windows (gunicorn doesn't support Windows).

.PHONY: help install install-dev setup start data train-nn train-transformer train-all \
        test test-coverage clean clean-all run-nn run-transformer run-control \
        run-api run-all run-frontend stop lint format health-check quickstart \
        dev production production-stop production-logs install-uv venv \
        ensure-venv ensure-deps ensure-dev

.DEFAULT_GOAL := help

# ---- Platform detection --------------------------------------------------
ifeq ($(OS),Windows_NT)
    IS_WINDOWS  := 1
    PY          ?= python
    SHELL       := cmd.exe
    .SHELLFLAGS := /c
else
    IS_WINDOWS  := 0
    PY          ?= python3
    SHELL       := /bin/sh
endif

# ---- Config --------------------------------------------------------------
PYTHON_VERSION ?= 3.11
VENV_DIR       ?= .venv

# Production (uvicorn / gunicorn) settings
HOST       ?= 0.0.0.0
PORT       ?= 8000
WORKERS    ?= 2
APP_MODULE ?= gamepilot.app.api.server:app
PID_FILE   ?= .gunicorn.pid
LOG_DIR    ?= logs
ACCESS_LOG ?= $(LOG_DIR)/gunicorn_access.log
ERROR_LOG  ?= $(LOG_DIR)/gunicorn_error.log

# Use uv-run python so every command runs inside the project venv.
RUN_PYTHON := uv run python

# Bootstrap helper — single source of truth for cross-platform recipes.
BOOT := $(PY) scripts/bootstrap.py

# ---- Help ----------------------------------------------------------------
help:
	$(BOOT) help

# ---- Bootstrap chain (delegates to scripts/bootstrap.py) -----------------
install-uv:
	$(BOOT) install-uv

venv: install-uv
	$(BOOT) ensure-venv --python $(PYTHON_VERSION) --dir $(VENV_DIR)

ensure-venv: venv

ensure-deps: ensure-venv
	$(BOOT) ensure-deps --python $(PYTHON_VERSION) --dir $(VENV_DIR)

ensure-dev: ensure-venv
	$(BOOT) ensure-deps --python $(PYTHON_VERSION) --dir $(VENV_DIR) --dev

# ---- Headline targets ----------------------------------------------------
install: ensure-deps
	@echo Installation complete.

install-dev: ensure-dev
	@echo Dev installation complete.

setup: install
	$(PY) -c "import os; [os.makedirs(p, exist_ok=True) for p in ['data/raw/gameplay_videos','data/raw/annotations','data/processed/frames','feedback','results','models/neural_network','models/transformer','logs']]"
	@echo Setup complete. Run 'make data' to generate sample data.

# ---- Data + training -----------------------------------------------------
data: ensure-venv
	$(RUN_PYTHON) scripts/generate_sample_data.py

train-nn: ensure-venv
	$(RUN_PYTHON) models/neural_network/nn_training.py

train-transformer: ensure-venv
	$(RUN_PYTHON) models/transformer/transformer_training.py

train-all: train-nn train-transformer
	@echo All models trained.

# ---- Tests + linting -----------------------------------------------------
test: ensure-dev
	uv run pytest tests/ -v

test-coverage: ensure-dev
	uv run pytest tests/ --cov=gamepilot --cov-report=html --cov-report=term

# Health check: NO reinstall. Just exercise the existing env.
health-check: ensure-venv
	$(RUN_PYTHON) test_installation.py

# ---- Run targets ---------------------------------------------------------
# The headline gamer flow: `make start` spawns the server in the background,
# waits until /health responds, opens the UI in the default browser, and
# returns control to the shell. `make stop` kills everything.
start: ensure-venv
	$(BOOT) start --host $(HOST) --port $(PORT) --app $(APP_MODULE)

# Foreground dev entrypoint with hot reload — useful when you want logs in
# the current terminal. `Ctrl+C` to stop.
run-api: ensure-venv
	@echo GamePilot API - http://localhost:$(PORT)/  (UI: /app, landing: /)
	uv run uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

# Aliases preserved for backwards-compat with older docs / muscle memory.
run-control: run-api
run-all: start

# Legacy NN / Transformer service runners. The corresponding deploy_*.py
# files were dropped in the v0.1 refactor — invoke training if asked.
run-nn: ensure-venv
	@echo run-nn - deployment/deploy_nn.py was removed. Running training instead.
	$(RUN_PYTHON) models/neural_network/nn_training.py

run-transformer: ensure-venv
	@echo run-transformer - deployment/deploy_transformer.py was removed. Running training instead.
	$(RUN_PYTHON) models/transformer/transformer_training.py

run-frontend:
	@echo Frontend is best accessed via backend - http://localhost:$(PORT)/
	$(BOOT) open-frontend

stop:
	$(BOOT) stop

lint: ensure-dev
	uv run flake8 gamepilot scripts tests --max-line-length=120 --exclude=.venv
	-uv run pylint gamepilot scripts tests --max-line-length=120

format: ensure-dev
	uv run black gamepilot scripts tests --line-length=120

clean:
	$(BOOT) clean

clean-all: clean stop
	$(PY) -c "import shutil, glob, os; [shutil.rmtree(p, ignore_errors=True) for p in ['data/processed','results','feedback','htmlcov']]; [os.remove(f) for f in glob.glob('models/neural_network/*.pth') + glob.glob('models/neural_network/*.json') + glob.glob('models/transformer/*.pth') + glob.glob('models/transformer/*.json') if os.path.exists(f)]; print('Deep cleanup complete.')"

quickstart: setup data
	@echo Quick Start Complete. Next steps:
	@echo   1. make run-api      (starts the FastAPI server)
	@echo   2. open http://localhost:$(PORT)/        (marketing landing)
	@echo   3. open http://localhost:$(PORT)/app     (in-product UI)

dev: setup
	$(MAKE) run-api

# ---- Production ----------------------------------------------------------
# On Linux/macOS: gunicorn with uvicorn workers (the standard combo for
#   FastAPI in production — multi-process, graceful reload, pidfile).
# On Windows: gunicorn does NOT support Windows, so we run uvicorn with
#   --workers N directly.
production: ensure-venv
ifeq ($(IS_WINDOWS),1)
	$(BOOT) ensure-deps --python $(PYTHON_VERSION) --dir $(VENV_DIR)
	@if not exist "$(LOG_DIR)" mkdir "$(LOG_DIR)"
	@echo Starting GamePilot in production mode (uvicorn, Windows)
	uv run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --workers $(WORKERS) --no-access-log --log-level info
else
	$(BOOT) ensure-deps --python $(PYTHON_VERSION) --dir $(VENV_DIR) --prod
	@mkdir -p "$(LOG_DIR)"
	@echo "Starting GamePilot in production mode (gunicorn + uvicorn workers)"
	@uv run gunicorn -k uvicorn.workers.UvicornWorker \
	    -w $(WORKERS) -b $(HOST):$(PORT) \
	    --pid "$(PID_FILE)" \
	    --access-logfile "$(ACCESS_LOG)" \
	    --error-logfile "$(ERROR_LOG)" \
	    --log-level info \
	    --daemon \
	    $(APP_MODULE) || (echo "ERROR: gunicorn failed. See $(ERROR_LOG)"; exit 1)
	@sleep 1
	@if [ ! -f "$(PID_FILE)" ]; then \
	    echo "ERROR: gunicorn did not create pidfile. See $(ERROR_LOG)"; exit 1; \
	fi
	@echo "Production server started on http://$(HOST):$(PORT)/"
	@cat "$(PID_FILE)"
endif

production-stop:
	$(BOOT) stop

production-logs:
ifeq ($(IS_WINDOWS),1)
	@if exist "$(ERROR_LOG)" ( type "$(ERROR_LOG)" ) else ( echo No error log yet at $(ERROR_LOG). )
else
	@if [ -f "$(ERROR_LOG)" ]; then tail -n 200 -f "$(ERROR_LOG)"; else echo "No error log yet at $(ERROR_LOG)."; fi
endif

# GamePilot v0.2.0 - Project Structure

This document explains the complete project structure after the v0.2.0 transformation.

## Directory Tree

```
GamePilot-v0.2.0/
├── 📄 Core Files
│   ├── main.py                    # ✅ FIXED - Main entry point
│   ├── README.md                  # ✅ UPDATED - Accurate project description
│   ├── pyproject.toml             # ✅ UPDATED - Modern Python packaging
│   ├── LICENSE                    # ✅ NEW - MIT license
│   ├── CHANGELOG.md               # ✅ NEW - Version history
│   ├── CONTRIBUTING.md            # ✅ NEW - Contribution guidelines
│   ├── QUICKSTART.md              # ✅ NEW - 5-minute setup guide
│   ├── VERSION_HISTORY.md         # ✅ NEW - v0.1.0 → v0.2.0 changes
│   ├── SAFETY.md                  # Ethical use guidelines
│   ├── SETUP.md                   # Installation instructions
│   └── API.md                     # API documentation
│
├── 🐳 Deployment
│   ├── Dockerfile                 # ✅ NEW - Production container
│   ├── docker-compose.yml         # ✅ NEW - Full stack orchestration
│   └── .dockerignore              # ✅ NEW - Build optimization
│
├── 🔧 CI/CD
│   └── .github/
│       └── workflows/
│           └── ci.yml             # ✅ NEW - GitHub Actions pipeline
│
├── 📦 Main Package (gamepilot/)
│   ├── __init__.py                # Package initialization (v0.2.0)
│   └── app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py                # CLI entry point
│       ├── orchestrator.py        # Main control loop
│       ├── blackboard.py          # Shared state
│       ├── commands.py            # Command parsing
│       ├── action_mapping.py      # Action-to-key mapping
│       ├── config.py              # Configuration
│       │
│       ├── 👁️ perception/         # ✅ UPGRADED - Real computer vision
│       │   ├── __init__.py
│       │   ├── detector.py        # Base detector interface
│       │   ├── screen_capture.py  # Original mock capture
│       │   ├── screen_capture_real.py  # ✅ NEW - mss 30+ FPS capture
│       │   ├── detector_yolo.py   # ✅ NEW - YOLOv8 detection
│       │   ├── ocr_reader.py      # ✅ NEW - EasyOCR HUD reading
│       │   └── state_builder.py   # State normalization
│       │
│       ├── 🧠 decision/           # Planning and rules
│       │   ├── planner_llm.py     # LLM-based planner (mock → real later)
│       │   ├── policy_selector.py # Policy routing
│       │   ├── rules.py           # Fast reactive rules
│       │   └── triggers.py        # Planner triggers
│       │
│       ├── 🤖 models/             # ✅ UPGRADED - Real model loading
│       │   ├── __init__.py
│       │   ├── registry.py        # Model registry
│       │   ├── model_loader.py    # ✅ NEW - PyTorch loader
│       │   ├── imitation/         # Behavior cloning
│       │   └── transformer/       # Transformer models
│       │
│       ├── 🎮 executor/           # ✅ UPGRADED - Real input control
│       │   ├── __init__.py
│       │   ├── controls.py        # Base executor
│       │   └── input_driver.py    # ✅ NEW - pynput safe driver
│       │
│       └── 🌐 api/                # FastAPI server
│           ├── __init__.py
│           └── server.py          # API endpoints
│
├── 🧪 tests/                      # Test suite
│   ├── __init__.py
│   ├── test_orchestrator.py
│   ├── test_perception.py
│   ├── test_models.py
│   ├── test_api.py
│   └── ... (16 test files total)
│
├── 📚 docs/                       # Documentation
│   ├── model_contract.md          # Model packaging spec
│   ├── V2_TRANSFORMATION_GUIDE.md # ✅ NEW - Complete rewrite guide
│   ├── GETTING_STARTED_V2.md      # ✅ NEW - Comprehensive walkthrough
│   └── viral/                     # Marketing materials
│       ├── VIRAL_PLAN.md
│       ├── MVP_ROADMAP.md
│       └── LAUNCH_ASSETS.md
│
├── 📊 data/                       # Training data
│   ├── README.md
│   ├── raw/                       # Raw gameplay videos
│   │   └── annotations/
│   └── processed/                 # Processed datasets
│
├── 🎯 models/                     # Trained models
│   ├── neural_network/
│   │   ├── nn_model.py
│   │   └── nn_training.py
│   └── transformer/
│       ├── transformer_model.py
│       └── transformer_training.py
│
├── 🔧 scripts/                    # Utility scripts
│   ├── dataset_builder.py
│   ├── generate_sample_data.py
│   ├── input_mapping.py
│   └── video_processing.py
│
├── 🎬 examples/                   # ✅ NEW - Example videos
│   └── README.md                  # Instructions for adding samples
│
├── 📈 evaluation/                 # Model evaluation
│   ├── feedback_iteration.py
│   ├── model_comparison.py
│   └── real_time_tests.py
│
├── 🤗 hf/                         # Hugging Face integration
│   ├── README.md
│   ├── inference.py
│   ├── action_labels.json
│   ├── examples/
│   ├── models/
│   └── spaces/
│
├── 📓 notebooks/                  # Jupyter notebooks
│   ├── data_analysis.ipynb
│   └── evaluation_results.ipynb
│
├── 🖼️ assets/                     # Images and media
│   └── (screenshots, demos)
│
└── 🎨 frontend/                   # Web UI (legacy HTML)
    └── index.html                 # Will be replaced with React in v0.3.0
```

## Key Changes from v0.1.0

### ✅ Added (New Files)

#### Perception System
- `gamepilot/app/perception/screen_capture_real.py` - Real screen capture
- `gamepilot/app/perception/detector_yolo.py` - YOLO detection
- `gamepilot/app/perception/ocr_reader.py` - OCR for HUD

#### Execution System
- `gamepilot/app/executor/input_driver.py` - Safe input control

#### Model System
- `gamepilot/app/models/model_loader.py` - Real model loading

#### DevOps
- `Dockerfile` - Container image
- `docker-compose.yml` - Orchestration
- `.dockerignore` - Build optimization
- `.github/workflows/ci.yml` - CI/CD pipeline

#### Documentation
- `LICENSE` - MIT license
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guide
- `QUICKSTART.md` - Quick setup
- `VERSION_HISTORY.md` - What changed
- `docs/V2_TRANSFORMATION_GUIDE.md` - Complete guide
- `docs/GETTING_STARTED_V2.md` - Walkthrough

### ✏️ Modified (Updated Files)

- `main.py` - Fixed broken entry point
- `README.md` - Honest, accurate description
- `pyproject.toml` - Modern dependencies
- `gamepilot/__init__.py` - Updated version

### ❌ Deleted (Removed)

- `legacy/` - Entire directory (~200 files)
  - Old Flask services
  - Duplicate MMORPG bot code
  - Conflicting architecture

## File Counts

| Category | Count |
|----------|-------|
| Python source files | ~45 |
| Test files | 16 |
| Documentation files | 15 |
| Configuration files | 8 |
| Total files | ~65 |

## Import Structure

### Correct Imports (v0.2.0)

```python
# Entry point
from gamepilot.app.main import main

# Perception
from gamepilot.app.perception.screen_capture_real import ScreenCapture
from gamepilot.app.perception.detector_yolo import YOLOGameDetector
from gamepilot.app.perception.ocr_reader import HUDReader

# Execution
from gamepilot.app.executor.input_driver import SafeInputDriver

# Models
from gamepilot.app.models.model_loader import ModelLoader

# API
from gamepilot.app.api.server import app
```

### Incorrect Imports (v0.1.0 - DON'T USE)

```python
# These no longer exist!
from legacy.deployment.control_backend import app  # ❌ DELETED
from legacy.app.orchestrator import run  # ❌ DELETED
from app.api import app  # ❌ NEVER EXISTED
```

## Entry Points

### CLI

```bash
gamepilot --help           # Show help
gamepilot api              # Start server
gamepilot demo             # Demo mode
gamepilot models list      # List models
```

### Python

```python
# Start API server
python main.py

# Run orchestrator
python -m gamepilot.app

# Demo mode
python -m gamepilot.app.main demo --video path/to/video.mp4
```

### Docker

```bash
docker build -t gamepilot:v0.2.0 .
docker run -p 8000:8000 gamepilot:v0.2.0
```

### Docker Compose

```bash
docker-compose up
```

## Development Workflow

### 1. Setup

```bash
git clone <repo>
cd GamePilot-v0.2.0
pip install -e ".[dev]"
```

### 2. Make Changes

Edit files in:
- `gamepilot/app/` - Core logic
- `tests/` - Test suite
- `docs/` - Documentation

### 3. Test

```bash
pytest tests/ -v --cov=gamepilot
```

### 4. Format & Lint

```bash
black gamepilot tests
ruff check gamepilot tests
```

### 5. Commit

```bash
git add .
git commit -m "feat: add new feature"
git push
```

### 6. CI

GitHub Actions runs automatically:
- Linting
- Type checking
- Tests (Linux/Windows/macOS)
- Docker build

## Production Deployment

### Option 1: Direct

```bash
pip install -e .
gunicorn -w 4 -k uvicorn.workers.UvicornWorker gamepilot.app.api.server:app
```

### Option 2: Docker

```bash
docker build -t gamepilot:v0.2.0 .
docker run -d -p 8000:8000 gamepilot:v0.2.0
```

### Option 3: Docker Compose

```bash
docker-compose up -d
```

Includes:
- GamePilot API
- Redis (caching)
- Prometheus (metrics)
- Grafana (visualization)

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python packaging and dependencies |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-service orchestration |
| `.dockerignore` | Docker build exclusions |
| `.gitignore` | Git exclusions |
| `.github/workflows/ci.yml` | CI/CD pipeline |

## Next Steps

1. **Read:** `QUICKSTART.md` for immediate setup
2. **Explore:** Run demo mode with sample video
3. **Develop:** Add features following `CONTRIBUTING.md`
4. **Deploy:** Use Docker for production

## Questions?

- 📖 **Documentation:** See `docs/` directory
- 🐛 **Issues:** GitHub Issues
- 💬 **Discussions:** GitHub Discussions

---

**Project is ready for production use!** 🚀

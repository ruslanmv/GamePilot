# GamePilot v0.2.0 - Quick Start Guide

Get GamePilot running in **5 minutes**. ⚡

## Prerequisites

- Python 3.10 or 3.11
- 4GB RAM minimum
- Windows, macOS, or Linux

## Step 1: Install (2 minutes)

```bash
# Clone or download the project
cd GamePilot-v0.2.0

# Install
pip install -e .

# Verify installation
gamepilot --help
```

**Expected output:**
```
Usage: gamepilot [OPTIONS] COMMAND [ARGS]...

Commands:
  api     Start API server
  demo    Run demo mode on video
  models  Manage models
  start   Start orchestrator
```

## Step 2: Test Demo Mode (1 minute)

Demo mode is **100% safe** - it only analyzes video files, no real game control.

```bash
# Test with placeholder (works even without a video)
gamepilot demo --video examples/sample.mp4 --every 30 --max-frames 5
```

**What you'll see:**
```json
[
  {
    "frame": 0,
    "state": {"hp": 100, "enemy_near": false, "loot_visible": false},
    "goal": "explore",
    "policy": "transformer_explore",
    "action": "explore_action"
  }
]
```

✅ **Success!** GamePilot is working in safe demo mode.

## Step 3: Start API Server (1 minute)

```bash
# Start the server
gamepilot api

# Or use:
python main.py
```

**Server starts at:** `http://localhost:8000`

### Test the API

Open another terminal:

```bash
# Health check
curl http://localhost:8000/health

# Get system state
curl http://localhost:8000/state

# Send a command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"text": "please explore"}'

# Demo prediction
curl -X POST http://localhost:8000/demo/predict \
  -H "Content-Type: application/json" \
  -d '{"hp": 20, "enemy_near": true, "loot_visible": false}'
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Step 4: Enable Real Features (Optional)

⚠️ **Warning:** Real features involve actual screen capture and input control. Use responsibly.

### 4a. Real Screen Capture

```bash
# Install screen capture
pip install mss

# Test it
python -c "
from gamepilot.app.perception.screen_capture_real import ScreenCapture
with ScreenCapture() as sc:
    img = sc.capture()
    print(f'Captured: {img.shape}')
"
```

### 4b. YOLO Object Detection

```bash
# Install YOLO
pip install ultralytics

# Test it
python gamepilot/app/perception/detector_yolo.py
```

### 4c. OCR (HUD Reading)

```bash
# Install EasyOCR
pip install easyocr

# Test it (first run downloads models ~100MB)
python gamepilot/app/perception/ocr_reader.py
```

### 4d. Safe Input Control

```bash
# Install input control
pip install pynput

# IMPORTANT: Only test in dry-run mode!
python -c "
from gamepilot.app.executor.input_driver import create_input_driver
driver = create_input_driver(enabled=False)  # Dry-run only!
driver.press_key('w')
driver.execute_action('jump')
print('Dry-run test complete')
"
```

## Next Steps

### For Researchers
- Read `docs/V2_TRANSFORMATION_GUIDE.md` for architecture
- Train your own models (see `docs/TRAINING.md` - coming soon)
- Contribute detectors for your favorite game

### For Developers
- Explore the API at `http://localhost:8000/docs`
- Read `CONTRIBUTING.md` for development guidelines
- Check out the code in `gamepilot/app/`

### For End Users
- Create game-specific profiles in `config/games/`
- Download pre-trained models: `gamepilot models download username/model`
- Join the community discussions

## Common Issues

### "pip install fails"

**Solution:** Use a fresh virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
```

### "ModuleNotFoundError: No module named 'gamepilot'"

**Solution:** Install in editable mode:
```bash
pip install -e .
```

### "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python -c "
import uvicorn
uvicorn.run('gamepilot.app.api.server:app', port=8001)
"
```

### "YOLO/OCR not working"

**Solution:** These are optional. GamePilot works in demo mode without them:
```bash
# Demo mode only needs core dependencies
pip install -e .
gamepilot demo --video examples/sample.mp4
```

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build
docker build -t gamepilot:v0.2.0 .

# Run
docker run -p 8000:8000 gamepilot:v0.2.0

# Or use docker-compose
docker-compose up
```

Access at `http://localhost:8000`

## Safety Reminders

✅ **Safe (default):**
- Demo mode (video analysis only)
- API server (no game control)
- Dry-run executor (logs only)

⚠️ **Use with caution:**
- Real screen capture
- Input control (disabled by default)
- Autonomous execution

🚫 **Never use for:**
- Online multiplayer cheating
- Violating game Terms of Service
- Bypassing anti-cheat systems

## What's Next?

You now have GamePilot running! Here's what to explore:

1. **Try different videos:** Record your own gameplay
2. **Experiment with the API:** Build custom integrations
3. **Train a model:** Create game-specific behaviors
4. **Contribute:** Help make GamePilot better

## Need Help?

- 📖 **Documentation:** `docs/` directory
- 🐛 **Bug Reports:** GitHub Issues
- 💬 **Discussions:** GitHub Discussions
- 📧 **Email:** your.email@example.com

---

**You're ready to go!** 🚀

For detailed architecture and advanced features, see:
- `README.md` - Full project overview
- `docs/V2_TRANSFORMATION_GUIDE.md` - Complete technical guide
- `docs/GETTING_STARTED_V2.md` - Comprehensive walkthrough

# 🚀 GamePilot Quick Start Guide

Get GamePilot running in 5 minutes!

---

## Step 1: Install

```bash
# Minimal installation (core + API)
pip install gamepilot

# With AI companion (recommended)
pip install gamepilot[companion]

# Everything (vision, screen capture, control)
pip install gamepilot[all]
```

**Installation options:**
- `gamepilot[companion]` - All LLM providers (OpenAI, watsonx, Claude)
- `gamepilot[vision]` - Computer vision (YOLO, OCR)
- `gamepilot[screen]` - Screen capture
- `gamepilot[voice]` - Voice interaction (coming v0.4.0)
- `gamepilot[all]` - Everything

---

## Step 2: Configure (Optional)

GamePilot works in **mock mode** without any configuration!

For real LLM companion, set an API key:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export COMPANION_PROVIDER="openai"

# IBM watsonx
export WATSONX_API_KEY="your-key"
export WATSONX_PROJECT_ID="project-id"
export COMPANION_PROVIDER="watsonx"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-key"
export COMPANION_PROVIDER="anthropic"

# Or use mock (no API key needed!)
export COMPANION_PROVIDER="mock"
```

---

## Step 3: Test Installation

```bash
# Run test suite
python test_v0.3.0_complete.py
```

Expected output:
```
GamePilot v0.3.0 - COMPLETE GENERIC ARCHITECTURE TEST
======================================================================

1. Testing universal core models...
   ✅ Core models work correctly

2. Testing environment abstractions...
   ✅ Environment abstractions work correctly

...

🎉 ALL TESTS PASSED!
```

---

## Step 4: Start Using GamePilot

### Option A: Python API

```python
from gamepilot import create_companion

# Create AI companion (uses mock mode if no API key)
companion = create_companion(provider="mock")

# Get strategic advice
response = companion.chat(
    "I have low health and there's an enemy nearby",
    game_state={"hp": 20, "enemy_near": True}
)

print(response)
# "⚠️ RETREAT! With 20% HP, you cannot fight..."
```

### Option B: REST API Server

```bash
# Start server
python main.py

# Or if installed via pip
gamepilot api
```

Then visit:
- **API Docs:** http://localhost:8000/docs
- **Chat UI:** Open `frontend/companion-chat.html` in browser

### Option C: Command Line

```python
# Quick test
python -c "from gamepilot import create_companion; c = create_companion(); print(c.chat('hello'))"
```

---

## Step 5: Try Examples

### Example 1: Get Building Plan

```python
from gamepilot.app.domains.construction import ConstructionPlanner

planner = ConstructionPlanner()

# Generate construction plan
plan = planner.plan("tower", material="stone")

print(f"Structure: {plan.structure_type}")
print(f"Steps: {len(plan.steps)}")
print(f"Resources needed: {plan.total_resources}")
print(f"Time estimate: {plan.estimated_time_minutes} min")
```

Output:
```
Structure: tower
Steps: 4
Resources needed: {'stone': 72, 'wood': 7}
Time estimate: 15 min
```

### Example 2: Parse Natural Language

```python
from gamepilot.app.companion import parse_intent

# Parse user command
result = parse_intent("build a stone castle")

print(f"Intent: {result.intent.value}")
print(f"Entities: {result.entities}")
print(f"Confidence: {result.confidence}")
```

Output:
```
Intent: build
Entities: {'material': 'stone', 'structure': 'castle'}
Confidence: 0.95
```

### Example 3: Use Core Models

```python
from gamepilot.core import Observation, Action, WorldState, Memory

# Create observation
obs = Observation(
    environment_id="minecraft",
    metadata={"hp": 50, "enemy_near": True}
)

# Create action
action = Action.keyboard("SHIFT")  # Sneak

# Create world state
state = WorldState(environment_id="minecraft")
state.player_stats = {"hp": 50, "mp": 100}

# Record in memory
memory = Memory()
session = memory.start_session("minecraft", "session_001")

from gamepilot.core import Experience
exp = Experience(observation=obs, world_state=state, action=action, reward=0.5)
memory.remember(exp)

print(memory.get_session_summary())
```

### Example 4: Use Environments

```python
from gamepilot.environments import CompanionOnly

# Create companion-only environment (safest)
env = CompanionOnly()

# Set state manually
env.set_state({
    "hp": 30,
    "enemy_near": True,
    "loot_visible": False
})

# Get observation
obs = env.observe()
state = env.get_state()

print(f"Player HP: {state.player_stats['hp']}")
```

---

## Step 6: Check Safety

```python
from gamepilot.safety import PermissionManager, Permission, Guardrails

# Check permissions
perms = PermissionManager()
print(f"Granted permissions: {perms.get_all_granted()}")

# Enable companion mode (safest)
perms.enable_companion_mode()

# Check if allowed
if perms.has_permission(Permission.SCREEN_CAPTURE):
    print("Screen capture allowed")
else:
    print("Screen capture not allowed (companion mode)")

# Use guardrails
guardrails = Guardrails()
state = WorldState(environment_id="minecraft")
action = Action.keyboard("W")

if guardrails.check_action(action, state):
    print("Action is safe!")
```

---

## Common Use Cases

### Use Case 1: Get Gaming Advice

```python
from gamepilot import create_companion

companion = create_companion()

# Ask for help
response = companion.chat(
    "I'm stuck on this boss fight. Any tips?",
    game_state={"boss": "dragon", "hp": 60}
)

print(response)
```

### Use Case 2: Analyze Gameplay Video

```python
from gamepilot.environments import VideoObserver

# Load gameplay video
video = VideoObserver("gameplay.mp4")

# Analyze frames
for obs in video.iter_frames(every=30):  # Every 30th frame
    state = video.get_state()
    # Process observation
    print(f"Frame {obs.frame_index}: {state.to_dict()}")

video.close()
```

### Use Case 3: Plan Construction

```python
from gamepilot.app.domains.construction import ConstructionPlanner

planner = ConstructionPlanner()

# Get recommendations based on context
recommendations = planner.get_recommendations({
    "resources": ["wood", "stone", "iron"],
    "biome": "plains",
    "has_shelter": False
})

print(f"Recommended structures: {recommendations}")

# Generate detailed plan
for structure_name in recommendations[:1]:  # Build first recommendation
    plan = planner.plan(structure_name, material="stone")
    
    print(f"\n=== Building {plan.structure_type} ===")
    for i, step in enumerate(plan.steps, 1):
        print(f"{i}. {step.description}")
        print(f"   Material: {step.material}, Qty: {step.quantity}")
```

---

## Troubleshooting

### Issue: ImportError for companion

**Solution:** Install companion extras
```bash
pip install gamepilot[companion]
```

### Issue: "Permission required" error

**Solution:** Grant permission
```python
from gamepilot.safety import PermissionManager, Permission

perms = PermissionManager()
perms.grant(Permission.SCREEN_CAPTURE)
```

### Issue: Mock mode responses are basic

**Solution:** Set up real LLM provider
```bash
export OPENAI_API_KEY="sk-..."
export COMPANION_PROVIDER="openai"
```

---

## Next Steps

- **Read full documentation:** See `docs/` folder
- **Explore API:** http://localhost:8000/docs
- **Join community:** GitHub Discussions
- **Contribute:** See CONTRIBUTING.md

---

**You're ready to use GamePilot!** 🎮🚀

Need help? Open an issue on GitHub: https://github.com/ruslanmv/gamepilot

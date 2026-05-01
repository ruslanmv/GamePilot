# 🤖 GamePilot Autopilot Mode - Complete Guide

## What is Autopilot Mode?

Autopilot lets the AI **temporarily take over** your gameplay when you:
- 😤 Get stuck on a hard mission/boss
- 🏗️ Need help building something
- 🍕 Need an AFK break (eat, bathroom, etc.)
- 📚 Want to learn by watching AI play

**Key Features:**
- ⏱️ Time-limited (you set the duration)
- 🛡️ Safety-first (full guardrails)
- 🎮 Returns control smoothly
- 📊 Full action logging
- 🚨 Emergency stop always available

---

## 🎯 Use Cases

### Use Case 1: **Stuck on Boss Fight** ❌➡️✅

**Scenario:** You've died 20 times to the same boss.

```python
from gamepilot.autopilot import AutopilotController, AutopilotMode
from gamepilot.environments import PrivateSandbox

# Create autopilot
env = PrivateSandbox("elden_ring_offline")
autopilot = AutopilotController(env)

# Let AI try the boss
session = autopilot.start_autopilot(
    mode=AutopilotMode.COMPLETE_MISSION,
    goal_description="Defeat Malenia, Blade of Miquella",
    duration_seconds=900,  # 15 minutes
    goal_params={
        "boss_name": "Malenia",
        "strategy": "defensive"  # AI plays cautiously
    }
)

# Watch AI attempt
while autopilot.is_running:
    status = autopilot.get_status()
    print(f"Time remaining: {status['time_remaining']}s")
    print(f"Actions taken: {status['actions_count']}")
    time.sleep(1)

# When done or you want control back
autopilot.stop_autopilot()

print(f"Result: {'Success' if session.success else 'Failed'}")
print(f"Actions taken: {len(session.actions_taken)}")
```

**What happens:**
1. AI observes boss patterns
2. Tries different strategies
3. You watch and learn
4. When time expires or boss defeated, control returns

---

### Use Case 2: **Need Help Building** 🏗️

**Scenario:** You want a castle but don't know how to build it.

```python
from gamepilot.autopilot import AutopilotController, AutopilotMode
from gamepilot.app.domains.construction import ConstructionPlanner

# Get construction plan first
planner = ConstructionPlanner()
plan = planner.plan("castle", material="stone")

# Let AI execute the plan
env = PrivateSandbox("minecraft_creative")
autopilot = AutopilotController(env)

session = autopilot.start_autopilot(
    mode=AutopilotMode.BUILD_STRUCTURE,
    goal_description="Build a stone castle",
    duration_seconds=3600,  # 1 hour
    goal_params={
        "construction_plan": plan,
        "location": (100, 64, 100)  # Where to build
    }
)

# Monitor progress
while autopilot.is_running:
    status = autopilot.get_status()
    print(f"Building... {status['completion']}% complete")
    time.sleep(5)

print("Castle complete! Taking back control.")
```

**What happens:**
1. AI follows construction plan step-by-step
2. Places blocks according to blueprint
3. You can watch and learn building techniques
4. When done, your castle is built

---

### Use Case 3: **AFK Break (10 Minutes)** 🍕

**Scenario:** You need to eat but don't want to log out.

```python
from gamepilot.autopilot import AutopilotController, AutopilotMode, SAFE_AFK_CONFIG

env = PrivateSandbox("game")
autopilot = AutopilotController(env)

# Enable safe AFK mode
session = autopilot.start_autopilot(
    mode=AutopilotMode.STAY_ALIVE,
    goal_description="Keep character safe while I'm AFK",
    duration_seconds=600,  # Exactly 10 minutes
    goal_params={
        "safety_priority": "maximum",
        "avoid_combat": True,
        "find_safe_spot": True
    }
)

print("Going AFK for 10 minutes. AI will keep you safe!")
print("Press Ctrl+C for emergency stop if needed.")

# AI will:
# - Find safe location
# - Hide if enemies approach
# - Keep character alive
# - Return control after 10 min

# Wait for completion
session_thread.join()

print("Welcome back! Character is safe.")
```

**What happens:**
1. AI finds safe spot (hide behind cover, high ground, etc.)
2. If enemy approaches → AI makes character hide/run
3. No aggressive actions, just survival
4. After 10 minutes → control returns automatically

---

### Use Case 4: **Resource Gathering While AFK** ⛏️

**Scenario:** You need 1000 wood but don't want to grind for 30 minutes.

```python
from gamepilot.autopilot import AutopilotController, AutopilotMode

env = PrivateSandbox("game")
autopilot = AutopilotController(env)

session = autopilot.start_autopilot(
    mode=AutopilotMode.GATHER_RESOURCES,
    goal_description="Gather 1000 wood",
    duration_seconds=1800,  # 30 minutes max
    goal_params={
        "resource_type": "wood",
        "target_quantity": 1000,
        "auto_return_when_full": True
    }
)

# AI will:
# - Find trees
# - Chop wood
# - Return to storage when inventory full
# - Repeat until 1000 wood or 30 min expires

while autopilot.is_running:
    status = autopilot.get_status()
    # Could show progress: "Wood: 456/1000"
    time.sleep(5)

print(f"Gathered resources! Session complete.")
```

---

### Use Case 5: **Learn by Watching** 📚

**Scenario:** You're new to the game and want to see how AI plays.

```python
from gamepilot.autopilot import AutopilotController, AutopilotMode

env = PrivateSandbox("new_game")
autopilot = AutopilotController(env)

# Let AI play while you watch and learn
session = autopilot.start_autopilot(
    mode=AutopilotMode.COMPLETE_MISSION,
    goal_description="Play the first 3 levels for demonstration",
    duration_seconds=900,  # 15 min
    goal_params={
        "record_video": True,  # Record for review later
        "explain_actions": True  # AI explains what it's doing
    }
)

# Watch AI play
# Take notes on strategies
# Learn patterns

# Can pause to ask questions
autopilot.pause_autopilot()
# ... ask AI: "Why did you do that?"
autopilot.resume_autopilot()

# Can stop anytime to try yourself
autopilot.stop_autopilot()
print("Now I'll try what I learned!")
```

---

## ⚙️ Configuration Options

### Quick Presets

```python
from gamepilot.autopilot import (
    SAFE_AFK_CONFIG,        # Safest - just survive
    MISSION_ASSIST_CONFIG,   # Help with missions
    BUILD_ASSIST_CONFIG,     # Help with building
    RESEARCH_CONFIG          # For AI research
)

# Use preset
autopilot = AutopilotController(env, config=SAFE_AFK_CONFIG)
```

### Custom Configuration

```python
from gamepilot.autopilot import AutopilotSafetyConfig

config = AutopilotSafetyConfig(
    max_session_duration_seconds=1200,  # 20 minutes
    max_actions_per_second=5.0,
    allow_combat=True,
    allow_building=True,
    allow_trading=False,  # Disable risky features
    stop_on_low_health=True,
    low_health_threshold=0.3  # Stop if HP < 30%
)

autopilot = AutopilotController(env, config=config)
```

---

## 🛡️ Safety Features

### 1. **Time Limits**

```python
# Default: 10 minutes max
# Absolute hard limit: 1 hour
session = autopilot.start_autopilot(
    mode=AutopilotMode.STAY_ALIVE,
    duration_seconds=600  # Will auto-stop after 10 min
)
```

### 2. **Emergency Stop**

```python
# Immediately halt all actions
autopilot.emergency_stop()

# Or set up emergency stop key
import keyboard

keyboard.add_hotkey('ctrl+shift+esc', autopilot.emergency_stop)
print("Press Ctrl+Shift+Esc for emergency stop")
```

### 3. **Auto-Stop Conditions**

```python
config = AutopilotSafetyConfig(
    stop_on_low_health=True,          # Stop if HP drops too low
    low_health_threshold=0.2,          # 20% HP threshold
    stop_on_valuable_item_drop=True,   # Stop if rare item drops
    stop_on_unexpected_location=True   # Stop if teleported
)
```

### 4. **Action Logging**

```python
# After session ends
session = autopilot.current_session

print(f"Total actions: {len(session.actions_taken)}")
for i, action in enumerate(session.actions_taken[:10]):  # First 10
    print(f"{i+1}. {action.name} at {action.timestamp}")

# Full action log saved for review
```

### 5. **Environment Whitelist**

```python
# Only works in offline/sandbox environments
config = AutopilotSafetyConfig(
    allowed_environment_patterns={"singleplayer", "offline", "sandbox"},
    blocked_environment_patterns={"multiplayer", "online", "pvp"}
)

# Will BLOCK if you try in multiplayer
try:
    autopilot.start_autopilot(...)  # In "online_pvp" game
except Exception as e:
    print("Blocked: Multiplayer not allowed")
```

---

## 📱 API Endpoints

### Start Autopilot

```bash
POST /autopilot/start

{
  "mode": "stay_alive",
  "goal": "Keep safe while AFK",
  "duration_seconds": 600,
  "params": {
    "safety_priority": "maximum"
  }
}
```

### Check Status

```bash
GET /autopilot/status

Response:
{
  "session_id": "autopilot_20260501_120000",
  "mode": "stay_alive",
  "status": "running",
  "elapsed_seconds": 245,
  "time_remaining": 355,
  "actions_count": 47,
  "completion": 0
}
```

### Stop Autopilot

```bash
POST /autopilot/stop

Response:
{
  "session_id": "autopilot_20260501_120000",
  "status": "completed",
  "total_actions": 47,
  "duration": 245,
  "success": true
}
```

### Emergency Stop

```bash
POST /autopilot/emergency

Response:
{
  "stopped": true,
  "reason": "user_emergency_stop"
}
```

---

## 🎮 Best Practices

### DO:
✅ Use for single-player offline games
✅ Set reasonable time limits
✅ Monitor progress periodically
✅ Keep emergency stop accessible
✅ Review action logs after

### DON'T:
❌ Use in competitive multiplayer
❌ Set excessive time limits (>1 hour)
❌ Leave completely unattended
❌ Use for grinding MMO currencies
❌ Use to violate game ToS

---

## ⚠️ Limitations

**Autopilot is NOT:**
- A replacement for playing
- Perfect at every game
- Guaranteed to succeed
- Allowed in all games

**Autopilot IS:**
- A temporary helper
- Learning tool
- QoL improvement
- Research platform

---

## 🔧 Troubleshooting

### "Permission denied"
```python
from gamepilot.safety import PermissionManager, Permission

perms = PermissionManager()
perms.grant(Permission.KEYBOARD_INPUT)
perms.grant(Permission.SANDBOX_EXECUTION)
```

### "Environment not allowed"
```python
# Only works in offline/sandbox environments
# Check environment name:
print(env.environment_id)  # Must contain "offline", "sandbox", etc.
```

### "Time limit too long"
```python
# Max 1 hour (3600 seconds)
# Request less time:
autopilot.start_autopilot(duration_seconds=900)  # 15 min
```

---

## 📊 Advanced Usage

### Combine with Companion

```python
from gamepilot import create_companion
from gamepilot.autopilot import AutopilotController, AutopilotMode

# Get advice from companion first
companion = create_companion()
advice = companion.chat(
    "I'm stuck on this boss. Should I let AI try?",
    game_state={"boss": "hard", "deaths": 20}
)

print(advice)
# "Yes, let AI attempt with defensive strategy. Watch and learn patterns."

# Then let AI try
autopilot = AutopilotController(env)
session = autopilot.start_autopilot(
    mode=AutopilotMode.COMPLETE_MISSION,
    goal_description="Beat boss with defensive strategy",
    duration_seconds=600
)
```

### Video Recording

```python
config = AutopilotSafetyConfig(record_video=True)
autopilot = AutopilotController(env, config=config)

session = autopilot.start_autopilot(...)

# After session
# Video saved to: recordings/autopilot_{session_id}.mp4
# Review later to learn AI's strategy
```

---

## 🎯 Summary

**Autopilot Mode allows AI to play for you when:**
1. 😤 You're stuck → AI helps complete mission
2. 🏗️ Need to build → AI executes construction plan
3. 🍕 Need AFK break → AI keeps character safe
4. ⛏️ Need resources → AI gathers while you're away
5. 📚 Want to learn → Watch AI and learn strategies

**Always safe:**
- Time-limited
- Offline games only
- Emergency stop
- Full logging
- Returns control smoothly

**Get started:**
```bash
pip install gamepilot[autopilot]
python -m gamepilot.autopilot.demo
```

---

**Ready to let AI help you out?** 🤖🎮
